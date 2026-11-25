"""UNFILED 60: the ribbon's wall refusal. The #893 probe's L1 placement (cell 0.1, trace top
0.9, interior, about 0.1 from the outer wall) is refused; print the message.

    python p_wall_message.py [top radius] [refinement]"""
import sys
import numpy as np
import underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d

r_top = float(sys.argv[1]) if len(sys.argv) > 1 else 0.9
ref = int(sys.argv[2]) if len(sys.argv) > 2 else 1
cell = 0.1
m = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=cell, refinement=ref, qdegree=2)
h = cell / 4
th, dip = np.radians(80.0), np.radians(35.0)
top = np.array([np.cos(th), np.sin(th)]) * r_top
inward = -np.array([np.cos(th - dip), np.sin(th - dip)])
n = int(0.3 / h)
t2 = top + (np.arange(n // 2 + 1) * 2 * h)[:, None] * inward
try:
    place_fault_ribbon_2d(m, [("Fault", t2)], 4 * h, margin_rings=1, clearance=0.7,
                          split=False, mesher="ladder")
    print("RES top", r_top, "refinement", ref, "placed")
except RuntimeError as err:
    print("RES top", r_top, "refinement", ref, "refused:", err)
