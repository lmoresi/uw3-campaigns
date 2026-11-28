"""Dip 15, k = 0: where does the assembly overstep the CAD outline, and does it reach the final wall?"""
import numpy as np
import underworld3 as uw
import underworld3.utilities.place_surface as ps

real = ps._occ_ladder_assembly_2d
info = {}


def poly_signed(points, loop):
    """Signed distance to a closed polygon: + outside, - inside."""
    from matplotlib.path import Path as MPath
    d = ps._segments_distance(points, loop, [(i, (i + 1) % len(loop)) for i in range(len(loop))])
    inside = MPath(loop).contains_points(points, radius=0)
    return np.where(inside, -d, d)


def wrapped(polylines, width, size, assembly, domain=None):
    pts, tris, cad = real(polylines, width, size, assembly, domain=domain)
    P = pts[tris]
    twice = ((P[:, 1, 0] - P[:, 0, 0]) * (P[:, 2, 1] - P[:, 0, 1]) - (P[:, 1, 1] - P[:, 0, 1]) * (P[:, 2, 0] - P[:, 0, 0]))
    area = float(np.abs(twice).sum() / 2)
    edges = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (min(a, b), max(a, b))
            edges[k] = edges.get(k, 0) + 1
    bv = np.unique([v for k, c in edges.items() if c == 1 for v in k])
    outer = max(domain, key=lambda L: np.linalg.norm(L, axis=1).mean())
    sd = poly_signed(pts[bv], outer)
    r = np.linalg.norm(pts[bv], axis=1)
    order = np.argsort(-sd)[:6]
    print(f"assembly: mesh {area:.15e} cad {cad:.15e} diff {area - cad:+.3e}; {len(bv)} boundary vertices")
    print("  most outside the domain polygon (signed dist, r-1):")
    for i in order:
        print(f"    v{bv[i]} ({pts[bv[i],0]:+.12f}, {pts[bv[i],1]:.12f})  sd {sd[i]:+.3e}  r-1 {r[i]-1:+.3e}")
    # signed area of triangles: any inverted?
    print("  inverted triangles:", int((twice < 0).sum()), "of", len(tris), " min |area| %.2e" % (np.abs(twice).min() / 2))
    info["outer"] = outer
    return pts, tris, area          # let the placement run on


ps._occ_ladder_assembly_2d = wrapped
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=0.05, refinement=1, qdegree=2)
h = 0.025; th = np.radians(90); dip = np.radians(15)
r_hat = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r_hat
trace = r_hat + (h * np.arange(7))[:, None] * d
mesh, inf = ps.place_fault_ribbon_2d(base, [("Fault", trace)], 2 * h, margin_rings=2, clearance=0.3, split=False, mesher="ladder")
dm = mesh.dm
vS, vE = dm.getDepthStratum(0); eS, eE = dm.getDepthStratum(1)
X = dm.getCoordinatesLocal().array.reshape(-1, 2)
wall_v = set()
for e in range(eS, eE):
    if dm.getSupportSize(e) == 1:
        v = [int(q) - vS for q in dm.getCone(e)]
        if (np.linalg.norm(X[v], axis=1) > 0.7).all():
            wall_v.update(v)
W = np.array(sorted(wall_v))
r = np.linalg.norm(X[W], axis=1)
b = base.dm.getCoordinatesLocal().array.reshape(-1, 2)
rb = np.linalg.norm(b, axis=1); base_wall = b[rb > 1 - 1e-6]
from scipy.spatial import cKDTree
dd, _ = cKDTree(base_wall).query(X[W])
sd = poly_signed(X[W], info["outer"])
print(f"final: {len(W)} outer-wall vertices; max |r-1| {np.abs(r-1).max():.3e}; "
      f"max distance to a base wall vertex {dd.max():.3e}; max signed distance outside the base polygon {sd.max():+.3e}")
new = W[dd > 1e-12]
for v in new[:8]:
    print(f"   new wall vertex ({X[v,0]:+.12f}, {X[v,1]:.12f}) r-1 {np.linalg.norm(X[v])-1:+.3e} sd {poly_signed(X[[v]], info['outer'])[0]:+.3e}")
