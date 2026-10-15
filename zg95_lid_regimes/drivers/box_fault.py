"""A fault in the yielding-lid box: does a weak dipping fault move a stagnant lid onto
the mobile branch?

At tau1/Ra = 1 the box is bistable: the standard start settles to a stagnant lid, a
start from a mobile state stays mobile. This driver restarts from a saturated box
state and adds a fault through the lid.

The base box (never cut) carries the temperature and its advection-diffusion. The
faulted mesh is a copy of the base's finest level with the fault placed as the
structured ladder (one element either side of the spine): the spine is split and in
frictionless contact from three rung spacings below the surface down to
``uw_fault_depth``, and the ladder's last rungs up to the surface are a weak
isotropic bridge (viscosity and yield stress both times ``uw_eta_w``). Stokes is
solved on the faulted mesh, with multigrid on the base's own levels, and the
velocity goes back to the base by evaluation for the transport step. The fault dips
at ``uw_dip`` degrees from the surface trench at ``uw_trench_x``, down toward +x.

With ``uw_migrate`` the trench moves with the overriding plate (the +x side): at the
median surface velocity over the window ``uw_trench_off`` to ``uw_trench_off +
uw_trench_span`` beyond it (the plate itself, not the sliver next to the fault, which
goes stationary once the fault takes the slip). The faulted mesh is rebuilt whenever
the trench has moved by a rung spacing, and the new solve starts from the old one.

The first solve on the first faulted mesh starts from rest (``uw_cold_start``): a
warm start from a fault-free velocity stalls the Picard line search. A rebuilt mesh
starts from the previous faulted solution, and falls back to rest if that fails.

    mpirun -np 4 python box_fault.py -uw_out ~/+Simulations/zg95/box_faults/runs/<name> \\
        -uw_source ~/+Simulations/zg95/box_regimes/runs/mobile_ref_H1.42 -uw_source_index 1975
"""
import gc
import json
import os
import time

import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

from box_model import BoxDiagnostics, box_mesh, free_slip_walls, set_viscoplastic

params = uw.Params(
    uw_out="~/+Simulations/zg95/box_faults/runs/test",
    uw_source="~/+Simulations/zg95/box_regimes/runs/mobile_ref_H1.42",
    uw_source_index=1975,       # the box checkpoint the fault run starts from
    uw_restart=-1,              # this run's own checkpoint to continue from (-1: start from the source)
    uw_width=4.0,
    uw_cell=0.125,
    uw_refinement=2,
    uw_ra=9.1125e5,
    uw_deta=3.0e4,
    uw_tau0=2.025e4,
    uw_tau1=9.1125e5,
    uw_heating=1.4175,
    uw_yield_softness=0.2,
    uw_trench_x=2.0,            # surface position of the trench
    uw_dip=45.0,                # fault dip from the horizontal, down toward +x (degrees)
    uw_fault_depth=0.35,        # depth of the fault's lower tip
    uw_spacing=0.004,           # ladder rung spacing (the band is two rungs wide)
    uw_eta_w=1.0e-3,            # weak-bridge factor on viscosity and yield stress
    uw_chain=2,                 # split ladder levels below the finest (0: welded coarse levels)
    uw_band_widen=1,            # 1: each chain level's band is two of its own rungs wide
    uw_fac=0,                   # 1: strong patch smoother on the band cells (multigrid finest level)
    uw_migrate=0,               # 1: the trench moves with the overriding plate
    uw_trench_off=0.2,          # trench-velocity window: offset beyond the trench
    uw_trench_span=0.4,         # trench-velocity window: width
    uw_rebuild_rungs=1,         # rebuild the faulted mesh when the trench has moved this many rungs
    uw_rebuild_newton_switch=1.0e-2,  # rebuilt mesh: Picard until this reduction of its own start, then Newton (0.1 stalled Newton, measured)
    uw_tol=1.0e-3,
    uw_picard=2,                # frozen-tangent steps before Newton on every solve
    uw_newton_switch=1.0e-2,    # first solve: Picard hands over to Newton at this residual reduction
    uw_warm_newton_switch=1.0,  # later solves: the same, measured from the warm start's own residual
    uw_verbose=0,               # 1: print every nonlinear iteration
    uw_cold_start=0,            # 1: first solve from rest instead of the source velocity
    uw_dt_mult=3.0,
    uw_courant=1.0,
    uw_dt_max=5.0e-3,
    uw_steps=20,
    uw_ckpt_every=10,
)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
width = float(params.uw_width)
S = float(params.uw_spacing)
W = 2.0 * S

