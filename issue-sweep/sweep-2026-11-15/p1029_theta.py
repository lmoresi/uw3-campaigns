"""#1029: does theta change a Diffusion step with the default (symbolic) flux history?

T(x, 0) = sin(pi x) on a box, T = 0 on Left and Right, kappa = 1; one step of dt.
The decay of the mode over the step is 1/(1 + k dt) for backward Euler and
(1 - k dt/2)/(1 + k dt/2) for Crank-Nicolson, with k the discrete eigenvalue
(close to pi^2). The ratio is read at the box centre.
"""
import numpy as np
import sympy
import underworld3 as uw

dt = 0.05
k = np.pi ** 2
print(f"backward Euler {1 / (1 + k * dt):.5f}; Crank-Nicolson {(1 - k * dt / 2) / (1 + k * dt / 2):.5f} (k = pi^2)")
for theta in (0.0, 0.5, 1.0):
    mesh = uw.meshing.StructuredQuadBox(elementRes=(32, 4), minCoords=(0, 0), maxCoords=(1, 0.125))
    T = uw.discretisation.MeshVariable(f"T{int(theta * 10)}", mesh, 1, degree=2)
    s = uw.systems.Diffusion(mesh, u_Field=T, theta=theta)
    s.constitutive_model = uw.constitutive_models.DiffusionModel
    s.constitutive_model.Parameters.diffusivity = 1.0
    s.add_dirichlet_bc(0.0, "Left")
    s.add_dirichlet_bc(0.0, "Right")
    T.array[:, 0, 0] = np.sin(np.pi * np.asarray(T.coords)[:, 0])
    centre = np.array([[0.5, 0.0625]])
    before = float(np.asarray(uw.function.evaluate(T.sym[0], centre)).ravel()[0])
    s.solve(timestep=dt)
    after = float(np.asarray(uw.function.evaluate(T.sym[0], centre)).ravel()[0])
    print(f"theta {theta}: DFDt {type(s.DFDt).__name__}, ratio over one step {after / before:.5f}")
