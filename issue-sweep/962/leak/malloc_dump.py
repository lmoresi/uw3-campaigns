"""Does the two-call Jacobian routine leave PETSc memory behind? (#962)

Run with PETSC_OPTIONS="-malloc_debug -malloc_dump": PETSc then lists, at
finalize, every block from PetscMalloc that was not freed, with the function
and line that asked for it. The routine asks for one array per call.
"""
import sympy
import underworld3 as uw

params = uw.Params(uw_evaluations=50)
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=0.5, refinement=1, qdegree=3)
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = sympy.Matrix([0, sympy.cos(sympy.pi * mesh.X[0])])
stokes.add_essential_bc((0.0, 0.0), "Left")
stokes.add_essential_bc((0.0, 0.0), "Right")
stokes.add_nitsche_bc(0.0, "Top")
stokes.add_nitsche_bc(0.0, "Bottom")
stokes.solve()
J, P, _ = stokes.snes.getJacobian()
for _ in range(int(params.uw_evaluations)):
    stokes.snes.computeJacobian(stokes.snes.getSolution(), J, P)
print("evaluations", int(params.uw_evaluations), "J is P", J.handle == P.handle)
