"""Row 120 at np > 1: where two runs of the same script first differ, stage by stage.

    mpirun -n 2 python stage_dump.py <out-prefix> <script.py> [script args...]

Every rank writes <out-prefix>-rank<r>.log: one line per call, in call order, of
  Mat.mult / Mat.multTranspose  (the rotation into the constrained basis and back)
  NullSpace.remove              (before and after)
  KSP.solve                     (the operator's local CSR values, the rhs, the solution)
  Vec.norm                      (an MPI reduction)
with a hash of each vector's LOCAL array (and the operator's local rows). Compare two
runs with stage_compare.py; the first differing line names the stage.
Run it with PETSC_OPTIONS="-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0" to isolate a
source other than the GEMV path.
"""
import hashlib
import runpy
import sys

import numpy as np
from petsc4py import PETSc

prefix, script = sys.argv[1], sys.argv[2]
rank = PETSc.COMM_WORLD.getRank()
out = open(f"{prefix}-rank{rank}.log", "w")
seq = [0]


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:12]


def hv(v):
    return h(v.getArray(readonly=True))


def hm(M):
    try:
        ia, ja, a = M.getValuesCSR()
        return h(a)
    except Exception as e:
        return f"({type(e).__name__})"


def log(msg):
    seq[0] += 1
    out.write(f"{seq[0]:6d} {msg}\n")


def wrap(cls, name, fn):
    real = getattr(cls, name)

    def wrapped(self, *a, **k):
        return fn(real, self, *a, **k)
    setattr(cls, name, wrapped)


def mult(real, self, x, y):
    r = real(self, x, y)
    log(f"Mat.mult size {self.getSize()} in {hv(x)} out {hv(y)}")
    return r


def multT(real, self, x, y):
    r = real(self, x, y)
    log(f"Mat.multTranspose size {self.getSize()} in {hv(x)} out {hv(y)}")
    return r


def remove(real, self, v):
    before = hv(v)
    r = real(self, v)
    log(f"NullSpace.remove before {before} after {hv(v)}")
    return r


def solve(real, self, b, x):
    A, _P = self.getOperators()
    pre = f"KSP.solve {self.getOptionsPrefix()} A {hm(A)} b {hv(b)}"
    r = real(self, b, x)
    log(f"{pre} x {hv(x)} its {self.getIterationNumber()} rnorm {self.getResidualNorm()!r}")
    return r


def norm(real, self, *a, **k):
    r = real(self, *a, **k)
    log(f"Vec.norm {r!r}")
    return r


wrap(PETSc.Mat, "mult", mult)
wrap(PETSc.Mat, "multTranspose", multT)
wrap(PETSc.NullSpace, "remove", remove)
wrap(PETSc.KSP, "solve", solve)
wrap(PETSc.Vec, "norm", norm)

sys.argv = [script] + sys.argv[3:]
try:
    runpy.run_path(script, run_name="__main__")
finally:
    out.close()
