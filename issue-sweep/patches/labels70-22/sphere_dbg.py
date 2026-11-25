import os, numpy as np, underworld3 as uw
from underworld3.utilities import line_cut as lc
ns = dict(lc.__dict__); exec(open("old_label.py").read(), ns); old = ns["_old_label_cut_edges"]; new = lc._label_cut_edges
for cell, a in ((0.05, 0.3), (0.15, 0.5)):
    sph = uw.meshing.SphericalManifold(radius=1.0, cellSize=cell, degree=1, qdegree=5)
    phi = np.linspace(-a, a, 9); P = np.column_stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)])
    dm = lc.pull_vertex_onto(sph.dm, P, on_shared="note")
    cut, info = lc.cut_along_lines(dm, [P])
    scale = lc._global_extent(cut)
    mo = set(old(cut, [P], 1e-9 * scale, "o", 1)); mn = set(new(cut, [P], 1e-9 * scale, "n", 1))
    X = lc._coords(cut); ends = lc._edge_vertices(cut); eS, _ = cut.getDepthStratum(1)
    d, t = lc._line_parameters(X, P)
    print(f"SPH cell {cell} a {a}: info {info['n_split']} split {info['n_on_surface']} on; old {len(mo)} new {len(mn)}; only-old {len(mo - mn)} only-new {len(mn - mo)}")
    on = d < 1e-9 * scale
    print("SPH  on-line vertices", int(on.sum()), "params", np.round(np.sort(t[on]), 4).tolist()[:20])
    for e in sorted(mo - mn)[:4]:
        a0, b0 = ends[e - eS]
        print("SPH  only-old edge", e, "t", round(t[a0], 4), round(t[b0], 4), "chord", round(float(np.linalg.norm(X[a0] - X[b0])), 4))
