"""A ribbon near a box corner: its cavity may run along two walls at once.

Unit box, regular simplex mesh of cellSize 1/20 (h = 0.05), a ladder ribbon of
width 2h, a 7-point trace spaced h, margin 2 rings, clearance 0.3, split.  The
trace's top sits a cells below Top and b cells left of Right; it runs down and
left at 45 degrees, so the band's extended end points into the corner.

For each (a, b): the outcome, and on a placement every boundary edge must carry
the wall label of the side it lies on, the corner vertex must stay, and the
smallest angles are printed (all cells; cells touching a wall within 0.3 of the
corner).
"""
import argparse

import numpy as np

import underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d

ap = argparse.ArgumentParser()
ap.add_argument("--cells", type=float, default=20)
ap.add_argument("--a", type=str, default="2,2.5,3,3.5,4,5")
ap.add_argument("--regular", type=int, default=1)
args = ap.parse_args()

h = 1.0 / args.cells
width = 2 * h
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1),
                                         cellSize=h, regular=bool(args.regular))
SIDES = {"Top": (1, 1.0), "Bottom": (1, 0.0), "Left": (0, 0.0), "Right": (0, 1.0)}


def checks(mesh):
    dm = mesh.dm
    vS, vE = dm.getDepthStratum(0)
    eS, eE = dm.getDepthStratum(1)
    cS, cE = dm.getHeightStratum(0)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    value = {b.name: b.value for b in mesh.boundaries}
    bad = 0
    for e in range(eS, eE):
        if dm.getSupportSize(e) != 1:
            continue
        v = [int(q) - vS for q in dm.getCone(e)]
        for name, (ax, at) in SIDES.items():
            if (np.abs(X[v, ax] - at) < 1e-9).all():
                if dm.getLabel(name).getValue(e) != value[name]:
                    bad += 1
    corner = int((np.linalg.norm(X - [1.0, 1.0], axis=1) < 1e-12).sum())
    amin, anear = 180.0, 180.0
    for c in range(cS, cE):
        cl = dm.getTransitiveClosure(c)[0]
        P = X[cl[(cl >= vS) & (cl < vE)] - vS]
        ang = []
        for i in range(3):
            u, w = P[(i + 1) % 3] - P[i], P[(i + 2) % 3] - P[i]
            ang.append(np.degrees(np.arccos(np.clip(u @ w / np.linalg.norm(u) / np.linalg.norm(w), -1, 1))))
        amin = min(amin, min(ang))
        on_wall = ((np.abs(P - 1.0) < 1e-9) | (np.abs(P) < 1e-9)).any()
        if on_wall and np.linalg.norm(P.mean(0) - [1, 1]) < 0.3:
            anear = min(anear, min(ang))
    return (f"wall-mislabelled {bad} corner-vertex {corner} minangle {amin:.1f} "
            f"near-corner-minangle {anear:.1f} plus {'FaultPlus' in value}")


d = np.array([-1.0, -1.0]) / np.sqrt(2)
for a in [float(x) for x in args.a.split(",")]:
    for b in (a, a + 1.0, a + 2.0):
        top = np.array([1 - b * h, 1 - a * h])
        trace = top + (h * np.arange(7))[:, None] * d
        ext = top - 2 * h * d
        rail = 0.5 * width * np.array([d[1], -d[0]])
        corners = [ext + rail, ext - rail]
        g_top = min(1 - c[1] for c in corners) / h
        g_right = min(1 - c[0] for c in corners) / h
        tag = f"a={a:3.1f} b={b:3.1f}  band corner gap: Top {g_top:+.2f} h, Right {g_right:+.2f} h"
        try:
            mesh, info = place_fault_ribbon_2d(base, [("Fault", trace)], width, margin_rings=2,
                                               clearance=0.3, split=True, mesher="ladder")
            out = "placed  " + checks(mesh)
        except Exception as exc:  # noqa: BLE001 - the probe records it
            out = f"REFUSED {type(exc).__name__}: {str(exc)[:200]}"
        print(f"{tag} | {out}", flush=True)
