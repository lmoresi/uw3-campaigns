"""#1151: what does FGMRES do with the factorisation of P as its preconditioner?"""
import sys, warnings, importlib.util
import numpy as np
import underworld3 as uw
warnings.simplefilter("ignore")
spec = importlib.util.spec_from_file_location("lib", __file__.replace("fgmres_lu_check.py", "probe_lib.py"))
sys.argv = [sys.argv[0]]
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)

for ksp_type in ("fgmres", "gmres", "richardson"):
    stokes, v = lib.build("plain", {"snes_type": "ksponly", "ksp_type": ksp_type, "pc_type": "lu",
                                    "ksp_rtol": 1.0e-12, "ksp_max_it": 200})
    stokes.solve(zero_init_guess=True)
    snes = stokes.snes; ksp = snes.ksp
    A, P = ksp.getOperators()
    J, Jp, _ = snes.getJacobian()
    x = snes.getSolution()
    f = x.duplicate(); snes.computeFunction(x, f)
    zero = x.duplicate(); zero.set(0.0)
    f0 = x.duplicate(); snes.computeFunction(zero, f0)
    speed = float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max())
    print(f"{ksp_type:10s} | ksp operators: A is J {A.handle == J.handle}, P is Jp {P.handle == Jp.handle}, "
          f"A is P {A.handle == P.handle} | pc type {ksp.getPC().getType()} use_amat {ksp.getPC().getUseAmat()} "
          f"| tolerances {ksp.getTolerances()} | reason {ksp.getConvergedReason()} its {ksp.getIterationNumber()} "
          f"| ksp rnorm {ksp.getResidualNorm():.3e} | |F|/|F0| {f.norm()/f0.norm():.3e} | speed {speed:.8e}", flush=True)
