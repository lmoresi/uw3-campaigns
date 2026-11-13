"""One case of the add_condition truth table. Serial. Prints one JSON line.

usage: python truth_table.py <case-name> | --list
"""
import sys
import json
import hashlib
import warnings

import numpy as np
import sympy

import underworld3 as uw

oo = sympy.oo
Q = uw.quantity


def stokes2d():
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.25, qdegree=3)
    x, z = mesh.X
    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    s.bodyforce = sympy.Matrix([[0, sympy.cos(sympy.pi * x)]])
    s.add_dirichlet_bc((0.0, 0.0), "Bottom")
    s.add_dirichlet_bc((0.0, None), "Right")
    return mesh, s, v, p


def stokes3d():
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0), cellSize=0.5, qdegree=3)
    x, y, z = mesh.X
    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    s.bodyforce = sympy.Matrix([[0, 0, sympy.cos(sympy.pi * x)]])
    s.add_dirichlet_bc((0.0, 0.0, 0.0), "Bottom")
    s.add_dirichlet_bc((0.0, None, None), "Right")
    return mesh, s, v, p


def poisson():
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.25, qdegree=3)
    t = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
    s = uw.systems.Poisson(mesh, u_Field=t)
    s.constitutive_model = uw.constitutive_models.DiffusionModel
    s.constitutive_model.Parameters.diffusivity = 1
    s.f = 0.0
    s.add_dirichlet_bc(1.0, "Bottom")
    return mesh, s, t, None


def vector():
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.25, qdegree=3)
    x, z = mesh.X
    w = uw.discretisation.MeshVariable("W", mesh, mesh.dim, degree=2)
    s = uw.systems.Vector_Projection(mesh, w)
    s.uw_function = sympy.Matrix([[sympy.sin(x), 1 + z]])
    s.smoothing = 0.0
    return mesh, s, w, None


FIX = dict(stokes2d=stokes2d, stokes3d=stokes3d, poisson=poisson, vector=vector)

# name: (fixture, method, conds-builder, boundary, components-or-"absent", target (component -> asked))
C = {}


def case(name, fixture, method, conds, boundary, components="absent", asked=None, f_id=None):
    C[name] = dict(fixture=fixture, method=method, conds=conds, boundary=boundary,
                   components=components, asked=asked or {}, f_id=f_id)


