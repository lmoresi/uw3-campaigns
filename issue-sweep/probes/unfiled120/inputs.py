"""For every rotated KSP solve: hashes of the operator (CSR), the preconditioning
matrix, the right-hand side and the result, and the final residual."""
import hashlib, sys
import numpy as np
from petsc4py import PETSc
import pytest

out = open(sys.argv[1], "w")
_ksp = PETSc.KSP.solve


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:12]


def mat_hash(M):
    try:
        ia, ja, a = M.getValuesCSR()
        return f"{h(ia)}/{h(ja)}/{h(a)}"
    except Exception as e:
        return f"({type(e).__name__})"


def ksp_solve(self, b, x):
    pfx = self.getOptionsPrefix() or ""
    if pfx.startswith("rotfs"):
        A, P = self.getOperators()
        rec = f"{pfx} A {mat_hash(A)} P {mat_hash(P)} b {h(b.getArray())}"
        np.save(sys.argv[1].replace(".txt", f"-{pfx}b.npy"), b.getArray().copy())
    r = _ksp(self, b, x)
    if pfx.startswith("rotfs"):
        out.write(f"{rec} x {h(x.getArray())} its {self.getIterationNumber()} rnorm {self.getResidualNorm()!r}\n")
    return r


PETSc.KSP.solve = ksp_solve
code = pytest.main(sys.argv[2:] + ["-q", "-p", "no:cacheprovider"])
out.close()
sys.exit(code)
