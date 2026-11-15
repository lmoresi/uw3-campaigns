"""#742: what psi_star[0] holds after a solve, Stokes against NavierStokesSLCN (Maxwell shear box, ETD-1)."""
import numpy as np
import sympy
import underworld3 as uw

eta = mu = 1.0
speed, height, width, dt, steps = 0.5, 1.0, 2.0, 0.1, 5
rate = 2.0 * speed / height
exact = lambda k: eta * rate * (1.0 - np.exp(-k * dt * mu / eta))


def run(solver):
    mesh = uw.meshing.StructuredQuadBox(elementRes=(16, 8), minCoords=(-width / 2, -height / 2),
                                        maxCoords=(width / 2, height / 2))
    v = uw.discretisation.MeshVariable(f"U{solver}", mesh, mesh.dim, degree=2)
    p = uw.discretisation.MeshVariable(f"P{solver}", mesh, 1, degree=1)
    if solver == "stokes":
        st = uw.systems.Stokes(mesh, velocityField=v, pressureField=p, verbose=False)
    else:
        st = uw.systems.NavierStokesSLCN(mesh, v, p, rho=1.0e-6, order=1)
        st.bodyforce = sympy.Matrix([[0.0, 0.0]])
    st.stress_transport = "semi_lagrangian"
    st.constitutive_model = uw.constitutive_models.ViscoElasticPlasticFlowModel(
        st.Unknowns, order=1, integrator="etd")
    st.constitutive_model.Parameters.shear_viscosity_0 = eta
    st.constitutive_model.Parameters.shear_modulus = mu
    st.constitutive_model.Parameters.dt_elastic = dt
    st.add_dirichlet_bc((speed, 0.0), "Top")
    st.add_dirichlet_bc((-speed, 0.0), "Bottom")
    st.add_dirichlet_bc((sympy.oo, 0.0), "Left")
    st.add_dirichlet_bc((sympy.oo, 0.0), "Right")
    st.tolerance = 1.0e-6
    st.petsc_options["snes_type"] = "newtonls"
    st.petsc_options["ksp_type"] = "fgmres"
    for _ in range(steps):
        st.solve(timestep=dt, zero_init_guess=False)
    val = float(np.asarray(uw.function.evaluate(st.DFDt.psi_star[0].sym[0, 1], np.array([[0.0, 0.0]]))).ravel()[0])
    print(f"{solver:6s} after {steps} solves: psi_star[0]_xy = {val:.6f}; "
          f"exact({steps}) = {exact(steps):.6f}, exact({steps - 1}) = {exact(steps - 1):.6f}", flush=True)


run("stokes")
run("slcn")
