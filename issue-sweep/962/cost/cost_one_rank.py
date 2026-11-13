"""#962: what the one-matrix-per-call Jacobian routine costs on one rank.

A 3-D Stokes solve, solved once to build everything and then `uw_repeats` times
from a zero field inside a PETSc log stage, with the solver's own routine
(`-uw_one_pass 0`) or with PETSc's DMPlexSNESComputeJacobianFEM put back
(`-uw_one_pass 1`). Prints iteration counts and the stage's event counts, times
and flops. On one rank PETSc's routine is right, so the two runs solve the same
system.

    python cost_one_rank.py -uw_one_pass 0 -uw_cell_size 0.1
"""
import ctypes
import os
import sys

import numpy as np
import petsc4py
import sympy
import underworld3 as uw
from petsc4py import PETSc

params = uw.Params(uw_one_pass=0, uw_cell_size=0.1, uw_repeats=3, uw_nonlinear=0, uw_refinement=1)
PETSc.Log.begin()

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0),
                                         cellSize=float(params.uw_cell_size), refinement=int(params.uw_refinement), qdegree=3)
v = uw.discretisation.MeshVariable("V", mesh, 3, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
x, y, z = mesh.X
if int(params.uw_nonlinear):
    # a smooth shear-thinning viscosity, so that Newton takes several steps
    edot = stokes.Unknowns.Einv2
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0 / (1.0 + 10.0 * edot) + 0.1
else:
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0 + 9.0 * z
stokes.bodyforce = sympy.Matrix([[0.0, 0.0, sympy.cos(sympy.pi * x) * sympy.cos(sympy.pi * y)]])
for wall in ("Top", "Bottom", "Left", "Right", "Front", "Back"):
    stokes.add_essential_bc((0.0, 0.0, 0.0), wall)
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = 1.0e-6
stokes.solve()

if int(params.uw_one_pass):
    config = petsc4py.get_config()
    name = "libpetsc.dylib" if sys.platform == "darwin" else "libpetsc.so"
    library = ctypes.CDLL(os.path.join(config["PETSC_DIR"], config.get("PETSC_ARCH", ""), "lib", name))
    library.DMPlexSetSNESLocalFEM.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p]
    library.DMPlexSetSNESLocalFEM.restype = ctypes.c_int
    assert library.DMPlexSetSNESLocalFEM(stokes.dm.handle, False, None) == 0

stage = PETSc.Log.Stage("repeats")
snes_its, ksp_its, speed = [], [], []
stage.push()
for _ in range(int(params.uw_repeats)):
    v.array[...] = 0.0
    p.array[...] = 0.0
    stokes.solve(zero_init_guess=True)
    snes_its.append(stokes.snes.getIterationNumber())
    ksp_its.append(stokes.snes.getLinearSolveIterations())
    speed.append(float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max()))
stage.pop()

print("one_pass", int(params.uw_one_pass), "cells", mesh.dm.getHeightStratum(0)[1],
      "rows", stokes.snes.getJacobian()[0].getSize()[0], "reason", stokes.snes.getConvergedReason())
print("snes its", snes_its, "ksp its", ksp_its, "max speed", ["%.12e" % s for s in speed])
for event in ("SNESSolve", "SNESFunctionEval", "SNESJacobianEval", "DMPlexJacobianFE", "DMPlexResidualFE",
              "MatAssemblyEnd", "KSPSolve", "PCSetUp"):
    try:
        info = PETSc.Log.Event(event).getPerfInfo(stage.id)
    except Exception as err:
        print(f"{event:18s} not available: {err}")
        continue
    print(f"{event:18s} count {info['count']:5d}  time {info['time']:9.3f} s  flops {info['flops']:.6e}")
