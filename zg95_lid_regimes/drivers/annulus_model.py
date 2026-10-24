"""The pieces the yielding-lid annulus drivers share: the mesh, the rheology, the walls,
and the per-step diagnostics. The counterpart of ``box_model.py``.

Lengths are in units of the layer depth, so the annulus of the ZG95 campaign (inner
radius 0.55 of the outer) has r_o = 1 / 0.45 and r_i = 0.55 / 0.45, and every other
parameter (Ra, H, tau0, tau1, time) is the box's without conversion.

    eta(T)  = deta ** (1 - T)                (1 at the basal temperature)
    tau_y   = tau0 + tau1 * depth            (depth = r_o - r)
    eta_eff = softmin(eta(T), tau_y / (2 edot_II))
"""
import numpy as np
import sympy
import underworld3 as uw

RADIUS_RATIO = 0.55        # r_i / r_o of the ZG95 annulus


def annulus_radii(ratio=RADIUS_RATIO):
    """Outer and inner radius of an annulus of unit depth."""
    return 1.0 / (1.0 - ratio), ratio / (1.0 - ratio)


def annulus_mesh(cell, refinement, ratio=RADIUS_RATIO):
    """The unit-depth annulus with its refinement hierarchy (the multigrid levels);
    refined boundary nodes are snapped to the circles."""
    r_o, r_i = annulus_radii(ratio)
    return uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=float(cell),
                              refinement=int(refinement), qdegree=3)


def radius_of(mesh):
    x, y = mesh.X
    return sympy.sqrt(x ** 2 + y ** 2)


def asthenosphere_factor(depth, factor, top, bottom, ramp):
    """A viscosity factor below 1 in a channel between the depths ``top`` and
    ``bottom`` (layer depths), with tanh ramps of width ``ramp`` at both edges; 1
    elsewhere. ``factor`` 1 is no channel."""
    if factor >= 1:
        return 1
    window = (1 + sympy.tanh((depth - top) / ramp)) * (1 - sympy.tanh((depth - bottom) / ramp)) / 4
    return 1 - (1 - factor) * window


def ridge_factor(mesh, r_o, thetas, half_width, depth_cut, factor, ramp=0.02):
    """An imposed mid-ocean ridge: a factor ``factor`` (below 1) in a vertical seam
    through the lid at each angle in ``thetas``, Gaussian across the seam with the
    half-width ``half_width`` (arc length, layer depths) and ending at the depth
    ``depth_cut`` with a tanh ramp of width ``ramp``; 1 elsewhere. Multiplies the
    viscosity and the yield stress alike, so the plates can part there."""
    if factor >= 1 or not thetas:
        return 1
    x, y = mesh.X
    depth = r_o - radius_of(mesh)
    window = 0
    for theta_r in thetas:
        # the distance from the ridge, periodic, without acos (singular derivative at the ridge)
        cos_d = (x * np.cos(theta_r) + y * np.sin(theta_r)) / radius_of(mesh)
        chord2 = 2 * r_o ** 2 * (1 - cos_d)         # the squared chord, the arc squared near the ridge
        window = window + sympy.exp(-chord2 / half_width ** 2)
    window = sympy.Min(window, 1) * (1 - sympy.tanh((depth - depth_cut) / ramp)) / 2
    return 1 - (1 - factor) * window


def set_viscoplastic(stokes, T_sym, deta, tau0, tau1, softness, r_o, weak=1, yield_factor=1,
                     asthenosphere=None):
    """Temperature-dependent viscosity capped by a yield stress that grows with depth
    below the outer wall. ``weak`` (1 by default) multiplies both the viscosity and
    the yield stress, for a weak zone; ``yield_factor`` multiplies the yield stress
    alone (strain weakening); ``asthenosphere`` = (factor, top, bottom, ramp) multiplies
    the viscosity by ``factor`` in a depth channel (see ``asthenosphere_factor``).
    Returns eta(T) with the channel factor, the viscosity the yield law caps."""
    depth = r_o - radius_of(stokes.mesh)
    eta_T = sympy.exp(sympy.log(deta) * (1 - T_sym))
    if asthenosphere is not None:
        eta_T = eta_T * asthenosphere_factor(depth, *asthenosphere)
    stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = eta_T * weak
    stokes.constitutive_model.Parameters.shear_viscosity_min = 1
    stokes.constitutive_model.Parameters.yield_stress = (tau0 + tau1 * depth) * weak * yield_factor
    stokes.constitutive_model.yield_softness = softness
    return eta_T


def free_slip_walls(stokes):
    """Rotated strong free-slip on both walls, constrained to the exact radial normal,
    and the pressure gauge an enclosed domain needs. The rigid-rotation gauge is
    removed by the rotated solve."""
    unit_r = stokes.mesh.CoordinateSystem.unit_e_0
    stokes.add_rotated_freeslip_bc(0, "Upper", normal=unit_r)
    stokes.add_rotated_freeslip_bc(0, "Lower", normal=unit_r)
    stokes.petsc_use_pressure_nullspace = True


