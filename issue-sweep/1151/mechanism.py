"""#1151: is the step of ksponly + preonly + lu the solution of P x = b with P the preconditioner matrix?

Linear problem, zero start: F(x) = A x - b. If the step solves P x = b then
F(x) = (A - P) x. Reports |F(x)| / |F(0)|, |F(x) - (A - P) x| / |F(0)| and
|A - P| / |A| (Frobenius). Matrices are read, never changed.
"""
import sys
import warnings
import numpy as np
import underworld3 as uw

warnings.simplefilter("ignore")
sys.argv = [sys.argv[0], sys.argv[1], "ksponly preonly+lu"]
import importlib.util
spec = importlib.util.spec_from_file_location("probe", __file__.replace("mechanism.py", "probe_lib.py"))
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)

kind = sys.argv[1]
stokes, v = lib.build(kind, {"snes_type": "ksponly", "ksp_type": "preonly", "pc_type": "lu"})
stokes.solve()
snes = stokes.snes
A, P, _ = snes.getJacobian()
x = snes.getSolution()
f = x.duplicate()
snes.computeFunction(x, f)
zero = x.duplicate(); zero.set(0.0)
f0 = x.duplicate()
snes.computeFunction(zero, f0)
ax = x.duplicate(); A.mult(x, ax)
px = x.duplicate(); P.mult(x, px)
gap = f.copy(); gap.axpy(-1.0, ax); gap.axpy(1.0, px)
D = A.copy(); D.axpy(-1.0, P, structure=D.Structure.DIFFERENT_NONZERO_PATTERN)
print(f"{kind:11s} | same matrix object {A.handle == P.handle} | |F(x)|/|F(0)| {f.norm()/f0.norm():.3e} "
      f"| |F(x)-(A-P)x|/|F(0)| {gap.norm()/f0.norm():.3e} | |A-P|/|A| {D.norm()/A.norm():.3e} "
      f"| unknowns {x.getSize()}", flush=True)
