import numpy as np
from petsc4py import PETSc
cnt = {"NORM_2": 0, "dot": 0, "NORM_1": 0, "sum": 0, "NORM_INF": 0}
trials = 0
for seed in range(30):
    rng = np.random.default_rng(100 + seed)
    for n in (384, 1536, 20011):
        trials += 1
        x0, y0 = rng.standard_normal(n), rng.standard_normal(n)
        def place(a, off):
            buf = np.empty(n + 64); base = (-(buf.ctypes.data // 8)) % 8
            v = buf[base + off: base + off + n]; v[:] = a; return v
        res = {k: set() for k in cnt}
        for off in range(8):
            x = PETSc.Vec().createWithArray(place(x0, off), comm=PETSc.COMM_SELF)
            y = PETSc.Vec().createWithArray(place(y0, (off * 5) % 8), comm=PETSc.COMM_SELF)
            res["NORM_1"].add(x.norm(PETSc.NormType.NORM_1).hex()); res["sum"].add(x.sum().hex())
            res["NORM_2"].add(x.norm().hex()); res["dot"].add(x.dot(y).hex())
            res["NORM_INF"].add(x.norm(PETSc.NormType.NORM_INFINITY).hex())
        for k in cnt:
            cnt[k] += len(res[k]) > 1
print(f"{trials} random vectors (30 seeds x n 384, 1536, 20011), 8 offsets each; vectors whose result depends on the offset:", cnt)
