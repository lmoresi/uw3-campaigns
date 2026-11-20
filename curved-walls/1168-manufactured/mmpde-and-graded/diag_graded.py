"""Graded-wall diagnosis (#1168): the circles measurement, with the option of taking the
discrete net torque out of the body force.

    python diag_graded.py -uw_cell_size 0.05 -uw_kind c3 -uw_slide graded -uw_detorque 1

With -uw_declare_rotation 0 the mesh declares no rotation null mode, so the rotated solve
projects out no gauge it was told about (only a rotation that is an exact null mode).
With -uw_detorque 1 the body force is f - T (-y, x), with T the mesh integral of
f . (-y, x) over that of |(-y, x)|^2: the forcing then exerts no net torque on the
discrete mesh, so a rotation mode that is not exactly null cannot be driven by it.
Everything else is measure_annulus.py's.

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

params = uw.Params(uw_cell_size=0.05, uw_kind="s2", uw_pressure_nullspace=True, uw_only="", uw_slide="none", uw_detorque=False, uw_lu_default=False, uw_declare_rotation=True)
CELL = float(params.uw_cell_size)
KIND = str(params.uw_kind)
NULLSPACE = bool(params.uw_pressure_nullspace)
ONLY = str(params.uw_only)
SLIDE = str(params.uw_slide)
DETORQUE = bool(params.uw_detorque)
LU_DEFAULT = bool(params.uw_lu_default)
DECLARE = bool(params.uw_declare_rotation)

mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
slide.slide(mesh, SLIDE)
if not DECLARE:
    # the mesh declares no rotation null mode (#906): the rotated solve then gauges a
    # rotation only if it is an exact null mode of the constrained problem
    mesh.nullspace_rotations = []
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
torque = uw.maths.Integral(mesh, f_e.dot(rot)).evaluate() / I_rr
if DETORQUE:
    f_e = f_e - torque * rot


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
            # direct MUMPS LU per increment (one pressure pin instead of the null
            # space); with the default normal the summed continuity row is already
            # implied by the wall constraint, so dropping one row changes nothing
            stokes._rotated_use_lu = LU_DEFAULT
        elif method == "rotated, normal=X/|X|":
            stokes.add_rotated_freeslip_bc(0, wall, normal=radial)
    stokes.solve(zero_init_guess=True)
    info = getattr(stokes, "_rotated_freeslip_info", None) or {}
    reason = stokes.snes.getConvergedReason()
    if info:
        uw.pprint(f"  [{method}] rotated solve: converged {info.get('converged')}, "
                  f"lu {bool(getattr(stokes, '_rotated_use_lu', False))}, "
                  f"rnorm {info.get('rnorm', float('nan')):.3e} (rnorm0 "
                  f"{info.get('rnorm0', float('nan')):.3e}), last ksp_reason "
                  f"{info.get('ksp_reason')}, ksp_its {info.get('ksp_its')}, "
                  f"vel_its_last {info.get('vel_its_last')}")
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    omega_h = uw.maths.Integral(mesh, v.sym.dot(rot)).evaluate() / I_rr
    du = (v.sym - omega_h * rot) - ue_mod
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    draw = v.sym - u_e
    e_raw = np.sqrt(uw.maths.Integral(mesh, draw.dot(draw)).evaluate()) / norm_raw
    return reason, e_u, e_raw, omega_h, mean_p - mean_p_e


uw.pprint(f"declare rotation {DECLARE}  detorque {DETORQUE}  forcing torque T {torque:+.3e}  slide {SLIDE}  kind {KIND}  cell {CELL}  cells {mesh.dm.getHeightStratum(0)[1]}  "
          f"pressure nullspace {NULLSPACE}  omega_e {omega_e:+.4e}")
uw.pprint(f"{'method':26s} reason {'u L2':>10s} {'u L2 raw':>10s} {'omega_h':>11s} {'<p>-<p_e>':>11s}")
for method in ("essential (control)", "rotated, default normal", "rotated, normal=X/|X|"):
    if ONLY and not any(w in method for w in ONLY.split(",")):
        continue
    reason, e_u, e_raw, om, dp = solve(method)
    uw.pprint(f"{method:26s} {reason:6d} {e_u:10.3e} {e_raw:10.3e} {om:+11.3e} {dp:+11.3e}")
