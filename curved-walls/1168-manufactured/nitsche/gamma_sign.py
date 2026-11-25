"""Sign and form of mesh.Gamma on each wall of the elliptical annulus: integral of
Gamma.x over the wall (positive: outward from the origin) and of |Gamma|^2."""
import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sympy
import underworld3 as uw
import measure_mesh

mesh = measure_mesh.ellipse_mesh(0.1)
X, Y = mesh.X
_v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
G = mesh.Gamma
print("Gamma:", G)
for wall in ("Outer", "Inner"):
    gx = uw.maths.BdIntegral(mesh, G[0] * X + G[1] * Y, wall).evaluate()
    gg = uw.maths.BdIntegral(mesh, G[0] ** 2 + G[1] ** 2, wall).evaluate()
    L = uw.maths.BdIntegral(mesh, 1.0, wall).evaluate()
    bn = mesh.boundary_normal(wall)
    bx = uw.maths.BdIntegral(mesh, bn[0] * X + bn[1] * Y, wall).evaluate()
    print(f"{wall}: length {L:.6f}  int Gamma.x {gx:+.6f}  int |Gamma|^2 / L {gg / L:.12f}  int bnormal.x {bx:+.6f}")
