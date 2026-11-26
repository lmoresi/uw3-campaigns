import sys, numpy as np, warnings
warnings.simplefilter("ignore")
mk, ds, want = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", mk, ds, "kinks" if want.startswith("kink") else "lines_arcs"]
src = open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0]
exec(src)
from underworld3.utilities import line_cut as lc
for tag, Q in traces():
    if tag != want: continue
    dm = lc.pull_vertex_onto(mesh.dm, Q, on_shared="note")
    X = lc._coords(dm)
    for i in range(3):
        d = np.linalg.norm(X - Q[i], axis=1); print(f"TIP sample {i} {np.round(Q[i],4).tolist()}: nearest vertex at {d.min()/h:.2e} cells")
    print("TIP shared", lc.last_shared_targets)
    cut, info = lc.cut_along_lines(dm, [Q], label="F", label_value=7)
    X = lc._coords(cut); ends = lc._edge_vertices(cut); eS, _ = cut.getDepthStratum(1)
    mk_ = np.asarray(cut.getLabel("F").getStratumIS(7).getIndices()) - eS
    v0 = int(np.argmin(np.linalg.norm(X - Q[0], axis=1))); v1 = int(np.argmin(np.linalg.norm(X - Q[1], axis=1)))
    print("TIP vertex of sample 0:", v0, "dist", np.linalg.norm(X[v0]-Q[0]), "| sample 1:", v1, "dist", np.linalg.norm(X[v1]-Q[1]))
    e01 = [k for k, (a, b) in enumerate(ends) if {int(a), int(b)} == {v0, v1}]
    print("TIP edge 0-1 exists:", e01, "labelled:", [k in set(mk_) for k in e01])
    lab_verts = set(ends[mk_].ravel().tolist())
    print("TIP v0 on chain:", v0 in lab_verts, "v1 on chain:", v1 in lab_verts)
    # edges touching v0
    for k, (a, b) in enumerate(ends):
        if v0 in (a, b):
            o = b if a == v0 else a
            print("TIP   edge from v0 to", np.round(X[o], 4).tolist(), "labelled", k in set(mk_))
