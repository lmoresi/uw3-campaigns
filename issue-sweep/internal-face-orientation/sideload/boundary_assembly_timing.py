"""The cost of the boundary terms in residual and Jacobian assembly (#1188).

A Stokes solver on the Kramer shell (internal boundary), assembled with and
without a natural load on Upper, Lower and Internal. The difference is the
boundary share; comparing it between development and the side-load gives the
cost of the remap. Best of several assemblies, one rank.
"""
import time

import numpy as np
import sympy

import underworld3 as uw

params = uw.Params(uw_cell_size=0.5, uw_refinement=1, uw_repeats=5)


def solver(mesh, tag, natural):
    v = uw.discretisation.MeshVariable(f"U{tag}", mesh, 3, degree=2, vtype=uw.VarType.VECTOR)
    p = uw.discretisation.MeshVariable(f"P{tag}", mesh, 1, degree=1, continuous=True)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.bodyforce = sympy.Matrix([0.0, 0.0, 0.0]).T
    if natural:
        X = mesh.CoordinateSystem.X
        load = X[0] * X[1] * mesh.CoordinateSystem.unit_e_0
        for wall in ("Upper", "Lower", "Internal"):
            stokes.add_natural_bc(load, wall)
    stokes._build()
    stokes.snes.setUp()
    return stokes


def best_times(stokes, repeats):
    snes = stokes.snes
    x = stokes.dm.getGlobalVec()
    x.setRandom()
    F = x.duplicate()
    J = snes.getJacobian()[0]
    snes.computeFunction(x, F)
    snes.computeJacobian(x, J, J)
    tf, tj = [], []
    for _ in range(repeats):
        t0 = time.perf_counter()
        snes.computeFunction(x, F)
        tf.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        snes.computeJacobian(x, J, J)
        tj.append(time.perf_counter() - t0)
    return min(tf), min(tj)


mesh = uw.meshing.SphericalShellInternalBoundary(
    radiusOuter=2.22, radiusInternal=1.72, radiusInner=1.22,
    cellSize=float(params.uw_cell_size), refinement=int(params.uw_refinement), qdegree=3)

dm = mesh.dm
f_start, f_end = dm.getHeightStratum(1)
faces, rotated = 0, 0
for wall in ("Upper", "Lower", "Internal"):
    for face in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries[wall].value).getIndices():
        if f_start <= face < f_end:
            cell = dm.getSupport(face)[0]
            faces += 1
            rotated += int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(face)] != 0)

repeats = int(params.uw_repeats)
f0, j0 = best_times(solver(mesh, "a", False), repeats)
f1, j1 = best_times(solver(mesh, "b", True), repeats)
uw.pprint(f"refinement {params.uw_refinement}: cells {dm.getHeightStratum(0)[1]}, "
          f"boundary faces {faces} ({rotated} not at 0); best of {repeats}: "
          f"residual {f0:.4f} s without, {f1:.4f} s with (boundary {f1 - f0:.4f} s); "
          f"Jacobian {j0:.4f} s without, {j1:.4f} s with (boundary {j1 - j0:.4f} s)")
