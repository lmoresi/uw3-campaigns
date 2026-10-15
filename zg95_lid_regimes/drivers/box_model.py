"""The pieces the yielding-lid box drivers share: the mesh, the rheology, the walls,
and the per-step diagnostics.

    eta(T)  = deta ** (1 - T)                (1 at the basal temperature)
    tau_y   = tau0 + tau1 * (1 - y)          (depth measured from the surface)
    eta_eff = softmin(eta(T), tau_y / (2 edot_II))

Ra is on the basal viscosity, the layer has depth 1, and H is the internal heating.
"""
import numpy as np
import sympy
import underworld3 as uw


def box_mesh(width, cell, refinement):
    """The width x 1 simplex box with its refinement hierarchy (the multigrid levels)."""
    return uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(float(width), 1.0), cellSize=float(cell),
        refinement=int(refinement), qdegree=3, regular=False)


def set_viscoplastic(stokes, T_sym, deta, tau0, tau1, softness, weak=1):
    """Temperature-dependent viscosity capped by a depth-dependent yield stress.
    ``weak`` (1 by default) multiplies both the viscosity and the yield stress, for a
    weak zone. Returns eta(T), the viscosity the yield law caps."""
    y = stokes.mesh.X[1]
    eta_T = sympy.exp(sympy.log(deta) * (1 - T_sym))
    stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = eta_T * weak
    stokes.constitutive_model.Parameters.shear_viscosity_min = 1
    stokes.constitutive_model.Parameters.yield_stress = (tau0 + tau1 * (1 - y)) * weak
    stokes.constitutive_model.yield_softness = softness
    return eta_T


def free_slip_walls(stokes):
    """Zero normal velocity on the four walls, exact on flat walls."""
    stokes.add_essential_bc((None, 0.0), "Top")
    stokes.add_essential_bc((None, 0.0), "Bottom")
    stokes.add_essential_bc((0.0, None), "Left")
    stokes.add_essential_bc((0.0, None), "Right")


class BoxDiagnostics:
    """Per-step diagnostics of a box run, all global on every rank.

    The flow quantities (rms velocities, yielded fractions) are integrals over
    ``flow_mesh``, the mesh the Stokes solve lives on; the heat fluxes and the
    temperature profile are taken from ``T`` on its own mesh. The fluxes are the
    conductive fluxes out of the top and into the base per unit width: with no motion
    and no heating both are 1, and in a statistically steady state
    q_top = q_base + H, so H / q_top is the internally heated fraction.
    """

    def __init__(self, T, v, eta_eff, eta_T, width, heating):
        self.width = float(width)
        self.heating = float(heating)
        self.T = T
        flow_mesh = v.mesh
        y_flow = flow_mesh.X[1]
        y_T = T.mesh.X[1]
        yielded = sympy.Piecewise((1, eta_eff / eta_T < sympy.Rational(9, 10)), (0, True))
        in_lid = sympy.Piecewise((1, y_flow > sympy.Rational(2, 3)), (0, True))
        dTdy = T.sym[0].diff(y_T)
        self.integrals = {
            "v2": uw.maths.Integral(flow_mesh, v.sym.dot(v.sym)),
            "yielded": uw.maths.Integral(flow_mesh, yielded),
            "yielded_lid": uw.maths.Integral(flow_mesh, yielded * in_lid),
            "vs2": uw.maths.BdIntegral(flow_mesh, v.sym[0] ** 2, "Top"),
            "T": uw.maths.Integral(T.mesh, T.sym[0]),
            "q_top": uw.maths.BdIntegral(T.mesh, -dTdy, "Top"),
            "q_base": uw.maths.BdIntegral(T.mesh, -dTdy, "Bottom"),
        }
        self.profile_y = np.linspace(0.0, 1.0, 65)
        profile_x = np.linspace(0.0, self.width, int(32 * self.width) + 1)
        self.profile_xy = np.array([[px, py] for py in self.profile_y for px in profile_x])

    def temperature_profile(self):
        """Horizontally averaged T at 65 heights, and the lid thickness: the depth at
        which that profile first reaches 0.8 of its mid-depth value (the annulus
        campaign's definition). Collective: every rank evaluates the same points."""
        Tg = np.asarray(uw.function.global_evaluate(self.T.sym[0], self.profile_xy)).reshape(
            len(self.profile_y), -1)
        profile = Tg.mean(axis=1)
        T_mid = profile[len(self.profile_y) // 2]
        reached = np.flatnonzero(profile[::-1] >= 0.8 * T_mid)
        lid = float(1.0 - self.profile_y[::-1][reached[0]]) if reached.size else float("nan")
        return profile, float(T_mid), lid

    def record(self):
        val = {name: float(integral.evaluate()) for name, integral in self.integrals.items()}
        area = self.width
        vrms = np.sqrt(val["v2"] / area)
        vsurf = np.sqrt(val["vs2"] / self.width)
        profile, T_mid, lid = self.temperature_profile()
        record = {
            "vrms": vrms,
            "vsurf_rms": vsurf,
            "mobility": vsurf / max(vrms, 1e-30),
            "q_top": val["q_top"] / self.width,
            "q_base": val["q_base"] / self.width,
            "T_mean": val["T"] / area,
            "T_mid": T_mid,
            "lid_depth": lid,
            "yield_frac": val["yielded"] / area,
            "yield_frac_lid": val["yielded_lid"] / (area / 3),
        }
        record["internal_fraction"] = self.heating / max(record["q_top"], 1e-30)
        return record, profile
