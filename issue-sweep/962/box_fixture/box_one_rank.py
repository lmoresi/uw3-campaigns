"""One-rank reference for the 1 x 2 structured box Stokes solve (#962 CI guard)."""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(uw_force=0)
mesh = uw.meshing.StructuredQuadBox(elementRes=(1, 2), qdegree=3)
print("boundaries", [b.name for b in mesh.boundaries])
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
x, y = mesh.X
force = [sympy.Matrix([[0.0, sympy.cos(sympy.pi * x)]]),
         sympy.Matrix([[0.0, x]]),
         sympy.Matrix([[y, 0.0]]),
         sympy.Matrix([[sympy.sin(sympy.pi * y), 0.0]])][int(params.uw_force)]
stokes.bodyforce = force
# no flow through a wall, free to slide along it
for wall in ("Top", "Bottom"):
    stokes.add_essential_bc((None, 0.0), wall)
for wall in ("Left", "Right"):
    stokes.add_essential_bc((0.0, None), wall)
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = 1.0e-10
stokes.solve()
u = np.asarray(v.array)[:, 0, :]
c = np.asarray(v.coords)
free = np.ones(len(c), dtype=bool)
print("force", force, "reason", stokes.snes.getConvergedReason(), "its", stokes.snes.getIterationNumber(), "ksp", stokes.snes.getLinearSolveIterations(),
      "free nodes", int(free.sum()), "velocity nodes", len(c))
print("max speed %.16e" % np.linalg.norm(u, axis=1).max())
print(np.c_[c[free], u[free]])
