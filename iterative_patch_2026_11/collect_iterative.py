"""Tabulate the iterative-patch probe records (experiments 1 and 2, and the ratio 1-2
points) against the LU arm at the same problem, ratio and cut.

    python collect_iterative.py records            # every A_* and B_* record in records/

Problem A (the linear fixture): velocity iterations summed over the second solve's
applications, that solve's time, and the block KSP's applications and iterations in
it. Problem B (the box): Newton steps, the velocity iterations summed over each
Newton step's last application, the steps that hit the 200 cap, and the solve time.
Records written before campaigns ed513c1 on Linux divided ru_maxrss (KiB) by 2**20;
their RSS is scaled by 1024 here and marked *.
"""
import glob
import json
import os
import sys


def spec_label(s):
    if s.get("block") == "lu":
        arm = "LU"
    else:
        pc = s.get("block_pc", "?")
        pc = f"{pc}({s.get('ilu_levels')})" if pc == "ilu" else pc
        rtol = float(s.get("rtol", 0))
        arm = f"{pc} rtol {rtol:g}" if rtol > 0 else f"{pc} {s.get('max_it')} steps"
    extra = []
    if float(s.get("strip", 0) or 0) > 0:
        extra.append(f"strip {s['strip']}")
    if int(s.get("slip", 0) or 0):
        extra.append("slip")
    return arm + (" + " + ", ".join(extra) if extra else "")


def rss_mb(r):
    v = max(r.get("peak_rss_mb_per_rank") or [0])
    return (f"{v * 1024:.0f}*" if 0 < v < 10 else f"{v:.0f}")


def main(folder):
    recs = []
    for path in sorted(glob.glob(os.path.join(folder, "[AB]_*.json"))):
        with open(path) as f:
            r = json.load(f)
        r["_tag"] = os.path.basename(path)[:-5]
        r["_A"] = r["problem"].startswith("A")
        r["_cut"] = int(r.get("spec", {}).get("cut", 0) or 0)
        recs.append(r)
    # the reference: plain LU blocks, no strips and no slip space
    lu = {(r["_A"], round(r["h_b_over_S"], 2), r["_cut"]): r for r in recs
          if r.get("spec", {}).get("block") == "lu"
          and not float(r["spec"].get("strip", 0) or 0) and not int(r["spec"].get("slip", 0) or 0)}

    for problem in (True, False):
        rows = [r for r in recs if r["_A"] == problem]
        if not rows:
            continue
        if problem:
            print("\nProblem A (linear): velocity its summed over the second solve; x LU at the "
                  "same ratio and cut\n")
            print("| h_b/S | cut | arm | conv | vel its (x LU) | block apps / its | blocks | "
                  "largest block | t_setup s | t_solve s (x LU) | RSS MB | tag |")
            print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        else:
            print("\nProblem B (box): Newton; velocity its summed over each Newton step's last "
                  "application; x LU at the same ratio and cut\n")
            print("| h_b/S | cut | arm | conv | Newton | vel its (x LU) | caps 200 | blocks | "
                  "largest block | t_solve s (x LU) | RSS MB | tag |")
            print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in sorted(rows, key=lambda r: (r["h_b_over_S"], r["_cut"], r["_tag"])):
            ref = lu.get((r["_A"], round(r["h_b_over_S"], 2), r["_cut"]))
            patch = r.get("patch") or {}
            if problem:
                its = r.get("vel_its_all_applications_again")
                its_ref = ref.get("vel_its_all_applications_again") if ref else None
                t, t_ref = r.get("t_solve_again_s"), ref.get("t_solve_again_s") if ref else None
            else:
                its = r.get("vel_its_last_total")
                its_ref = ref.get("vel_its_last_total") if ref else None
                t, t_ref = r.get("t_solve_s"), ref.get("t_solve_s") if ref else None
            x_its = f" ({its / its_ref:.2f})" if its and its_ref else ""
            x_t = f" ({t / t_ref:.2f})" if t and t_ref else ""
            common = (f"| {r['h_b_over_S']:.2f} | {r['_cut']} | {spec_label(r.get('spec', {}))} | "
                      f"{'T' if r.get('converged', True) else 'F'} | ")
            if problem:
                bw = r.get("block_work_again") or {}
                print(common + f"{its}{x_its} | {bw.get('block_applications', '-')} / "
                      f"{bw.get('block_iterations', '-')} | {patch.get('blocks', '-')} | "
                      f"{patch.get('block_rows_max', '-')} | {r.get('t_setup_s_est', '-')} | "
                      f"{t}{x_t} | {rss_mb(r)} | {r['_tag']} |")
            else:
                print(common + f"{r.get('newton_iterations')} | {its}{x_its} | "
                      f"{r.get('vel_caps_200', '-')} | {patch.get('blocks', '-')} | "
                      f"{patch.get('block_rows_max', '-')} | {t}{x_t} | {rss_mb(r)} | {r['_tag']} |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "records")
