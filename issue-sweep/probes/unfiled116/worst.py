import sys
import numpy as np
import underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=0.05, refinement=1, qdegree=2)
bX = base.dm.getCoordinatesLocal().array.reshape(-1, 2)
base_wall = bX[np.linalg.norm(bX, axis=1) > 1 - 1e-9]
h = 0.025
for dip_deg, k in [(30, 1.75), (15, 0.15), (20, 0.95), (45, 0.45), (60, 1.35)]:
    th, dip = np.radians(90), np.radians(dip_deg)
    r = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r
    trace = (1 - k * h) * r + (h * np.arange(7))[:, None] * d
    mesh, info = place_fault_ribbon_2d(base, [("F", trace)], 2 * h, margin_rings=2, clearance=0.3, split=True, mesher="ladder")
    dm = mesh.dm; vS, vE = dm.getDepthStratum(0); cS, cE = dm.getHeightStratum(0)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    band = np.asarray(info["band"])
    worst = (180, None)
    for c in range(cS, cE):
        cl = dm.getTransitiveClosure(c)[0]; v = cl[(cl >= vS) & (cl < vE)] - vS; P = X[v]
        a = []
        for i in range(3):
            u, w = P[(i+1)%3]-P[i], P[(i+2)%3]-P[i]
            a.append(np.degrees(np.arccos(np.clip(u@w/np.linalg.norm(u)/np.linalg.norm(w), -1, 1))))
        if min(a) < worst[0]: worst = (min(a), c, v, P)
    ang, c, v, P = worst
    onw = np.linalg.norm(P, axis=1) > 1 - 1e-6
    isbase = [np.linalg.norm(base_wall - p, axis=1).min() < 1e-12 for p in P]
    L = [np.linalg.norm(P[i]-P[(i+1)%3])/h for i in range(3)]
    import underworld3.utilities.place_surface as ps
    ang_ = np.arctan2(base_wall[:, 1], base_wall[:, 0]); loop = base_wall[np.argsort(ang_)]
    dpoly = ps._segments_distance(P, loop, [(i, (i + 1) % len(loop)) for i in range(len(loop))])
    print(f"   distance of each worst-cell vertex to the wall polygon, in h: {[f'{x/h:.2e}' for x in dpoly]}")
    print(f"dip {dip_deg} k {k}: worst {ang:.1f} deg, cell in band {bool(band[c-cS])}, on wall {onw.tolist()}, "
          f"base wall vertex {isbase}, edges/h {[round(x,3) for x in L]}")
