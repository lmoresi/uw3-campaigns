"""Krylov iterations per Newton step against refinement, tight FMG (every linear
solve to rtol 1e-8, no Eisenstat-Walker), for the micromorphic runs (beta 0.1, xi 0,
l = 0.25 .. 2 km) and the plain-law control (xi = 0.03, no micromorphic field).

Counts are read from the runs' logs: every "Linear ... solve" line after the last
"0 SNES Function norm" (the main Newton solve, not the viscous seed). A solve that
stops on ATOL (a late step whose residual is already below the absolute tolerance)
is counted but flagged; one that hits the cap is reported as such. Band widths are
the integral width, background outside +-9 km. h_k is the band-crossing element
size on FMG level k: about 4.24 km / 2^k (measured 529 m at ref 3), and the
hierarchy runs from level 0 (the base mesh) to the run's refinement.
Writes ../results/fmg_table.json and prints the markdown table."""
import glob
import json
import os
import re

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
NLS = os.path.join(_here, "..")
H0_KM = 4.24
LOGS = {
    ("micro", 1.0, 1): "results/fmg/micro_ref1_tight.log",
    ("micro", 1.0, 2): "results/fmg/micro_ref2_tight.log",
    ("micro", 1.0, 3): "results/fmg/micro_ref3_tight.log",
    ("micro", 1.0, 4): "results/fmg/micro_ref4_l1_tight_gridseq.log",
    ("micro", 1.0, 5): "jobs/logs/micro_ref5_l1_tight_np16.log",
    ("micro", 0.5, 4): "results/fmg/micro_ref4_l0.5_tight_gridseq.log",
    ("micro", 0.5, 5): "jobs/logs/micro_ref5_l0.5_tight_np16.log",
    ("micro", 2.0, 4): "results/fmg/micro_ref4_l2_tight_gridseq.log",
    **{("micro", l, r): f"jobs/logs/fmgtable_micro_ref{r}_l{l:g}.log"
       for l in (0.25, 0.5, 2.0) for r in (1, 2, 3)},
    **{("plain", 0.0, r): f"jobs/logs/fmgtable_plain_ref{r}.log" for r in (1, 2, 3)},
    **{("coss", l, r): f"jobs/logs/fmgtable_coss_ref{r}_l{l:g}.log"
       for l in (0.5, 1.0) for r in (1, 2, 3)},
    **{("coss", l, 4): f"jobs/logs/coss_ref4_l{l:g}_np8.log" for l in (0.5, 1.0)},
    **{("coss", l, 5): f"jobs/logs/coss_ref5_l{l:g}_np16.log" for l in (0.5, 1.0)},
}
LINE = re.compile(r"Linear \S+ solve (converged|did not converge) due to (\w+) iterations (\d+)")
SUMMARY = re.compile(r"\[(?:micromorphic|plain|cosserat)\].*?: (\w+) its (\d+)")


def krylov(path):
    text = open(os.path.join(NLS, path), errors="replace").read().splitlines()
    starts = [i for i, s in enumerate(text) if re.match(r"\s*0 SNES Function norm", s)]
    if not starts:
        return None
    solves = [LINE.search(s) for s in text[starts[-1]:]]
    solves = [(m.group(2), int(m.group(3))) for m in solves if m]
    summary = [SUMMARY.search(s) for s in text]
    summary = [m for m in summary if m]
    killed = any("MPI SUPERVISOR: no output" in s for s in text)
    outcome = (summary[-1].group(1) if summary else
               "killed: the next linear solve gave no output for 1 h" if killed else "running")
    return dict(solves=solves, outcome=outcome,
                nl_its=int(summary[-1].group(2)) if summary else None)


widths = {("micro", r["ref"], r["l_km"]): r["W_km"]
          for r in json.load(open(os.path.join(NLS, "results", "current_widths.json")))}
_coss = os.path.join(NLS, "results", "current_widths_cosserat.json")
if os.path.exists(_coss):
    widths.update({("coss", r["ref"], r["l_km"]): r["W_km"] for r in json.load(open(_coss))})
rows = []
for (kind, l_km, ref), path in sorted(LOGS.items()):
    if not os.path.exists(os.path.join(NLS, path)):
        continue
    k = krylov(path)
    if k is None or not k["solves"]:
        continue
    its = [n for _, n in k["solves"]]
    rtol_its = [n for reason, n in k["solves"] if reason == "CONVERGED_RTOL"]
    W = widths.get((kind, ref, l_km))
    if kind == "plain":
        found = sorted(glob.glob(os.path.join(NLS, "results", "plain",
                                              f"plain_ref{ref}_xi0.03_production_tight*.json")))
        W = json.load(open(found[0]))["W_outside9_km"] if found else None
    # the coarsest FMG level whose band-crossing element fits 2 into W
    level = (next((j for j in range(ref + 1) if W / (H0_KM / 2 ** j) >= 2), None)
             if W else None)
    rows.append(dict(kind=kind, l_km=l_km, ref=ref, log=path, outcome=k["outcome"],
                     nl_its=k["nl_its"], krylov=k["solves"], median=float(np.median(its)),
                     max=int(max(its)), median_rtol=(float(np.median(rtol_its)) if rtol_its else None),
                     capped=any(r == "DIVERGED_ITS" for r, _ in k["solves"]),
                     W_km=W, h_fine_m=1e3 * H0_KM / 2 ** ref, resolving_level=level))
json.dump(rows, open(os.path.join(NLS, "results", "fmg_table.json"), "w"), indent=1)

print("| model | ref | h in band (m) | W (km) | W / h | coarsest level with W ≥ 2h | Krylov per Newton step | median / max | outcome |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    model = {"micro": f"micromorphic, l = {r['l_km']:g} km",
             "coss": f"Cosserat, l = {r['l_km']:g} km",
             "plain": "plain, ξ = 0.03"}[r["kind"]]
    steps = ", ".join(f"{n}{'*' if reason == 'CONVERGED_ATOL' else ''}"
                      f"{'(cap)' if reason == 'DIVERGED_ITS' else ''}" for reason, n in r["krylov"])
    # a width only where this run, or (micromorphic and Cosserat) the table's exact-LU
    # run at this (ref, l), converged; the plain law's ref-3 iterate did not
    usable = r["W_km"] and not (r["kind"] == "plain" and not r["outcome"].startswith("CONVERGED"))
    W = f"{r['W_km']:.2f}" if usable else "—"
    ratio = f"{r['W_km'] / (r['h_fine_m'] / 1e3):.0f}" if usable else "—"
    lvl = (f"{r['resolving_level']} ({1e3 * H0_KM / 2 ** r['resolving_level']:.0f} m)"
           if usable and r["resolving_level"] is not None else ("none" if usable else "—"))
    print(f"| {model} | {r['ref']} | {r['h_fine_m']:.0f} | {W} | {ratio} | {lvl} | {steps} | "
          f"{r['median']:.0f} / {r['max']} | {r['outcome']} ({r['nl_its']}) |")