base = box_mesh(width, params.uw_cell, params.uw_refinement)
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
adv.add_dirichlet_bc(0.0, "Top")
adv.add_dirichlet_bc(1.0, "Bottom")


def fault_trace(x_trench, coarsening=1):
    """The spine (from just above the surface down past the tip) and the trace to
    cut (the spine below three finest rung spacings under the surface), sampled at
    ``coarsening`` times the rung spacing. The finest count is a multiple of
    2**uw_chain, so every coarser sampling is a subset of the finest one."""
    dip = np.deg2rad(params.uw_dip)
    down_dip = np.array([np.cos(dip), -np.sin(dip)])
    top = np.array([x_trench, 1.0 + 0.02])
    length = (params.uw_fault_depth + 0.02) / np.sin(dip)
    block = 2 ** int(params.uw_chain)
    n = block * max(1, int(round(length / (block * S))))
    spine = np.array([top + down_dip * (length * i / n) for i in range(n + 1)])[::coarsening]
    return spine, spine[spine[:, 1] <= 1.0 - 3.0 * S]


def placed_ladder(host, x_trench, coarsening):
    """The fault's ladder band placed on ``host`` at ``coarsening`` times the rung
    spacing, split along its own rungs."""
    spine, trace = fault_trace(x_trench, coarsening)
    width = W * coarsening if params.uw_band_widen else W
    mesh, info = place_fault_ribbon_2d(host, [("Trench", trace)], width, spines=[("Trench", spine)],
                                       margin_rings=1, clearance=0.7, split=True, mesher="ladder")
    return mesh, info, spine, trace


