"""Tabulate the add-on matrix row 7 records against their references.

    python collect_row7.py records            # every A7_* and B7_* record in records/

References: problem A, the unrefined ladder at the most rungs (h_b/S 48); problem B,
the unrefined ladder at the smallest S with the tip held at 0.012 (h_b/S 16). Each arm's
slip profile is compared at its own pair positions against the reference interpolated
there; the box's surface velocity and its vertical velocity at depth 0.05 likewise.
For the box, the velocity iterations are summed over every application in the log
('Linear rotfsN_fieldsplit_vel_ solve ... iterations K').
"""
import glob
import json
import os
import re
import sys

import numpy as np

VEL_LINE = re.compile(r"Linear rotfs\d+_fieldsplit_vel_ solve (?:converged|did not converge) due to (\w+) iterations (\d+)")


def load(folder):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "[AB]7_*.json"))):
        with open(path) as f:
            r = json.load(f)
        r["_tag"] = os.path.basename(path)[:-5]
        log = os.path.join(os.path.dirname(os.path.abspath(folder)), "logs", r["_tag"] + ".log")
        if r["problem"].startswith("B") and os.path.exists(log):
            with open(log) as f:
                its = [int(m.group(2)) for m in VEL_LINE.finditer(f.read())]
            r["vel_applications"] = len(its)
            r["vel_its_all_applications"] = int(sum(its))
        out.append(r)
    return out


def rel_diff(x, y, x_ref, y_ref):
    """Largest and rms difference of y(x) from the reference interpolated at x, both as
    a share of the reference's largest magnitude."""
    x, y = np.asarray(x), np.asarray(y)
    order = np.argsort(x_ref)
    yr = np.interp(x, np.asarray(x_ref)[order], np.asarray(y_ref)[order])
    scale = float(np.abs(y_ref).max()) or 1.0
    return float(np.abs(y - yr).max() / scale), float(np.sqrt(np.mean((y - yr) ** 2)) / scale)


def table_A(recs):
    ref = max([r for r in recs if r["depth"] == 0] or recs, key=lambda r: r["n_rungs"])
    rp = ref["slip_profile"]
    print(f"Problem A (h_b = {ref['h_b']:.5f}); reference: unrefined, {ref['n_rungs']} rungs, "
          f"h_b/S {ref['h_b_over_S']:.1f}, peak slip {ref['peak_slip']:.5f}\n")
    print("| depth | rings | rungs | h_b/S | h_loc/S | vel its (apps) | peak slip | integral | "
          "profile max / rms | patch rows | block rows | block solve s | solve s (again) | RSS MB |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(recs, key=lambda r: (r["depth"], r["rings"], r["n_rungs"])):
        pmax, prms = rel_diff(r["slip_profile"]["s"], r["slip_profile"]["V"], rp["s"], rp["V"])
        fb = r["fac_blocks_again"]
        rss = max(r["peak_rss_raw_per_rank"]) / (2 ** 20 if r["rss_unit"] == "bytes" else 2 ** 10)
        print(f"| {r['depth']} | {r['rings'] if r['depth'] else '-'} | {r['n_rungs']} | "
              f"{r['h_b_over_S']:.2f} | {r['h_local_over_S']:.2f} | "
              f"{r['vel_its_all_applications_again']} ({r['vel_applications_again']}) | "
              f"{r['peak_slip']:.5f} | {r['slip_integral']:.5f} | {pmax:.4f} / {prms:.4f} | "
              f"{r['fac_gate'].get('patch_owned_rows')} | {max(fb['block_rows'], default=0)} | "
              f"{fb.get('t_block_total_s_rank_max', float('nan')):.3f} | {r['t_solve_again_s']} | {rss:.0f} |")


def table_B(recs):
    unref = [r for r in recs if r["depth"] == 0 and r["tip_rule"] != "3S"]
    ref = min(unref or recs, key=lambda r: r["S"])
    rp, rs, rv = ref["slip_profile"], ref["surface_vx"], ref["vy_at_depth_0.05"]
    print(f"\nProblem B (h_b = {ref['h_b']:.5f}); reference: unrefined, S {ref['S']:.5f}, "
          f"h_b/S {ref['h_b_over_S']:.1f}, tip {ref['tip_depth']:.4f}, peak slip {ref['peak_slip']:.2f}\n")
    print("| depth | rings | S | h_b/S | h_loc/S | tip | Newton | vel its (apps) | peak slip | "
          "slip max / rms | surface vx max | vy(0.95) max | patch rows | block rows | "
          "block total s | solve s | RSS MB |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(recs, key=lambda r: (r["depth"], r["rings"], -r["S"], r["tip_rule"])):
        pmax, prms = rel_diff(r["slip_profile"]["s"], r["slip_profile"]["V"], rp["s"], rp["V"])
        smax, _ = rel_diff(r["surface_vx"]["x"], r["surface_vx"]["vx"], rs["x"], rs["vx"])
        vmax, _ = rel_diff(r["vy_at_depth_0.05"]["x"], r["vy_at_depth_0.05"]["vy"], rv["x"], rv["vy"])
        fb = r["fac_blocks"]
        smoothers = r.get("level_smoothers") or [{}]
        rss = max(r["peak_rss_raw_per_rank"]) / (2 ** 20 if r["rss_unit"] == "bytes" else 2 ** 10)
        tip = f"{r['tip_depth']:.4f}" + (" (3S)" if r["tip_rule"] == "3S" else "")
        print(f"| {r['depth']} | {r['rings'] if r['depth'] else '-'} | {r['S']:.5f} | "
              f"{r['h_b_over_S']:.2f} | {r['h_local_over_S']:.2f} | {tip} | "
              f"{r['newton_iterations']}{'' if r['converged'] else ' (unconverged)'} | "
              f"{r.get('vel_its_all_applications', '?')} ({r.get('vel_applications', '?')}) | "
              f"{r['peak_slip']:.2f} | {pmax:.4f} / {prms:.4f} | {smax:.4f} | {vmax:.4f} | "
              f"{smoothers[-1].get('asm_rows')} | {max(fb['block_rows'], default=0)} | "
              f"{fb.get('t_block_total_s_rank_max', float('nan')):.2f} | {r['t_solve_s']} | {rss:.0f} |")


if __name__ == "__main__":
    recs = load(sys.argv[1] if len(sys.argv) > 1 else "records")
    A = [r for r in recs if r["problem"].startswith("A")]
    B = [r for r in recs if r["problem"].startswith("B")]
    if A:
        table_A(A)
    if B:
        table_B(B)
