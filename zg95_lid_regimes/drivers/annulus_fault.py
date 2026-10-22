"""A fault in the yielding-lid annulus: the periodic counterpart of ``box_fault.py``.
Does a weak dipping fault, moving with the overriding plate, take a stagnant annulus
lid onto the mobile branch as it did in the box?

The base annulus (never cut) carries the temperature and its advection-diffusion.
The faulted mesh is a copy of the base's finest level with the fault placed as the
structured ladder: the spine split and in frictionless contact from three rung
spacings below the surface down to ``uw_fault_depth``, the ladder's last rungs up to
the surface a weak isotropic bridge (viscosity and yield stress both times
``uw_eta_w``). Stokes is solved on the faulted mesh with rotated free-slip on both
walls and the lean split-ladder multigrid tail (the guide ``faults-in-convection``);
every coarse level takes the wall rotation. The velocity goes back to the base by
evaluation for the transport step.

The trench sits on the outer wall at angle ``uw_theta_trench``; the fault is the
straight line from it dipping at ``uw_dip`` degrees below the local horizontal,
down toward +theta, to depth ``uw_fault_depth`` below the outer wall. Lengths are in
layer depths (``annulus_model.py``).

With ``uw_migrate`` the trench moves with the overriding plate (the +theta side), at
the median tangential surface velocity over the arc ``uw_trench_off`` to
``uw_trench_off + uw_trench_span`` beyond it (``uw_trench_law = "window"``), or with the
fault itself (``"fault_normal"``): the straight fault, held at its dip, translates at
its mean normal velocity (the integral of v.n over the fault's Plus facets over their
length), which moves the trench along the surface by v_n dt / (t.n). The faulted mesh is rebuilt when the
trench has moved ``uw_rebuild_rungs`` rung spacings along the surface; the new
solve starts from the old solution rotated with the trench, with Picard steps first.

With ``uw_weakening`` the yield stress weakens with accumulated plastic strain:
tau_y -> tau_y * uw_yield_boost * W(gamma), W = 1 - (1 - uw_weak_min) min(gamma /
uw_strain_crit, 1). gamma lives on the base, is carried by the flow (SUPG, as T) and
grows at the plastic strain rate edot_II (1 - eta_eff / eta_viscous), projected on
the faulted mesh so the slip on the fault itself is not counted. With
``uw_heal_time`` > 0 it also decays at the rate gamma / uw_heal_time. ``uw_eta_reg``
adds the declared plastic rate strengthening, eta_pl = tau_y / (2 edot_II) + eta_reg,
which floors the yielded viscosity and its tangent.

    mpirun -np 4 python annulus_fault.py -uw_out ~/+Simulations/zg95/annulus_faults/runs/<name> \\
        -uw_source ~/+Simulations/zg95/annulus_regimes/runs/tau1x1.50_seed5 -uw_source_index 1700
"""
import gc
import json
import os
import sys
import time

import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import _fault_pair_nodes_on, fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annulus_model import (AnnulusDiagnostics, annulus_mesh, annulus_radii, clamp_radii,
                           free_slip_walls, set_viscoplastic)
from strain_band import boundary_layer_depth, detect_fault, polar_grid, rank_bands

