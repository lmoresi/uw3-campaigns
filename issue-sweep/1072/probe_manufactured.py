"""#1072: a manufactured free-slip Stokes solution, with the walls made three ways.

Unit box, viscosity 1, stream function sin(pi x) sin(pi y):

    u = (pi sin(pi x) cos(pi y), -pi cos(pi x) sin(pi y)),   p = cos(pi x) cos(pi y)

The normal velocity and the shear stress are zero on all four walls, so the
solution is free slip everywhere. The body force is 2 pi^2 u + grad p.

The four walls are made by essential conditions on the normal component, by
rotated free slip, or by Nitsche. For each we report the SNES reason, the
linear iterations, the L2 errors of velocity and pressure (pressure with its
mean removed) and the largest normal velocity at a wall node.

Serial. `-uw_res N` sets the resolution, `-uw_gamma G` the Nitsche parameter
(0 leaves the default).
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(res=8, gamma=0.0, qdegree=4, tol=1.0e-9)
print(f"res={params.res} gamma={params.gamma} qdegree={params.qdegree} tol={params.tol}", flush=True)

WALLS = {"Left": 0, "Right": 0, "Top": 1, "Bottom": 1}


def solve(method, res):
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=1.0 / res, qdegree=int(params.qdegree))
    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2, vtype=uw.VarType.VECTOR)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.saddle_preconditioner = 1.0

    x, y = mesh.X
    pi = sympy.pi
    u_exact = sympy.Matrix([[pi * sympy.sin(pi * x) * sympy.cos(pi * y),
                             -pi * sympy.cos(pi * x) * sympy.sin(pi * y)]])
    p_exact = sympy.cos(pi * x) * sympy.cos(pi * y)
    stokes.bodyforce = 2 * pi**2 * u_exact + sympy.Matrix([[p_exact.diff(x), p_exact.diff(y)]])

    for wall, normal_component in WALLS.items():
        if method == "essential":
            value = [sympy.oo, sympy.oo]
            value[normal_component] = 0.0
            stokes.add_dirichlet_bc(tuple(value), wall)
        elif method == "rotated":
            stokes.add_rotated_freeslip_bc(0, wall)
        elif method == "nitsche":
            if params.gamma > 0:
                stokes.add_nitsche_bc(0.0, wall, gamma=float(params.gamma))
            else:
                stokes.add_nitsche_bc(0.0, wall)
        else:
            raise ValueError(method)

    stokes.petsc_use_pressure_nullspace = True
    stokes.tolerance = float(params.tol)
    stokes.petsc_options["ksp_type"] = "fgmres"

    note = ""
    try:
        stokes.solve()
    except Exception as err:
        note = f" raised {type(err).__name__}: {str(err)[:80]}"
    reason = stokes.snes.getConvergedReason()
    its = stokes.snes.getLinearSolveIterations()

    du = v.sym - u_exact
    err_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate())
    p_mean = uw.maths.Integral(mesh, p.sym[0]).evaluate()
    dp = p.sym[0] - p_mean - p_exact
    err_p = np.sqrt(uw.maths.Integral(mesh, dp * dp).evaluate())

    xy = np.asarray(v.coords)
    vel = np.asarray(v.array)[:, 0, :]
    eps = 1.0e-10
    vn = max(np.abs(vel[xy[:, 0] < eps, 0]).max(), np.abs(vel[xy[:, 0] > 1 - eps, 0]).max(),
             np.abs(vel[xy[:, 1] < eps, 1]).max(), np.abs(vel[xy[:, 1] > 1 - eps, 1]).max())
    print(f"{method:9s} res {res:3d}: reason {reason:3d}, newton {stokes.snes.getIterationNumber()}, "
          f"linear {its:4d}, |u - u_e| {err_u:.6e}, |p - p_e| {err_p:.6e}, max|u.n| wall {vn:.3e}{note}",
          flush=True)
    return err_u, err_p


for method in ("essential", "rotated", "nitsche"):
    solve(method, int(params.res))
