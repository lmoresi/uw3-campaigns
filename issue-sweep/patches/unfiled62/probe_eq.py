import numpy as np
from underworld3.utilities import custom_mg
ns = {"np": np, "_record": custom_mg._record}
exec(open("old_bary.py").read(), ns)
old = ns["_old_barycentric_prolongation"]
for n in (40, 60):
    g = np.linspace(0, 1, n)
    coarse = np.array([(x, y) for x in g for y in g])
    fine = np.random.default_rng(0).random((n * n, 2)) * [0.5, 1.0]
    a, b = {}, {}
    Pn = custom_mg.barycentric_prolongation(coarse, fine, stats=a); Po = old(coarse, fine, stats=b)
    print(n, "same", (Pn != Po).nnz == 0, "nnz", Pn.nnz, "orph", a["orphans_repaired"],
          "empty", int((np.asarray((Pn != 0).sum(axis=0)).ravel() == 0).sum()),
          "rowsum dev", float(abs(np.asarray(Pn.sum(axis=1)).ravel() - 1).max()))
# scattered random clouds, 3-D too, with moved fine nodes
rng = np.random.default_rng(1)
bad = 0
for trial in range(40):
    d = 2 + trial % 2
    c = rng.random((300 + 20 * trial, d)); f = rng.random((200 + 10 * trial, d))
    if trial % 3 == 0: f = f[f[:, 0] < 0.6]
    Pn = custom_mg.barycentric_prolongation(c, f); Po = old(c, f)
    bad += int((Pn != Po).nnz != 0)
print("random trials differing:", bad, "of 40")