# --- essential, Stokes 2-D ---------------------------------------------------
E = "add_dirichlet_bc"
case("s2_scalar_c1", "stokes2d", E, lambda m, v: 0.05, "Left", 1, {1: 0.05})
case("s2_tuple1_c1", "stokes2d", E, lambda m, v: (0.05,), "Left", (1,), {1: 0.05})
case("s2_list1_c1", "stokes2d", E, lambda m, v: [0.05], "Left", [1], {1: 0.05})
case("s2_tuple1_c01", "stokes2d", E, lambda m, v: (0.05,), "Left", (0, 1), {0: 0.05, 1: 0.05})
case("s2_scalar_c0", "stokes2d", E, lambda m, v: 0.05, "Left", 0, {0: 0.05})
case("s2_tuple1_c0", "stokes2d", E, lambda m, v: (0.05,), "Left", (0,), {0: 0.05})
case("s2_scalar_nocomp", "stokes2d", E, lambda m, v: 0.05, "Left", "absent", {0: 0.05})
case("s2_int_c1", "stokes2d", E, lambda m, v: 0, "Left", 1, {1: 0.0})
case("s2_full_c1", "stokes2d", E, lambda m, v: (0.0, 0.05), "Left", (1,), {1: 0.05})
case("s2_full_c1_int", "stokes2d", E, lambda m, v: (0.0, 0.05), "Left", 1, {1: 0.05})
case("s2_full_c01", "stokes2d", E, lambda m, v: (0.01, 0.05), "Left", (0, 1), {0: 0.01, 1: 0.05})
case("s2_full_c10", "stokes2d", E, lambda m, v: (0.01, 0.05), "Left", (1, 0), {0: 0.01, 1: 0.05})
case("s2_None_005", "stokes2d", E, lambda m, v: (None, 0.05), "Left", "absent", {1: 0.05})
case("s2_None_005_compNone", "stokes2d", E, lambda m, v: (None, 0.05), "Left", None, {1: 0.05})
case("s2_oo_005", "stokes2d", E, lambda m, v: (oo, 0.05), "Left", "absent", {1: 0.05})
case("s2_moo_005", "stokes2d", E, lambda m, v: (-oo, 0.05), "Left", "absent", {1: 0.05})
case("s2_listNone_005", "stokes2d", E, lambda m, v: [None, 0.05], "Left", "absent", {1: 0.05})
case("s2_None_005_c1", "stokes2d", E, lambda m, v: (None, 0.05), "Left", 1, {1: 0.05})
case("s2_005_None_c1", "stokes2d", E, lambda m, v: (0.05, None), "Left", 1, {1: 0.05})
case("s2_None_005_c0", "stokes2d", E, lambda m, v: (None, 0.05), "Left", 0, {})
case("s2_matrow_oo", "stokes2d", E, lambda m, v: sympy.Matrix([[oo, 0.05]]), "Left", "absent", {1: 0.05})
case("s2_matcol_oo", "stokes2d", E, lambda m, v: sympy.Matrix([oo, 0.05]), "Left", "absent", {1: 0.05})
case("s2_matrow_full_c1", "stokes2d", E, lambda m, v: sympy.Matrix([[0.0, 0.05]]), "Left", (1,), {1: 0.05})
case("s2_matcol_full_c1", "stokes2d", E, lambda m, v: sympy.Matrix([0.0, 0.05]), "Left", (1,), {1: 0.05})
case("s2_mat1_c1", "stokes2d", E, lambda m, v: sympy.Matrix([0.05]), "Left", (1,), {1: 0.05})
case("s2_mat1_c0", "stokes2d", E, lambda m, v: sympy.Matrix([0.05]), "Left", (0,), {0: 0.05})
case("s2_nparray_full", "stokes2d", E, lambda m, v: np.array([0.0, 0.05]), "Left", "absent", {0: 0.0, 1: 0.05})
case("s2_nparray1_c1", "stokes2d", E, lambda m, v: np.array([0.05]), "Left", 1, {1: 0.05})
case("s2_npfloat_c1", "stokes2d", E, lambda m, v: np.float64(0.05), "Left", 1, {1: 0.05})
case("s2_npfloat_c0", "stokes2d", E, lambda m, v: np.float64(0.05), "Left", 0, {0: 0.05})
case("s2_npint_comp", "stokes2d", E, lambda m, v: (0.0, 0.05), "Left", np.int64(1), {1: 0.05})
case("s2_nparray_comp", "stokes2d", E, lambda m, v: (0.0, 0.05), "Left", np.array([1]), {1: 0.05})
case("s2_quantity_c1", "stokes2d", E, lambda m, v: Q(0.05, "m/s"), "Left", 1, {1: 0.05})
case("s2_quantity_c0", "stokes2d", E, lambda m, v: Q(0.05, "m/s"), "Left", 0, {0: 0.05})
case("s2_None_quantity", "stokes2d", E, lambda m, v: (None, Q(0.05, "m/s")), "Left", "absent", {1: 0.05})
case("s2_tupquantity_c1", "stokes2d", E, lambda m, v: (Q(0.05, "m/s"),), "Left", (1,), {1: 0.05})
case("s2_pint_c1", "stokes2d", E, lambda m, v: 0.05 * uw.units("m/s"), "Left", 1, {1: 0.05})
case("s2_sym_expr_full", "stokes2d", E, lambda m, v: (None, 0.05 * (1 + m.X[1])), "Left", "absent", {})
case("s2_sym_scalar_c1", "stokes2d", E, lambda m, v: 0.05 * (1 + m.X[1]), "Left", 1, {})
case("s2_varsym_nocomp", "stokes2d", E, lambda m, v: v.sym, "Left", "absent", {})
case("s2_varsym_c1", "stokes2d", E, lambda m, v: v.sym, "Left", (1,), {})
case("s2_varsym1_c1", "stokes2d", E, lambda m, v: v.sym[1], "Left", 1, {})
case("s2_varsym1tuple_c1", "stokes2d", E, lambda m, v: (v.sym[1],), "Left", (1,), {})
case("s2_neg_comp", "stokes2d", E, lambda m, v: (0.0, 0.05), "Left", -1, {1: 0.05})
case("s2_comp2_len3", "stokes2d", E, lambda m, v: (0.0, 0.0, 0.05), "Left", 2, {})
case("s2_comp2_len1", "stokes2d", E, lambda m, v: 0.05, "Left", 2, {})
case("s2_empty_comp_short", "stokes2d", E, lambda m, v: (0.05,), "Left", (), {0: 0.05, 1: 0.05})
case("s2_empty_value_c1", "stokes2d", E, lambda m, v: (), "Left", 1, {})
case("s2_comp_str", "stokes2d", E, lambda m, v: 0.05, "Left", "1", {})
case("s2_comp_float", "stokes2d", E, lambda m, v: 0.05, "Left", 1.0, {})
case("s2_ess_alias_c1", "stokes2d", "add_essential_bc", lambda m, v: [0.05], "Left", [1], {1: 0.05})
case("s2_ess_alias_full", "stokes2d", "add_essential_bc", lambda m, v: (None, 0.05), "Left", "absent", {1: 0.05})
case("s2_kw_components", "stokes2d", E, lambda m, v: 0.05, "Left", ("kw", 1), {1: 0.05})

