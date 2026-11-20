"""Rotated free slip on the spherical shell against the exact solutions of manufactured_shell.py.

    python measure_shell.py -uw_cell_size 0.2 -uw_kind pol

uw.meshing.SphericalShell(radiusOuter=1, radiusInner=0.5): both walls take the
treatment under test; the all-essential control takes the exact velocity on both.
P2/P1, viscosity 1, velocity block solved directly (MUMPS), tolerance 1e-10,
pressure null space attached. Free slip on two concentric spheres leaves three
rigid rotations undetermined; errors are taken modulo the least-squares rigid
rotation omega x X removed from both u_h and u_e (as in measure_annulus.py).
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured_shell as ms

params = uw.Params(uw_cell_size=0.2, uw_kind="pol", uw_only="")
CELL = float(params.uw_cell_size)
KIND = str(params.uw_kind)
ONLY = str(params.uw_only)

mesh = uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
X = mesh.X
F = ms.fields(KIND)
on_mesh = {ms.x: X[0], ms.y: X[1], ms.z: X[2]}
u_e = F["u"].T.xreplace(on_mesh)
p_e = F["p"].xreplace(on_mesh)
f_e = F["f"].T.xreplace(on_mesh)
Xr = sympy.Matrix([[X[0], X[1], X[2]]])
radial = Xr / sympy.sqrt(Xr.dot(Xr))
rots = [sympy.Matrix([[0, -X[2], X[1]]]), sympy.Matrix([[X[2], 0, -X[0]]]),
        sympy.Matrix([[-X[1], X[0], 0]])]

v = uw.discretisation.MeshVariable("U", mesh, 3, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
M = np.array([[uw.maths.Integral(mesh, ri.dot(rj)).evaluate() for rj in rots] for ri in rots])


def remove_rotation(u):
    omega = np.linalg.solve(M, [uw.maths.Integral(mesh, u.dot(ri)).evaluate() for ri in rots])
    rigid = sympy.zeros(1, 3)
    for w, ri in zip(omega, rots):
        rigid += float(w) * ri
    return u - rigid, omega


ue_mod, omega_e = remove_rotation(u_e)
norm_u = np.sqrt(uw.maths.Integral(mesh, ue_mod.dot(ue_mod)).evaluate())
area = uw.maths.Integral(mesh, 1.0).evaluate()
mean_p_e = uw.maths.Integral(mesh, p_e).evaluate() / area


def solve(method):
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    stokes.petsc_use_pressure_nullspace = True
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    for wall in ("Upper", "Lower"):
        if method == "essential (control)":
            stokes.add_essential_bc(u_e, wall)
        elif method == "rotated, default normal":
            stokes.add_rotated_freeslip_bc(0, wall)
        elif method == "rotated, normal=X/|X|":
            stokes.add_rotated_freeslip_bc(0, wall, normal=radial)
    stokes.solve(zero_init_guess=True)
    reason = stokes.snes.getConvergedReason()
    u_mod, omega_h = remove_rotation(v.sym)
    du = u_mod - ue_mod
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    return reason, e_u, np.abs(omega_h).max(), mean_p - mean_p_e


uw.pprint(f"kind {KIND}  cell {CELL}  cells {mesh.dm.getHeightStratum(0)[1]}  |omega_e| {np.abs(omega_e).max():.3e}")
uw.pprint(f"{'method':26s} reason {'u L2':>10s} {'|omega_h|':>10s} {'<p>-<p_e>':>11s}")
for method in ("essential (control)", "rotated, default normal", "rotated, normal=X/|X|"):
    if ONLY and not any(w in method for w in ONLY.split(",")):
        continue
    reason, e_u, om, dp = solve(method)
    uw.pprint(f"{method:26s} {reason:6d} {e_u:10.3e} {om:10.3e} {dp:+11.3e}")
