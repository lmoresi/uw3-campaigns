"""The pieces the yielding-lid annulus drivers share: the mesh, the rheology, the walls,
and the per-step diagnostics. The counterpart of ``box_model.py``.

Lengths are in units of the layer depth, so the annulus of the ZG95 campaign (inner
radius 0.55 of the outer) has r_o = 1 / 0.45 and r_i = 0.55 / 0.45, and every other
parameter (Ra, H, tau0, tau1, time) is the box's without conversion.

    eta(T)  = deta ** (1 - T)                (1 at the basal temperature; or Arrhenius, see eta_of_T)
    tau_y   = tau0 + tau1 * depth            (depth = r_o - r)
    eta_eff = softmin(eta(T), tau_y / (2 edot_II))
"""
from enum import Enum

import numpy as np
import sympy
import underworld3 as uw

RADIUS_RATIO = 0.55        # r_i / r_o of the ZG95 annulus


def annulus_radii(ratio=RADIUS_RATIO):
    """Outer and inner radius of an annulus of unit depth."""
    return 1.0 / (1.0 - ratio), ratio / (1.0 - ratio)


def annulus_mesh(cell, refinement, ratio=RADIUS_RATIO, outer=0.0, inner=0.0, filename=None):
    """The unit-depth annulus with its refinement hierarchy (the multigrid levels);
    refined boundary nodes are snapped to the circles. ``outer`` / ``inner`` > 0 grade the
    coarse mesh from that size at the outer wall to that at the inner one (gmsh interpolates
    between the walls); a graded mesh needs its own ``filename``, because the library's
    cached .msh name carries cellSize only."""
    r_o, r_i = annulus_radii(ratio)
    if not (outer or inner):
        return uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=float(cell),
                                  refinement=int(refinement), qdegree=3)
    outer, inner = float(outer or cell), float(inner or cell)
    return uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=max(outer, inner),
                              cellSizeOuter=outer, cellSizeInner=inner,
                              refinement=int(refinement), qdegree=3, filename=filename)


def focused_annulus_mesh(refinement, fine, theta, half_arc, depth, growth, outer, inner, filename,
                         ratio=RADIUS_RATIO):
    """The unit-depth annulus with a fine region and its refinement hierarchy. The coarse cells are ``fine``
    within the arc ``half_arc`` (measured at the surface) either side of the angle ``theta`` and above the depth
    ``depth``; outside that box they grow by ``growth`` per unit distance from it, up to the background, which
    runs linearly in depth from ``outer`` at the outer wall to ``inner`` at the inner one. uw.meshing.Annulus
    takes sizes at its walls only, so this is its construction (the same boundary names and tags, snapping of
    the refined wall nodes, null space and wall surfaces) with a gmsh size callback in place of the point sizes."""
    from underworld3.coordinates import CoordinateSystemType
    from underworld3.meshing._mesh_files import write_gmsh
    from underworld3.meshing.bounding_surface import register_radial_surfaces
    r_o, r_i = annulus_radii(ratio)

    class boundaries(Enum):
        Lower = 1
        Upper = 2
        Centre = 10

    def size(dim, tag, x, y, z, lc):
        d = r_o - np.hypot(x, y)
        h = outer + (inner - outer) * min(max(d / (r_o - r_i), 0.0), 1.0)
        along = r_o * abs((np.arctan2(y, x) - theta + np.pi) % (2.0 * np.pi) - np.pi)
        return min(h, fine + growth * np.hypot(max(0.0, along - half_arc), max(0.0, d - depth)))

    if uw.mpi.rank == 0:
        import gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("Annulus")
        centre = gmsh.model.geo.add_point(0.0, 0.0, 0.0)
        curves = {}
        for name, radius in (("Lower", r_i), ("Upper", r_o)):
            east = gmsh.model.geo.add_point(radius, 0.0, 0.0)
            west = gmsh.model.geo.add_point(-radius, 0.0, 0.0)
            curves[name] = [gmsh.model.geo.add_circle_arc(east, centre, west),
                            gmsh.model.geo.add_circle_arc(west, centre, east)]
        loops = [gmsh.model.geo.add_curve_loop(curves[name]) for name in ("Upper", "Lower")]
        surface = gmsh.model.geo.add_plane_surface(loops)
        gmsh.model.geo.synchronize()
        for name in ("Lower", "Upper"):
            gmsh.model.addPhysicalGroup(1, curves[name], boundaries[name].value, name=name)
        gmsh.model.addPhysicalGroup(2, [surface], 666666, "Elements")
        gmsh.model.mesh.setSizeCallback(size)
        for option in ("MeshSizeExtendFromBoundary", "MeshSizeFromPoints", "MeshSizeFromCurvature"):
            gmsh.option.setNumber(f"Mesh.{option}", 0)
        gmsh.model.mesh.generate(2)
        write_gmsh(filename)
        gmsh.finalize()

    def snap_walls(dm):
        coords = dm.getCoordinatesLocal()
        xy = coords.array.reshape(-1, 2)
        radius = np.hypot(xy[:, 0], xy[:, 1])
        for name, target in (("Upper", r_o), ("Lower", r_i)):
            nodes = uw.cython.petsc_discretisation.petsc_dm_find_labeled_points_local(dm, name)
            xy[nodes] *= target / radius[nodes].reshape(-1, 1)
        coords.array[...] = xy.reshape(-1)
        dm.setCoordinatesLocal(coords)

    def inside_walls(coords):
        radius = np.hypot(coords[:, 0], coords[:, 1])
        outside, inside = radius > r_o, radius < r_i
        coords[outside] *= 0.99 * r_o / radius[outside].reshape(-1, 1)
        coords[inside] *= 1.01 * r_i / radius[inside].reshape(-1, 1)
        return coords

    mesh = uw.discretisation.Mesh(
        filename, degree=1, qdegree=3, useMultipleTags=True, useRegions=True, markVertices=True,
        boundaries=boundaries, coordinate_system_type=CoordinateSystemType.CYLINDRICAL2D,
        refinement=int(refinement), refinement_callback=snap_walls, return_coords_to_bounds=inside_walls)
    x, y = mesh.X
    mesh._nullspace_rotations = [sympy.Matrix([-y, x])]
    register_radial_surfaces(mesh, centre=(0.0, 0.0), label_radius={"Upper": r_o, "Lower": r_i})
    return mesh


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


