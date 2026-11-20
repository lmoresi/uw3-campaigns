"""H6-fix-1 (#1168): the circumcircle normal at the wall nodes of the annulus, against X/|X|.

    python circumcircle.py -uw_cell_size 0.05 -uw_mesh graded

At each wall vertex, the unit normal of the circle through the vertex and its two wall
neighbours (outward from that circle's centre). At each P2 edge-midpoint node, two choices:
  "mean"  the normalised mean of the edge's two vertex normals;
  "cc3"   the normal of the circle through the edge's two vertices and the nearer of their
          other neighbours, at the midpoint's angle.
Reported per wall: the largest angle between each and X/|X| at the same node; the largest
|n . (-y, x)| / R over the wall nodes (a rigid rotation's normal component, which must be
round-off for the rotation to be an exact null mode); and sum |r_i| with r_i = W_i . t, the
force a uniform pressure puts on node i's free row (#1168), for the circumcircle normal and
for X/|X|. W_i is the measure-weighted facet normal (P2 weights L/6 at a vertex, 2L/3 at the
midpoint). The mesh variants are those of the converged reruns: "none", "graded"
(theta + 0.1 sin 3 theta), "trench" (the MMPDE move of mmpde_measure.py).
"""
import numpy as np
import sympy
import underworld3 as uw

import slide

params = uw.Params(uw_cell_size=0.05, uw_mesh="none")
CELL = float(params.uw_cell_size)
MESH = str(params.uw_mesh)
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
if MESH == "trench":
    xs, ys = mesh.X
    r = sympy.sqrt(xs**2 + ys**2)
    dth = sympy.atan2(xs, ys)
    density = 1 + 24 * sympy.exp(-(((r - 0.95) / 0.06) ** 2) - (dth / 0.25) ** 2)
    uw.meshing.node_redistribution(mesh, density, slip_surfaces=True, skip_threshold=None,
                                   method_kwargs=dict(accel="none", n_outer=20))
else:
    slide.slide(mesh, MESH)

dm = mesh.dm
coords = dm.getCoordinatesLocal().array.reshape(-1, 2)
csec = dm.getCoordinateSection()
fS, fE = dm.getHeightStratum(1)


def circle_normal(a, b, c, at):
    """Unit normal at point ``at`` of the circle through a, b, c (outward from its centre)."""
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    n = np.asarray(at) - np.array([ux, uy])
    return n / np.linalg.norm(n)


def outward(n, x):
    return n if n @ x >= 0 else -n


for wall, R in (("Upper", 1.0), ("Lower", 0.5)):
    label = dm.getLabel(wall)
    facets = [int(q) for q in label.getStratumIS(mesh.boundaries[wall].value).getIndices()
              if fS <= q < fE]
    vx = {}
    edges = []
    for f in facets:
        a, b = (int(p) for p in dm.getCone(f))
        xa = coords[csec.getOffset(a) // 2]; xb = coords[csec.getOffset(b) // 2]
        vx[a], vx[b] = xa, xb
        edges.append((f, a, b))
    # wall neighbours of each vertex, from the facets (topology, not angle)
    nbr = {v: [] for v in vx}
    for f, a, b in edges:
        nbr[a].append(b); nbr[b].append(a)
    vn = {v: outward(circle_normal(vx[nbr[v][0]], vx[v], vx[nbr[v][1]], vx[v]), vx[v]) for v in vx}
    radial = lambda x: np.asarray(x) / np.linalg.norm(x)
    ang = lambda n, x: np.degrees(np.arccos(np.clip(abs(n @ radial(x)), -1, 1)))
    rot = lambda x: np.array([-x[1], x[0]])
    vert_angle = max(ang(vn[v], vx[v]) for v in vx)
    mid_mean, mid_cc3, rot_res = [], [], [abs(vn[v] @ rot(vx[v])) / R for v in vx]
    W = {v: np.zeros(2) for v in vx}
    Wm, Xm, Nm = {}, {}, {}
    for f, a, b in edges:
        xa, xb = vx[a], vx[b]
        L = np.linalg.norm(xb - xa)
        nf = outward(np.array([xb[1] - xa[1], -(xb[0] - xa[0])]) / L, (xa + xb) / 2)
        W[a] += L / 6 * nf; W[b] += L / 6 * nf
        m = (xa + xb) / 2
        n_mean = outward((vn[a] + vn[b]) / np.linalg.norm(vn[a] + vn[b]), m)
        # nearer of the other neighbours
        others = [w for w in nbr[a] if w != b] + [w for w in nbr[b] if w != a]
        c = min(others, key=lambda w: min(np.linalg.norm(vx[w] - xa), np.linalg.norm(vx[w] - xb)))
        n_cc3 = outward(circle_normal(xa, xb, vx[c], m), m)
        mid_mean.append(ang(n_mean, m)); mid_cc3.append(ang(n_cc3, m))
        rot_res.append(abs(n_mean @ rot(m)) / R)
        Wm[f], Xm[f], Nm[f] = 2 * L / 3 * nf, m, n_mean
    r_circ, r_rad = [], []
    for v in vx:
        n = vn[v]; t = np.array([-n[1], n[0]])
        tr = np.array([-radial(vx[v])[1], radial(vx[v])[0]])
        r_circ.append(W[v] @ t); r_rad.append(W[v] @ tr)
    for f in Wm:
        n = Nm[f]; t = np.array([-n[1], n[0]])
        tr = np.array([-radial(Xm[f])[1], radial(Xm[f])[0]])
        r_circ.append(Wm[f] @ t); r_rad.append(Wm[f] @ tr)
    L = [np.linalg.norm(vx[b] - vx[a]) for _f, a, b in edges]
    uw.pprint(f"mesh {MESH} cell {CELL} {wall}: {len(vx)} vertices, chords max/min "
              f"{max(L) / min(L):.3f}; angle to X/|X|: vertices {vert_angle:.2e} deg, "
              f"midpoints mean-rule {max(mid_mean):.2e} deg, cc3-rule {max(mid_cc3):.2e} deg; "
              f"rigid rotation |n.(-y,x)|/R max {max(rot_res):.2e}; sum |r_i| circumcircle "
              f"{np.abs(r_circ).sum():.4e}, X/|X| {np.abs(r_rad).sum():.4e}")