class FaultedMesh:
    """The trench placed into a copy of the base's finest level, with its Stokes
    solver, the bridge zone and the P1 fields the renders read."""

    def __init__(self, x_trench, tag):
        wall = time.perf_counter()
        self.x_trench = x_trench
        # The multigrid hierarchy carries the fault through its coarse levels (C on the
        # ladder): the ladder at 2**k times the rung spacing on the base level k steps
        # below the finest, each split along its own rungs, so the coarse spaces contain
        # the slip. Welded coarse levels cannot represent it: the velocity solve then
        # caps once Newton starts on a mobilising lid.
        chain = int(params.uw_chain)
        base_levels = levels
        mids = [placed_ladder(base_levels[len(base_levels) - k], x_trench, 2 ** k)[0]
                for k in range(chain, 0, -1)]
        self.levels = base_levels[:len(base_levels) - chain] + mids if chain else base_levels
        self.mesh, info, self.spine, self.trace = placed_ladder(base, x_trench, 1)
        mesh = self.mesh
        band = np.asarray(info["band"], dtype=bool)
        self.T = uw.discretisation.MeshVariable(f"T_{tag}", mesh, 1, degree=2)
        self.v = uw.discretisation.MeshVariable(f"V_{tag}", mesh, mesh.dim, degree=2)
        self.p = uw.discretisation.MeshVariable(f"P_{tag}", mesh, 1, degree=1, continuous=True)
        self.zone = uw.discretisation.MeshVariable(f"zone_{tag}", mesh, 1, degree=0, continuous=False)
        self.log_eta = uw.discretisation.MeshVariable(f"log10_eta_{tag}", mesh, 1, degree=1)
        self.yield_ratio = uw.discretisation.MeshVariable(f"yield_ratio_{tag}", mesh, 1, degree=1)
        # The bridge: the band cells above the split's upper tip (the cap and the last
        # rungs), weak in viscosity and yield stress so the fault reaches the surface.
        centroids = np.asarray(self.zone.coords)
        bridge = band & (centroids[:, 1] > self.trace[0, 1] - 0.5 * W)
        self.zone.array[:, 0, 0] = bridge.astype(float)

        s = uw.systems.Stokes(mesh, velocityField=self.v, pressureField=self.p)
        weak = 1 - (1 - params.uw_eta_w) * self.zone.sym[0]
        self.eta_T = set_viscoplastic(s, self.T.sym[0], deta, tau0, tau1, params.uw_yield_softness, weak)
        s.bodyforce = Ra * self.T.sym[0] * mesh.CoordinateSystem.unit_e_1
        free_slip_walls(s)
        s.add_fault_bc(0, boundary="Trench")
        s.petsc_use_pressure_nullspace = True       # closed box: pressure is free to a constant
        s.tolerance = params.uw_tol
        # Picard (frozen tangent) to newton_switch_rtol, then Newton: the rotated
        # strong-constraint path needs the blended tangent for the Picard steps.
        s.consistent_jacobian = "continuation"
        s.newton_switch_rtol = params.uw_newton_switch
        # The multigrid's coarse levels are the unfaulted base: they cannot represent the
        # slip, the weak bridge or the fine ladder cells. The band patch smoother does that
        # work on the finest level instead.
        set_custom_fmg(s, self.levels, field_id=0, fac_zone=band if params.uw_fac else None)
        self.stokes = s
        self.has_guess = False

        eta_eff = s.constitutive_model.viscosity
        self.eta_projection = uw.systems.Projection(mesh, self.log_eta)
        self.eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
        self.ratio_projection = uw.systems.Projection(mesh, self.yield_ratio)
        self.ratio_projection.uw_function = eta_eff / self.eta_T
        self.diagnostics = BoxDiagnostics(T_b, self.v, eta_eff, self.eta_T, width, params.uw_heating)
        self.t_build = time.perf_counter() - wall
        uw.pprint(f"faulted mesh {tag}: trench at x {x_trench:.3f}, {len(self.trace)} trace points, "
                  f"built in {self.t_build:.1f} s")

    def warm_start(self, V, P=None, shift=0.0):
        """Initial guess from velocity (and pressure, when given) on another mesh.
        ``shift`` is how far the trench has moved since that mesh: each node takes the
        old field at its position shifted back by it, so the old slip lands on the new
        fault rather than a rung or two away from it."""
        def at(var, coords):
            query = np.asarray(coords, dtype=float).copy()
            query[:, 0] = np.clip(query[:, 0] - shift, 0.0, width)
            return np.asarray(uw.function.global_evaluate(var.sym, query))
        self.v.array[:, 0, :] = at(V, self.v.coords).reshape(-1, 2)
        if P is not None:
            self.p.array[:, 0, 0] = at(P, self.p.coords).ravel()
        self.has_guess = True

    def _stokes_solve(self, from_rest):
        self.stokes.solve(zero_init_guess=from_rest, picard=params.uw_picard,
                          verbose=bool(params.uw_verbose))
        return self.stokes._rotated_freeslip_info

    def solve(self):
        self.T.array[:, 0, 0] = np.asarray(uw.function.global_evaluate(T_b.sym[0], self.T.coords)).ravel()
        info = self._stokes_solve(from_rest=not self.has_guess)
        if not info.get("converged") and self.has_guess:
            uw.pprint("  the warm start did not converge: solving from rest")
            self.stokes.newton_switch_rtol = params.uw_newton_switch
            info = self._stokes_solve(from_rest=True)
        # The rotated loop's Picard-to-Newton switch is measured from each solve's own
        # starting residual, so a warm start already near convergence would need the
        # full switch reduction from Picard alone (linear, ~0.85 per iteration). After
        # the first solve the warm starts are inside Newton's basin: switch at once.
        # TODO(DESIGN): rotated_bc.solve_rotated_freeslip tests the switch against r0,
        # its convergence against the cold reference; the switch should follow ref.
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
        """Median surface velocity of the overriding plate, over the window beyond the
        trench (collective: every rank evaluates the same points)."""
        x0 = self.x_trench + params.uw_trench_off
        xs = np.linspace(x0, min(x0 + params.uw_trench_span, width), 41)
        surface = np.column_stack([xs, np.ones_like(xs)])
        vx = np.asarray(uw.function.global_evaluate(self.v.sym[0], surface)).ravel()
        return float(np.median(vx))

    def to_base(self):
        """Velocity, and the render fields, onto the base's nodes (collective)."""
        V_b.array[:, 0, :] = np.asarray(uw.function.global_evaluate(self.v.sym, V_b.coords)).reshape(-1, 2)

    def render_fields_to_base(self):
        self.eta_projection.solve()
        self.ratio_projection.solve()
        log_eta_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.log_eta.sym[0], log_eta_b.coords)).ravel()
        yield_ratio_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.yield_ratio.sym[0], yield_ratio_b.coords)).ravel()


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def checkpoint(step, t, records, faulted):
    faulted.render_fields_to_base()
    base.write_timestep("box", index=step, outputPath=out,
                        meshVars=[V_b, T_b, log_eta_b, yield_ratio_b])
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, f"state_{step:05d}.json"), "w") as f:
                json.dump({"step": step, "t": t, "params": params.to_dict(),
                           "x_trench": x_trench, "trace": faulted.trace.tolist()},
                          f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- initial state
records = []
if params.uw_restart < 0:
    source = os.path.expanduser(params.uw_source)
    for var in (T_b, V_b):
        var.read_timestep("box", var.name, params.uw_source_index, outputPath=source)
    with open(os.path.join(source, f"state_{params.uw_source_index:05d}.json")) as f:
        state = json.load(f)
    # the source's history up to the restart, so the record runs on unbroken
    if os.path.exists(os.path.join(source, "records.json")):
        with open(os.path.join(source, "records.json")) as f:
            records = [r for r in json.load(f) if r["step"] <= params.uw_source_index]
    P_source = None
    if not params.uw_cold_start:
        P_source = uw.discretisation.MeshVariable("P", base, 1, degree=1, continuous=True)
        P_source.read_timestep("box", "P", params.uw_source_index, outputPath=source)
else:
    for var in (T_b, V_b):
        var.read_timestep("box", var.name, params.uw_restart, outputPath=out)
    with open(os.path.join(out, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    with open(os.path.join(out, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]
    P_source = None
t, step = float(state["t"]), int(state["step"]) + 1
x_trench = float(state.get("x_trench", params.uw_trench_x)) if params.uw_restart >= 0 else params.uw_trench_x

n_built = 1
faulted = FaultedMesh(x_trench, "f0")
if not params.uw_cold_start:
    faulted.warm_start(V_b, P_source)

uw.pprint(f"box {width} x 1, Ra {params.uw_ra:.4g}, deta {params.uw_deta:.3g}, tau {params.uw_tau0:.4g} + "
          f"{params.uw_tau1:.4g} z, H {params.uw_heating:.4g}; fault at x {params.uw_trench_x}, dip "
          f"{params.uw_dip} to depth {params.uw_fault_depth}; from t {t:.4f}; output {out}")

# ----------------------------------------------------------------------------- time loop
for k in range(params.uw_steps):
    wall = time.perf_counter()
    if not 0.3 <= x_trench <= width - 0.3 - params.uw_fault_depth / np.tan(np.deg2rad(params.uw_dip)):
        uw.pprint(f"the trench (x {x_trench:.3f}) has reached a wall: stopping")
        checkpoint(step - 1, t, records, faulted)
        break
    if abs(x_trench - faulted.x_trench) > params.uw_rebuild_rungs * S:
        previous = faulted
        faulted = FaultedMesh(x_trench, f"f{n_built}")
        n_built += 1
        # The previous solution, evaluated onto the new mesh, puts the slip a rung out of
        # place near the fault (a point takes whichever side it lands on), so the new
        # solve starts with Picard steps: Newton from there stalls (40 iterations at
        # 0.1 of the reference residual, measured); Picard converges in ~15.
        faulted.warm_start(previous.v, previous.p, shift=faulted.x_trench - previous.x_trench)
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
    t += dt
    v_trench = faulted.overriding_plate_velocity()
    if params.uw_migrate:
        x_trench += v_trench * dt
    record, profile = faulted.diagnostics.record()
    record.update(rec)
    record.update({"x_trench": x_trench, "v_trench": v_trench, "x_built": faulted.x_trench,
                   "n_built": n_built, "t_build": round(faulted.t_build, 1)})
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    records.append(record)
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"q_top {record['q_top']:6.2f} q_base {record['q_base']:6.2f} "
              f"yield {record['yield_frac']:.3f}/{record['yield_frac_lid']:.3f} slip {record['slip_max']:.2f} "
              f"x_t {x_trench:.3f} v_t {v_trench:.1f} | "
              f"newton {record['newton']} vel {record['vel_its']} pres {record['pres_its']} "
              f"{record['t_stokes']:.1f}/{record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == params.uw_steps - 1:
        checkpoint(step, t, records, faulted)
    step += 1

uw.pprint("done")
