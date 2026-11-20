"""Rotated free slip on the gmsh annulus against the exact solutions of manufactured_annulus.py.

    python measure_annulus.py -uw_cell_size 0.05 -uw_kind s2

uw.meshing.Annulus(radiusOuter=1, radiusInner=0.5): the default unstructured gmsh
mesh. Both walls take the treatment under test; the all-essential control takes
the exact velocity on both. P2/P1, viscosity 1, velocity block solved directly
(MUMPS), tolerance 1e-10, pressure null space attached (as the annulus tests and
science runs do; -uw_pressure_nullspace 0 turns it off).

Free slip on two concentric circles leaves a rigid rotation undetermined, and the
solver's gauge removes it from the answer. Errors are therefore taken modulo a
rigid rotation: from both u_h and u_e the least-squares rotation omega (-y, x) is
removed before comparing.
  u L2      ||u - u_e|| / ||u_e||  (modulo rotation)
  u L2 raw  without removing the rotation
  omega_h   the rotation left in the answer; omega_e the exact solution's
  <p>-<p_e> the mean pressure offset
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured_annulus as ma
import slide

params = uw.Params(uw_cell_size=0.05, uw_kind="s2", uw_pressure_nullspace=True, uw_only="", uw_slide="none")
CELL = float(params.uw_cell_size)
KIND = str(params.uw_kind)
NULLSPACE = bool(params.uw_pressure_nullspace)
ONLY = str(params.uw_only)
SLIDE = str(params.uw_slide)

mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
slide.slide(mesh, SLIDE)
X, Y = mesh.X
F = ma.fields(KIND)
on_mesh = {ma.x: X, ma.y: Y}
u_e = F["u"].T.xreplace(on_mesh)
p_e = F["p"].xreplace(on_mesh)
f_e = F["f"].T.xreplace(on_mesh)
radial = sympy.Matrix([[X, Y]]) / sympy.sqrt(X**2 + Y**2)
rot = sympy.Matrix([[-Y, X]])

v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
area = uw.maths.Integral(mesh, 1.0).evaluate()
I_rr = uw.maths.Integral(mesh, rot.dot(rot)).evaluate()
mean_p_e = uw.maths.Integral(mesh, p_e).evaluate() / area
omega_e = uw.maths.Integral(mesh, u_e.dot(rot)).evaluate() / I_rr
ue_mod = u_e - omega_e * rot
norm_u = np.sqrt(uw.maths.Integral(mesh, ue_mod.dot(ue_mod)).evaluate())
norm_raw = np.sqrt(uw.maths.Integral(mesh, u_e.dot(u_e)).evaluate())


def solve(method):
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    stokes.petsc_use_pressure_nullspace = NULLSPACE
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
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    omega_h = uw.maths.Integral(mesh, v.sym.dot(rot)).evaluate() / I_rr
    du = (v.sym - omega_h * rot) - ue_mod
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    draw = v.sym - u_e
    e_raw = np.sqrt(uw.maths.Integral(mesh, draw.dot(draw)).evaluate()) / norm_raw
    return reason, e_u, e_raw, omega_h, mean_p - mean_p_e


uw.pprint(f"slide {SLIDE}  kind {KIND}  cell {CELL}  cells {mesh.dm.getHeightStratum(0)[1]}  "
          f"pressure nullspace {NULLSPACE}  omega_e {omega_e:+.4e}")
uw.pprint(f"{'method':26s} reason {'u L2':>10s} {'u L2 raw':>10s} {'omega_h':>11s} {'<p>-<p_e>':>11s}")
for method in ("essential (control)", "rotated, default normal", "rotated, normal=X/|X|"):
    if ONLY and not any(w in method for w in ONLY.split(",")):
        continue
    reason, e_u, e_raw, om, dp = solve(method)
    uw.pprint(f"{method:26s} {reason:6d} {e_u:10.3e} {e_raw:10.3e} {om:+11.3e} {dp:+11.3e}")
