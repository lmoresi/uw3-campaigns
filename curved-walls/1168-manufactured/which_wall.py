"""Issue #1168's fixture: which wall's given normal moves the answer.

    python which_wall.py -uw_cell_size 0.1

Geometry, load and solver of the issue: elliptical annulus (semi-axes 1.5 and 1,
inner circle 0.5), radial body force cos(4 theta), P2/P1, rotated free slip on
both walls; velocity block solved directly. Each wall takes either its default
normal or its exact normal (normal=). Reported: rms velocity, mean pressure, and
the relative L2 difference of the velocity from the default/default solve.
"""
import numpy as np
import sympy
import underworld3 as uw

import measure_mesh

params = uw.Params(uw_cell_size=0.1)
CELL = float(params.uw_cell_size)
mesh = measure_mesh.ellipse_mesh(CELL)
x, y = mesh.X
A = 1.5
n_outer = sympy.Matrix([[2 * x / A**2, 2 * y]])
n_outer = n_outer / sympy.sqrt(n_outer.dot(n_outer))
n_inner = -sympy.Matrix([[x, y]]) / sympy.sqrt(x**2 + y**2)
v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
area = uw.maths.Integral(mesh, 1.0).evaluate()


def solve(outer_given, inner_given):
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = sympy.cos(4 * sympy.atan2(y, x)) * sympy.Matrix([[x, y]]) / sympy.sqrt(x**2 + y**2)
    stokes.tolerance = 1.0e-10
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    stokes.add_rotated_freeslip_bc(0, "Outer", normal=n_outer if outer_given else None)
    stokes.add_rotated_freeslip_bc(0, "Inner", normal=n_inner if inner_given else None)
    stokes.solve(zero_init_guess=True)
    rms = np.sqrt(uw.maths.Integral(mesh, v.sym.dot(v.sym)).evaluate() / area)
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    return np.array(v.array[:, 0, :]), stokes.snes.getConvergedReason(), rms, mean_p


reference, *_ = solve(False, False)
uw.pprint(f"cell {CELL}")
for outer_given, inner_given in ((False, False), (True, False), (False, True), (True, True)):
    u, reason, rms, mean_p = solve(outer_given, inner_given)
    diff = np.sqrt(((u - reference) ** 2).sum() / (reference ** 2).sum())
    uw.pprint(f"outer {'given  ' if outer_given else 'default'} inner {'given  ' if inner_given else 'default'} "
              f"reason {reason}  rms {rms:.5e}  mean p {mean_p:+.4e}  from default/default {diff:.4e}")
