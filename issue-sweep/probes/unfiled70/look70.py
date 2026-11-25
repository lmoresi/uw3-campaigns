import warnings, numpy as np, underworld3 as uw
warnings.simplefilter("ignore")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
h = 1 / 12; rng = np.random.default_rng(22)
for k in range(2):
    ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
    c = 0.5 + rng.uniform(-0.05, 0.05, 2)
L = 1.6; n = max(2, int(round(L / h)))
s = np.linspace(-L / 2, L / 2, n + 1); th = ang + turn * s / L
d = np.column_stack([np.cos(th), np.sin(th)])
P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
child = mesh.add_conforming_surface(uw.meshing.Surface("S", mesh, P))
dm = child.dm
b = [bb for bb in child.boundaries if bb.name == "S"][0]
lab = dm.getLabel("S")
print("LOOK turn", turn, "label values", list(lab.getValueIS().getIndices()), "boundary value", b.value,
      "sizes", [lab.getStratumSize(int(v)) for v in lab.getValueIS().getIndices()])
print("LOOK info", getattr(child, "_surface_info", None) and {k2: v for k2, v in child._surface_info.items() if not hasattr(v, 'shape')})
vS, _ = dm.getDepthStratum(0)
X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
ends = np.array([dm.getCone(int(e)) for e in lab.getStratumIS(b.value).getIndices()]) - vS
mids = 0.5 * (X[ends[:, 0]] + X[ends[:, 1]])
ins = np.all((P >= 0) & (P <= 1), axis=1)
Pin = P[ins]
from scipy.spatial import cKDTree
dd = cKDTree(mids).query(Pin)[0]
print("LOOK inside trace points", len(Pin), "distance to nearest chain-edge midpoint / h:", np.round(dd / h, 2).tolist())
