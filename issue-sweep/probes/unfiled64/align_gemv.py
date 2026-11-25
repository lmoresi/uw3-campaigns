"""UNFILED 64: do multi-vector dots (BLAS dgemv 'T', PETSc VecMDot) of IDENTICAL data depend on
the address alignment?"""
import numpy as np
from petsc4py import PETSc
from scipy.linalg import blas
rng = np.random.default_rng(0)
n, m = 2752, 30
X = rng.standard_normal((n, m)); y = rng.standard_normal(n)
res = {}
for off in range(8):
    buf = np.zeros(n * m + n + 64)
    A = buf[off:off + n * m].reshape(m, n).T          # column-major n x m view at offset
    A[...] = X
    yb = np.zeros(n + 16); yy = yb[off:off + n]; yy[:] = y
    g = blas.dgemv(1.0, A, yy, trans=1)
    vs = [PETSc.Vec().createWithArray(np.ascontiguousarray(buf[off + j * n: off + (j + 1) * n])) for j in range(m)]
    # PETSc VecMDot against vectors whose arrays live at this offset
    cols = []
    for j in range(m):
        b2 = np.zeros(n + 16); a2 = b2[off:off + n]; a2[:] = X[:, j]; cols.append(a2)
    vv = [PETSc.Vec().createWithArray(c) for c in cols]
    w = PETSc.Vec().createWithArray(yy)
    md = np.array(w.mDot(vv))
    res[off] = (g, md)
    print("off", off, "gemv sha", hash(g.tobytes()) % 10**8, "mdot sha", hash(md.tobytes()) % 10**8)
g0, m0 = res[0]
print("gemv differs across offsets:", any(not np.array_equal(res[k][0], g0) for k in res),
      "| mdot differs:", any(not np.array_equal(res[k][1], m0) for k in res))
for k in res:
    print("off", k, "addr%64 of col0 =", (np.zeros(1).ctypes.data) and "", "mdot max |diff| vs off0 %.3e" % np.abs(res[k][1] - m0).max())
