"""Pick deterministic UNFILED 68 fixtures from hunt3's traces (seed 22): an empty and a partial
fault at 0.3-cell sampling on development, and a complete one at 1 cell."""
import warnings, numpy as np, underworld3 as uw
warnings.simplefilter("ignore")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
h = 1 / 12
def traces(DS):
    rng = np.random.default_rng(22)
    out = []
    for k in range(20):
        ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
        c = 0.5 + rng.uniform(-0.05, 0.05, 2)
        L = 6 * h; n = max(2, int(round(6 / DS)))
        s = np.linspace(-L / 2, L / 2, n + 1)
        th = ang + turn * s / L
        d = np.column_stack([np.cos(th), np.sin(th)])
        P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
        out.append((k, ang, turn, c, P))
    return out
def seg_dist(P, A, B):
    best = np.full(len(P), np.inf)
    for a, b in zip(A, B):
        e = b - a; L = e @ e
        u = np.clip(((P - a) @ e) / L, 0, 1) if L > 0 else np.zeros(len(P))
        best = np.minimum(best, np.linalg.norm(P - (a + u[:, None] * e), axis=1))
    return best
for DS in (0.3, 1.0):
    for k, ang, turn, c, P in traces(DS):
        for rev, Q in ((0, P), (1, P[::-1].copy())):
            try:
                m2 = mesh.add_fault(("F", Q))
            except Exception as e:
                continue
            b = [bb for bb in m2.boundaries if bb.name == "F"][0]
            lab = m2.dm.getLabel("F"); n = lab.getStratumSize(b.value)
            if n == 0:
                print(f"FIX68 ds {DS} k {k} rev {rev} EMPTY ang {ang!r} turn {turn!r} c {c.tolist()!r}"); continue
            dm = m2.dm; vS, _ = dm.getDepthStratum(0)
            X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
            ends = np.array([dm.getCone(int(e)) for e in lab.getStratumIS(b.value).getIndices()]) - vS
            dense = np.vstack([Q[:-1] + x * (Q[1:] - Q[:-1]) for x in np.linspace(0, 1, 11)])
            a = seg_dist(dense, X[ends[:, 0]], X[ends[:, 1]]).max() / h
            kind = "PARTIAL" if a > 0.5 else "COMPLETE"
            print(f"FIX68 ds {DS} k {k} rev {rev} {kind} cover {a:.3f} facets {n}")
