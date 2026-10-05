"""Drag, lift and shedding frequency of each run from forces.csv, over a common window."""
import sys, numpy as np
t0, t1 = float(sys.argv[1]), float(sys.argv[2])
D, U = 0.1, 1.0
print(f"window t = {t0} to {t1}")
print(f"{'run':15s} {'cd mean':>8s} {'cd amp':>7s} {'cl amp':>7s} {'St':>6s} {'cycles':>6s}")
for run in sys.argv[3:]:
    a = np.genfromtxt(f"runs/{run}/forces.csv", delimiter=",", names=True)
    m = (a["t"] >= t0) & (a["t"] <= t1)
    t, cd, cl = a["t"][m], a["cd"][m], a["cl"][m]
    if t.size < 10 or t[-1] < t1 - 0.05:
        print(f"{run:15s} (reaches t = {a['t'][-1]:.2f} only)"); continue
    up = np.flatnonzero((cl[:-1] < 0) & (cl[1:] >= 0))           # upward zero crossings
    tz = t[up] - cl[up] * (t[up + 1] - t[up]) / (cl[up + 1] - cl[up])
    St = (len(tz) - 1) / (tz[-1] - tz[0]) * D / U if len(tz) > 2 else float("nan")
    print(f"{run:15s} {cd.mean():8.3f} {0.5*(cd.max()-cd.min()):7.3f} {0.5*(cl.max()-cl.min()):7.3f} {St:6.3f} {len(tz)-1:6d}")
