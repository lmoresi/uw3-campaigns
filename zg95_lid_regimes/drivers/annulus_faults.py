"""Faults that form where the lid fails: the strain-weakening annulus with a set of
split-node faults, each placed on, and moving with, a plastic-strain band of a
downwelling.

The rheology, walls and transport are those of ``annulus_fault.py`` (yield stress
weakened by an accumulated plastic strain gamma that is carried by the flow and heals
in warm mantle; a declared plastic regularisation eta_reg). The faults:

- every ``uw_detect_every`` steps each fault follows its own band: the saturated,
  cold, descending plastic-strain band near it (``strain_band.detect_fault``) gives a
  trench angle and a dip angle phi (measured below the local horizontal from +theta,
  so phi > 90 dips toward -theta), and the local thermal boundary layer gives the
  depth; the fault relaxes toward them by bounded steps;
- every ``uw_global_every`` steps the whole annulus is scanned
  (``strain_band.rank_bands``). A band whose damage (gamma integrated over its area)
  exceeds ``uw_damage_spawn`` with no fault within ``uw_fault_separation`` becomes a
  new fault, up to ``uw_max_faults``; a fault whose own band has healed below
  ``uw_damage_retire`` is removed (the last fault stays);
- all faults are placed into one copy of the base's finest level (and its split
  chain levels), each split along its own ladder and bridged to the surface, each
  with its own frictionless contact. The faulted mesh is rebuilt whenever a fault has
  moved, turned or changed depth enough, or the set has changed.

Start from an annulus run's checkpoint (``uw_source``/``uw_source_index``, a first
fault at ``uw_theta_trench``), or from a checkpoint of ``annulus_fault.py`` or of this
driver (``uw_restart`` in ``uw_out``; a single-fault state becomes the first fault).

    mpirun -np 7 python annulus_faults.py -uw_out <dir> -uw_restart 2450
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
from strain_band import (boundary_layer_depth, detect_fault, fit_fault_lines, polar_grid, rank_bands,
                         spine_separation)

params = uw.Params(
    uw_out="~/+Simulations/zg95/annulus_faults/runs/test_multi",
    uw_source="~/+Simulations/zg95/annulus_regimes/runs/tau1x1.50_seed5",
    uw_source_index=2050,
    uw_restart=-1,
    uw_cell=0.5,
    uw_refinement=4,
    uw_ra=9.1125e5,
    uw_deta=3.0e4,
    uw_tau0=2.025e4,
    uw_tau1=1.366875e6,
    uw_heating=1.4175,
    uw_yield_softness=0.2,
    # the first fault, when starting from an annulus run
    uw_theta_trench=0.0,
    uw_dip=45.0,
    uw_fault_depth=0.35,
    # the fault band
    uw_spacing=0.004,
    uw_eta_w=1.0e-3,
    uw_chain=2,
    uw_band_widen=1,
    uw_rebuild_rungs=4,
    uw_rebuild_dip=2.0,
    uw_rebuild_newton_switch=1.0e-2,
    # strain weakening, regularisation, healing
    uw_strain_crit=0.5,
    uw_weak_min=0.5,
    uw_yield_boost=1.25,
    uw_eta_reg=10.0,
    uw_heal_time=0.002,
    uw_heal_T=0.7,
    # following the bands
    uw_detect_every=5,
    uw_detect_window=40.0,      # largest half-width of a fault's own search arc (degrees)
    uw_detect_gamma_sat=0.5,
    uw_detect_T_lith=0.6,
    uw_detect_depth_max=0.45,
    uw_detect_depth_min=0.1,    # shallowest band point in the fit: the near-surface damage fans out (a V-top) above it
    uw_detect_max_dtheta=2.0,
    uw_detect_max_ddip=5.0,
    uw_dip_min=40.0,            # the ladder cap of a shallower fault reaches the outer wall and cannot be carved
    uw_dip_max=140.0,
    uw_bl_T=0.7,
    uw_fault_depth_min=0.06,
    uw_fault_depth_max=0.25,
    uw_detect_max_ddepth=0.05,
    # forming and removing faults
    uw_fault_law="lines",       # "lines": N faults fitted to the damage each detection; "bands": per-fault band tracking
    uw_line_gamma=2.0,          # "lines": damage counted (plastic strain at or above this)
    uw_line_min_damage=0.01,    # "lines": smallest damage (strain x area) that is a fault
    uw_line_width=0.035,        # "lines": half-width of a line's inlier band
    uw_line_surface=0.05,       # "lines": a fault's damage must start within this of the surface
    uw_line_match=6.0,          # "lines": a line within this arc of a fault's trench is that fault (degrees)
    uw_line_patience=3,         # "lines": detections a fault survives without a line before retiring
    uw_fault_damage=0.0,        # > 0: a fault damages its surroundings at this rate x slip, within a band width,
                                #      from its trench to one band width past its tip (so it can grow)
    uw_global_every=10,
    uw_damage_spawn=0.05,       # band damage (strain x area, layer depths squared) that forms a fault
    uw_damage_retire=0.01,      # a fault whose band has healed below this is removed
    uw_max_faults=3,
    uw_fault_separation=20.0,   # no new fault within this arc of an existing one (degrees)
    uw_fault_clearance=0.08,    # smallest distance between two faults' spines (layer depths): a
                                #   converging pair (the conjugate V) is kept apart by shortening the
                                #   weaker one; two ribbons through one cell hang the mesher
    # solver and time stepping
    uw_tol=1.0e-3,
    uw_picard=0,
    uw_newton_switch=1.0e-2,
    uw_warm_newton_switch=1.0,
    uw_verbose=0,
    uw_dt_mult=3.0,
    uw_courant=1.0,
    uw_dt_max=5.0e-3,
    uw_steps=20,
    uw_ckpt_every=10,
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
gamma_b = uw.discretisation.MeshVariable("plastic_strain", base, 1, degree=2)
edot_p_b = uw.discretisation.MeshVariable("edot_plastic", base, 1, degree=1)

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

# Accumulated plastic strain, carried by the flow, growing at the plastic strain rate
# and healing where the material has warmed into the mantle.
strain_adv = uw.systems.AdvDiffusion(base, gamma_b, V_b.sym, order=1)
strain_adv.constitutive_model = uw.constitutive_models.DiffusionModel
strain_adv.constitutive_model.Parameters.diffusivity = 1.0e-6
heal_rate = 0
if params.uw_heal_time > 0:
    heal_rate = 1 / params.uw_heal_time
    if params.uw_heal_T > 0:
        heal_rate = heal_rate * (1 + sympy.tanh((T_b.sym[0] - params.uw_heal_T) / 0.02)) / 2
fault_damage_b = uw.discretisation.MeshVariable("fault_damage", base, 1, degree=1)
strain_adv.f = edot_p_b.sym[0] + fault_damage_b.sym[0] - gamma_b.sym[0] * heal_rate


def onto(points):
    return clamp_radii(np.asarray(points, dtype=float), r_o, r_i, inset=1.0e-10)


def wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def fault_trace(fault, coarsening=1):
    """A fault's spine (from just above the outer wall to its tip) and the trace to cut
    (more than three finest rungs inside the wall), at ``coarsening`` times the rung
    spacing; the dip angle phi is measured below the local horizontal from +theta."""
    theta_t, phi = fault["theta"], np.deg2rad(fault["dip"])
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down_dip = np.cos(phi) * t_hat - np.sin(phi) * r_hat
    top = r_hat * (r_o + 0.02)
    b = top @ down_dip
    c = top @ top - (r_o - fault["depth"]) ** 2
    length = -b - np.sqrt(b * b - c)
    block = 2 ** int(params.uw_chain)
    n = block * max(1, int(round(length / (block * S))))
    spine = np.array([top + down_dip * (length * i / n) for i in range(n + 1)])[::coarsening]
    return spine, spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - 3.0 * S]


def placed_ladders(host, faults, coarsening):
    """Every fault's ladder band placed on ``host`` at ``coarsening`` times the rung
    spacing, each split along its own rungs. The fill-ring self-crossing check gives a
    false positive when a ring runs along mesh nodes collinear to round-off (the annulus
    has a line of them at theta = 0); a wider band or margin moves the ring off it."""
    pieces = [(f["name"],) + fault_trace(f, coarsening) for f in faults]
    width = W * coarsening if params.uw_band_widen else W
    # Every set places in serial; in parallel the "gather" seam handling can reach
    # the domain wall when several bands sit close together (measured: four bands
    # within 11 degrees on 7 ranks), so the ligament seams are the last resort.
    # The ligament seams need the network mesher (one CAD call for all the bands, spines
    # embedded), which also does without the gather. Its levels do not nest, so it is
    # the last resort, on the finest level only (a chain level that refuses is welded).
    # (the network mesher with ligament seams DEADLOCKED in parallel on a four-band set,
    # 2026-10-18: one rank raised inside the CAD call, the others waited; not retried)
    attempts = [(1, 0.7, 1.0, "gather", "ladder"), (1, 0.7, 1.25, "gather", "ladder"),
                (2, 0.7, 1.0, "gather", "ladder"), (1, 0.7, 1.5, "gather", "ladder")]
    for n, (rings, clearance, widen, seams, mesher) in enumerate(attempts):
        try:
            mesh, info = place_fault_ribbon_2d(
                host, [(name, trace) for name, _, trace in pieces], width * widen,
                spines=[(name, spine) for name, spine, _ in pieces], margin_rings=rings,
                clearance=clearance, split=True, mesher=mesher, seams=seams)
            if n:
                uw.pprint(f"  placed with margin_rings {rings}, clearance {clearance}, width x{widen}, "
                          f"seams {seams}, mesher {mesher}")
            return mesh, info, {name: (spine, trace) for name, spine, trace in pieces}
        except (RuntimeError, ValueError) as err:
            retryable = any(s in str(err) for s in ("crosses itself", "domain wall", "ligament", "seam"))
            if not retryable or n == len(attempts) - 1:
                raise RuntimeError(str(err))


def keep_apart(faults, slips, damage, events):
    """Shorten the weaker of any two faults whose spines come within uw_fault_clearance
    of each other, so the mesher never has to carve two ribbons through one cell (a
    conjugate pair closing into a V hung gmsh on the surgery rank, 2026-10-21, at a
    separation of 0.2 fine cells). The weaker fault is the one with less slip (then
    less line damage, then the younger); it loses depth in rung steps until it clears,
    and retires if it cannot clear at the shallowest depth allowed."""
    clearance = float(params.uw_fault_clearance)
    if clearance <= 0 or len(faults) < 2:
        return

    def strength(f):
        return (slips.get(f["name"], 0.0) or 0.0, damage.get(f["name"], 0.0) or 0.0, -int(f["name"][1:]))

    changed = True
    while changed:
        changed = False
        spines = {f["name"]: fault_trace(f)[0] for f in faults}
        for i in range(len(faults)):
            for j in range(i + 1, len(faults)):
                a, b = faults[i], faults[j]
                if spine_separation(spines[a["name"]], spines[b["name"]]) >= clearance:
                    continue
                weak, strong = (a, b) if strength(a) < strength(b) else (b, a)
                depth = weak["depth"]
                while depth - S >= params.uw_fault_depth_min:
                    depth -= S
                    trial = dict(weak, depth=depth)
                    if spine_separation(fault_trace(trial)[0], spines[strong["name"]]) >= clearance:
                        break
                else:
                    depth = None
                if depth is None:
                    faults.remove(weak)
                    events.append(f"retired {weak['name']} at {np.degrees(weak['theta']):.1f} deg "
                                  f"(converges on {strong['name']} at every depth)")
                else:
                    events.append(f"shortened {weak['name']} to depth {depth:.3f} (clear of {strong['name']} "
                                  f"by {clearance:.2f})")
                    weak["depth"] = float(depth)
                changed = True
                break
            if changed:
                break


def segment_distance(points, a, b):
    ab = b - a
    s = np.clip(((points - a) @ ab) / max(ab @ ab, 1e-30), 0.0, 1.0)
    return np.linalg.norm(points - (a + s[:, None] * ab), axis=1)


class FaultedMesh:
    """All the faults placed into a copy of the base's finest level, with the Stokes
    solver, the bridge zones and the P1 fields the renders read."""

    def __init__(self, faults, tag):
        wall = time.perf_counter()
        self.faults = [dict(f) for f in faults]
        self.names = [f["name"] for f in self.faults]
        chain = int(params.uw_chain)
        mids = []
        for k in range(chain, 0, -1):
            host = levels[len(levels) - k]
            try:
                mids.append(placed_ladders(host, self.faults, 2 ** k)[0])
            except (RuntimeError, ValueError) as err:
                uw.pprint(f"  chain level {2 ** k}S refused ({str(err)[:80]}): welded")
                mids.append(host)
        self.levels = levels[:len(levels) - chain] + mids if chain else levels
        self.mesh, info, self.pieces = placed_ladders(base, self.faults, 1)
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
        # Each fault's bridge: its band cells outside its split's upper tip.
        centroids = np.asarray(self.zone.coords)
        radius = np.hypot(centroids[:, 0], centroids[:, 1])
        bridge = np.zeros(len(centroids), dtype=bool)
        for name, (spine, trace) in self.pieces.items():
            near = segment_distance(centroids, spine[0], spine[-1]) < 2.0 * W
            bridge |= band & near & (radius > np.hypot(*trace[0]) - 0.5 * W)
        self.zone.array[:, 0, 0] = bridge.astype(float)

        s = uw.systems.Stokes(mesh, velocityField=self.v, pressureField=self.p)
        weak = 1 - (1 - params.uw_eta_w) * self.zone.sym[0]
        yield_factor = params.uw_yield_boost * (1 - (1 - params.uw_weak_min) * sympy.Min(
            self.gamma.sym[0] / params.uw_strain_crit, 1))
        self.eta_T = set_viscoplastic(s, self.T.sym[0], deta, tau0, tau1, params.uw_yield_softness,
                                      r_o, weak, yield_factor)
        if params.uw_eta_reg > 0:
            s.constitutive_model.Parameters.plastic_rate_strengthening = params.uw_eta_reg
        s.bodyforce = Ra * self.T.sym[0] * mesh.CoordinateSystem.unit_e_0
        free_slip_walls(s)
        for name in self.names:
            s.add_fault_bc(0, boundary=name)
        s.tolerance = params.uw_tol
        s.consistent_jacobian = "continuation"
        s.newton_switch_rtol = params.uw_newton_switch
        set_custom_fmg(s, self.levels, field_id=0)
        self.stokes = s
        self.has_guess = False

        eta_eff = s.constitutive_model.viscosity
        self.eta_projection = uw.systems.Projection(mesh, self.log_eta)
        self.eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
        self.ratio_projection = uw.systems.Projection(mesh, self.yield_ratio)
        self.ratio_projection.uw_function = eta_eff / self.eta_T
        cm = s.constitutive_model
        self.edot_projection = uw.systems.Projection(mesh, self.edot_p)
        self.edot_projection.uw_function = cm._strainrate_inv_II * sympy.Max(
            0, 1 - eta_eff / (self.eta_T * weak))
        self.diagnostics = AnnulusDiagnostics(T_b, self.v, eta_eff, self.eta_T, params.uw_heating)
        self.t_build = time.perf_counter() - wall
        level_cells = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                       for m in self.levels + [mesh]]
        described = ", ".join(f"{f['name']} {np.degrees(f['theta']):.2f} deg / dip {f['dip']:.1f} / "
                              f"depth {f['depth']:.3f}" for f in self.faults)
        uw.pprint(f"faulted mesh {tag}: {described}; levels (cells) {level_cells}, "
                  f"built in {self.t_build:.1f} s")

    def split_nudges(self, var):
        """Offsets that put each split copy of ``var``'s DOFs on its own side of its
        fault (Plus at -n, Minus at +n, 0.1 rungs), so an evaluation on a faulted source
        takes each side's own slip."""
        nudge = np.zeros((var.array.shape[0], 2))
        _, sub = self.mesh.dm.createSubDM(var.field_id)
        sec = sub.getLocalSection()
        width = var.num_components
        for name in self.names:
            pairs = _fault_pair_nodes_on(self.mesh, self.mesh.dm, self.mesh.dm.getLocalSection(),
                                         name, field=self.v.field_id)
            for q_plus, q_minus, n_hat in pairs:
                for q, sign in ((q_plus, -1.0), (q_minus, 1.0)):
                    if sec.getDof(q) > 0:
                        nudge[sec.getOffset(q) // width] = sign * 0.1 * S * np.asarray(n_hat)
        return nudge

    def warm_start(self, V, P=None):
        """Initial guess from velocity (and pressure) on another mesh, the split copies
        evaluated a hair inside their own side."""
        split_source = getattr(V.mesh, "_fault_point_pairs", None)

        def at(var, source, coords):
            points = np.asarray(coords, dtype=float)
            if split_source:
                points = points + self.split_nudges(var)
            return np.asarray(uw.function.global_evaluate(source.sym, onto(points)))

        self.v.array[:, 0, :] = at(self.v, V, self.v.coords).reshape(-1, 2)
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
        self.gamma.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(gamma_b.sym[0], onto(self.gamma.coords))).ravel()
        info = self._stokes_solve(from_rest=not self.has_guess)
        if not info.get("converged") and self.has_guess:
            uw.pprint("  the warm start did not converge: solving from rest")
            self.stokes.newton_switch_rtol = params.uw_newton_switch
            info = self._stokes_solve(from_rest=True)
        self.stokes.newton_switch_rtol = params.uw_warm_newton_switch
        self.has_guess = True
        slips = {}
        for name in self.names:
            _, slip, _ = fault_slip(self.stokes, name, info)
            slips[name] = float(uw.utilities.gather_data(
                np.abs(slip).max() if len(slip) else 0.0, bcast=True).max())
        return {
            "newton": info.get("nonlinear_iterations"),
            "vel_its": info.get("vel_its_last"),
            "pres_its": info.get("pres_its_last"),
            "converged": bool(info.get("converged")),
            "slip": slips,
            "slip_max": max(slips.values()) if slips else 0.0,
        }

    def to_base(self, slips=None):
        slips = slips or {}
        V_b.array[:, 0, :] = np.asarray(
            uw.function.global_evaluate(self.v.sym, onto(V_b.coords))).reshape(-1, 2)
        self.edot_projection.solve()
        edot = np.asarray(uw.function.global_evaluate(
            self.edot_p.sym[0], onto(edot_p_b.coords))).ravel()
        edot_p_b.array[:, 0, 0] = np.maximum(edot, 0.0)
        if params.uw_fault_damage > 0:
            self.fault_damage(slips)

    def fault_damage(self, slips):
        """The damage a fault does to its surroundings: at rate uw_fault_damage x its slip,
        within one band width of its line, from the trench to one band width past the
        tip, so the band ahead of the tip saturates and the next fit lengthens the fault."""
        pts = np.asarray(fault_damage_b.coords)
        rate = np.zeros(len(pts))
        for f in self.faults:
            spine, _ = self.pieces[f["name"]]
            a, b = spine[0], spine[-1]
            u = (b - a) / np.linalg.norm(b - a)
            b = b + u * 2.0 * W
            d = segment_distance(pts, a, b)
            rate = np.maximum(rate, params.uw_fault_damage * slips.get(f["name"], 0.0) * (d < 2.0 * W))
        fault_damage_b.array[:, 0, 0] = rate

    def render_fields_to_base(self):
        self.eta_projection.solve()
        self.ratio_projection.solve()
        log_eta_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.log_eta.sym[0], onto(log_eta_b.coords))).ravel()
        yield_ratio_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.yield_ratio.sym[0], onto(yield_ratio_b.coords))).ravel()


