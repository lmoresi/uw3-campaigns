"""#1151: preonly + lu with the pressure block of the preconditioner matrix scaled by 1/lambda.

The factorised matrix P is the system matrix plus a pressure mass block weighted
by `saddle_preconditioner` (default 1/viscosity). Here that weight is 1/lambda
and `stokes.penalty` stays 0, so the one application solves
    K u + G p = f,   -G^T u + (1/lambda) M p = 0,
the penalty method on the pressure-projected divergence. Plain Stokes only:
Stokes_Constrained refuses `saddle_preconditioner`.

Same box and load as penalty_route.py. Against ref0 (the default solve,
tolerance 1e-10): velocity and pressure in L2, relative; |div v|; largest
speed; |F(x)| / |F(0)|; what the solver reports.
"""
import warnings
import numpy as np
import sympy
import underworld3 as uw

warnings.simplefilter("ignore")

params = uw.Params(uw_res=4, uw_penalties="1,1e2,1e3,1e4,1e5,1e6,1e7,1e8")
RES = int(params.uw_res)
PENALTIES = [float(s) for s in str(params.uw_penalties).split(",")]


def l2(mesh, expr):
    return float(np.sqrt(uw.maths.Integral(mesh, expr).evaluate()))


def make(mesh, tag):
    v = uw.discretisation.MeshVariable(f"V{tag}", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable(f"P{tag}", mesh, 1, degree=1)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    x, _y = mesh.X
    stokes.bodyforce = sympy.Matrix([[0.0, sympy.cos(sympy.pi * x)]])
    stokes.tolerance = 1.0e-10
    for wall in ("Bottom", "Left", "Right"):
        stokes.add_essential_bc((0.0, 0.0), wall)
    return stokes, v, p


def speed(v):
    return float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max())


print(f"plain | res {RES} | snes ksponly | preonly + lu | saddle_preconditioner = 1/lambda, penalty 0", flush=True)
for lam in PENALTIES:
    mesh = uw.meshing.StructuredQuadBox(elementRes=(RES, RES), qdegree=3)
    ref, v0, p0 = make(mesh, "ref")
    ref.solve()
    stokes, v, p = make(mesh, "mass")
    stokes.saddle_preconditioner = 1.0 / lam
    stokes.petsc_options["snes_type"] = "ksponly"
    stokes.petsc_options["ksp_type"] = "preonly"
    stokes.petsc_options["pc_type"] = "lu"
    stokes.solve(zero_init_guess=True)

    snes = stokes.snes
    x = snes.getSolution()
    f = x.duplicate(); snes.computeFunction(x, f)
    zero = x.duplicate(); zero.set(0.0)
    f0 = x.duplicate(); snes.computeFunction(zero, f0)
    _A, P, _ = snes.getJacobian()
    _names, isets, _dms = stokes.dm.createFieldDecomposition()
    pp = P.createSubMatrix(isets[1], isets[1])
    vnorm = l2(mesh, v0.sym.dot(v0.sym))
    pnorm = l2(mesh, p0.sym[0] ** 2)
    dv = v.sym - v0.sym
    print(f"lambda {lam:8.1e} | snes reason {snes.getConvergedReason():2d} ksp reason {snes.ksp.getConvergedReason():2d} "
          f"| |F|/|F0| {f.norm() / f0.norm():.2e} | |P_pp| {pp.norm():.3e} "
          f"| v test-ref0 {l2(mesh, dv.dot(dv)) / vnorm:.3e} | p test-ref0 {l2(mesh, (p.sym[0] - p0.sym[0]) ** 2) / pnorm:.3e} "
          f"| div test {l2(mesh, mesh.vector.divergence(v.sym) ** 2):.3e} ref0 {l2(mesh, mesh.vector.divergence(v0.sym) ** 2):.3e} "
          f"| speed ref0 {speed(v0):.6e} test {speed(v):.6e}", flush=True)
