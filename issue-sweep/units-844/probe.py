"""Units PR 1, the Stokes constructor hunk (#844) at 4cd075be: which fields a
Stokes solver ends up with, and what it solves, for each way of passing them.
Run under the branch build and under a development build; compare the lines.
Serial."""
import hashlib, warnings
import numpy as np, sympy
import underworld3 as uw

warnings.simplefilter("ignore")


def digest(a):
    return hashlib.sha1(np.ascontiguousarray(np.asarray(a, dtype=float)).tobytes()).hexdigest()[:10]


def box():
    return uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.125, qdegree=3)


def run(label, make, viscosity=1, force=None):
    mesh = box()
    x, z = mesh.X
    try:
        st, passed_v, passed_p = make(mesh)
        u, p = st.Unknowns.u, st.Unknowns.p
        kept = f"u kept={u is passed_v if passed_v is not None else '-'} p kept={p is passed_p if passed_p is not None else '-'}"
        print(f"{label}\n   {kept}  u: {u.name} P{u.degree} units={u.units}   p: {p.name} P{p.degree} "
              f"continuous={p.continuous} units={p.units}", flush=True)
        st.constitutive_model = uw.constitutive_models.ViscousFlowModel
        st.constitutive_model.Parameters.shear_viscosity_0 = viscosity
        shape = sympy.cos(sympy.pi * x) * sympy.sin(sympy.pi * z)
        st.bodyforce = sympy.Matrix([[0, shape]]) if force is None else [0, force * shape]
        st.add_dirichlet_bc((0.0, 0.0), "Bottom")
        st.add_dirichlet_bc((0.0, None), "Left")
        st.add_dirichlet_bc((0.0, None), "Right")
        st.tolerance = 1.0e-8
        st.solve()
        print(f"   snes reason {st.snes.getConvergedReason()} its {st.snes.getIterationNumber()} "
              f"ksp its {st.snes.getLinearSolveIterations()}  stored u {digest(u.data)} p {digest(p.data)} "
              f"max|stored u| {np.abs(np.asarray(u.data)).max():.12e} max|stored p| {np.abs(np.asarray(p.data)).max():.12e}\n"
              f"   max|u.array| {np.abs(np.asarray(u.array)).max():.12e} max|p.array| {np.abs(np.asarray(p.array)).max():.12e}",
              flush=True)
    except Exception as err:
        print(f"   RAISED {type(err).__name__}: {str(err).splitlines()[0][:200]}", flush=True)


def V(mesh, degree=2, units=None):
    return uw.discretisation.MeshVariable("Uq", mesh, mesh.dim, degree=degree, units=units)


def P(mesh, degree=1, continuous=True, units=None):
    return uw.discretisation.MeshVariable("Pq", mesh, 1, degree=degree, continuous=continuous, units=units)


def default(mesh):
    return uw.systems.Stokes(mesh), None, None


def both(mesh):
    v, p = V(mesh), P(mesh)
    return uw.systems.Stokes(mesh, velocityField=v, pressureField=p), v, p


def only_v(v_degree=2, units=None, **kw):
    def make(mesh):
        v = V(mesh, v_degree, units)
        return uw.systems.Stokes(mesh, velocityField=v, **kw), v, None
    return make


def only_p(p_degree=1, continuous=True, units=None, **kw):
    def make(mesh):
        p = P(mesh, p_degree, continuous, units)
        return uw.systems.Stokes(mesh, pressureField=p, **kw), None, p
    return make


import sys
SECTION = sys.argv[1]

if SECTION == 'plain':
    print("== no reference quantities ==")
    run("Stokes(mesh)", default)
    run("Stokes(mesh, v P2, p P1)", both)
    run("Stokes(mesh, velocityField=v P2)", only_v())
    run("Stokes(mesh, pressureField=p P1)", only_p())
    run("Stokes(mesh, velocityField=v P1)", only_v(1))
    run("Stokes(mesh, velocityField=v P3)", only_v(3))
    run("Stokes(mesh, velocityField=v P3, degree=3)", only_v(3, degree=3))
    run("Stokes(mesh, pressureField=p P2)", only_p(2))
    run("Stokes(mesh, pressureField=p P0 discontinuous)", only_p(0, False))
    run("Stokes(mesh, velocityField=v P2, p_continuous=False)", only_v(p_continuous=False))


if SECTION == 'units':
    print("== reference quantities: length 30 km, viscosity 1e24 Pa s, velocity 2.5 mm/year ==")
    orchestration_model = uw.get_default_model()
    orchestration_model.set_reference_quantities(length=uw.quantity(30, "km"), viscosity=uw.quantity(1e24, "Pa*s"),
                                                 velocity=uw.quantity(2.5, "mm/year"))
    print("   fundamental scales:", sorted(orchestration_model.get_fundamental_scales()))
    eta = uw.quantity(1e24, "Pa*s")
    rho_g = uw.quantity(3300, "kg/m**3") * uw.quantity(10, "m/s**2")
    run("Stokes(mesh), plain viscosity 1 and plain force", default)
    run("Stokes(mesh), viscosity 1e24 Pa s, force 3300 kg/m3 x 10 m/s2", default, eta, rho_g)
    run("Stokes(mesh, v m/s, p Pa), viscosity 1e24 Pa s, force with units",
        lambda mesh: (lambda v, p: (uw.systems.Stokes(mesh, velocityField=v, pressureField=p), v, p))(V(mesh, units="m/s"), P(mesh, units="Pa")),
        eta, rho_g)
    run("Stokes(mesh, velocityField=v without units), viscosity and force with units", only_v(), eta, rho_g)
    run("Stokes(mesh, velocityField=v in cm/year), viscosity and force with units", only_v(units="cm/year"), eta, rho_g)
    run("Stokes(mesh, pressureField=p without units), viscosity and force with units", only_p(), eta, rho_g)
    uw.reset_default_model()


if SECTION == 'no_mass':
    print("== reference quantities without a mass scale: length and time only ==")
    orchestration_model = uw.get_default_model()
    try:
        orchestration_model.set_reference_quantities(length=uw.quantity(30, "km"), time=uw.quantity(1, "Myr"))
        print("   fundamental scales:", sorted(orchestration_model.get_fundamental_scales()))
        run("Stokes(mesh), plain viscosity and force", default)
    except Exception as err:
        print(f"   RAISED {type(err).__name__}: {str(err).splitlines()[0][:200]}")
    uw.reset_default_model()
