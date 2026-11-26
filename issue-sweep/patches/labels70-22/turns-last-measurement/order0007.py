"""Does 0007 (turns, then tips, pulled last) against 0006 (tips last) change the mesh? The pull is the same function on development and
0006, and the cut is deterministic given the pulled mesh, so a mesh changes exactly when the two
orders pull a different vertex set. One JSON line per trace of the box grid."""
import os, sys, json, warnings
import numpy as np
mesh_kind, family = sys.argv[1], sys.argv[2]
pre = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0]
for DS in (1.0, 0.5, 0.3):
    sys.argv = ["x", mesh_kind, str(DS), family]
    g = {"__name__": "order"}; exec(pre, g)
    lc = g["lc"]
    for tag, Q in g["traces"]():
        r = dict(mesh=mesh_kind, ds=DS, trace=tag)
        try:
            a = lc._coords(lc.pull_vertex_onto(g["mesh"].dm, Q if len(Q) <= 2 else np.vstack([Q[1:-1], Q[[0, -1]]]), on_shared="note"))
            from underworld3.utilities.fault_split import _in_pull_order
            T = _in_pull_order(Q)
            b = lc._coords(lc.pull_vertex_onto(g["mesh"].dm, T, on_shared="note"))
            r["changed"] = bool(a.shape != b.shape or not np.array_equal(a, b))
            r["moved_differently"] = int((np.abs(a - b) > 0).any(axis=1).sum()) if a.shape == b.shape else -1
        except Exception as e:
            r["error"] = str(e)[:80]
        print("ORDER " + json.dumps(r), flush=True)
