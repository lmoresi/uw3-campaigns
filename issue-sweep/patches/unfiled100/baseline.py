"""Bit-identity probe for UNFILED 100: solution hashes and iteration counts."""
import hashlib, sys
import numpy as np
import sympy
import underworld3 as uw


def digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def standard(strategy=None):
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
    v = uw.discretisation.MeshVariable("v", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable("p", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    x, y = mesh.X
    s.bodyforce = sympy.Matrix([0, sympy.sin(sympy.pi * x) * sympy.cos(sympy.pi * y)])
    for side in ("Top", "Bottom", "Left", "Right"):
        s.add_dirichlet_bc((0.0, 0.0), side)
    if strategy:
        s.strategy = strategy
    s.solve()
    return s, digest(v.array, p.array)


def rotated():
    mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.1, qdegree=3)
    v = uw.discretisation.MeshVariable("vr", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable("pr", mesh, 1, degree=1, continuous=False)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    r = sympy.sqrt(mesh.X[0] ** 2 + mesh.X[1] ** 2)
    s.bodyforce = sympy.Matrix(mesh.X) / r * sympy.cos(3 * sympy.atan2(mesh.X[1], mesh.X[0]))
    s.add_rotated_freeslip_bc(0, "Upper")
    s.add_rotated_freeslip_bc(0, "Lower")
    s.solve()
    return s, digest(v.array, p.array)


for name, fn in (("standard", standard), ("standard+strategy", lambda: standard("fast")), ("rotated P2/dP1", rotated)):
    try:
        s, d = fn()
        print(f"{name}: snes its {s.snes.getIterationNumber()} ksp its {s.snes.getLinearSolveIterations()} "
              f"reason {s.snes.getConvergedReason()} digest {d}", flush=True)
    except Exception as e:
        print(f"{name}: FAILED {type(e).__name__}: {str(e)[:150]}", flush=True)