# --- essential, Stokes 3-D ---------------------------------------------------
case("s3_scalar_c1", "stokes3d", E, lambda m, v: 0.05, "Left", 1, {1: 0.05})
case("s3_scalar_c2", "stokes3d", E, lambda m, v: 0.05, "Left", 2, {2: 0.05})
case("s3_scalar_c0", "stokes3d", E, lambda m, v: 0.05, "Left", 0, {0: 0.05})
case("s3_len2_c1", "stokes3d", E, lambda m, v: (0.0, 0.05), "Left", 1, {1: 0.05})
case("s3_len2_c2", "stokes3d", E, lambda m, v: (0.0, 0.05), "Left", 2, {2: 0.05})
case("s3_len2_c12", "stokes3d", E, lambda m, v: (0.01, 0.05), "Left", (1, 2), {1: 0.01, 2: 0.05})
case("s3_full_c12", "stokes3d", E, lambda m, v: (0.0, 0.01, 0.05), "Left", (1, 2), {1: 0.01, 2: 0.05})
case("s3_None_None_005", "stokes3d", E, lambda m, v: (None, None, 0.05), "Left", "absent", {2: 0.05})
case("s3_None_005_short", "stokes3d", E, lambda m, v: (None, 0.05), "Left", "absent", {1: 0.05})

# --- natural, Stokes 2-D -----------------------------------------------------
N = "add_natural_bc"
case("n2_scalar_c1", "stokes2d", N, lambda m, v: 0.05, "Top", 1)
case("n2_tuple1_c1", "stokes2d", N, lambda m, v: (0.05,), "Top", (1,))
case("n2_scalar_c0", "stokes2d", N, lambda m, v: 0.05, "Top", 0)
case("n2_scalar_nocomp", "stokes2d", N, lambda m, v: 0.05, "Top", "absent")
case("n2_full_nocomp", "stokes2d", N, lambda m, v: (0.0, 0.05), "Top", "absent")
case("n2_full_c1", "stokes2d", N, lambda m, v: (0.0, 0.05), "Top", (1,))
case("n2_full_c01", "stokes2d", N, lambda m, v: (0.0, 0.05), "Top", (0, 1))
case("n2_None_005", "stokes2d", N, lambda m, v: (None, 0.05), "Top", "absent")
case("n2_matrix_full", "stokes2d", N, lambda m, v: sympy.Matrix([[0.0, 0.05]]), "Top", "absent")
case("n2_penalty_sym", "stokes2d", N, lambda m, v: 100 * v.sym, "Top", "absent")
case("n3_scalar_c1", "stokes3d", N, lambda m, v: 0.05, "Top", 1)
case("n3_full_nocomp", "stokes3d", N, lambda m, v: (0.0, 0.0, 0.05), "Top", "absent")

# --- scalar solver (Poisson) -------------------------------------------------
case("p_scalar", "poisson", E, lambda m, v: 0.0, "Top", "absent", {0: 0.0})
case("p_scalar_c0", "poisson", E, lambda m, v: 0.0, "Top", 0, {0: 0.0})
case("p_tuple_c0", "poisson", E, lambda m, v: (0.0,), "Top", (0,), {0: 0.0})
case("p_scalar_c1", "poisson", E, lambda m, v: 0.0, "Top", 1, {})
case("p_int", "poisson", E, lambda m, v: 0, "Top", "absent", {0: 0.0})
case("p_quantity", "poisson", E, lambda m, v: Q(0.0, "K"), "Top", "absent", {0: 0.0})
case("p_matrix", "poisson", E, lambda m, v: sympy.Matrix([0.0]), "Top", "absent", {0: 0.0})
case("p_sym_expr", "poisson", E, lambda m, v: sympy.sin(m.X[0]), "Top", "absent", {})
case("p_sym_expr_tuple", "poisson", E, lambda m, v: (sympy.sin(m.X[0]),), "Top", "absent", {})
case("p_nat_scalar", "poisson", N, lambda m, v: 1.0, "Top", "absent")
case("p_nat_scalar_c0", "poisson", N, lambda m, v: 1.0, "Top", 0)
case("p_nat_scalar_c1", "poisson", N, lambda m, v: 1.0, "Top", 1)