params = uw.Params(
    uw_out="~/+Simulations/zg95/annulus_faults/runs/test",
    uw_source="~/+Simulations/zg95/annulus_regimes/runs/tau1x1.50_seed5",
    uw_source_index=1700,       # the annulus checkpoint the fault run starts from
    uw_restart=-1,              # this run's own checkpoint to continue from (-1: start from the source)
    uw_cell=0.5,
    uw_refinement=4,
    uw_ra=9.1125e5,
    uw_deta=3.0e4,
    uw_tau0=2.025e4,
    uw_tau1=1.366875e6,         # tau1 / Ra = 1.5: the annulus's stagnant counterpart of the box reference
    uw_heating=1.4175,
    uw_yield_softness=0.2,
    uw_theta_trench=0.0,        # angle of the trench on the outer wall (radians)
    uw_dip=45.0,                # fault dip below the local horizontal, down toward +theta (degrees)
    uw_fault_depth=0.35,        # depth of the fault's lower tip below the outer wall
    uw_spacing=0.004,           # ladder rung spacing (the band is two rungs wide)
    uw_eta_w=1.0e-3,            # weak-bridge factor on viscosity and yield stress
    uw_chain=2,                 # split ladder levels below the finest (0: welded coarse levels)
    uw_band_widen=1,            # 1: each chain level's band is two of its own rungs wide
    uw_migrate=1,               # 1: the trench moves with the overriding plate
    uw_trench_law="window",     # "window": overriding-plate surface velocity; "fault_normal": the fault's mean
                                # normal velocity; "strain": placed (trench and dip) on the plastic-strain band
    uw_detect_every=5,          # "strain": steps between detections
    uw_detect_window=40.0,      # "strain": half-width of the searched arc about the trench (degrees)
    uw_detect_gamma_sat=0.5,    # "strain": plastic strain counted as saturated
    uw_detect_T_lith=0.6,       # "strain": warmest material counted as lithosphere
    uw_detect_depth_max=0.45,   # "strain": deepest band point used in the fit
    uw_detect_max_dtheta=2.0,   # "strain": largest trench move per detection (degrees)
    uw_detect_max_ddip=5.0,     # "strain": largest dip change per detection (degrees)
    uw_dip_min=30.0,            # "strain": limits on the dip angle phi, measured below the local
    uw_dip_max=150.0,           # horizontal from +theta: phi > 90 dips toward -theta (a slab past vertical)
    uw_rebuild_dip=2.0,         # rebuild the faulted mesh when the dip has changed this much (degrees)
    uw_depth_law="fixed",       # "fixed": uw_fault_depth; "bl": the local thermal boundary layer (with "strain")
    uw_bl_T=0.7,                # "bl": the isotherm whose depth beside the trench sets the fault depth
    uw_fault_depth_min=0.06,    # "bl": limits on the fault depth
    uw_fault_depth_max=0.25,
    uw_detect_max_ddepth=0.02,  # "bl": largest fault-depth change per detection
    uw_global_every=10,         # "strain": steps between scans of the whole annulus (0: off)
    uw_relocate_ratio=1.5,      # "strain": move the fault to a band elsewhere holding this much more strain
    uw_trench_off=0.2,          # trench-velocity window: arc length beyond the trench
    uw_trench_span=0.4,         # trench-velocity window: arc length
    uw_rebuild_rungs=4,         # rebuild the faulted mesh when the trench has moved this many rungs
    uw_rebuild_newton_switch=1.0e-2,  # rebuilt mesh: Picard to this reduction of its own start, then Newton
    uw_tol=1.0e-3,
    uw_picard=0,                # minimum Picard steps on every solve
    uw_newton_switch=1.0e-2,    # first solve: Picard hands over to Newton at this residual reduction
    uw_warm_newton_switch=1.0,  # later solves: Newton at once
    uw_verbose=0,               # 1: print every nonlinear iteration
    uw_cold_start=1,            # 1: first solve from rest (a fault-free warm start stalls Picard)
    uw_dt_mult=3.0,
    uw_courant=1.0,
    uw_dt_max=5.0e-3,
    uw_steps=20,
    uw_ckpt_every=10,
    uw_weakening=0,             # 1: the yield stress weakens with accumulated plastic strain
    uw_strain_crit=0.5,         # plastic strain at which the weakening is complete
    uw_weak_min=0.5,            # yield-stress factor once fully weakened
    uw_yield_boost=1.0,         # factor on the intact yield stress (compensates the weakening)
    uw_heal_time=0.0,           # > 0: plastic strain decays on this time scale
    uw_heal_T=0.0,              # > 0: healing only above this temperature (a step of width 0.02)
    uw_eta_reg=0.0,             # plastic rate strengthening: eta_pl = tau_y / (2 edot_II) + eta_reg
)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
r_o, r_i = annulus_radii()
S = float(params.uw_spacing)
W = 2.0 * S

base = annulus_mesh(params.uw_cell, params.uw_refinement)
levels = base._coarse_level_meshes()[:-1] + [base]
T_b = uw.discretisation.MeshVariable("T", base, 1, degree=2)
V_b = uw.discretisation.MeshVariable("V", base, base.dim, degree=2)
log_eta_b = uw.discretisation.MeshVariable("log10_eta", base, 1, degree=1)
yield_ratio_b = uw.discretisation.MeshVariable("yield_ratio", base, 1, degree=1)

Ra = uw.expression(r"\mathrm{Ra}", params.uw_ra, "Rayleigh number on the basal viscosity")
deta = uw.expression(r"\Delta\eta", params.uw_deta, "viscosity contrast across the layer")
tau0 = uw.expression(r"\tau_0", params.uw_tau0, "yield stress at the surface")
tau1 = uw.expression(r"\tau_1", params.uw_tau1, "yield stress gradient with depth")
H = uw.expression(r"H", params.uw_heating, "internal heating rate")

