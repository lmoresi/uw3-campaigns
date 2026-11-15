"""Kramer, Davies & Wilson (2021) spherical shell, delta forcing on the internal
surface, free slip on both walls (rotated strong constraint), ell = 2, m = 0.
One rank. The forcing is a natural condition on the internal surface written in
the coordinates, g Y(x) x / |x|, the term #1188 mispairs on faces not at
orientation 0. Reports the nodal RMS error of velocity and pressure against the
analytic solution, and the solver's iteration counts.
"""
import time

import numpy as np

import underworld3 as uw
from underworld3.analytic.spherical.kramer import KramerSphericalStokes

params = uw.Params(uw_cell_size=0.5, uw_refinement=1)
CELL, REFINE = float(params.uw_cell_size), int(params.uw_refinement)

mesh = uw.meshing.SphericalShellInternalBoundary(
    radiusOuter=2.22, radiusInternal=1.72, radiusInner=1.22, cellSize=CELL,
    qdegree=3, refinement=REFINE)
v = uw.discretisation.MeshVariable("U", mesh, 3, degree=2, vtype=uw.VarType.VECTOR)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1, continuous=True)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
sol = KramerSphericalStokes(mesh, ell=2, m=0, density="delta", boundary="free")
sol.apply_boundary_conditions(stokes)
sol.apply_forcing(stokes, "Internal")
stokes.tolerance = 1.0e-8

dm = mesh.dm
f_start, f_end = dm.getHeightStratum(1)
counts = {}
for q in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Internal.value).getIndices():
    if f_start <= q < f_end:
        cell = dm.getSupport(q)[0]
        o = int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(q)])
        counts[o] = counts.get(o, 0) + 1

t0 = time.time()
stokes.solve()
elapsed = time.time() - t0
report = stokes.solve_report

X = np.asarray(v.coords)
u = np.asarray(v.array).reshape(len(X), 3)
u_a = np.asarray(sol.evaluate("velocity", X)).reshape(len(X), 3)
Xp = np.asarray(p.coords)
pp = np.asarray(p.array).ravel()
p_a = np.asarray(sol.evaluate("pressure", Xp)).ravel()
pp, p_a = pp - pp.mean(), p_a - p_a.mean()
rms = lambda a: float(np.sqrt(np.mean(a * a)))
print(f"cell {CELL} refinement {REFINE}: cells {mesh.dm.getHeightStratum(0)[1]}, velocity nodes {len(X)}; "
      f"Internal faces by orientation {dict(sorted(counts.items()))}; "
      f"reason {report.reason}, Newton its {report.nl_its}, Krylov its (outer) {report.ksp_its}; "
      f"velocity rms error / rms {rms(u - u_a) / rms(u_a):.6e}; pressure rms error / rms {rms(pp - p_a) / rms(p_a):.6e}; "
      f"solve {elapsed:.0f} s", flush=True)