# --- vector solver (Vector_Projection) --------------------------------------
case("v_None_0", "vector", E, lambda m, v: (None, 0.05), "Left", "absent", {1: 0.05})
case("v_scalar_c1", "vector", E, lambda m, v: 0.05, "Left", 1, {1: 0.05})
case("v_scalar_c0", "vector", E, lambda m, v: 0.05, "Left", 0, {0: 0.05})
case("v_full_c1", "vector", E, lambda m, v: (0.0, 0.05), "Left", (1,), {1: 0.05})

# --- pressure field, through add_condition ----------------------------------
A = "add_condition"
case("pr_scalar", "stokes2d", A, lambda m, v: 0.0, "Top", "absent", f_id=1)
case("pr_mat_c0", "stokes2d", A, lambda m, v: sympy.Matrix([0]), "Top", (0), f_id=1)
case("pr_scalar_c1", "stokes2d", A, lambda m, v: 0.0, "Top", 1, f_id=1)


def digest(a):
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a)).tobytes()).hexdigest()[:16]


def run(name):
    c = C[name]
    out = dict(case=name)
    mesh, s, var, p = FIX[c["fixture"]]()
    conds = c["conds"](mesh, var)
    comps = c["components"]
    kw = False
    if isinstance(comps, tuple) and len(comps) == 2 and comps[0] == "kw":
        kw, comps = True, comps[1]
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        try:
            if c["method"] == "add_condition":
                ctype = "dirichlet"
                if comps == "absent":
                    s.add_condition(c["f_id"], ctype, conds, c["boundary"])
                else:
                    s.add_condition(c["f_id"], ctype, conds, c["boundary"], components=comps)
            elif comps == "absent":
                getattr(s, c["method"])(conds, c["boundary"])
            elif kw:
                getattr(s, c["method"])(conds, c["boundary"], components=comps)
            else:
                getattr(s, c["method"])(conds, c["boundary"], comps)
            out["add"] = "accepted"
        except Exception as e:  # the outcome being recorded
            out["add"] = f"{type(e).__name__}: {str(e)[:400]}"
    out["deprecation"] = sorted({str(w.message)[:60] for w in rec
                                 if issubclass(w.category, DeprecationWarning)})
    if out["add"] != "accepted":
        return out
    bcs = s.natural_bcs if c["method"] == "add_natural_bc" else s.essential_bcs
    bc = bcs[-1]
    out["stored_fn"] = str(list(bc.fn_f if c["method"] == "add_natural_bc" else bc.fn))
    out["stored_components"] = [int(k) for k in bc.components]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            s.solve()
        except Exception as e:  # the outcome being recorded
            out["solve"] = f"{type(e).__name__}: {str(e)[:300]}"
            return out
    out["solve"] = "ran"
    out["snes_reason"] = int(s.snes.getConvergedReason())
    out["snes_its"] = int(s.snes.getIterationNumber())
    out["ksp_its"] = int(s.snes.getLinearSolveIterations())
    out["u_hash"] = digest(var.array)
    if p is not None:
        out["p_hash"] = digest(p.array)
    X = np.asarray(var.coords)
    U = np.asarray(var.array)[:, 0, :]
    b = c["boundary"]
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    if b == "Left":
        on = np.abs(X[:, 0] - lo[0]) < 1e-9
        # leave out nodes shared with Bottom (its value is registered separately)
        on &= X[:, -1] > lo[-1] + 1e-9
    elif b == "Top":
        on = np.abs(X[:, -1] - hi[-1]) < 1e-9
        on &= X[:, 0] < hi[0] - 1e-9
    else:
        on = np.zeros(len(X), bool)
    out["on_boundary"] = {}
    for k in range(U.shape[1]):
        vals = U[on, k]
        out["on_boundary"][k] = [float(f"{vals.min():.6g}"), float(f"{vals.max():.6g}")]
    out["max_err"] = {int(k): float(f"{np.abs(U[on, k] - a).max():.3e}") for k, a in c["asked"].items()}
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--list":
        print("\n".join(C))
    else:
        try:
            res = run(sys.argv[1])
        except Exception as e:  # a failure of the fixture itself
            res = dict(case=sys.argv[1], fixture_error=f"{type(e).__name__}: {str(e)[:300]}")
        print("RESULT " + json.dumps(res))
