"""Convection-style box: free slip on four walls, written two ways. Serial.

usage: python conv_box.py short|full
"""
import sys, json, hashlib, warnings
import numpy as np, sympy
import underworld3 as uw

form = sys.argv[1]
mesh = uw.meshing.UnstructuredSimplexBox(
    minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.1, qdegree=3)
x, y = mesh.X
v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.bodyforce = sympy.Matrix([0, 1.0e4 * (1 - y + 0.1 * sympy.cos(sympy.pi * x) * sympy.sin(sympy.pi * y))])
out = dict(form=form)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        stokes.add_dirichlet_bc((0.0), "Left", (0))
        stokes.add_dirichlet_bc((0.0), "Right", (0))
        if form == "short":
            stokes.add_dirichlet_bc((0.0), "Top", (1))
            stokes.add_dirichlet_bc((0.0), "Bottom", (1))
        else:
            stokes.add_dirichlet_bc((None, 0.0), "Top")
            stokes.add_dirichlet_bc((None, 0.0), "Bottom")
        out["add"] = "accepted"
    except Exception as e:
        out["add"] = f"{type(e).__name__}: {e}"
    if out["add"] == "accepted":
        try:
            stokes.solve()
            out["solve"] = "ran"
        except Exception as e:
            out["solve"] = f"{type(e).__name__}: {str(e)[:300]}"
if out.get("solve") == "ran":
    X = np.asarray(v.coords); U = np.asarray(v.array)[:, 0, :]
    out["snes_reason"] = int(stokes.snes.getConvergedReason())
    out["snes_its"] = int(stokes.snes.getIterationNumber())
    out["ksp_its"] = int(stokes.snes.getLinearSolveIterations())
    for name, on in (("Top", np.abs(X[:, 1] - 1) < 1e-9), ("Bottom", np.abs(X[:, 1]) < 1e-9),
                     ("Left", np.abs(X[:, 0]) < 1e-9), ("Right", np.abs(X[:, 0] - 1) < 1e-9)):
        k = 1 if name in ("Top", "Bottom") else 0
        out[f"u_{'xy'[k]}_{name}"] = [float(f"{U[on, k].min():.6g}"), float(f"{U[on, k].max():.6g}")]
    out["u_hash"] = hashlib.sha256(np.ascontiguousarray(U).tobytes()).hexdigest()[:16]
    out["p_hash"] = hashlib.sha256(np.ascontiguousarray(np.asarray(p.array)).tobytes()).hexdigest()[:16]
print("RESULT " + json.dumps(out))
