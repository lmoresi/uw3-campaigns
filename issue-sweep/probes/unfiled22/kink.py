"""UNFILED 22: does a sharp interior turn need its own vertex? Two-segment traces with a turn of
`angle` degrees at the middle, each arm 2.5 cells, cut with the tips pulled, tips + the corner
pulled, or every control point pulled (arms sampled at 0.5 cell)."""
import sys, warnings
import numpy as np
import underworld3 as uw
from underworld3.utilities import line_cut as lc
warnings.simplefilter("ignore")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=False)
h = 1 / 12
rng = np.random.default_rng(7)
for angle in (10, 30, 60, 90, 120, 150):
    res = {"tips": [0, 0], "tips+corner": [0, 0], "all": [0, 0]}
    for trial in range(20):
        c = rng.uniform(0.35, 0.65, 2); a0 = rng.uniform(0, 2 * np.pi)
        d1 = np.array([np.cos(a0), np.sin(a0)]); a1 = a0 + np.radians(180 - angle) * rng.choice([-1, 1])
        d2 = np.array([np.cos(a1), np.sin(a1)])
        arm = np.linspace(0, 2.5 * h, 6)
        P = np.vstack([c + arm[::-1, None] * d1, c + arm[1:, None] * d2])   # corner at index 5
        import corners_plugin as cp
        for name, idx in (("tips", [0, len(P) - 1]), ("tips+corner", [0, 5, len(P) - 1]), ("all", list(range(len(P)))), ("rule45", None)):
            res.setdefault(name, [0, 0])
            try:
                tg = cp.corners(P) if idx is None else P[idx]
                dm = cp._orig(mesh.dm, tg, on_shared="note")
                lc.cut_along_lines(dm, [P])
                res[name][0] += 1
            except Exception as e:
                res[name][1] += 1
    print("KINK turn", angle, "deg  ok/fail:", res, flush=True)
