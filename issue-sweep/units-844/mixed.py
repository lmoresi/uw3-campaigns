"""Units PR 1 at 4cd075be: a kept field without units beside a created field
with units, read through evaluate. Serial."""
import warnings
import numpy as np, sympy
import underworld3 as uw

warnings.simplefilter("ignore")
uw.get_default_model().set_reference_quantities(length=uw.quantity(30, "km"), viscosity=uw.quantity(1e24, "Pa*s"),
                                                velocity=uw.quantity(2.5, "mm/year"))
PTS = np.array([[0.5, 0.5]])


def report(label, make):
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.25)
    st = make(mesh)
    u, p = st.Unknowns.u, st.Unknowns.p
    st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = uw.quantity(1e24, "Pa*s")
    u.data[:, 0] = np.asarray(u.coords_nd)[:, 1]
    u.data[:, 1] = 0.0
    p.data[:, 0] = 1.0
    print(f"{label}: u units={u.units} p units={p.units}")
    for name, expr in [("stress[0,1]", lambda: st.stress[0, 1]), ("u[0]", lambda: u.sym[0]), ("p", lambda: p.sym[0]),
                       ("stress[0,0] - p", lambda: st.stress[0, 0] - p.sym[0])]:
        try:
            print(f"   evaluate({name}) = {uw.function.evaluate(expr(), PTS)!r}"[:220])
        except Exception as err:
            print(f"   evaluate({name}) RAISED {type(err).__name__}: {str(err).splitlines()[0][:160]}")


report("Stokes(mesh)", lambda mesh: uw.systems.Stokes(mesh))
report("Stokes(mesh, velocityField=v without units)",
       lambda mesh: uw.systems.Stokes(mesh, velocityField=uw.discretisation.MeshVariable("Uq", mesh, 2, degree=2)))
report("Stokes(mesh, pressureField=p without units)",
       lambda mesh: uw.systems.Stokes(mesh, pressureField=uw.discretisation.MeshVariable("Pq", mesh, 1, degree=1)))