def lower_mantle_factor(depth, factor, top, ramp):
    """A viscosity factor ``factor`` below the depth ``top`` (layer depths; 670 km of a
    2900 km mantle is 0.231), with a tanh step of width ``ramp``; 1 above. ``factor`` 1 is
    no step."""
    if factor == 1:
        return 1
    return 1 + (factor - 1) * (1 + sympy.tanh((depth - top) / ramp)) / 2


def arrhenius_E(deta, T_i, T0):
    """The activation term E for which exp(E / (T + T0)) has the Frank-Kamenetskii law's slope,
    d ln(eta) / dT = -ln(deta), at the interior temperature ``T_i``."""
    return float(np.log(float(deta)) * (T_i + T0) ** 2)


def eta_of_T(T_sym, deta, arrhenius=None):
    """The viscosity's temperature law. Frank-Kamenetskii (the default): deta ** (1 - T), 1
    at the basal temperature. ``arrhenius`` = (E, T0, T_i, eta_max): exp(E / (T + T0)), scaled
    to equal the Frank-Kamenetskii viscosity deta ** (1 - T_i) at the interior temperature
    ``T_i`` (so Ra and the yield stresses keep their meaning) and capped at ``eta_max``; ``T0``
    is the surface temperature in units of the temperature drop, and T is taken no lower than
    0 (below -T0 an undershoot would turn the law over). With E from ``arrhenius_E`` the two
    laws also have the same slope at T_i: the cold side is then stiffer than Frank-Kamenetskii
    and the hot side less weak (the basal viscosity is above 1)."""
    if arrhenius is None:
        return sympy.exp(sympy.log(deta) * (1 - T_sym))
    E, T0, T_i, eta_max = (float(a) for a in arrhenius)
    rise = E * (1 / (sympy.Max(T_sym, 0) + T0) - 1 / (T_i + T0))
    return sympy.exp(sympy.Min(sympy.log(deta) * (1 - T_i) + rise, float(np.log(eta_max))))


def set_viscoplastic(stokes, T_sym, deta, tau0, tau1, softness, r_o, weak=1, yield_factor=1,
                     asthenosphere=None, lower_mantle=None, eta_ref=None, arrhenius=None):
    """Temperature-dependent viscosity capped by a yield stress that grows with depth
    below the outer wall. ``weak`` (1 by default) multiplies both the viscosity and
    the yield stress, for a weak zone; ``yield_factor`` multiplies the yield stress
    alone (strain weakening); ``asthenosphere`` = (factor, top, bottom, ramp) multiplies
    the viscosity by ``factor`` in a depth channel (see ``asthenosphere_factor``);
    ``lower_mantle`` = (factor, top, ramp) multiplies it below ``top`` (see
    ``lower_mantle_factor``); ``arrhenius``: the temperature law's Arrhenius form (see
    ``eta_of_T``; None is Frank-Kamenetskii). ``eta_ref`` (a units run): the viscosity at the basal
    temperature as an expression with units, which then also floors the viscosity;
    ``tau0`` and ``tau1`` are then a stress and a stress per length, and the solver
    non-dimensionalises all three. Returns eta(T) with those factors, the viscosity the
    yield law caps."""
    depth = r_o - radius_of(stokes.mesh)
    eta_T = eta_of_T(T_sym, deta, arrhenius)
    if asthenosphere is not None:
        eta_T = eta_T * asthenosphere_factor(depth, *asthenosphere)
    if lower_mantle is not None:
        eta_T = eta_T * lower_mantle_factor(depth, *lower_mantle)
    if eta_ref is not None:
        eta_T = eta_ref * eta_T
    stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = eta_T * weak
    stokes.constitutive_model.Parameters.shear_viscosity_min = 1 if eta_ref is None else eta_ref
    stokes.constitutive_model.Parameters.yield_stress = (tau0 + tau1 * depth) * weak * yield_factor
    # no floor: tau0 > 0 and weak, yield_factor are bounded below by positive factors, so the yield stress
    # stays positive; the library refuses an unstated floor on a yield stress that reads fields (#759)
    stokes.constitutive_model.Parameters.yield_stress_min = -sympy.oo
    stokes.constitutive_model.yield_softness = softness
    return eta_T


def free_slip_walls(stokes, normal="analytic"):
    """Rotated strong free-slip on both walls and the pressure gauge an enclosed domain
    needs. The rigid-rotation gauge is removed by the rotated solve. ``normal``:
    "analytic" constrains to the exact radial normal (unit_r); "geometric" leaves the
    library's default (normal=None), the measure-weighted facet normal summed across
    ranks. Kaiju, 2026-11-01: on the analytic path a wall node whose owning rank holds
    none of its labelled facets gets no constraint (np 24/32/40/52)."""
    if normal not in ("analytic", "geometric"):
        raise ValueError(f"wall normal must be analytic or geometric, not {normal!r}")
    unit_r = stokes.mesh.CoordinateSystem.unit_e_0 if normal == "analytic" else None
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
