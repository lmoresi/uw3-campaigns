"""Which tolerance stops the warm Stokes solves of box_convection.py at zero Newton
iterations? Prints the SNES tolerances and the converged reason after each solve."""
import numpy as np, sympy, underworld3 as uw
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(2.0, 1.0), cellSize=0.25,
                                         refinement=1, qdegree=3, regular=False)
x, y = mesh.X
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
T.array[:, 0, 0] = np.asarray(uw.function.evaluate(1 - y + 0.05 * sympy.cos(sympy.pi * x) * sympy.sin(sympy.pi * y), T.coords)).ravel()
s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
s.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = sympy.exp(sympy.log(3e4) * (1 - T.sym[0]))
s.constitutive_model.Parameters.shear_viscosity_min = 1
s.constitutive_model.Parameters.yield_stress = 2e4 + 9e5 * (1 - y)
s.bodyforce = 9e5 * T.sym[0] * mesh.CoordinateSystem.unit_e_1
for b, c in (("Top", (None, 0.0)), ("Bottom", (None, 0.0)), ("Left", (0.0, None)), ("Right", (0.0, None))):
    s.add_essential_bc(c, b)
s.tolerance = 1e-3
for k in range(4):
    if k:
        T.array[:, 0, 0] = T.array[:, 0, 0] + 1e-3 * np.asarray(uw.function.evaluate(sympy.sin(sympy.pi * x), T.coords)).ravel()
    s.solve()
    r = s.solve_report
    uw.pprint(f"solve {k}: its {r.nl_its} reason {r.reason_str} history {['%.3g' % h for h in r.history]} "
              f"tolerances (rtol, atol, stol, maxit) {s.snes.getTolerances()}")
