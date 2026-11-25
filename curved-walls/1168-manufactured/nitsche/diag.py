"""Why Nitsche free slip does not converge on the elliptical annulus (UNFILED 24).

    python diag.py -uw_cell_size 0.05 -uw_cases A,B -uw_variant both-xy

The manufactured solutions of ../manufactured.py (exact free slip on both walls;
variant both-xy has slip odd in x and y). Each case puts a treatment on each wall:

  ess        the exact velocity as essential data
  nit:bn     Nitsche, default normal (mesh.boundary_normal: P1 vertex-averaged facet normals)
  nit:ex     Nitsche, normal= the wall's exact normal
  nit:fa     Nitsche, normal= mesh.Gamma (each facet's own unit normal at the quadrature points)
  nat        the exact traction as a natural condition (an open boundary)

Nitsche on Stokes adds -(n.d)(u.d - g) q to the continuity row. With q = 1 the row is
int div u - sum_walls int u.n_used = sum_walls int u.(n_facet - n_used) (the discrete
divergence theorem is exact for P2 velocity on straight facets), a constraint on the
slip unless n_used is the facet normal: hypothesis (a).

P2/P1, viscosity 1, velocity block by MUMPS, tolerance 1e-10.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sympy
import underworld3 as uw

import manufactured
import measure_mesh

params = uw.Params(uw_cell_size=0.05, uw_cases="A", uw_variant="both-xy", uw_gamma=12.5,
                   uw_pressure_nullspace=True)
CELL = float(params.uw_cell_size)
VARIANT = str(params.uw_variant)
GAMMA = float(params.uw_gamma)
NULLSPACE = bool(params.uw_pressure_nullspace)

# (outer, inner) treatments per case
CASES = {
    "A": ("nit:bn", "nit:bn"),       # #1168's reported Nitsche row
    "B": ("nit:fa", "nit:fa"),       # facet normal: no extra constraint predicted
    "C": ("nit:ex", "nit:ex"),
    "D1": ("nit:bn", "ess"),         # which wall: outer Nitsche only
    "D2": ("ess", "nit:bn"),         # inner Nitsche only
    "E": ("nit:bn", "nat"),          # open inner boundary: the domain is not closed
    "E0": ("ess", "nat"),            # control for the natural condition's sign
    "E0-": ("ess", "nat-"),
    "E-": ("nit:bn", "nat-"),
    "F-": ("nit:fa", "nat-"),
    "F": ("nit:fa", "nat"),
    "R": ("rot", "rot"),             # rotated, default normal (reference)
    "X": ("ess", "ess"),             # control
}

mesh = measure_mesh.ellipse_mesh(CELL)
X, Y = mesh.X
F = manufactured.fields(VARIANT)
on_mesh = {manufactured.x: X, manufactured.y: Y}
u_e = F["u"].T.xreplace(on_mesh)
p_e = F["p"].xreplace(on_mesh)
f_e = F["f"].T.xreplace(on_mesh)
normals = {"Outer": F["n"].T.xreplace(on_mesh), "Inner": F["n_inner"].T.xreplace(on_mesh)}
grad = F["u"].jacobian([manufactured.x, manufactured.y])
sigma = ((grad + grad.T) - F["p"] * sympy.eye(2)).xreplace(on_mesh)

v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
area = uw.maths.Integral(mesh, 1.0).evaluate()
mean_p_e = uw.maths.Integral(mesh, p_e).evaluate() / area
norm_u = np.sqrt(uw.maths.Integral(mesh, u_e.dot(u_e)).evaluate())


def apply(stokes, wall, how):
    n_ex = normals[wall]
    if how == "ess":
        stokes.add_essential_bc(u_e, wall)
    elif how == "rot":
        stokes.add_rotated_freeslip_bc(0, wall)
    elif how == "nit:bn":
        stokes.add_nitsche_bc(0, wall, gamma=GAMMA)
    elif how == "nit:ex":
        stokes.add_nitsche_bc(0, wall, normal=n_ex, gamma=GAMMA)
    elif how == "nit:fa":
        stokes.add_nitsche_bc(0, wall, normal=mesh.Gamma, gamma=GAMMA)
    elif how in ("nat", "nat-"):
        # traction sigma.n on the wall, n the unit normal out of the fluid; "nat-"
        # takes the opposite sign (the control E0/E0- decides which convention holds)
        sign = 1 if how == "nat" else -1
        stokes.add_natural_bc(sign * (sigma * n_ex.T).T, wall)
    else:
        raise ValueError(how)


def solve(case):
    outer, inner = CASES[case]
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    closed = not any(t.startswith("nat") for t in (outer, inner))
    stokes.petsc_use_pressure_nullspace = NULLSPACE and closed
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    apply(stokes, "Outer", outer)
    apply(stokes, "Inner", inner)
    stokes.solve(zero_init_guess=True)
    reason = stokes.snes.getConvergedReason()
    ksp = stokes.snes.getKSP().getConvergedReason()
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    du = v.sym - u_e
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    # the extra constraint's residual: int u.(Gamma - n_used) over the Nitsche walls
    return reason, ksp, e_u, mean_p - mean_p_e


uw.pprint(f"variant {VARIANT}  cell {CELL}  gamma {GAMMA}  nullspace(closed) {NULLSPACE}  "
          f"cells {mesh.dm.getHeightStratum(0)[1]}")
for case in str(params.uw_cases).split(","):
    reason, ksp, e_u, dp = solve(case)
    uw.pprint(f"case {case:3s} outer {CASES[case][0]:7s} inner {CASES[case][1]:7s} "
              f"snes {reason:3d} ksp {ksp:3d}  u L2 {e_u:10.3e}  <p>-<p_e> {dp:+11.3e}", flush=True)
