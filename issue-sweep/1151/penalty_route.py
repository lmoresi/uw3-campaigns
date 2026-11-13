"""#1151: does preonly + lu with a large grad-div penalty give the Stokes answer?

Box, body force (0, cos(pi x)), viscosity 1. Plain: no slip on Bottom, Left,
Right. Constrained: no slip on Bottom, no flow through Left and Right by
multipliers. Top is open in both, so the pressure has no free constant.

Three solves on one mesh:
  ref0  the default solve (FGMRES + Schur field split), tolerance 1e-10, no penalty;
  refL  the same penalised system solved to tolerance: FGMRES on A, preconditioned
        by the factorisation of P (ksp_type=fgmres, pc_type=lu, rtol 1e-12);
  test  ksp_type=preonly, pc_type=lu, stokes.penalty = lambda, snes ksponly or newtonls.

Reported as L2 norms over the box, relative to ref0's: test - ref0, test - refL
(the error of the one application), refL - ref0 (what the penalty itself does to
the discrete answer); |div v| of test and refL; the largest nodal speeds; the
pressure and p - lambda div v against ref0's pressure; the residual
|F(x)| / |F(0)|; and what the system matrix A and the preconditioner matrix P
hold block by block. Matrices are read through copies of their blocks only.
"""
import warnings
import numpy as np
import sympy
import underworld3 as uw

warnings.simplefilter("ignore")

params = uw.Params(
    uw_res=4,
    uw_kind="plain",          # plain | constrained
    uw_snes="ksponly",        # ksponly | newtonls
    uw_penalties="0,1,1e2,1e3,1e4,1e5,1e6,1e7,1e8",
)
RES, KIND, SNES = int(params.uw_res), str(params.uw_kind), str(params.uw_snes)
PENALTIES = [float(s) for s in str(params.uw_penalties).split(",")]


def l2(mesh, expr):
    return float(np.sqrt(uw.maths.Integral(mesh, expr).evaluate()))


