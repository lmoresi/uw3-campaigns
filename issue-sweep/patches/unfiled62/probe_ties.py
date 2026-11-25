"""Tie-heavy clouds: integer grids scaled by a power of two, so equal distances are exact."""
import numpy as np
from underworld3.utilities import custom_mg
ns = {"np": np, "_record": custom_mg._record}
exec(open("old_bary.py").read(), ns)
old = ns["_old_barycentric_prolongation"]
diff = 0; cases = 0; orph = []
for n in (16, 24, 32):
    for shift in (0.0, 0.5):
        c = np.array([(i, j) for i in range(n) for j in range(n)], float) / 32.0
        f = (np.array([(i + shift, j + shift) for i in range(n // 2) for j in range(n)], float)) / 32.0
        a = {}
        Pn = custom_mg.barycentric_prolongation(c, f, stats=a); Po = old(c, f)
        cases += 1; orph.append(a["orphans_repaired"]); d = int((Pn != Po).nnz)
        diff += d > 0
        print(n, shift, "orphans", a["orphans_repaired"], "entries differing", d)
print("cases differing", diff, "of", cases)
