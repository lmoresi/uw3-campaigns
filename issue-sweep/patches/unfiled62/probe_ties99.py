import numpy as np
from underworld3.utilities import custom_mg
ns = {"np": np, "_record": custom_mg._record}
exec(open("old_bary.py").read(), ns); exec(open("b99.py").read(), ns)
old, b99 = ns["_old_barycentric_prolongation"], ns["_b99"]
for n in (16, 24, 32, 48):
    for shift in (0.0, 0.5, 0.25):
        c = np.array([(i, j) for i in range(n) for j in range(n)], float) / 32.0
        f = np.array([(i + shift, j + shift) for i in range(n // 2) for j in range(n)], float) / 32.0
        print(n, shift, "99cfea1e vs development, entries differing", int((b99(c, f) != old(c, f)).nnz))
