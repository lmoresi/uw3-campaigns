"""#1138: an essential condition on All_Boundaries of a mesh wrapped around a bare DMPlex."""
import numpy as np, sympy
from petsc4py import PETSc
import underworld3 as uw

coords = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.5, 0.5]])
cells = np.array([[0, 1, 4], [1, 3, 4], [3, 2, 4], [2, 0, 4]], dtype=PETSc.IntType)
dm = PETSc.DMPlex().createFromCellList(2, cells, coords, comm=PETSc.COMM_WORLD)
mesh = uw.discretisation.Mesh(dm, qdegree=3)
print([b.name for b in mesh.boundaries], mesh.dm.hasLabel("All_Boundaries"), flush=True)
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
x, _ = mesh.X
stokes.bodyforce = sympy.Matrix([[0.0, sympy.cos(sympy.pi * x)]])
try:
    stokes.add_essential_bc((0.0, 0.0), "All_Boundaries")
    stokes.petsc_use_pressure_nullspace = True
    stokes.solve()
    print("solved, reason", stokes.snes.getConvergedReason(), "max|v|", np.abs(v.array).max())
except Exception as e:
    print("raised", type(e).__name__, str(e)[:300])
