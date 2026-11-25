"""UNFILED 64: the cold solve of test_1157's mu 1e-4 case with every velocity sub-solve's reason
and first/last residual. python verbose1157.py <tag>"""
import sys, runpy
from petsc4py import PETSc
o = PETSc.Options()
o["rotfs1_fieldsplit_vel_ksp_converged_reason"] = None
o["rotfs1_fieldsplit_vel_ksp_monitor_short"] = None
o["rotfs1_fieldsplit_pres_ksp_converged_reason"] = None
o["rotfs1_ksp_converged_reason"] = None
T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_1157_rotated_warm_resolve_at_roundoff.py")
v, stokes = T["_annulus"]("mu", mu=1.0e-4)
stokes.solve(zero_init_guess=True)
print("TAG", sys.argv[1], "vel_its_last", stokes._rotated_freeslip_info["vel_its_last"], flush=True)
