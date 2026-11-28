"""Run pytest on the given files, recording every Python-level SNES and KSP solve's
iteration count and final residual norm (repr, full precision)."""
import sys
from petsc4py import PETSc
import pytest

out = open(sys.argv[1], "w")
_snes, _ksp = PETSc.SNES.solve, PETSc.KSP.solve


def snes_solve(self, *a, **k):
    r = _snes(self, *a, **k)
    out.write(f"SNES {self.getOptionsPrefix()} its {self.getIterationNumber()} "
              f"lin {self.getLinearSolveIterations()} reason {self.getConvergedReason()} "
              f"fnorm {self.getFunctionNorm()!r}\n")
    return r


def ksp_solve(self, *a, **k):
    r = _ksp(self, *a, **k)
    out.write(f"KSP {self.getOptionsPrefix()} its {self.getIterationNumber()} "
              f"reason {self.getConvergedReason()} rnorm {self.getResidualNorm()!r}\n")
    return r


PETSc.SNES.solve, PETSc.KSP.solve = snes_solve, ksp_solve
code = pytest.main(sys.argv[2:] + ["-q", "-p", "no:cacheprovider"])
out.close()
sys.exit(code)
