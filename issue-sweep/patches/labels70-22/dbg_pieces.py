import sys, numpy as np
sys.argv = ["x", "box_irr", "1.0", "kinks"]
src = open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0]
src = src.replace('MODE = os.environ.get("MODE", "dev")', 'MODE = "new_all"')
exec(src)
from underworld3.utilities import line_cut as lc, fault_split as fs
for tag, Q in traces():
    if tag != "kink120_1": continue
    dm = lc.pull_vertex_onto(mesh.dm, Q, on_shared="note")
    cut, info = lc.cut_along_lines(dm, [Q], label="F", label_value=7)
    eS, _ = cut.getDepthStratum(1); ends = lc._edge_vertices(cut); X = lc._coords(cut)
    marked = np.asarray(cut.getLabel("F").getStratumIS(7).getIndices()) - eS
    nbr = {}
    for a, b in ends[marked]:
        nbr.setdefault(int(a), set()).add(int(b)); nbr.setdefault(int(b), set()).add(int(a))
    tips = [v for v, ns in nbr.items() if len(ns) == 1]
    junct = [v for v, ns in nbr.items() if len(ns) > 2]
    print("DBGP edges", len(marked), "vertices", len(nbr), "tips", len(tips), "junction vertices", len(junct))
    print("DBGP tip coords", [tuple(np.round(X[v], 4)) for v in tips], "trace ends", np.round(Q[[0, -1]], 4).tolist())
    from underworld3.utilities.fault_split import _fault_chain
    vS, _ = cut.getDepthStratum(0)
    shared = np.zeros(cut.getChart()[1] - cut.getChart()[0], dtype=bool)
    fe = [(int(a), int(b)) for a, b in ends[marked]]
    try:
        prob, chain = _fault_chain(cut, [int(e) + eS for e in marked], X, vS, shared, cut.getChart()[0])
        print("DBGP split check problem:", prob)
    except Exception as e:
        print("DBGP split check raised:", type(e).__name__, str(e)[:120])
