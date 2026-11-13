"""#1072: does the Stokes preconditioner matrix P carry the boundary Jacobian terms?

test_1060's box (free slip on Top and Bottom, no slip on the sides) with the
Top and Bottom condition made four ways. After one solve the SNES holds the
Jacobian J and the preconditioner matrix P. For each field block we report
the norms of J, P and J - P, and the change of each against the build with
no condition on Top and Bottom, which has the same unknowns.

Serial. `-uw_res N` sets the resolution.
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(res=8)
print(f"res={params.res}", flush=True)


def build(method, res):
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=1.0 / res, qdegree=3)
    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2, vtype=uw.VarType.VECTOR)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.saddle_preconditioner = 1.0
    x, y = mesh.X
    stokes.bodyforce = sympy.Matrix([0, sympy.cos(sympy.pi * x)])
    stokes.add_dirichlet_bc((0.0, 0.0), "Left")
    stokes.add_dirichlet_bc((0.0, 0.0), "Right")
    if method == "essential":
        stokes.add_dirichlet_bc((sympy.oo, 0.0), "Top")
        stokes.add_dirichlet_bc((sympy.oo, 0.0), "Bottom")
    elif method == "penalty":
        Gamma = mesh.Gamma
        stokes.add_natural_bc(1e4 * Gamma.dot(v.sym) * Gamma, "Top")
        stokes.add_natural_bc(1e4 * Gamma.dot(v.sym) * Gamma, "Bottom")
    elif method == "nitsche":
        stokes.add_nitsche_bc(0.0, "Top")
        stokes.add_nitsche_bc(0.0, "Bottom")
    elif method != "none":
        raise ValueError(method)
    stokes.tolerance = 1e-6
    stokes.petsc_options["ksp_type"] = "fgmres"
    return stokes


def blocks(stokes):
    """The four field blocks of J and of P, as new scipy matrices."""
    import scipy.sparse as sp
    J, P, _ = stokes.snes.getJacobian()
    _, ises, _ = stokes.dm.createFieldDecomposition()
    iu, ip = ises[0], ises[1]
    out = {"same": J.handle == P.handle, "J_type": J.getType(), "P_type": P.getType()}
    for name, (r, c) in {"uu": (iu, iu), "up": (iu, ip), "pu": (ip, iu), "pp": (ip, ip)}.items():
        for tag, M in (("J", J), ("P", P)):
            S = M.createSubMatrix(r, c)
            ia, ja, a = S.getValuesCSR()
            out[tag + name] = sp.csr_matrix((a, ja, ia), shape=S.getSize())
            S.destroy()
    return out


def fro(M):
    return float(np.sqrt((M.multiply(M)).sum())) if M.nnz else 0.0


results = {}
for method in ("none", "essential", "penalty", "nitsche"):
    s = build(method, params.res)
    try:
        s.solve()
        reason = s.snes.getConvergedReason()
    except Exception as err:
        reason = f"raised {type(err).__name__}"
    b = blocks(s)
    results[method] = b
    print(f"\n{method}: SNES reason {reason}, J and P are one matrix: {b['same']}, "
          f"types {b['J_type']} / {b['P_type']}, unknowns u {b['Juu'].shape[0]}, p {b['Jpp'].shape[0]}", flush=True)
    for name in ("uu", "up", "pu", "pp"):
        Jb, Pb = b["J" + name], b["P" + name]
        print(f"  {name}: |J| {fro(Jb):.6e}  |P| {fro(Pb):.6e}  |J - P| {fro(Jb - Pb):.6e}", flush=True)

ref = results["none"]
print("\nChange against the build with no condition on Top and Bottom:")
for method in ("penalty", "nitsche"):
    b = results[method]
    for name in ("uu", "up", "pu", "pp"):
        dJ = fro(b["J" + name] - ref["J" + name])
        dP = fro(b["P" + name] - ref["P" + name])
        print(f"  {method:8s} {name}: |dJ| {dJ:.6e}  |dP| {dP:.6e}  |dJ - dP| "
              f"{fro((b['J' + name] - ref['J' + name]) - (b['P' + name] - ref['P' + name])):.6e}", flush=True)