def sample(th, dep, xy):
    """T, v_r, gamma and edot_plastic at grid points (collective: every rank evaluates
    the same points and so takes the same decisions)."""
    pts = onto(xy)
    shape = (len(dep), len(th))
    T = np.asarray(uw.function.global_evaluate(T_b.sym[0], pts)).reshape(shape)
    v = np.asarray(uw.function.global_evaluate(V_b.sym, pts)).reshape(-1, 2)
    v_r = ((v[:, 0] * pts[:, 0] + v[:, 1] * pts[:, 1]) / np.hypot(pts[:, 0], pts[:, 1])).reshape(shape)
    gamma = np.asarray(uw.function.global_evaluate(gamma_b.sym[0], pts)).reshape(shape)
    edot = np.asarray(uw.function.global_evaluate(edot_p_b.sym[0], pts)).reshape(shape)
    return T, v_r, gamma, edot


def detect_band(theta_c, half_width, fit_depth=None, prefer=True):
    """The band nearest ``theta_c`` within ``half_width``: trench, dip angle phi, the
    local boundary-layer depth and the band's damage, or None. The line is fitted over
    the band down to ``fit_depth`` only (the depth the fault occupies: a band that kinks
    below it would tilt the fit), and clusters nearer ``theta_c`` are preferred."""
    th, dep, xy = polar_grid(r_o, n_theta=max(41, int(4 * np.degrees(2 * half_width))), depth_max=0.5,
                             n_depth=64, centre=theta_c, half_width=half_width)
    T, v_r, gamma, edot = sample(th, dep, xy)
    found = detect_fault(th, dep, gamma, edot, T, v_r, r_o, params.uw_detect_gamma_sat,
                         params.uw_detect_T_lith,
                         params.uw_detect_depth_max if fit_depth is None else fit_depth,
                         depth_min=params.uw_detect_depth_min,
                         periodic=False, prefer=theta_c if prefer else None)
    if found is None:
        return None
    if abs(wrap(found["theta_t"] - theta_c)) > half_width:
        # a fitted line that reaches the surface outside the searched arc is not this
        # band (measured: a V-topped band fitted from 0.05 d gave a 23 degree line whose
        # trench lay 21 degrees away); the fault keeps its place
        return None
    found["phi"] = found["dip"] if found["direction"] > 0 else 180.0 - found["dip"]
    found["bl_depth"] = boundary_layer_depth(th, dep, T, found["theta_t"], params.uw_bl_T)
    bands = rank_bands(th, dep, gamma, edot, T, v_r, params.uw_detect_gamma_sat,
                       params.uw_detect_T_lith, params.uw_detect_depth_max, min_points=10,
                       periodic=False, r_o=r_o)
    found["damage"] = bands[0][4] if bands else 0.0
    return found