def clamp_radii(points, r_o, r_i, inset=1e-3):
    """Pull points onto [r_i + inset, r_o - inset]: the faceted walls lie inside the
    circles, so a point on a circle between two wall nodes is outside the mesh."""
    r = np.hypot(points[:, 0], points[:, 1])
    f = np.clip(r, r_i + inset, r_o - inset) / np.maximum(r, 1e-14)
    return points * f[:, None]


class AnnulusDiagnostics:
    """Per-step diagnostics of an annulus run, all global on every rank, defined as the
    box's: rms velocities over the area and along the outer wall, their ratio (the
    mobility), yielded fractions, the conductive heat fluxes, and the lid thickness
    from the averaged temperature profile.

    The flow quantities are integrals over ``v.mesh`` (the mesh the Stokes solve lives
    on); the fluxes and the profile are taken from ``T`` on its own mesh. q_top is the
    flux out through the outer wall per unit outer length, q_base the flux in through
    the inner wall per unit inner length: in a statistically steady state
    q_top L_o = q_base L_i + H A, and H A / (q_top L_o) is the internally heated
    fraction. Wall lengths and areas are integrals of 1 over the faceted mesh.
    """

    def __init__(self, T, v, eta_eff, eta_T, heating, ratio=RADIUS_RATIO):
        self.r_o, self.r_i = annulus_radii(ratio)
        self.heating = float(heating)
        self.T = T
        flow_mesh, T_mesh = v.mesh, T.mesh
        r_flow, r_T = radius_of(flow_mesh), radius_of(T_mesh)
        x, y = T_mesh.X
        yielded = sympy.Piecewise((1, eta_eff / eta_T < sympy.Rational(9, 10)), (0, True))
        in_lid = sympy.Piecewise((1, r_flow > self.r_o - sympy.Rational(1, 3)), (0, True))
        dTdr = (T.sym[0].diff(x) * x + T.sym[0].diff(y) * y) / r_T
        self.integrals = {
            "v2": uw.maths.Integral(flow_mesh, v.sym.dot(v.sym)),
            "yielded": uw.maths.Integral(flow_mesh, yielded),
            "yielded_lid": uw.maths.Integral(flow_mesh, yielded * in_lid),
            "vs2": uw.maths.BdIntegral(flow_mesh, v.sym.dot(v.sym), "Upper"),
            "T": uw.maths.Integral(T_mesh, T.sym[0]),
            "q_top": uw.maths.BdIntegral(T_mesh, -dTdr, "Upper"),
            "q_base": uw.maths.BdIntegral(T_mesh, -dTdr, "Lower"),
        }
        measure = {
            "area": uw.maths.Integral(flow_mesh, 1),
            "area_lid": uw.maths.Integral(flow_mesh, in_lid),
            "L_o": uw.maths.BdIntegral(flow_mesh, 1, "Upper"),
            "L_i": uw.maths.BdIntegral(flow_mesh, 1, "Lower"),
        }
        self.measure = {name: float(integral.evaluate()) for name, integral in measure.items()}
        self.profile_depth = np.linspace(0.0, 1.0, 65)
        n_theta = int(32 * 2 * np.pi * 0.5 * (self.r_o + self.r_i))
        theta = np.linspace(-np.pi, np.pi, n_theta, endpoint=False)
        radius = self.r_o - self.profile_depth
        self.profile_xy = clamp_radii(np.array([[rr * np.cos(th), rr * np.sin(th)]
                                                for rr in radius for th in theta]),
                                      self.r_o, self.r_i)

    def temperature_profile(self):
        """T averaged around the annulus at 65 depths, and the lid thickness: the depth
        at which that profile first reaches 0.8 of its mid-depth value (the box's and
        the annulus campaign's definition). Collective: every rank evaluates the same
        points."""
        Tg = np.asarray(uw.function.global_evaluate(self.T.sym[0], self.profile_xy)).reshape(
            len(self.profile_depth), -1)
        profile = Tg.mean(axis=1)
        T_mid = profile[len(self.profile_depth) // 2]
        reached = np.flatnonzero(profile >= 0.8 * T_mid)
        lid = float(self.profile_depth[reached[0]]) if reached.size else float("nan")
        return profile, float(T_mid), lid

    def record(self):
        val = {name: float(integral.evaluate()) for name, integral in self.integrals.items()}
        m = self.measure
        vrms = np.sqrt(val["v2"] / m["area"])
        vsurf = np.sqrt(val["vs2"] / m["L_o"])
        profile, T_mid, lid = self.temperature_profile()
        record = {
            "vrms": vrms,
            "vsurf_rms": vsurf,
            "mobility": vsurf / max(vrms, 1e-30),
            "q_top": val["q_top"] / m["L_o"],
            "q_base": val["q_base"] / m["L_i"],
            "T_mean": val["T"] / m["area"],
            "T_mid": T_mid,
            "lid_depth": lid,
            "yield_frac": val["yielded"] / m["area"],
            "yield_frac_lid": val["yielded_lid"] / m["area_lid"],
        }
        record["internal_fraction"] = self.heating * m["area"] / max(val["q_top"], 1e-30)
        return record, profile
