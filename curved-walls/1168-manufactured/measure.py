"""Each wall treatment of the ellipse against the exact free-slip solution of manufactured.py.

    python measure.py -uw_cell_size 0.05

    python measure.py -uw_cell_size 0.05 -uw_variant both

Variant "outer": the ellipse (semi-axes 1.5 and 1) takes the treatment under
test; the inner circle (radius 0.5) takes the exact velocity as essential data.
Variant "both" (issue #1168's setting): both walls take the treatment under test,
each with its own exact normal where a normal is given; its slip is a one-signed
circulation. Variant "both-xy": the same with slip odd in x and in y, the
symmetry of issue #1168's flow.
P2/P1, viscosity 1, body force from manufactured.py, velocity block solved
directly (MUMPS), tolerance 1e-10.

Errors, all relative:
  u L2     ||u - u_e|| / ||u_e|| over the mesh
  p L2     ||(p - <p>) - (p_e - <p_e>)|| / ||p_e - <p_e>||
  wall u   ||u - u_e|| / ||u_e|| on the outer wall
  wall u.n ||u . n_e|| / ||u_e|| on the outer wall (n_e: the ellipse's normal)

-uw_lambda L adds L grad P to the body force, P = r^4 cos 4 theta: the exact
velocity is unchanged and the exact pressure becomes p + L P. Issue #1168's load
is mostly balanced by pressure (rms velocity 1.4e-2 against a pressure of
order 1); this reproduces that balance on a case with a known answer.
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured
import measure_mesh

params = uw.Params(uw_cell_size=0.05, uw_only="", uw_variant="outer", uw_lambda=0.0, uw_pressure_nullspace=False)
CELL = float(params.uw_cell_size)
ONLY = str(params.uw_only)
VARIANT = str(params.uw_variant)
LAMBDA = float(params.uw_lambda)
NULLSPACE = bool(params.uw_pressure_nullspace)


mesh = measure_mesh.ellipse_mesh(CELL)
X, Y = mesh.X
F = manufactured.fields(VARIANT)
on_mesh = {manufactured.x: X, manufactured.y: Y}
u_e = F["u"].T.xreplace(on_mesh)
# A pressure-balanced load: lambda grad P added to the body force leaves the exact
# velocity unchanged and adds lambda P to the exact pressure (P = r^4 cos 4 theta).
P = manufactured.x**4 - 6 * manufactured.x**2 * manufactured.y**2 + manufactured.y**4
p_e = (F["p"] + LAMBDA * P).xreplace(on_mesh)
f_e = (F["f"] + LAMBDA * sympy.Matrix([P.diff(manufactured.x), P.diff(manufactured.y)])).T.xreplace(on_mesh)
n_e = F["n"].T.xreplace(on_mesh)
n_i = F["n_inner"].T.xreplace(on_mesh)
# the walls under test, each with its exact unit normal
WALLS = [("Outer", n_e)] + ([("Inner", n_i)] if VARIANT != "outer" else [])

v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
area = uw.maths.Integral(mesh, 1.0).evaluate()
mean_p_e = uw.maths.Integral(mesh, p_e).evaluate() / area
norm_u = np.sqrt(uw.maths.Integral(mesh, u_e.dot(u_e)).evaluate())
norm_p = np.sqrt(uw.maths.Integral(mesh, (p_e - mean_p_e) ** 2).evaluate())
wall_norm_u = np.sqrt(uw.maths.BdIntegral(mesh, u_e.dot(u_e), "Outer").evaluate())


def solve(method, gamma=None):
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    # Off by default, as in issue #1168's script. The all-essential control of the
    # two-wall variants is singular in the constant pressure; -uw_pressure_nullspace 1
    # attaches that mode.
    stokes.petsc_use_pressure_nullspace = NULLSPACE
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    if VARIANT == "outer":
        stokes.add_essential_bc(u_e, "Inner")
    for wall, normal in WALLS:
        if method == "essential (control)":
            stokes.add_essential_bc(u_e, wall)
        elif method == "rotated, default normal":
            stokes.add_rotated_freeslip_bc(0, wall)
        elif method == "rotated, normal= exact":
            stokes.add_rotated_freeslip_bc(0, wall, normal=normal)
        elif method == "nitsche, default normal":
            stokes.add_nitsche_bc(0, wall, gamma=gamma)
        elif method == "nitsche, normal= exact":
            stokes.add_nitsche_bc(0, wall, normal=normal, gamma=gamma)
        elif method == "penalty, exact normal":
            stokes.add_natural_bc(gamma * normal.dot(v.sym) * normal, wall)
    stokes.solve(zero_init_guess=True)
    reason = stokes.snes.getConvergedReason()
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    du = v.sym - u_e
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    e_p = np.sqrt(uw.maths.Integral(mesh, ((p.sym[0] - mean_p) - (p_e - mean_p_e)) ** 2)
                  .evaluate()) / norm_p
    e_wall = np.sqrt(uw.maths.BdIntegral(mesh, du.dot(du), "Outer").evaluate()) / wall_norm_u
    e_un = np.sqrt(uw.maths.BdIntegral(mesh, v.sym.dot(n_e) ** 2, "Outer").evaluate()) / wall_norm_u
    return reason, e_u, e_p, e_wall, e_un, mean_p - mean_p_e


CASES = [("essential (control)", None),
         ("rotated, default normal", None),
         ("rotated, normal= exact", None),
         ("nitsche, default normal", 12.5),
         ("nitsche, default normal", 1000.0),
         ("nitsche, normal= exact", 12.5),
         ("nitsche, normal= exact", 1000.0),
         ("penalty, exact normal", 1.0e4),
         ("penalty, exact normal", 1.0e6)]

outer_facets = int(uw.maths.BdIntegral(mesh, 1.0, "Outer").evaluate() / CELL)
uw.pprint(f"variant {VARIANT}  lambda {LAMBDA}  pressure nullspace {NULLSPACE}  cell {CELL}  cells {mesh.dm.getHeightStratum(0)[1]}  outer perimeter/cell {outer_facets}")
uw.pprint(f"{'method':26s} {'gamma':>7s} reason {'u L2':>10s} {'p L2':>10s} {'wall u':>10s} "
          f"{'wall u.n':>10s} {'<p>-<p_e>':>11s}")
for method, gamma in CASES:
    if ONLY and not any(word in method for word in ONLY.split(",")):
        continue
    reason, e_u, e_p, e_wall, e_un, dp = solve(method, gamma)
    uw.pprint(f"{method:26s} {str(gamma):>7s} {reason:6d} {e_u:10.3e} {e_p:10.3e} {e_wall:10.3e} "
              f"{e_un:10.3e} {dp:+11.3e}")
