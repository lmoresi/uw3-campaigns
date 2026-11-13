"""_essential_value (PR #1127 at 07647295) on records that PR #1139 accepts. Serial."""
import ast, sys, warnings, json
import sympy
import underworld3 as uw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from truth_table import stokes2d, stokes3d

src = open(__file__.rsplit("/", 1)[0] + "/t1127/rotated_bc_at_1127.py").read()
tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_essential_value"][0]
ns = {"sympy": sympy}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "essential_value", "exec"), ns)
_essential_value = ns["_essential_value"]

def probe(name, fixture, conds, components, dim):
    mesh, s, v, p = fixture()
    out = {"case": name}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s.add_dirichlet_bc(conds, "Left", components) if components is not None else s.add_dirichlet_bc(conds, "Left")
    except Exception as e:
        out["add"] = f"{type(e).__name__}"; print(json.dumps(out)); return
    bc = s.essential_bcs[-1]
    out["fn"] = [str(e) for e in bc.fn]; out["components"] = [int(c) for c in bc.components]
    out["read"] = {}
    for c in range(dim):
        try:
            out["read"][c] = str(_essential_value(bc, c, dim))
        except Exception as e:
            out["read"][c] = f"{type(e).__name__}: {e}"
    print(json.dumps(out))

probe("2d (0.0) c0", stokes2d, 0.0, 0, 2)
probe("2d (None,0.05)", stokes2d, (None, 0.05), None, 2)
probe("2d (0.0,0.05) c1", stokes2d, (0.0, 0.05), 1, 2)
probe("3d (0.0,0.05) c1", stokes3d, (0.0, 0.05), 1, 3)
probe("3d (0.01,0.05) c(0,1)", stokes3d, (0.01, 0.05), (0, 1), 3)
probe("3d (0.05) c1", stokes3d, 0.05, 1, 3)
probe("2d (0.01,0.05) c(1,0)", stokes2d, (0.01, 0.05), (1, 0), 2)
probe("2d (0.05,) c(0,0)", stokes2d, (0.05,), (0, 0), 2)
probe("3d (0.01,0.05) c(1,1,0)", stokes3d, (0.01, 0.05), (1, 1, 0), 3)
