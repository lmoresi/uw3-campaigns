"""The overnight queue's results in one table: python night_report.py > runs/NIGHT_REPORT.md"""
import glob, os, subprocess, numpy as np
D = 1.0
print("# Overnight queue, 2026-10-04/05\n\nSettled window t = 4 to 8 where available, else the last time unit; cd/cl per unit span (D = 0.1, U = 1).\n")
print("| run | Re | Wi | scheme | res | reached t | cd mean | cl amp | St | note |\n|---|---|---|---|---|---|---|---|---|---|")
for log in sorted(glob.glob("runs/*.log")):
    r = os.path.basename(log)[:-4]
    if not r.startswith(("re100", "re200", "par_check")): continue
    f = f"runs/{r}/forces.csv"
    if not os.path.exists(f): continue
    a = np.genfromtxt(f, delimiter=",", names=True)
    if a.size < 10: continue
    t_end = float(a["t"][-1]); t0 = 4.0 if t_end >= 5.0 else max(t_end - 1.0, 0.0)
    m = (a["t"] >= t0) & (a["t"] <= t_end)
    cl = a["cl"][m]; t = a["t"][m]
    up = np.flatnonzero((cl[:-1] < 0) & (cl[1:] >= 0))
    St = f"{(len(up) - 1) / (t[up[-1]] - t[up[0]]) * 0.1:.3f}" if len(up) > 2 else "-"
    note = subprocess.run(["grep", "-h", f" {r} ", "runs/night_queue.log"], capture_output=True, text=True).stdout.strip().splitlines()
    note = note[-1].split(" ", 2)[-1][:60] if note else ""
    import re as _re
    Re = "100" if r.startswith("re100") else "200" if r.startswith("re200") else "200"
    wi = _re.search(r"Wi(\d+)", r); Wi = {"05": "0.5", "1": "1", "2": "2", "4": "4"}.get(wi.group(1), wi.group(1)) if wi else ("0" if "newt" in r else "0.5")
    scheme = ("Newtonian" if "newt" in r else "SUPG + Eulerian stress + DEVSS" if "grid" in r else "SUPG + forward stress (global)" if "supg_fwn" in r
              else "forward + cell-fit stress" if "cell" in r else "forward, both global (P2 beta 0.1)" if "global2" in r
              else "forward, FENE-P L2 100 (stress global)" if "fene" in r else "forward, Oldroyd-B (stress global)")
    res = "40" if "r40" in r else "20" if "r20" in r else "20"
    print(f"| {r} | {Re} | {Wi} | {scheme} | {res} | {t_end:.2f} | {a['cd'][m].mean():.3f} | {0.5 * (cl.max() - cl.min()):.3f} | {St} | {note} |")
