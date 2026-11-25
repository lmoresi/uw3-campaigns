"""UNFILED 22, end to end on smooth traces: 20 lines and gentle arcs (6 cells long, total turn
<= 1 rad, centred), sampled at DS cells, forward and reversed; add_fault outcome under RULE.

    RULE=dev|thin|corners python hunt3.py <mesh> <DS>"""
import os, sys, warnings
import numpy as np
mesh_kind, DS = sys.argv[1], float(sys.argv[2])
sys.argv = sys.argv[:1]
RULE = os.environ.get("RULE", "dev")
os.environ["THIN"] = "1.0" if RULE == "thin" else "0"
import underworld3 as uw
if RULE != "dev":
    import corners_plugin  # noqa
warnings.simplefilter("ignore")
if mesh_kind == "box_irr":
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=False)
else:
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
h = 1 / 12
rng = np.random.default_rng(22)
def seg_dist(P, A, B):
    best = np.full(len(P), np.inf)
    for a, b in zip(A, B):
        e = b - a; L = e @ e
        u = np.clip(((P - a) @ e) / L, 0, 1) if L > 0 else np.zeros(len(P))
        best = np.minimum(best, np.linalg.norm(P - (a + u[:, None] * e), axis=1))
    return best
out = {"raised": 0, "empty": 0, "partial": 0, "complete": 0}
Hs = []
for k in range(20):
    ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
    c = 0.5 + rng.uniform(-0.05, 0.05, 2)
    L = 6 * h; n = max(2, int(round(6 / DS)))
    s = np.linspace(-L / 2, L / 2, n + 1)
    th = ang + turn * s / L
    d = np.column_stack([np.cos(th), np.sin(th)])
    P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
    for Q in (P, P[::-1].copy()):
        try:
            m2 = mesh.add_fault(("F", Q))
        except Exception:
            out["raised"] += 1; continue
        b = [bb for bb in m2.boundaries if bb.name == "F"][0]
        lab = m2.dm.getLabel("F")
        n_f = lab.getStratumSize(b.value) if lab is not None and lab.handle else 0
        if n_f == 0:
            out["empty"] += 1; continue
        dm = m2.dm; vS, _ = dm.getDepthStratum(0)
        X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
        ends = np.array([dm.getCone(int(e)) for e in lab.getStratumIS(b.value).getIndices()]) - vS
        t = np.linspace(0, 1, 11)
        dense = np.vstack([Q[:-1] + x * (Q[1:] - Q[:-1]) for x in t])
        a = seg_dist(dense, X[ends[:, 0]], X[ends[:, 1]])
        cc = seg_dist(X[np.unique(ends.ravel())], Q[:-1], Q[1:])
        H = max(a.max(), cc.max()) / h; Hs.append(H)
        out["partial" if a.max() > 0.5 * h else "complete"] += 1
H = np.array(Hs or [np.nan])
print(f"HUNT3 {RULE} {mesh_kind} ds {DS}: {out}; Hausdorff/h max {np.nanmax(H):.3f} median {np.nanmedian(H):.3f}", flush=True)
