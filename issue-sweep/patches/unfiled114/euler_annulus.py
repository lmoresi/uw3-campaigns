import numpy as np
import underworld3 as uw
import underworld3.utilities.place_surface as ps
from euler import chi
real = ps._occ_ladder_assembly_2d
def wrapped(*a, **k):
    pts, tris, cad = real(*a, **k)
    print("annulus assembly chi", chi(tris), "of", len(tris), "triangles")
    return pts, tris, cad
ps._occ_ladder_assembly_2d = wrapped
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=0.05, refinement=1, qdegree=2)
h = 0.025
for dip_deg, k in ((15, 0.0), (15, 1.0), (30, 3.0), (45, 0.5)):
    th, dip = np.radians(90), np.radians(dip_deg)
    r = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r
    try:
        ps.place_fault_ribbon_2d(base, [("Z", (1 - k*h) * r + (h * np.arange(7))[:, None] * d)], 2 * h, margin_rings=2, clearance=0.3, split=False, mesher="ladder")
    except Exception as e:
        print("  ", dip_deg, k, str(e)[:60])