def global_bands():
    th, dep, xy = polar_grid(r_o, n_theta=720, depth_max=0.5, n_depth=48)
    T, v_r, gamma, edot = sample(th, dep, xy)
    return rank_bands(th, dep, gamma, edot, T, v_r, params.uw_detect_gamma_sat, params.uw_detect_T_lith,
                      params.uw_detect_depth_max, min_points=10, r_o=r_o)


def own_window(fault, faults):
    """A fault's search arc: the detection window, shrunk so it stops short of its
    neighbours' bands."""
    others = [abs(wrap(g["theta"] - fault["theta"])) for g in faults if g is not fault]
    half = np.deg2rad(params.uw_detect_window)
    return min([half] + [0.45 * d for d in others])


def as_fault(name, band, depth=None):
    return {"name": name, "theta": float(band["theta_t"]),
            "dip": float(np.clip(band["phi"], params.uw_dip_min, params.uw_dip_max)),
            "depth": float(np.clip(band["bl_depth"] if band.get("bl_depth") is not None
                                   else (depth or params.uw_fault_depth),
                                   params.uw_fault_depth_min, params.uw_fault_depth_max))}


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def checkpoint(step, t, records, faulted, faults, next_id):
    faulted.render_fields_to_base()
    base.write_timestep("annulus", index=step, outputPath=out,
                        meshVars=[V_b, T_b, log_eta_b, yield_ratio_b, gamma_b, edot_p_b])
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, f"state_{step:05d}.json"), "w") as f:
                json.dump({"step": step, "t": t, "params": params.to_dict(), "faults": faults,
                           "next_id": next_id,
                           # the first fault, for the single-fault readers (renders)
                           "theta_trench": faults[0]["theta"], "dip": faults[0]["dip"],
                           "fault_depth": faults[0]["depth"],
                           "trace": faulted.pieces[faults[0]["name"]][1].tolist(),
                           "traces": [faulted.pieces[f["name"]][1].tolist() for f in faults]},
                          f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- initial state
records = []
if params.uw_restart < 0:
    source = os.path.expanduser(params.uw_source)
    for var in (T_b, V_b):
        var.read_timestep("annulus", var.name, params.uw_source_index, outputPath=source)
    with open(os.path.join(source, f"state_{params.uw_source_index:05d}.json")) as f:
        state = json.load(f)
    if os.path.exists(os.path.join(source, "records.json")):
        with open(os.path.join(source, "records.json")) as f:
            records = [r for r in json.load(f) if r["step"] <= params.uw_source_index]
    faults = [{"name": "F0", "theta": float(params.uw_theta_trench), "dip": float(params.uw_dip),
               "depth": float(params.uw_fault_depth)}]
    next_id = 1
else:
    for var in (T_b, V_b, gamma_b):
        var.read_timestep("annulus", var.name, params.uw_restart, outputPath=out)
    with open(os.path.join(out, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    with open(os.path.join(out, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]
    if "faults" in state:
        faults, next_id = state["faults"], int(state["next_id"])
    else:                      # a single-fault state of annulus_fault.py
        faults = [{"name": "F0", "theta": float(state["theta_trench"]),
                   "dip": float(state.get("dip", params.uw_dip)),
                   "depth": float(state.get("fault_depth", params.uw_fault_depth))}]
        next_id = 1
t, step = float(state["t"]), int(state["step"]) + 1

n_built = 1
refused = {}                   # formation trenches the surgery refused: no new fault within 3 deg for a while
last_damage = {}               # each fault's line damage at the last detection
keep_apart(faults, (records[-1].get("slip") or {}) if records else {}, {}, [])
faulted = FaultedMesh(faults, "f0")
uw.pprint(f"annulus r_o {r_o:.4f} r_i {r_i:.4f}, Ra {params.uw_ra:.4g}, tau1/Ra "
          f"{params.uw_tau1 / params.uw_ra:.3g}, H {params.uw_heating:.4g}; {len(faults)} fault(s); "
          f"from t {t:.4f}; output {out}")


def needs_rebuild(faults, built):
    if [f["name"] for f in faults] != [f["name"] for f in built]:
        return True
    for f, g in zip(faults, built):
        if (abs(wrap(f["theta"] - g["theta"])) * r_o > params.uw_rebuild_rungs * S
                or abs(f["dip"] - g["dip"]) > params.uw_rebuild_dip
                or abs(f["depth"] - g["depth"]) > 2 * S):
            return True
    return False


# ----------------------------------------------------------------------------- time loop
for k in range(params.uw_steps):
    wall = time.perf_counter()
    events = []
    damage = last_damage
    if needs_rebuild(faults, faulted.faults):
        previous = faulted
        try:
            faulted = FaultedMesh(faults, f"f{n_built}")
        except RuntimeError as err:
            uw.pprint(f"  placement of {[f['name'] for f in faults]} failed ({str(err)[:120]})")
            # A set the surgery refuses: usually a new fault whose band collides with a
            # fading neighbour's. Try again without the weakest-damage old fault (the new
            # one keeps its place); if that fails too, keep the previous set.
            new_names = [f["name"] for f in faults if f["name"] not in previous.names]
            old = [f for f in faults if f["name"] in previous.names]
            retry = None
            if new_names and len(old) > 1:
                weakest = min(old, key=lambda f: damage.get(f["name"], 1.0))
                trial = [f for f in faults if f["name"] != weakest["name"]]
                try:
                    retry = FaultedMesh(trial, f"f{n_built}")
                    faults = trial
                    events.append(f"retired {weakest['name']} at {np.degrees(weakest['theta']):.1f} deg "
                                  f"(its band collided with {new_names})")
                except RuntimeError as err2:
                    uw.pprint(f"  retry without {weakest['name']} failed ({str(err2)[:80]})")
            if retry is not None:
                faulted = retry
            else:
                uw.pprint("  keeping the previous faults")
                for f in faults:
                    if f["name"] not in previous.names:
                        refused[f["name"]] = f["theta"]
                faults = [dict(f) for f in previous.faults]
                faulted = previous
        n_built += 1
        if faulted is not previous and faulted.names == previous.names:
            # the same faults, moved: start from the old solution. A changed set (a fault
            # formed or removed) starts from rest: the warm start from the old set failed
            # to converge (measured on forming a second fault) and was then repeated cold.
            faulted.warm_start(previous.v, previous.p)
            faulted.stokes.newton_switch_rtol = params.uw_rebuild_newton_switch
        del previous
        gc.collect()
    rec = faulted.solve()
    t_stokes = time.perf_counter() - wall
    faulted.to_base(rec["slip"])
    dt_accuracy = params.uw_dt_mult * float(adv.estimate_dt())
    adv.estimate_dt(basis="resolution", direction_aware=True)
    dt_crossing = adv.dt_adv
    dt = min(dt_accuracy, params.uw_courant * dt_crossing, params.uw_dt_max)
    adv.solve(timestep=dt)
    strain_adv.solve(timestep=dt)
    gamma_b.array[:, 0, 0] = np.maximum(gamma_b.array[:, 0, 0], 0.0)
    t += dt

    damage = {}
    if params.uw_fault_law == "lines" and k % params.uw_detect_every == 0:
        # N faults fitted to the damage: each existing fault takes the line nearest its
        # trench (by bounded steps), an unmatched line forms a fault, a fault with no
        # line for uw_line_patience detections retires
        th, dep, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
        T, v_r, gamma, edot = sample(th, dep, xy)
        lines = fit_fault_lines(th, dep, gamma, T, r_o, params.uw_line_gamma, params.uw_detect_T_lith,
                                0.02, params.uw_detect_depth_max, params.uw_max_faults + 2,
                                params.uw_line_min_damage, params.uw_line_width,
                                surface_reach=params.uw_line_surface)
        taken = set()
        for f in faults:
            best, best_d = None, np.deg2rad(params.uw_line_match)
            for n, ln in enumerate(lines):
                d = abs(wrap(ln["theta_t"] - f["theta"]))
                if n not in taken and d < best_d:
                    best, best_d = n, d
            if best is None:
                f["misses"] = f.get("misses", 0) + 1
                damage[f["name"]] = 0.0
                continue
            taken.add(best)
            ln = lines[best]
            f["misses"] = 0
            damage[f["name"]] = ln["damage"]
            cap = np.deg2rad(params.uw_detect_max_dtheta)
            f["theta"] = float(f["theta"] + np.clip(wrap(ln["theta_t"] - f["theta"]), -cap, cap))
            phi = float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max))
            f["dip"] = float(f["dip"] + np.clip(phi - f["dip"], -params.uw_detect_max_ddip,
                                                params.uw_detect_max_ddip))
            target = float(np.clip(ln["depth_bottom"], params.uw_fault_depth_min, params.uw_fault_depth_max))
            f["depth"] = float(f["depth"] + np.clip(target - f["depth"], -params.uw_detect_max_ddepth,
                                                    params.uw_detect_max_ddepth))
        if k % (10 * params.uw_detect_every) == 0:
            refused.clear()        # the band may have changed enough to place
        for f in list(faults):
            if len(faults) > 1 and f.get("misses", 0) >= params.uw_line_patience:
                faults.remove(f)
                events.append(f"retired {f['name']} at {np.degrees(f['theta']):.1f} deg (no line)")
        sep = np.deg2rad(params.uw_fault_separation)
        for n, ln in enumerate(lines):
            if n in taken or len(faults) >= params.uw_max_faults:
                continue
            if any(abs(wrap(ln["theta_t"] - f["theta"])) < sep for f in faults):
                continue
            if any(abs(wrap(ln["theta_t"] - th)) < np.deg2rad(3.0) for th in refused.values()):
                continue
            new = {"name": f"F{next_id}", "theta": float(ln["theta_t"]),
                   "dip": float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max)),
                   "depth": float(np.clip(ln["depth_bottom"], params.uw_fault_depth_min, params.uw_fault_depth_max)),
                   "misses": 0}
            next_id += 1
            faults.append(new)
            events.append(f"formed {new['name']} at {np.degrees(new['theta']):.1f} deg (line damage "
                          f"{ln['damage']:.3f}), dip {new['dip']:.1f}, depth {new['depth']:.3f}")
    elif k % params.uw_detect_every == 0:
        # each fault follows its own band, by bounded steps
        for f in faults:
            band = detect_band(f["theta"], own_window(f, faults), fit_depth=max(f["depth"] + 0.05, 0.15))
            if band is None:
                damage[f["name"]] = 0.0
                continue
            damage[f["name"]] = band["damage"]
            cap = np.deg2rad(params.uw_detect_max_dtheta)
            f["theta"] = float(f["theta"] + np.clip(wrap(band["theta_t"] - f["theta"]), -cap, cap))
            phi = float(np.clip(band["phi"], params.uw_dip_min, params.uw_dip_max))
            f["dip"] = float(f["dip"] + np.clip(phi - f["dip"], -params.uw_detect_max_ddip,
                                                params.uw_detect_max_ddip))
            if band.get("bl_depth") is not None:
                target = float(np.clip(band["bl_depth"], params.uw_fault_depth_min, params.uw_fault_depth_max))
                f["depth"] = float(f["depth"] + np.clip(target - f["depth"], -params.uw_detect_max_ddepth,
                                                        params.uw_detect_max_ddepth))
    if params.uw_fault_law == "bands" and params.uw_global_every and k % params.uw_global_every == 0:
        bands = global_bands()
        sep = np.deg2rad(params.uw_fault_separation)
        # a fault whose band has healed is removed (the last one stays)
        for f in list(faults):
            if len(faults) > 1 and damage.get(f["name"], 1.0) < params.uw_damage_retire:
                faults.remove(f)
                events.append(f"retired {f['name']} at {np.degrees(f['theta']):.1f} deg")
        # a damaged band away from every fault becomes a fault
        for b in bands:
            if len(faults) >= params.uw_max_faults or not b[4] >= params.uw_damage_spawn:
                continue
            if any(abs(wrap(b[0] - f["theta"])) < sep for f in faults):
                continue
            band = detect_band(b[0], np.deg2rad(min(params.uw_detect_window, 0.45 * params.uw_fault_separation * 2)),
                               fit_depth=0.3)
            if band is None:
                continue
            new = as_fault(f"F{next_id}", band)
            next_id += 1
            faults.append(new)
            events.append(f"formed {new['name']} at {np.degrees(new['theta']):.1f} deg (damage {b[4]:.3f}), "
                          f"dip {new['dip']:.1f}, depth {new['depth']:.3f}")
    if k % params.uw_detect_every == 0:
        keep_apart(faults, rec["slip"], damage, events)
    if damage:
        last_damage = dict(damage)
    for e in events:
        uw.pprint(f"  fault {e}")

    record, profile = faulted.diagnostics.record()
    record.update(rec)
    local = gamma_b.array[:, 0, 0]
    record["strain_max"] = float(uw.utilities.gather_data(local.max() if local.size else 0.0, bcast=True).max())
    record.update({"faults": [dict(f) for f in faults], "n_faults": len(faults), "damage": damage,
                   "events": events, "theta_trench": faults[0]["theta"], "dip": faults[0]["dip"],
                   "fault_depth": faults[0]["depth"], "n_built": n_built, "t_build": round(faulted.t_build, 1)})
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    records.append(record)
    described = " ".join(f"{f['name']}@{np.degrees(f['theta']):.1f}/{f['dip']:.0f}/{f['depth']:.2f}"
                         f"(slip {rec['slip'].get(f['name'], float('nan')):.0f})" for f in faults)
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"slip {record['slip_max']:.2f} | faults {described} | "
              f"newton {record['newton']} conv {record['converged']} "
              f"{record['t_stokes']:.1f}/{record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == params.uw_steps - 1:
        checkpoint(step, t, records, faulted, faults, next_id)
    step += 1

uw.pprint("done")
