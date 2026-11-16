"""Does Stokes.tau decode a log-conformation stress history on development? One solver, one step."""
import numpy as np
import sympy
import underworld3 as uw

mesh = uw.meshing.StructuredQuadBox(elementRes=(4, 2), minCoords=(-1.0, -0.5), maxCoords=(1.0, 0.5))
v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
st = uw.systems.Stokes(mesh, velocityField=v, pressureField=p, verbose=False)
st.constitutive_model = uw.constitutive_models.ViscoElasticPlasticFlowModel(
    st.Unknowns, order=1, integrator="etd", objective_rate="upper_convected",
    stress_history="log_conformation")
cm = st.constitutive_model
cm.Parameters.shear_viscosity_0 = 1.0
cm.Parameters.shear_modulus = 1.0
cm.Parameters.dt_elastic = 0.1
st.add_dirichlet_bc((0.5, 0.0), "Top")
st.add_dirichlet_bc((-0.5, 0.0), "Bottom")
st.add_dirichlet_bc((sympy.oo, 0.0), "Left")
st.add_dirichlet_bc((sympy.oo, 0.0), "Right")
st.solve(timestep=0.1)
try:
    t = st.tau
    print("tau decoded:", t.clean_name, np.asarray(t.array).shape)
except Exception as e:
    print("tau raised", type(e).__name__, str(e)[:200])