def make(mesh, tag, kind):
    v = uw.discretisation.MeshVariable(f"V{tag}", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable(f"P{tag}", mesh, 1, degree=1)
    cls = uw.systems.Stokes_Constrained if kind == "constrained" else uw.systems.Stokes
    stokes = cls(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    x, _y = mesh.X
    stokes.bodyforce = sympy.Matrix([[0.0, sympy.cos(sympy.pi * x)]])
    stokes.tolerance = 1.0e-10
    stokes.add_essential_bc((0.0, 0.0), "Bottom")
    if kind == "constrained":
        stokes.add_constraint_bc(0.0, "Left", normal=sympy.Matrix([[-1.0, 0.0]]))
        stokes.add_constraint_bc(0.0, "Right", normal=sympy.Matrix([[1.0, 0.0]]))
    else:
        stokes.add_essential_bc((0.0, 0.0), "Left")
        stokes.add_essential_bc((0.0, 0.0), "Right")
    return stokes, v, p


def blocks(stokes):
    """What A and P hold, by field block (Frobenius norms of copies)."""
    snes = stokes.snes
    A, P, _ = snes.getJacobian()
    names, isets, _dms = stokes.dm.createFieldDecomposition()
    out = [f"same object {A.handle == P.handle}"]
    for i in (0, 1):
        for j in (0, 1):
            a = A.createSubMatrix(isets[i], isets[j])
            b = P.createSubMatrix(isets[i], isets[j])
            d = a.copy()
            d.axpy(-1.0, b, structure=d.Structure.DIFFERENT_NONZERO_PATTERN)
            out.append(f"{'vp'[i]}{'vp'[j]}: |A| {a.norm():.3e} |P| {b.norm():.3e} |A-P| {d.norm():.3e}")
            if i == 1 and j == 1:
                diag = b.getDiagonal()
                out.append(f"P pp diagonal in [{diag.min()[1]:.3e}, {diag.max()[1]:.3e}]")
    vp = A.createSubMatrix(isets[0], isets[1])
    pv_t = A.createSubMatrix(isets[1], isets[0])
    pv_t.transpose()                       # in place, on our own copy
    minus = vp.copy(); minus.axpy(-1.0, pv_t, structure=minus.Structure.DIFFERENT_NONZERO_PATTERN)
    plus = vp.copy(); plus.axpy(1.0, pv_t, structure=plus.Structure.DIFFERENT_NONZERO_PATTERN)
    out.append(f"|A_vp - A_pv^T| {minus.norm():.3e} |A_vp + A_pv^T| {plus.norm():.3e}")
    return " | ".join(out)


def speed(v):
    return float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max())


def run(lam):
    mesh = uw.meshing.StructuredQuadBox(elementRes=(RES, RES), qdegree=3)
    ref, v0, p0 = make(mesh, "ref", KIND)
    ref.solve()

    exact, vL, pL = make(mesh, "exa", KIND)
    exact.penalty = lam
    exact.petsc_options["snes_type"] = "ksponly"
    exact.petsc_options["ksp_type"] = "fgmres"
    exact.petsc_options["ksp_rtol"] = 1.0e-12
    exact.petsc_options["ksp_atol"] = 1.0e-30
    exact.petsc_options["ksp_max_it"] = 500
    exact.petsc_options["pc_type"] = "lu"
    # the adaptive linear tolerance would otherwise set rtol 0.3 for this one solve
    exact.petsc_options["snes_ksp_ew"] = "false"
    exact.solve(zero_init_guess=True)
    xe = exact.snes.getSolution()
    fe = xe.duplicate(); exact.snes.computeFunction(xe, fe)
    ze = xe.duplicate(); ze.set(0.0)
    fe0 = xe.duplicate(); exact.snes.computeFunction(ze, fe0)
    exact_note = (f"refL ksp reason {exact.snes.ksp.getConvergedReason():2d} "
                  f"its {exact.snes.ksp.getIterationNumber():3d} rtol {exact.snes.ksp.getTolerances()[0]:.0e} "
                  f"|F|/|F0| {fe.norm() / fe0.norm():.1e}")

    stokes, v, p = make(mesh, "pen", KIND)
    stokes.penalty = lam
    stokes.petsc_options["snes_type"] = SNES
    stokes.petsc_options["ksp_type"] = "preonly"
    stokes.petsc_options["pc_type"] = "lu"
    try:
        stokes.solve(zero_init_guess=True)
    except Exception as err:  # noqa: BLE001 - a probe reports whatever stops it
        return f"lambda {lam:8.1e} | raised {type(err).__name__}: {str(err)[:200]}", None

    snes = stokes.snes
    x = snes.getSolution()
    f = x.duplicate(); snes.computeFunction(x, f)
    zero = x.duplicate(); zero.set(0.0)
    f0 = x.duplicate(); snes.computeFunction(zero, f0)

    def rel(a, b, norm):
        d = a - b
        return l2(mesh, d.dot(d)) / norm

    vnorm = l2(mesh, v0.sym.dot(v0.sym))
    pnorm = l2(mesh, p0.sym[0] ** 2)
    div, divL = mesh.vector.divergence(v.sym), mesh.vector.divergence(vL.sym)
    line = (f"lambda {lam:8.1e} | ref0 reason {ref.snes.getConvergedReason()} | {exact_note} "
            f"| test snes reason {snes.getConvergedReason():2d} its {snes.getIterationNumber():3d} "
            f"ksp reason {snes.ksp.getConvergedReason():2d} | |F|/|F0| {f.norm() / f0.norm():.2e}\n"
            f"      velocity: test-ref0 {rel(v.sym, v0.sym, vnorm):.3e} | test-refL {rel(v.sym, vL.sym, vnorm):.3e} "
            f"| refL-ref0 {rel(vL.sym, v0.sym, vnorm):.3e} | div test {l2(mesh, div ** 2):.3e} refL {l2(mesh, divL ** 2):.3e} "
            f"| speed ref0 {speed(v0):.6e} refL {speed(vL):.6e} test {speed(v):.6e}\n"
            f"      pressure vs ref0: p test {l2(mesh, (p.sym[0] - p0.sym[0]) ** 2) / pnorm:.3e} "
            f"| p - lam div, test {l2(mesh, (p.sym[0] - lam * div - p0.sym[0]) ** 2) / pnorm:.3e} "
            f"| p refL {l2(mesh, (pL.sym[0] - p0.sym[0]) ** 2) / pnorm:.3e} "
            f"| p - lam div, refL {l2(mesh, (pL.sym[0] - lam * divL - p0.sym[0]) ** 2) / pnorm:.3e} "
            f"| |p test|/|p ref0| {l2(mesh, p.sym[0] ** 2) / pnorm:.3e}")
    return line, blocks(stokes)


print(f"kind {KIND} | res {RES} | snes {SNES} | preonly + lu", flush=True)
for lam in PENALTIES:
    line, blk = run(lam)
    print(line, flush=True)
    if blk and lam in (0.0, 1.0e6):
        print("    " + blk, flush=True)
