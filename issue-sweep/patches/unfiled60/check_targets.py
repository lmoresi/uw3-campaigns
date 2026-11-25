import sys, numpy as np, underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d, place_sheet
m = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.1, refinement=1, qdegree=2)
th, dip = np.radians(80.0), np.radians(35.0)
top = 0.9 * np.array([np.cos(th), np.sin(th)]); inward = -np.array([np.cos(th - dip), np.sin(th - dip)])
tr = top + (0.05 * np.arange(7))[:, None] * inward
for wdt in (0.1, 0.05, 0.035, 0.03, 0.025):
    try:
        place_fault_ribbon_2d(m, [("Fault", tr)], wdt, margin_rings=1, clearance=0.7, split=False, mesher="ladder")
        print("RIBBON width", wdt, "placed")
    except RuntimeError as e:
        print("RIBBON width", wdt, "refused:", str(e)[60:])
s = np.linspace(-0.2, 0.2, 5)
tris = []
for i in range(4):
    for j in range(4):
        a, b, c, d = 5 * i + j, 5 * i + j + 1, 5 * (i + 1) + j, 5 * (i + 1) + j + 1
        tris += [(a, b, d), (a, d, c)]
for cs in (0.11, 0.1, 0.09, 0.08):
    box = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=cs, regular=False, qdegree=2)
    pts = np.array([(0.5 + a, 0.5 + b, 0.87) for a in s for b in s])
    try:
        place_sheet(box.dm, pts, np.array(tris, dtype=np.int64), label="Fault")
        print("SHEET cell", cs, "placed")
    except RuntimeError as e:
        print("SHEET cell", cs, "refused:", str(e)[180:])
