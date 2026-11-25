import sys, time, tracemalloc
import numpy as np
from underworld3.utilities import custom_mg
ns = {"np": np, "_record": custom_mg._record}
exec(open("old_bary.py").read(), ns)
n = int(sys.argv[1]); which = sys.argv[2]
g = np.linspace(0, 1, n)
coarse = np.array([(x, y) for x in g for y in g])
rng = np.random.default_rng(0)
fine = rng.random((n * n, 2)) * [0.5, 1.0]          # left half only
fn = ns["_old_barycentric_prolongation"] if which == "old" else custom_mg.barycentric_prolongation
tracemalloc.start(); t = time.time(); st = {}
P = fn(coarse, fine, stats=st)
cur, peak = tracemalloc.get_traced_memory()
print(which, n, "coarse", len(coarse), "fine", len(fine), "orphans", st["orphans_repaired"],
      "peak MB %.1f" % (peak / 1e6), "time %.2fs" % (time.time() - t),
      "empty cols", int((np.asarray((P != 0).sum(axis=0)).ravel() == 0).sum()))
