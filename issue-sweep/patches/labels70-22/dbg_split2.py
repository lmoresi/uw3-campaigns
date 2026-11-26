import sys, numpy as np, warnings
warnings.simplefilter("ignore")
sys.argv = ["x", "box_irr", "1.0", "kinks"]
src = open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0]
src = src.replace('MODE = os.environ.get("MODE", "dev")', 'MODE = "new_all"')
exec(src)
from underworld3.utilities import fault_split as fs, line_cut as lc
fs._refuse_an_empty_or_partial_cut = lambda *a, **k: None
def pieces_and_cover(m2, side, Q):
    dm = m2.dm; X = lc._coords(dm); ends = lc._edge_vertices(dm); eS, _ = dm.getDepthStratum(1)
    bb = [x for x in m2.boundaries if x.name == side][0]; L = dm.getLabel(side)
    mk = np.asarray(L.getStratumIS(bb.value).getIndices()) - eS
    mk = mk[(mk >= 0) & (mk < len(ends))]
    parent = {}
    def root(v):
        while parent.get(v, v) != v: v = parent[v]
        return v
    for a_, b_ in ends[mk]:
        ra, rb = root(int(a_)), root(int(b_)); parent.setdefault(ra, ra); parent.setdefault(rb, rb)
        if ra != rb: parent[ra] = rb
    dense = np.vstack([Q[:-1] + x * (Q[1:] - Q[:-1]) for x in np.linspace(0, 1, 11)])
    dd = np.full(len(dense), np.inf)
    for a_, c_ in zip(X[ends[mk, 0]], X[ends[mk, 1]]):
        e = c_ - a_; LL = e @ e; u = np.clip(((dense - a_) @ e) / LL, 0, 1); dd = np.minimum(dd, np.linalg.norm(dense - (a_ + u[:, None] * e), axis=1))
    return len(mk), len({root(v) for v in parent}), dd.max() / h
for tag, Q in traces():
    if tag not in ("kink120_1", "kink150_4", "kink120_4"): continue
    try:
        m2 = mesh.add_fault(("F", Q))
    except Exception as e:
        print("DBGS", tag, "raised:", str(e)[:100]); continue
    for side in ("F", "FPlus", "FMinus"):
        n, p, c = pieces_and_cover(m2, side, Q)
        print(f"DBGS {tag} {side}: edges {n}, pieces {p}, max trace-to-chain/h {c:.3f}")