adv = uw.systems.AdvDiffusion(base, T_b, V_b.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = 1
adv.f = H
adv.add_dirichlet_bc(0.0, "Upper")
adv.add_dirichlet_bc(1.0, "Lower")

# Accumulated plastic strain, carried by the flow on the base, and its source.
weakening = bool(params.uw_weakening)
gamma_b = uw.discretisation.MeshVariable("plastic_strain", base, 1, degree=2)
edot_p_b = uw.discretisation.MeshVariable("edot_plastic", base, 1, degree=1)
if weakening:
    strain_adv = uw.systems.AdvDiffusion(base, gamma_b, V_b.sym, order=1)
    strain_adv.constitutive_model = uw.constitutive_models.DiffusionModel
    strain_adv.constitutive_model.Parameters.diffusivity = 1.0e-6
    heal_rate = 0
    if params.uw_heal_time > 0:
        heal_rate = 1 / params.uw_heal_time
        if params.uw_heal_T > 0:
            # healing where the material has warmed into the mantle
            heal_rate = heal_rate * (1 + sympy.tanh((T_b.sym[0] - params.uw_heal_T) / 0.02)) / 2
    strain_adv.f = edot_p_b.sym[0] - gamma_b.sym[0] * heal_rate


def onto(points):
    """Mesh nodes as evaluation points: radii pulled inside the walls by a hair, so a
    wall node never falls outside the faceted mesh it is evaluated on."""
    return clamp_radii(np.asarray(points, dtype=float), r_o, r_i, inset=1.0e-10)


def rotation(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])


def fault_trace(theta_t, dip_deg, coarsening=1, fault_depth=None):
    """The spine (from just above the outer wall down past the tip) and the trace to
    cut (the spine more than three finest rung spacings inside the wall), sampled at
    ``coarsening`` times the rung spacing. The finest count is a multiple of
    2**uw_chain, so every coarser sampling is a subset of the finest one."""
    dip = np.deg2rad(dip_deg)
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down_dip = np.cos(dip) * t_hat - np.sin(dip) * r_hat
    top = r_hat * (r_o + 0.02)
    # the straight spine's length to the tip radius r_o - fault_depth (the outer wall
    # curves away beneath the chord, so this is longer than depth / sin(dip))
    b = top @ down_dip
    c = top @ top - (r_o - (params.uw_fault_depth if fault_depth is None else fault_depth)) ** 2
    length = -b - np.sqrt(b * b - c)
    block = 2 ** int(params.uw_chain)
    n = block * max(1, int(round(length / (block * S))))
    spine = np.array([top + down_dip * (length * i / n) for i in range(n + 1)])[::coarsening]
    return spine, spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - 3.0 * S]


def placed_ladder(host, theta_t, dip_deg, coarsening, fault_depth=None):
    """The fault's ladder band placed on ``host`` at ``coarsening`` times the rung
    spacing, split along its own rungs."""
    spine, trace = fault_trace(theta_t, dip_deg, coarsening, fault_depth)
    width = W * coarsening if params.uw_band_widen else W
    # The fill-ring self-crossing check gives a false positive when the ring runs along
    # a line of mesh nodes collinear to round-off (the annulus has one at theta = 0,
    # y ~ 1e-10). A different margin or clearance moves the ring off that line.
    # (measured at theta -4.26 deg, dip 75: the 4S level refused margins 1-2 and
    # clearances 0.6-0.7 at the standard width and placed at 1.25 x the width)
    attempts = [(1, 0.7, 1.0), (1, 0.7, 1.25), (2, 0.7, 1.0), (1, 0.7, 1.5)]
    for n, (rings, clearance, widen) in enumerate(attempts):
        try:
            mesh, info = place_fault_ribbon_2d(host, [("Trench", trace)], width * widen,
                                               spines=[("Trench", spine)], margin_rings=rings,
                                               clearance=clearance, split=True, mesher="ladder")
            if n:
                uw.pprint(f"  placed with margin_rings {rings}, clearance {clearance}, width x{widen}")
            return mesh, info, spine, trace
        except RuntimeError as err:
            if "crosses itself" not in str(err) or n == len(attempts) - 1:
                raise


