"""#1072: the Nitsche condition on the routes test_1060 does not take.

Each case is solved with the wall made by Nitsche and by a strong condition
(essential, or rotated free slip on a curved wall), and we report the SNES
reason, the Newton and linear iterations, the L2 difference of the two
velocity fields relative to the strong one, and the mismatch of the
pressure-velocity block against minus the transpose of the velocity-pressure
block.

Cases (`-uw_case`):
  inflow    box, no slip on the sides, u_y = 0.1 sin(2 pi x) on Top (no net flux)
  netflux   the same with u_y = 0.1 sin(pi x) on Top (net flux, so no solution)
  open      box, free slip on Top and Bottom, no slip on Left, nothing on Right
            (with nothing on either side a uniform horizontal flow is a null mode)
  box3d     3-D box, free slip on Top and Bottom, no slip on the four sides
  annulus   annulus, no slip on the inner wall, free slip on the outer wall
  resolve   the test_1060 box solved twice, the load doubled in between

Serial. `-uw_res N` sets the resolution.
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(case="inflow", res=8)
print(f"case={params.case} res={params.res}", flush=True)
res = int(params.res)
case = str(params.case)


def new_stokes(mesh):
    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2, vtype=uw.VarType.VECTOR)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.saddle_preconditioner = 1.0
    stokes.tolerance = 1e-8
    stokes.petsc_options["ksp_type"] = "fgmres"
    return stokes, v, p


def build(method):
    pi = sympy.pi
    if case in ("inflow", "netflux", "open", "resolve"):
        mesh = uw.meshing.UnstructuredSimplexBox(
            minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=1.0 / res, qdegree=3)
        stokes, v, p = new_stokes(mesh)
        x, y = mesh.X
        stokes.bodyforce = sympy.Matrix([0, sympy.cos(pi * x)])
        stokes.add_dirichlet_bc((0.0, 0.0), "Left")
        if case != "open":
            stokes.add_dirichlet_bc((0.0, 0.0), "Right")
        top = {"inflow": 0.1 * sympy.sin(2 * pi * x), "netflux": 0.1 * sympy.sin(pi * x)}.get(case, 0.0)
        if method == "strong":
            stokes.add_dirichlet_bc((sympy.oo, top), "Top")
            stokes.add_dirichlet_bc((sympy.oo, 0.0), "Bottom")
        else:
            stokes.add_nitsche_bc(top, "Top")
            stokes.add_nitsche_bc(0.0, "Bottom")
    elif case == "box3d":
        mesh = uw.meshing.UnstructuredSimplexBox(
            minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0), cellSize=1.0 / res, qdegree=3)
        stokes, v, p = new_stokes(mesh)
        x, y, z = mesh.X
        stokes.bodyforce = sympy.Matrix([0, 0, sympy.cos(pi * x) * sympy.cos(pi * y)])
        for wall in ("Left", "Right", "Front", "Back"):
            stokes.add_dirichlet_bc((0.0, 0.0, 0.0), wall)
        for wall in ("Top", "Bottom"):
            if method == "strong":
                stokes.add_dirichlet_bc((sympy.oo, sympy.oo, 0.0), wall)
            else:
                stokes.add_nitsche_bc(0.0, wall)
    elif case == "annulus":
        mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=1.0 / res, qdegree=3)
        stokes, v, p = new_stokes(mesh)
        x, y = mesh.X
        r = sympy.sqrt(x**2 + y**2)
        stokes.bodyforce = sympy.cos(3 * sympy.atan2(y, x)) * sympy.Matrix([x / r, y / r])
        stokes.add_dirichlet_bc((0.0, 0.0), "Lower")
        if method == "strong":
            stokes.add_rotated_freeslip_bc(0, "Upper")
        else:
            stokes.add_nitsche_bc(0.0, "Upper")
    else:
        raise ValueError(case)
    return stokes, v, p


def run(stokes):
    note = ""
    try:
        stokes.solve()
    except Exception as err:
        note = f" raised {type(err).__name__}: {str(err)[:100]}"
    return (stokes.snes.getConvergedReason(), stokes.snes.getIterationNumber(),
            stokes.snes.getLinearSolveIterations(), note)


def transpose_mismatch(stokes):
    J = stokes.snes.getJacobian()[0]
    _, ises, _ = stokes.dm.createFieldDecomposition()
    pu = J.createSubMatrix(ises[1], ises[0])
    up = J.createSubMatrix(ises[0], ises[1])
    scale = up.norm()
    up.transpose()  # in place, on the copy
    pu.axpy(1.0, up)
    return pu.norm(), scale


def l2(mesh, expr):
    return np.sqrt(uw.maths.Integral(mesh, expr.dot(expr)).evaluate())


results = {}
for method in ("strong", "nitsche"):
    stokes, v, p = build(method)
    out = run(stokes)
    line = f"{method:8s}: reason {out[0]:3d}, newton {out[1]}, linear {out[2]}{out[3]}"
    if method == "nitsche":
        mismatch, scale = transpose_mismatch(stokes)
        line += f"; |J_pu + J_up^T| {mismatch:.3e} of {scale:.3e}"
    print(line, flush=True)
    results[method] = (stokes, v, p)
    if case == "resolve":
        first = np.asarray(v.array).copy()
        stokes.bodyforce = 2 * stokes.bodyforce.sym
        out = run(stokes)
        second = np.asarray(v.array)
        print(f"{method:8s}: second solve reason {out[0]:3d}, newton {out[1]}, linear {out[2]}{out[3]}; "
              f"|v2 - 2 v1| / |2 v1| {np.linalg.norm(second - 2 * first) / np.linalg.norm(2 * first):.3e}",
              flush=True)

(s_strong, v_strong, _), (s_nitsche, v_nitsche, _) = results["strong"], results["nitsche"]
a, b = np.asarray(v_strong.array), np.asarray(v_nitsche.array)
if a.shape == b.shape:
    print(f"nodal |v_nitsche - v_strong| / |v_strong| {np.linalg.norm(a - b) / np.linalg.norm(a):.6e}", flush=True)
