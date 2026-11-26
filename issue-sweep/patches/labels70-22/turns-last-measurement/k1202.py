import sys, numpy as np, warnings
warnings.simplefilter("ignore")
sys.argv = ["x", "box_reg", "0.5", "kinks"]
exec(open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0])
from underworld3.utilities import line_cut as lc
for tag, Q in traces():
    if tag != "kink120_2": continue
    dm = lc.pull_vertex_onto(mesh.dm, np.vstack([Q[1:-1], Q[[0, -1]]]), on_shared="note")
    X = lc._coords(dm)
    has = [bool(np.any(np.all(X == q, axis=1))) for q in Q]
    print("K samples (index: has vertex):", [(i, h_) for i, h_ in enumerate(has)])
    a = Q[1:-1] - Q[:-2]; b = Q[2:] - Q[1:-1]
    turn = np.degrees(np.arccos(np.clip((a*b).sum(1)/np.linalg.norm(a,axis=1)/np.linalg.norm(b,axis=1), -1, 1)))
    print("K turn at sample", 1 + int(np.argmax(turn)), "%.1f deg" % turn.max())
    cut, info = lc.cut_along_lines(dm, [Q], label="F", label_value=7)
    X = lc._coords(cut); ends = lc._edge_vertices(cut); eS, _ = cut.getDepthStratum(1)
    mk = np.asarray(cut.getLabel("F").getStratumIS(7).getIndices()) - eS
    dense = np.vstack([Q[:-1] + x * (Q[1:] - Q[:-1]) for x in np.linspace(0, 1, 11)])
    seg_of = np.repeat(np.arange(len(Q) - 1)[None, :], 11, axis=0).ravel()
    d = np.full(len(dense), np.inf)
    for p, q in zip(X[ends[mk, 0]], X[ends[mk, 1]]):
        e = q - p; u = np.clip(((dense - p) @ e) / (e @ e), 0, 1); d = np.minimum(d, np.linalg.norm(dense - (p + u[:, None] * e), axis=1))
    w = int(np.argmax(d))
    print(f"K worst {d[w]/h:.3f} cells at {np.round(dense[w],4).tolist()}, in segment {seg_of[w]} (samples {seg_of[w]}-{seg_of[w]+1}); nearest sample {int(np.argmin(np.linalg.norm(Q-dense[w],axis=1)))}")
    print("K chain edges", len(mk), "| distance profile per segment (max, cells):", [round(float(d[seg_of == s].max()/h), 2) for s in range(len(Q) - 1)])
