"""Tabulate #895 stage 1: one structural block against per-rank pieces.

    python collect_895_stage1.py records

One row per (case, h_b/S, np, arm). Ranks: which ranks hold each fault's band cells.
Patch rows: ASM rows on the busiest and the quietest rank. LU: MatLUFactorNum flops on
the busiest rank and in total, its time on the busiest rank. Solve: MatSolve time on the
busiest rank. RSS: peak memory per rank, max and min (MB). Times: hierarchy set-up, the
first solve and the repeat solve (s). its: velocity iterations, first and repeat solve.
dslip: max |V - V_ref| over both faults, against the 'one' arm at the same np and against
np 1.
"""
import glob
import json
import os
import sys

import numpy as np

root = sys.argv[1] if len(sys.argv) > 1 else "records"
recs = {}
for f in sorted(glob.glob(os.path.join(root, "S1_*.json"))):
    r = json.load(open(f))
    r["_slip"] = os.path.splitext(f)[0] + "_slip.npz"
    recs[(r["case"], r["n_rungs"], r["np"], r["blocks"])] = r


def slip_diff(a, b):
    if a is None or b is None or not (os.path.exists(a["_slip"]) and os.path.exists(b["_slip"])):
        return None
    A, B = np.load(a["_slip"]), np.load(b["_slip"])
    d = 0.0
    for k in A.files:
        if k.endswith("_V"):
            if A[k].shape != B[k].shape:
                return float("nan")
            d = max(d, float(np.abs(A[k] - B[k]).max()))
    return d


def ranks_of(cells):
    return ",".join(str(i) for i, c in enumerate(cells) if c) or "-"


hdr = ("case", "hb/S", "np", "arm", "conv", "its", "main@", "second@", "patch rows max/min",
       "LU flops max/sum", "LU t max", "MatSolve t max", "RSS max/min", "t fmg/1st/again",
       "dslip(one)", "dslip(np1)")
print(" | ".join(hdr))
for key in sorted(recs, key=lambda k: (k[0], k[1], k[2], k[3] != "one")):
    case, n, np_, arm = key
    r = recs[key]
    fin = r["level_smoothers"][-1] if r.get("level_smoothers") else {}
    rows = fin.get("asm_rows_per_rank") or [0]
    lu = r.get("lu_num") or {}
    flops = lu.get("flops") or [0.0]
    ms = (r.get("mat_solve") or {}).get("time_s") or [0.0]
    rss = r["peak_rss_mb_per_rank"]
    bands = r["band_cells_per_rank"]
    print(" | ".join(str(x) for x in (
        case, round(r["h_b_over_S"], 1), np_, arm, r["converged"],
        f'{r["vel_its_last"]}/{r["vel_its_last_again"]}',
        ranks_of(bands["main"]), ranks_of(bands["second"]),
        f"{max(rows)}/{min(rows)}", f"{max(flops):.3g}/{sum(flops):.3g}",
        max(lu.get("time_s") or [0.0]), max(ms), f"{max(rss)}/{min(rss)}",
        f'{r["t_fmg_s"]}/{r["t_solve_first_s"]}/{r["t_solve_again_s"]}',
        slip_diff(r, recs.get((case, n, np_, "one"))) if arm != "one" else "",
        slip_diff(r, recs.get((case, n, 1, "one"))))))
