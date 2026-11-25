"""UNFILED 64: test_1157's low-viscosity case, cold solve then warm. Prints the counts.
python rep1157.py <tag>"""
import sys, os, runpy
import numpy as np
T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_1157_rotated_warm_resolve_at_roundoff.py")
v, stokes = T["_annulus"]("mu", mu=1.0e-4)
stokes.solve(zero_init_guess=True)
i = stokes._rotated_freeslip_info
cold = (i["ksp_its"], i["vel_its_last"], i["pres_its_last"], i["ksp_reason"])
v.array[...] = 1.05 * np.asarray(v.array).copy()
stokes.solve(zero_init_guess=False)
i = stokes._rotated_freeslip_info
print("REP", sys.argv[1], "cold", cold, "warm", (i["ksp_its"], i["vel_its_last"], i["pres_its_last"], i["ksp_reason"]),
      "|v| %.15e" % float(np.linalg.norm(np.asarray(v.array))))
