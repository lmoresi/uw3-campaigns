"""#410: a Dirichlet value written with mesh.t, solved with time= different from the model clock."""
import numpy as np
import underworld3 as uw

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.25)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1)
s = uw.systems.Poisson(mesh, u_Field=T)
s.constitutive_model = uw.constitutive_models.DiffusionModel
s.constitutive_model.Parameters.diffusivity = 1.0
s.f = 0.0
s.add_dirichlet_bc([mesh.t], "Bottom")
s.add_dirichlet_bc([0.0], "Top")
uw.get_default_model().tracker.time = 1.0
s.solve(time=3.0)
X = np.asarray(T.coords)
bottom = np.abs(X[:, 1]) < 1e-9
print(f"clock 1.0, solve(time=3.0): reason {s.snes.getConvergedReason()}, "
      f"bottom values min {np.asarray(T.array).ravel()[bottom].min():.6f} max {np.asarray(T.array).ravel()[bottom].max():.6f}")
