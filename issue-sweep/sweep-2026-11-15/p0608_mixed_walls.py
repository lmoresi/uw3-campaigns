"""#608: rotated free slip on Top beside component-Dirichlet side walls, against component Dirichlet on Top.

SolCx-type box: StructuredQuadBox 32 x 32, viscosity 1 for x < 0.5 and eta_B beyond,
body force (0, sin(pi y) cos(pi x)), pressure nullspace. Left/Right hold u_x = 0 and
Bottom u_y = 0 by component Dirichlet in both runs. Top is held either by
(None, 0) or by rotated free slip. Reports the relative velocity difference
between the two runs and the mean-removed pressure difference at the top corners.
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(eta_B=10.0)


def run(top):
    mesh = uw.meshing.StructuredQuadBox(elementRes=(32, 32), minCoords=(0, 0), maxCoords=(1, 1))
    v = uw.discretisation.MeshVariable(f"V{top}", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable(f"P{top}", mesh, 1, degree=1, continuous=True)
    st = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    x, y = mesh.X
    st.constitutive_model.Parameters.shear_viscosity_0 = sympy.Piecewise((1.0, x < 0.5), (float(params.eta_B), True))
    st.bodyforce = sympy.Matrix([[0.0, sympy.sin(sympy.pi * y) * sympy.cos(sympy.pi * x)]])
    st.add_dirichlet_bc((0.0, None), "Left")
    st.add_dirichlet_bc((0.0, None), "Right")
    st.add_dirichlet_bc((None, 0.0), "Bottom")
    if top == "dirichlet":
        st.add_dirichlet_bc((None, 0.0), "Top")
    else:
        st.add_rotated_freeslip_bc(0.0, "Top")
    st.petsc_use_pressure_nullspace = True
    st.tolerance = 1.0e-9
    st.solve()
    if top == "rotated":
        xs, sig = st.boundary_normal_traction("Top")
        xs = np.asarray(xs)[:, 0] if np.ndim(xs) > 1 else np.asarray(xs)
        sig = np.asarray(sig).ravel()
        inner = (xs > 2 / 32 + 1e-9) & (xs < 1 - 2 / 32 - 1e-9)
        print(f"rotated top sigma_nn: largest |value| over the wall {np.abs(sig).max():.4e}, "
              f"over the wall without two elements at each end {np.abs(sig[inner]).max():.4e}; "
              f"at the corners {sig[np.argmin(xs)]:+.4e} {sig[np.argmax(xs)]:+.4e}", flush=True)
    P = np.asarray(p.array).ravel()
    return np.asarray(v.array).reshape(-1, 2), P - P.mean(), np.asarray(p.coords), st.snes.getConvergedReason()


Vd, Pd, Xp, rd = run("dirichlet")
Vr, Pr, _, rr = run("rotated")
rel = np.linalg.norm(Vr - Vd) / np.linalg.norm(Vd)
dP = Pr - Pd
top = np.abs(Xp[:, 1] - 1.0) < 1e-9
below = ~top
corner = lambda xc: np.argmin(np.linalg.norm(Xp - np.array([xc, 1.0]), axis=1))
print(f"eta_B {params.eta_B}: reasons {rd} / {rr}")
print(f"relative velocity difference, rotated against Dirichlet top: {rel:.2e}")
print(f"pressure difference at (1, 1) {dP[corner(1.0)]:+.3e}, at (0, 1) {dP[corner(0.0)]:+.3e}; "
      f"rms below the top row {np.sqrt((dP[below] ** 2).mean()):.2e} (pressure rms {np.sqrt((Pd ** 2).mean()):.2e})")
