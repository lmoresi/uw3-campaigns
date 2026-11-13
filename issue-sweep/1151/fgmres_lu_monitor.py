"""#1151: the residual history of FGMRES preconditioned by the factorisation of P."""
import sys, warnings, importlib.util
import underworld3 as uw
warnings.simplefilter("ignore")
kind, ksp_type = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("lib", __file__.replace("fgmres_lu_monitor.py", "probe_lib.py"))
sys.argv = [sys.argv[0]]
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
stokes, v = lib.build(kind, {"snes_type": "ksponly", "ksp_type": ksp_type, "pc_type": "lu",
                             "ksp_rtol": 1.0e-12, "ksp_max_it": 200,
                             "ksp_monitor_true_residual": None, "ksp_converged_reason": None,
                             "ksp_view": None})
stokes.solve(zero_init_guess=True)
