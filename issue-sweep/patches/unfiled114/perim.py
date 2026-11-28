import numpy as np
import underworld3 as uw
import underworld3.utilities.place_surface as ps
real = ps._occ_ladder_assembly_2d
def wrapped(polylines, width, size, assembly, domain=None):
    pts, tris, cad = real(polylines, width, size, assembly, domain=domain)
    E = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (min(a, b), max(a, b)); E[k] = E.get(k, 0) + 1
    per = sum(np.linalg.norm(pts[a] - pts[b]) for (a, b), c in E.items() if c == 1)
    diam = float(np.linalg.norm(pts.max(0) - pts.min(0)))
    P = pts[tris]; tw = np.abs((P[:,1,0]-P[:,0,0])*(P[:,2,1]-P[:,0,1])-(P[:,1,1]-P[:,0,1])*(P[:,2,0]-P[:,0,0]))
    print(f"annulus k=0 dip15: cad {cad:.4e} excess {tw.sum()/2-cad:.3e} perimeter {per:.4f} diameter {diam:.4f} "
          f"-> needs delta >= {(tw.sum()/2-cad)/per:.2e} = {(tw.sum()/2-cad)/per/diam:.2e} x diameter")
    return pts, tris, tw.sum() / 2
ps._occ_ladder_assembly_2d = wrapped
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=0.05, refinement=1, qdegree=2)
h = 0.025; th, dip = np.radians(90), np.radians(15)
r = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r
try:
    ps.place_fault_ribbon_2d(base, [("Z", r + (h * np.arange(7))[:, None] * d)], 2 * h, margin_rings=2, clearance=0.3, split=False, mesher="ladder")
except Exception as e:
    print("placement:", str(e)[:80])
print("strip: missing 1e-6 sliver, perimeter 18, diameter 8.06 -> refused only if delta < %.2e = %.2e x diameter" % (1e-6 / 18, 1e-6 / 18 / 8.06))
