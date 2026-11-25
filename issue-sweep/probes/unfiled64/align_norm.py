"""UNFILED 64: does VecNorm / dnrm2 of IDENTICAL data depend on the array's address alignment?"""
import numpy as np
from petsc4py import PETSc
from scipy.linalg import blas
x = np.load("x0_c1.npy") * 123.456          # any data with many entries
n = x.size
buf = np.zeros(n + 16)
for off in range(8):
    a = buf[off:off + n]; a[:] = x
    v = PETSc.Vec().createWithArray(a)
    print("off", off, "addr%64", a.ctypes.data % 64, "VecNorm %.17e" % v.norm(), "dnrm2 %.17e" % blas.dnrm2(a),
          "ddot %.17e" % blas.ddot(a, a))