class FaultedMesh:
    """The trench placed into a copy of the base's finest level, with its Stokes
    solver, the bridge zone and the P1 fields the renders read."""

    def __init__(self, theta_t, tag, dip=None, fault_depth=None):
        wall = time.perf_counter()
        self.theta_t = theta_t
        self.dip = float(params.uw_dip if dip is None else dip)
        self.fault_depth = float(params.uw_fault_depth if fault_depth is None else fault_depth)
        # C on the ladder: the ladder at 2**k times the rung spacing on the base level
        # k steps below the finest, each split along its own rungs (the guide
        # faults-in-convection; welded coarse levels cap the velocity solve).
        chain = int(params.uw_chain)
        mids = []
        for k in range(chain, 0, -1):
            host = levels[len(levels) - k]
            try:
                mids.append(placed_ladder(host, theta_t, self.dip, 2 ** k, self.fault_depth)[0])
            except RuntimeError as err:
                # a chain level the surgery refuses stays welded (the base level itself)
                uw.pprint(f"  chain level {2 ** k}S refused ({str(err)[:80]}): welded")
                mids.append(host)
        self.levels = levels[:len(levels) - chain] + mids if chain else levels
        self.mesh, info, self.spine, self.trace = placed_ladder(base, theta_t, self.dip, 1, self.fault_depth)
        mesh = self.mesh
        band = np.asarray(info["band"], dtype=bool)
        self.T = uw.discretisation.MeshVariable(f"T_{tag}", mesh, 1, degree=2)
        self.v = uw.discretisation.MeshVariable(f"V_{tag}", mesh, mesh.dim, degree=2)
        self.p = uw.discretisation.MeshVariable(f"P_{tag}", mesh, 1, degree=1, continuous=True)
        self.zone = uw.discretisation.MeshVariable(f"zone_{tag}", mesh, 1, degree=0, continuous=False)
        self.log_eta = uw.discretisation.MeshVariable(f"log10_eta_{tag}", mesh, 1, degree=1)
        self.yield_ratio = uw.discretisation.MeshVariable(f"yield_ratio_{tag}", mesh, 1, degree=1)
        self.gamma = uw.discretisation.MeshVariable(f"plastic_strain_{tag}", mesh, 1, degree=2)
        self.edot_p = uw.discretisation.MeshVariable(f"edot_plastic_{tag}", mesh, 1, degree=1)
        # The bridge: the band cells outside the split's upper tip (the cap and the
        # last rungs), weak in viscosity and yield stress so the fault reaches the
        # surface. Pair nodes cannot sit on the rotated wall rows.
        centroids = np.asarray(self.zone.coords)
        r_tip = np.hypot(*self.trace[0])
        bridge = band & (np.hypot(centroids[:, 0], centroids[:, 1]) > r_tip - 0.5 * W)
        self.zone.array[:, 0, 0] = bridge.astype(float)

        s = uw.systems.Stokes(mesh, velocityField=self.v, pressureField=self.p)
        weak = 1 - (1 - params.uw_eta_w) * self.zone.sym[0]
        yield_factor = params.uw_yield_boost
        if weakening:
            yield_factor = yield_factor * (1 - (1 - params.uw_weak_min) * sympy.Min(
                self.gamma.sym[0] / params.uw_strain_crit, 1))
        self.eta_T = set_viscoplastic(s, self.T.sym[0], deta, tau0, tau1, params.uw_yield_softness,
                                      r_o, weak, yield_factor)
        if params.uw_eta_reg > 0:
            # a declared regularisation: floors the plastic viscosity and its tangent
            s.constitutive_model.Parameters.plastic_rate_strengthening = params.uw_eta_reg
        s.bodyforce = Ra * self.T.sym[0] * mesh.CoordinateSystem.unit_e_0
        free_slip_walls(s)
        s.add_fault_bc(0, boundary="Trench")
        s.tolerance = params.uw_tol
        s.consistent_jacobian = "continuation"
        s.newton_switch_rtol = params.uw_newton_switch
        set_custom_fmg(s, self.levels, field_id=0)
        self.stokes = s
        # The fault's unit normal (a straight chord has one) and the surface tangent at
        # the trench: a normal displacement dn of the fault moves the trench by dn / (t.n)
        dip = np.deg2rad(self.dip)
        t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
        r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
        down_dip = np.cos(dip) * t_hat - np.sin(dip) * r_hat
        n_fault = np.array([-down_dip[1], down_dip[0]])
        self.t_dot_n = float(t_hat @ n_fault)
        n_sym = sympy.Matrix([[float(n_fault[0]), float(n_fault[1])]])
        self.vn_integral = uw.maths.BdIntegral(mesh, self.v.sym.dot(n_sym), "TrenchPlus")
        self.fault_length = float(uw.maths.BdIntegral(mesh, 1, "TrenchPlus").evaluate())
        self.has_guess = False

        eta_eff = s.constitutive_model.viscosity
        self.eta_projection = uw.systems.Projection(mesh, self.log_eta)
        self.eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
        self.ratio_projection = uw.systems.Projection(mesh, self.yield_ratio)
        self.ratio_projection.uw_function = eta_eff / self.eta_T
        # the plastic strain rate: edot_II where the yield law caps the viscosity fully,
        # zero on the viscous branch (eta_eff / (eta_T weak) = 1)
        cm = s.constitutive_model
        self.edot_projection = uw.systems.Projection(mesh, self.edot_p)
        self.edot_projection.uw_function = cm._strainrate_inv_II * sympy.Max(
            0, 1 - eta_eff / (self.eta_T * weak))
        self.diagnostics = AnnulusDiagnostics(T_b, self.v, eta_eff, self.eta_T, params.uw_heating)
        self.t_build = time.perf_counter() - wall
        level_cells = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                       for m in self.levels + [mesh]]
        uw.pprint(f"faulted mesh {tag}: trench at theta {np.degrees(theta_t):.3f} deg, dip {self.dip:.1f}, "
                  f"depth {self.fault_depth:.3f}, "
                  f"{len(self.trace)} trace points, fault length {self.fault_length:.4f}, "
                  f"levels (cells) {level_cells}, "
                  f"built in {self.t_build:.1f} s")

    def split_nudges(self, var):
        """The evaluation offsets that put each split copy of ``var``'s DOFs on its own
        side of the fault: zero away from it, 0.1 rung spacings along -n on the Plus
        copies and +n on the Minus copies (n points from Plus to Minus). The two
        copies of a pair share coordinates, so an evaluation there gives both the
        value of whichever side the point locator lands in (measured: the wrong side
        for 37-63 % of the velocity pairs on the annulus)."""
        nudge = np.zeros((var.array.shape[0], 2))
        pairs = _fault_pair_nodes_on(self.mesh, self.mesh.dm, self.mesh.dm.getLocalSection(),
                                     "Trench", field=self.v.field_id)
        _, sub = self.mesh.dm.createSubDM(var.field_id)
        sec = sub.getLocalSection()
        width = var.num_components
        for q_plus, q_minus, n_hat in pairs:
            for q, sign in ((q_plus, -1.0), (q_minus, 1.0)):
                if sec.getDof(q) > 0:
                    nudge[sec.getOffset(q) // width] = sign * 0.1 * S * np.asarray(n_hat)
        return nudge

    def warm_start(self, V, P=None, dtheta=0.0):
        """Initial guess from velocity (and pressure, when given) on another mesh.
        ``dtheta`` is how far the trench has turned since that mesh: each node takes
        the old field at its position turned back by it, the velocity turned forward
        again, so the old slip lands on the new fault. On a faulted source the split
        copies are evaluated a hair inside their own side (``split_nudges``), so each
        side takes its own side's slip."""
        back = rotation(-dtheta)
        split_source = getattr(V.mesh, "_fault_point_pairs", None)

        def at(var, source, coords):
            points = np.asarray(coords, dtype=float)
            if split_source:
                points = points + self.split_nudges(var)
            query = onto(points @ back.T)
            return np.asarray(uw.function.global_evaluate(source.sym, query))

        v_old = at(self.v, V, self.v.coords).reshape(-1, 2)
        self.v.array[:, 0, :] = v_old @ rotation(dtheta).T
        if P is not None:
            self.p.array[:, 0, 0] = at(self.p, P, self.p.coords).ravel()
        self.has_guess = True

    def _stokes_solve(self, from_rest):
        self.stokes.solve(zero_init_guess=from_rest, picard=params.uw_picard,
                          verbose=bool(params.uw_verbose))
        return self.stokes._rotated_freeslip_info

    def solve(self):
        self.T.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(T_b.sym[0], onto(self.T.coords))).ravel()
        if weakening:
            self.gamma.array[:, 0, 0] = np.asarray(
                uw.function.global_evaluate(gamma_b.sym[0], onto(self.gamma.coords))).ravel()
        info = self._stokes_solve(from_rest=not self.has_guess)
        if not info.get("converged") and self.has_guess:
            uw.pprint("  the warm start did not converge: solving from rest")
            self.stokes.newton_switch_rtol = params.uw_newton_switch
            info = self._stokes_solve(from_rest=True)
        # The loop's Picard-to-Newton switch is measured from each solve's own start;
        # after the first solve the warm starts are inside Newton's basin.
        self.stokes.newton_switch_rtol = params.uw_warm_newton_switch
        self.has_guess = True
        _, slip, leak = fault_slip(self.stokes, "Trench", info)
        return {
            "newton": info.get("nonlinear_iterations"),
            "vel_its": info.get("vel_its_last"),
            "pres_its": info.get("pres_its_last"),
            "converged": bool(info.get("converged")),
            "slip_max": float(uw.utilities.gather_data(np.abs(slip).max() if len(slip) else 0.0, bcast=True).max()),
            "leak_max": float(uw.utilities.gather_data(np.abs(leak).max() if len(leak) else 0.0, bcast=True).max()),
        }

    def overriding_plate_velocity(self):
        """Median tangential surface velocity of the overriding plate, over the arc
        beyond the trench (collective: every rank evaluates the same points). The
        points sit a hair inside the outer wall, which is faceted between its nodes."""
        arc = (params.uw_trench_off + np.linspace(0.0, params.uw_trench_span, 41)) / r_o
        theta = self.theta_t + arc
        points = clamp_radii(np.column_stack([r_o * np.cos(theta), r_o * np.sin(theta)]), r_o, r_i)
        v = np.asarray(uw.function.global_evaluate(self.v.sym, points)).reshape(-1, 2)
        v_theta = -v[:, 0] * np.sin(theta) + v[:, 1] * np.cos(theta)
        return float(np.median(v_theta))

    def fault_trench_velocity(self):
        """The trench speed (along the surface, +theta positive) that carries the
        straight fault, at its dip, with its mean normal velocity (collective)."""
        v_n = float(self.vn_integral.evaluate()) / self.fault_length
        return v_n / self.t_dot_n, v_n

    def to_base(self):
        """Velocity onto the base's nodes (collective)."""
        V_b.array[:, 0, :] = np.asarray(
            uw.function.global_evaluate(self.v.sym, onto(V_b.coords))).reshape(-1, 2)
        if weakening:
            self.edot_projection.solve()
            edot = np.asarray(uw.function.global_evaluate(
                self.edot_p.sym[0], onto(edot_p_b.coords))).ravel()
            edot_p_b.array[:, 0, 0] = np.maximum(edot, 0.0)

    def render_fields_to_base(self):
        self.eta_projection.solve()
        self.ratio_projection.solve()
        log_eta_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.log_eta.sym[0], onto(log_eta_b.coords))).ravel()
        yield_ratio_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.yield_ratio.sym[0], onto(yield_ratio_b.coords))).ravel()


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def checkpoint(step, t, records, faulted):
    faulted.render_fields_to_base()
    base.write_timestep("annulus", index=step, outputPath=out,
                        meshVars=[V_b, T_b, log_eta_b, yield_ratio_b]
                        + ([gamma_b, edot_p_b] if weakening else []))
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, f"state_{step:05d}.json"), "w") as f:
                json.dump({"step": step, "t": t, "params": params.to_dict(),
                           "theta_trench": theta_t, "dip": dip_t, "fault_depth": depth_t,
                           "trace": faulted.trace.tolist()},
                          f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- initial state
records = []
P_source = None
if params.uw_restart < 0:
    source = os.path.expanduser(params.uw_source)
    for var in (T_b, V_b):
        var.read_timestep("annulus", var.name, params.uw_source_index, outputPath=source)
    with open(os.path.join(source, f"state_{params.uw_source_index:05d}.json")) as f:
        state = json.load(f)
    # the source's history up to the restart, so the record runs on unbroken
    if os.path.exists(os.path.join(source, "records.json")):
        with open(os.path.join(source, "records.json")) as f:
            records = [r for r in json.load(f) if r["step"] <= params.uw_source_index]
    if not params.uw_cold_start:
        P_source = uw.discretisation.MeshVariable("P", base, 1, degree=1, continuous=True)
        P_source.read_timestep("annulus", "P", params.uw_source_index, outputPath=source)
    theta_t = float(params.uw_theta_trench)
    dip_t = float(params.uw_dip)
    depth_t = float(params.uw_fault_depth)
else:
    for var in (T_b, V_b) + ((gamma_b,) if weakening else ()):
        var.read_timestep("annulus", var.name, params.uw_restart, outputPath=out)
    with open(os.path.join(out, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    with open(os.path.join(out, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]
    theta_t = float(state["theta_trench"])
    dip_t = float(state.get("dip", params.uw_dip))
    depth_t = float(state.get("fault_depth", params.uw_fault_depth))
t, step = float(state["t"]), int(state["step"]) + 1

n_built = 1
faulted = FaultedMesh(theta_t, "f0", dip_t, depth_t)
if not params.uw_cold_start:
    faulted.warm_start(V_b, P_source)

uw.pprint(f"annulus r_o {r_o:.4f} r_i {r_i:.4f}, Ra {params.uw_ra:.4g}, deta {params.uw_deta:.3g}, "
          f"tau {params.uw_tau0:.4g} + {params.uw_tau1:.4g} z (tau1/Ra {params.uw_tau1 / params.uw_ra:.3g}), "
          f"H {params.uw_heating:.4g}; fault at theta {np.degrees(theta_t):.2f} deg, dip {dip_t:.1f} "
          f"to depth {depth_t:.3f}; from t {t:.4f}; output {out}")

def detect_band(theta_c):
    """The plastic-strain band near the trench (collective: every rank samples the same
    points, so every rank takes the same decision)."""
    th, dep, xy = polar_grid(r_o, n_theta=321, depth_max=0.5, n_depth=64, centre=theta_c,
                             half_width=np.deg2rad(params.uw_detect_window))
    pts = onto(xy)
    shape = (len(dep), len(th))
    T = np.asarray(uw.function.global_evaluate(T_b.sym[0], pts)).reshape(shape)
    v = np.asarray(uw.function.global_evaluate(V_b.sym, pts)).reshape(-1, 2)
    v_r = ((v[:, 0] * pts[:, 0] + v[:, 1] * pts[:, 1]) / np.hypot(pts[:, 0], pts[:, 1])).reshape(shape)
    gamma = np.asarray(uw.function.global_evaluate(gamma_b.sym[0], pts)).reshape(shape)
    edot = np.asarray(uw.function.global_evaluate(edot_p_b.sym[0], pts)).reshape(shape)
    found = detect_fault(th, dep, gamma, edot, T, v_r, r_o, params.uw_detect_gamma_sat,
                         params.uw_detect_T_lith, params.uw_detect_depth_max, periodic=False)
    if found is not None:
        found["bl_depth"] = boundary_layer_depth(th, dep, T, found["theta_t"], params.uw_bl_T)
    return found


def global_bands():
    """Every saturated, cold, descending band around the annulus, strongest first
    (collective)."""
    th, dep, xy = polar_grid(r_o, n_theta=720, depth_max=0.5, n_depth=48)
    pts = onto(xy)
    shape = (len(dep), len(th))
    T = np.asarray(uw.function.global_evaluate(T_b.sym[0], pts)).reshape(shape)
    v = np.asarray(uw.function.global_evaluate(V_b.sym, pts)).reshape(-1, 2)
    v_r = ((v[:, 0] * pts[:, 0] + v[:, 1] * pts[:, 1]) / np.hypot(pts[:, 0], pts[:, 1])).reshape(shape)
    gamma = np.asarray(uw.function.global_evaluate(gamma_b.sym[0], pts)).reshape(shape)
    edot = np.asarray(uw.function.global_evaluate(edot_p_b.sym[0], pts)).reshape(shape)
    return rank_bands(th, dep, gamma, edot, T, v_r, params.uw_detect_gamma_sat, params.uw_detect_T_lith,
                      params.uw_detect_depth_max, min_points=10)


# ----------------------------------------------------------------------------- time loop
for k in range(params.uw_steps):
    wall = time.perf_counter()
    if (abs(theta_t - faulted.theta_t) * r_o > params.uw_rebuild_rungs * S
            or abs(dip_t - faulted.dip) > params.uw_rebuild_dip
            or abs(depth_t - faulted.fault_depth) > 2 * S):
        previous = faulted
        try:
            faulted = FaultedMesh(theta_t, f"f{n_built}", dip_t, depth_t)
        except RuntimeError as err:
            # a placement the surgery refuses is refused on every rank: keep the mesh
            # and the geometry that placed
            uw.pprint(f"  placement at theta {np.degrees(theta_t):.2f} deg, dip {dip_t:.1f} failed "
                      f"({str(err)[:120]}); keeping the previous fault")
            theta_t, dip_t, depth_t = previous.theta_t, previous.dip, previous.fault_depth
            faulted = previous
        n_built += 1
        # Newton from the turned solution fails even with each split copy taking its
        # own side's slip (measured: 4 increments, then the line search stopped at 0.7
        # of the reference residual; the box's unsided transfer stalled the same way);
        # Picard first converges, in 12-19 increments.
        if faulted is not previous:
            # a trench that moved with the flow carries its solution turned with it; a fault
            # relocated to another band takes the old field where it stands
            dtheta = faulted.theta_t - previous.theta_t
            if abs((dtheta + np.pi) % (2 * np.pi) - np.pi) > np.deg2rad(params.uw_detect_window):
                dtheta = 0.0
            faulted.warm_start(previous.v, previous.p, dtheta=dtheta)
            faulted.stokes.newton_switch_rtol = params.uw_rebuild_newton_switch
        del previous
        gc.collect()
    rec = faulted.solve()
    t_stokes = time.perf_counter() - wall
    faulted.to_base()
    dt_accuracy = params.uw_dt_mult * float(adv.estimate_dt())
    adv.estimate_dt(basis="resolution", direction_aware=True)   # sets adv.dt_adv
    dt_crossing = adv.dt_adv
    dt = min(dt_accuracy, params.uw_courant * dt_crossing, params.uw_dt_max)
    adv.solve(timestep=dt)
    if weakening:
        strain_adv.solve(timestep=dt)
        gamma_b.array[:, 0, 0] = np.maximum(gamma_b.array[:, 0, 0], 0.0)   # SUPG undershoot
    t += dt
    v_plate = faulted.overriding_plate_velocity()
    v_fault, v_normal = faulted.fault_trench_velocity()
    v_trench = v_fault if params.uw_trench_law == "fault_normal" else v_plate
    band = None
    relocated = None
    if params.uw_trench_law == "strain" and params.uw_global_every and k % params.uw_global_every == 0:
        # the lid may fail somewhere else: a stronger band away from the fault takes it
        bands = global_bands()
        if bands:
            near = [b for b in bands if abs((b[0] - theta_t + np.pi) % (2 * np.pi) - np.pi)
                    <= np.deg2rad(params.uw_detect_window)]
            local = near[0][1] if near else 0.0
            best = bands[0]
            far = abs((best[0] - theta_t + np.pi) % (2 * np.pi) - np.pi) > np.deg2rad(params.uw_detect_window)
            if far and best[1] > params.uw_relocate_ratio * local:
                new = detect_band(best[0])
                if new is not None:
                    relocated = (theta_t, new["theta_t"])
                    theta_t = new["theta_t"]
                    phi = new["dip"] if new["direction"] > 0 else 180.0 - new["dip"]
                    dip_t = float(np.clip(phi, params.uw_dip_min, params.uw_dip_max))
                    if params.uw_depth_law == "bl" and new.get("bl_depth") is not None:
                        depth_t = float(np.clip(new["bl_depth"], params.uw_fault_depth_min,
                                                params.uw_fault_depth_max))
                    uw.pprint(f"  relocating the fault: {np.degrees(relocated[0]):.1f} -> "
                              f"{np.degrees(theta_t):.1f} deg (band strain {best[1]:.0f} against "
                              f"{local:.0f} at the fault), dip {dip_t:.1f}, depth {depth_t:.3f}")
    if params.uw_trench_law == "strain" and relocated is None:
        # the fault follows the plastic-strain band of the downwelling: trench and dip
        # relax toward the fitted band, by bounded steps (the band is noisy step to step)
        if k % params.uw_detect_every == 0:
            band = detect_band(theta_t)
            if band is not None:
                dip_band = band["dip"] if band["direction"] > 0 else 180.0 - band["dip"]
                dip_band = float(np.clip(dip_band, params.uw_dip_min, params.uw_dip_max))
                dth = (band["theta_t"] - theta_t + np.pi) % (2 * np.pi) - np.pi
                cap = np.deg2rad(params.uw_detect_max_dtheta)
                theta_t += float(np.clip(dth, -cap, cap))
                dip_t += float(np.clip(dip_band - dip_t, -params.uw_detect_max_ddip,
                                       params.uw_detect_max_ddip))
                if params.uw_depth_law == "bl" and band.get("bl_depth") is not None:
                    target = float(np.clip(band["bl_depth"], params.uw_fault_depth_min,
                                           params.uw_fault_depth_max))
                    depth_t += float(np.clip(target - depth_t, -params.uw_detect_max_ddepth,
                                             params.uw_detect_max_ddepth))
    elif params.uw_migrate and params.uw_trench_law != "strain":
        theta_t += v_trench * dt / r_o
    record, profile = faulted.diagnostics.record()
    record.update(rec)
    if weakening:
        local = gamma_b.array[:, 0, 0]
        record["strain_max"] = float(uw.utilities.gather_data(
            local.max() if local.size else 0.0, bcast=True).max())
    record.update({"v_plate": v_plate, "v_fault_normal": v_normal, "v_trench_fault": v_fault,
                   "dip": dip_t, "dip_built": faulted.dip, "fault_depth": depth_t})
    if relocated is not None:
        record["relocated_from"] = relocated[0]
    if band is not None:
        record.update({"band_bl_depth": band.get("bl_depth"), "band_theta": band["theta_t"], "band_dip": band["dip"],
                       "band_direction": band["direction"], "band_points": band["n_points"]})
    record.update({"theta_trench": theta_t, "v_trench": v_trench, "theta_built": faulted.theta_t,
                   "n_built": n_built, "t_build": round(faulted.t_build, 1)})
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    records.append(record)
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"q_top {record['q_top']:6.2f} q_base {record['q_base']:6.2f} "
              f"yield {record['yield_frac']:.3f}/{record['yield_frac_lid']:.3f} slip {record['slip_max']:.2f} "
              f"theta_t {np.degrees(theta_t):.2f} dip {dip_t:.1f} depth {depth_t:.3f} v_t {v_trench:.1f} (plate {v_plate:.1f} fault {v_fault:.1f}) | "
              f"newton {record['newton']} vel {record['vel_its']} pres {record['pres_its']} "
              f"conv {record['converged']} {record['t_stokes']:.1f}/{record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == params.uw_steps - 1:
        checkpoint(step, t, records, faulted)
    step += 1

uw.pprint("done")
