"""#1168, separated fix (experiment): constrain u.n along the default facet-weighted normal
and gauge the constrained operator's own near-null mode, against development's gauge.

    python measure_sep.py -uw_cell_size 0.05 -uw_kind c3 -uw_mesh graded -uw_method sep

Built from the experiment branch (a local change to rotated_bc.py behind the private switch
``solver._rotated_separated_gauge``; the patch is separated-gauge.patch beside this file).

  -uw_mesh   none (as built) | graded (theta + 0.1 sin 3 theta, every node) |
             trench (an MMPDE move with wall slip, as ../mmpde-and-graded/mmpde_measure.py)
  -uw_method default  default normal, development's gauge (candidate A: the rigid rotation
                      with its constrained normal rows zeroed), direct LU
             sep      default normal, the separated gauge (candidate B: the constrained
                      velocity block's near-null mode by inverse iteration from A), direct LU
             sep2     default normal, candidate B2: the near-null mode of the whole
                      constrained saddle-point operator (velocity and pressure), direct LU
             radial   normal=X/|X|, development's gauge, iterative route (as in the earlier
                      tables; the LU route's pressure pin would drop #1168's constraint row)
On the LU route both gauges act only on the final answer: the same exact discrete solve, then
one mode projected out. Errors are modulo the least-squares rigid rotation, as before.
"""
import time
import numpy as np
import sympy
import underworld3 as uw

import manufactured_annulus as ma
import slide

params = uw.Params(uw_cell_size=0.05, uw_kind="c3", uw_mesh="none", uw_method="default")
CELL = float(params.uw_cell_size)
KIND = str(params.uw_kind)
MESH = str(params.uw_mesh)
METHOD = str(params.uw_method)

mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
if MESH == "trench":
    xs, ys = mesh.X
    rr = sympy.sqrt(xs**2 + ys**2)
    dth = sympy.atan2(xs, ys)
    density = 1 + 24 * sympy.exp(-(((rr - 0.95) / 0.06) ** 2) - (dth / 0.25) ** 2)
    uw.meshing.node_redistribution(mesh, density, slip_surfaces=True, skip_threshold=None,
                                   method_kwargs=dict(accel="none", n_outer=20))
else:
    slide.slide(mesh, MESH)

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

stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.saddle_preconditioner = 1.0
stokes.bodyforce = f_e
stokes.tolerance = 1.0e-10
stokes.petsc_use_pressure_nullspace = True
for wall in ("Upper", "Lower"):
    stokes.add_rotated_freeslip_bc(0, wall, normal=(radial if METHOD == "radial" else None))
stokes._rotated_use_lu = METHOD in ("default", "sep", "sep2")
stokes._rotated_separated_gauge = {"sep": True, "sep2": "saddle"}.get(METHOD, False)

t0 = time.perf_counter()
stokes.solve(zero_init_guess=True)
seconds = time.perf_counter() - t0
info = getattr(stokes, "_rotated_freeslip_info", None) or {}
mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
omega_h = uw.maths.Integral(mesh, v.sym.dot(rot)).evaluate() / I_rr
du = (v.sym - omega_h * rot) - ue_mod
e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u

uw.pprint(f"mesh {MESH} kind {KIND} cell {CELL} method {METHOD} cells {mesh.dm.getHeightStratum(0)[1]}")
uw.pprint(f"RESULT u_L2 {e_u:.4e} omega_h {omega_h:+.4e} omega_e {omega_e:+.4e} "
          f"mean_p_offset {mean_p - mean_p_e:+.4e} solve_s {seconds:.2f}")
uw.pprint(f"CONVERGENCE converged {info.get('converged')} rnorm {info.get('rnorm', float('nan')):.3e} "
          f"rnorm0 {info.get('rnorm0', float('nan')):.3e} ksp_reason {info.get('ksp_reason')} "
          f"ksp_its {info.get('ksp_its')} nonlinear_its {info.get('nonlinear_iterations')}")
rep = getattr(stokes, "_separated_gauge_report", None)
if rep is not None:
    uw.pprint(f"SEPARATED_GAUGE {rep}")
