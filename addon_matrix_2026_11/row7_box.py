"""Add-on matrix row 7, the yielding-lid box (problem B of the UWTN 2026-022 tail sweep):
does a finer ladder do physical work, and does refining the base under the fault
corridor give the slip resolution instead? (dev hub, 2026-11-01)

The box, its state and its solver are tail_sweep_box.py's (row4_interface_laws.py with
the frictionless fault): a 4 x 1 box, viscoplastic lid, free-slip walls, the fault
dipping 45 degrees from the trench at x 2.0 to depth 0.35; the guide's hard state
(checkpoint 2000), one Stokes solve from rest. Base: box_mesh(4, 0.125, refinement 2),
so h_b = 1/32; today's S is 0.004 (h_b/S 7.9). Hierarchy H0 only: the welded base
levels, then the ladder at S, split, with the FAC LU patch on it; the cover gate is
forced open (UW_FAC_COVER=1.01, #918).

The split starts below the bridge: the fixture puts the split's upper tip three rung
spacings under the surface, so the tip depth and the weak bridge move with S. Row 7
holds them physical by default: ``uw_tip`` a depth (0.012, today's 3 x 0.004) puts the
tip at the first spine point at least that deep, at every S; ``uw_tip 3S`` keeps the
fixture's rule. ``uw_tip 1el`` (or ``2el``, ...) is Louis's inset (2026-11-02, relayed:
"One element ... if it works. I am not sure about units. 1 is normalised by the element
size."): the tip at the first spine point at least k local elements down dip from where
the fault meets the surface. The local element is the band cell, a rung spacing S
along the fault. Every arm records the inset it got, measured on the placed mesh in
rung spacings, down dip and in depth (``tip_topology``), the top pair's frame normal
against the fault's, and the pairs next to the tip with their slip. ``-uw_mesh_only 1`` stops after
the placement with that record. The bridge is the band cells above the tip, as in the
fixture, so it is 2S wide: a weak zone cannot be narrower than the band it lives in.

    depth 0      the ladder at S in the base
    depth k > 0  RETIRED (Louis 2026-11-03: no node-adding adaptation of the base;
                 it breaks the FMG hierarchy); corridor_child refuses it

The record carries the slip profile (s down dip from the surface, V the tangential
jump), the surface velocity, the vertical velocity at depth 0.05, the Newton and
velocity iterations (each velocity application's count is in the log,
'Linear rotfsN_fieldsplit_vel_ solve ...'; collect_row7.py sums them), the times, the
FAC patch's rows and its blocks' set-up and solve time, and the peak resident memory
per rank.

    mpirun -np 4 python row7_box.py -uw_spacing 0.03125 -uw_out records/B7_s0.03125_d0.json
"""
import json
import os
import resource
import sys
import time

import numpy as np
import sympy
import underworld3 as uw
from petsc4py import PETSc
from underworld3.utilities import rotated_bc
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.place_surface import place_fault_ribbon_2d

HERE = os.path.dirname(os.path.abspath(__file__))
params = uw.Params(
    uw_drivers=os.path.join(HERE, "..", "zg95_lid_regimes", "drivers"),   # box_model.py
    uw_run=os.path.join(HERE, "data", "box_state_02000"),
    uw_index=2000,            # the guide's hard state
    uw_spacing=0.004,         # rung spacing S requested (today's 0.004)
    uw_depth=0,               # corridor refinement levels (0: the base as it is)
    uw_rings=1,               # corridor half-width in base cells h_b
    uw_tip="0.012",           # the split's upper tip depth, "3S" (the fixture's rule) or "1el" (k elements)
    uw_mesh_only=0,           # 1: stop after the placement, with the tip record
    uw_tip_exact=0,           # 1: sample the spine at S from the tip, so the tip is at the asked depth
    uw_bridge_width=0.0,      # > 0: the weak bridge a smooth zone this wide (physical), not 2S of band cells
    uw_max_it=200,            # the rotated loop's cap (its default 50; #920)
    uw_out="records/B7.json",
)
sys.path.insert(0, os.path.expanduser(params.uw_drivers))
from box_model import box_mesh, free_slip_walls, set_viscoplastic  # noqa: E402

sys.path.insert(0, HERE)
import row7_common as rc  # noqa: E402

os.environ.setdefault("UW_FAC_COVER", "1.01")          # the gate forced open (#918)
timer = rc.FacBlockTimer()

run = os.path.expanduser(params.uw_run)
with open(os.path.join(run, f"state_{params.uw_index:05d}.json")) as f:
    state = json.load(f)
p = state["params"]
H_B = float(p["uw_cell"]) / 2 ** int(p["uw_refinement"])
depth, rings = int(params.uw_depth), float(params.uw_rings)

# the fault: spine from just above the surface down past the tip
dip = np.deg2rad(float(p["uw_dip"]))
down_dip = np.array([np.cos(dip), -np.sin(dip)])
x_t = float(p["uw_trench_x"])
top = np.array([x_t, 1.02])
length = (float(p["uw_fault_depth"]) + 0.02) / np.sin(dip)
surface_point = top + down_dip * (0.02 / np.sin(dip))   # where the spine meets y = 1


def depth_for(spacing):
    """The smallest j with h_b / (2^j S) <= 4 (the sweep's spine-count rule)."""
    j = 1
    while H_B / (2 ** j * spacing) > 4.0:
        j += 1
    return j


# the sweep's spine count (a multiple of max(4, 2^J)), so S 0.004 is its 132 intervals
block = max(4, 2 ** depth_for(float(params.uw_spacing)))
n_fine = block * max(1, int(round(length / (block * float(params.uw_spacing)))))
S = length / n_fine
spine = np.array([top + down_dip * (length * i / n_fine) for i in range(n_fine + 1)])
tip_rule = str(params.uw_tip)
n_fault = np.array([np.sin(dip), np.cos(dip)])          # the fault's unit normal
if tip_rule.endswith("el"):
    # k local elements (rung spacings) down dip from the surface crossing
    inset_asked = float(tip_rule[:-2])
    trace = spine[(spine - surface_point) @ down_dip >= inset_asked * S - 1e-12]
    tip_depth_asked = None
else:
    inset_asked = None
    tip_depth_asked = 3.0 * S if tip_rule == "3S" else float(tip_rule)
    trace = spine[spine[:, 1] <= 1.0 - tip_depth_asked]
if int(params.uw_tip_exact):
    # the spine sampled at S from the tip itself, up past y = 1.02 and down to the
    # fault's depth, so the tip is at the asked depth at every S (the fixture samples
    # from y = 1.02 down, and its tip is the first spine point below the depth)
    if tip_depth_asked is None:
        raise ValueError("-uw_tip_exact needs a tip depth or 3S, not an element inset")
    tip_point = surface_point + down_dip * (tip_depth_asked / np.sin(dip))
    k_up = int(np.ceil((1.02 - tip_point[1]) / np.sin(dip) / S))
    k_down = max(1, int(round((float(p["uw_fault_depth"]) - tip_depth_asked) / np.sin(dip) / S)))
    spine = tip_point + (np.arange(-k_up, k_down + 1) * S)[:, None] * down_dip
    trace = spine[k_up:]
    n_fine = len(spine) - 1

wall = time.perf_counter()
base = box_mesh(p["uw_width"], p["uw_cell"], p["uw_refinement"])
T_b = uw.discretisation.MeshVariable("T", base, 1, degree=2)
T_b.read_timestep("box", "T", params.uw_index, outputPath=run)
corridor = np.array([surface_point, spine[-1]])
host = rc.corridor_child(base, corridor, H_B, rings, depth)
levels = list(host.multigrid_levels)            # base 1/8, 1/16, 1/32 [, corridor levels]
t_base = time.perf_counter() - wall
h_corridor = rc.cell_sizes_near(host, corridor, 0.5 * H_B)
h_local = H_B / 2 ** depth

wall = time.perf_counter()
mesh, _info = place_fault_ribbon_2d(host, [("Trench", trace)], 2 * S, spines=[("Trench", spine)],
                                    margin_rings=1, clearance=0.7, split=True, mesher="ladder")
t_place = time.perf_counter() - wall
tip = rc.tip_topology(mesh, "Trench", surface_point, down_dip, n_fault, S)
uw.pprint(f"TIP rule {tip_rule} S {S:.6f}: " + json.dumps(tip))
if int(params.uw_mesh_only):
    with uw.selective_ranks(0) as selected:
        if selected:
            out = os.path.expanduser(params.uw_out)
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "w") as f:
                json.dump({"problem": "B (mesh only)", "S": S, "h_b": H_B, "h_b_over_S": H_B / S,
                           "tip_rule": tip_rule, "inset_asked_elements": inset_asked,
                           "tip_depth_asked": tip_depth_asked, "tip": tip,
                           "level_cells": [rc.n_cells(m) for m in levels] + [rc.n_cells(mesh)],
                           "t_place_s": round(t_place, 2)}, f, indent=1)
    sys.exit(0)

T = uw.discretisation.MeshVariable("Tp", mesh, 1, degree=2)
v = uw.discretisation.MeshVariable("Vp", mesh, 2, degree=2)
pr = uw.discretisation.MeshVariable("Pp", mesh, 1, degree=1, continuous=True)
zone = uw.discretisation.MeshVariable("zone_p", mesh, 1, degree=0, continuous=False)
T.array[:, 0, 0] = np.asarray(uw.function.global_evaluate(T_b.sym[0], T.coords)).ravel()

# the weak bridge: cells within a band half-width of the spine between the split's
# upper tip and the surface (the fixture's definition)
c = np.asarray(zone.coords)
a, b = np.array([x_t, 1.0]), trace[0]
ab = b - a
s = np.clip(((c - a) @ ab) / (ab @ ab), 0.0, 1.0)
d = np.linalg.norm(c - (a + s[:, None] * ab), axis=1)
bridge = (d < S) & (c[:, 1] > trace[0, 1] - S)
bridge_width = float(params.uw_bridge_width)
s_tip = float((trace[0] - surface_point) @ down_dip)
if bridge_width > 0:
    # a smooth zone of physical width w across the fault (a super-Gaussian in the
    # distance from it) from the surface down to the tip (a tanh of width w/4 along
    # it), sampled at the quadrature points, so its width does not follow S
    xs, ys = mesh.X
    along = (xs - surface_point[0]) * down_dip[0] + (ys - surface_point[1]) * down_dip[1]
    across = (xs - surface_point[0]) * n_fault[0] + (ys - surface_point[1]) * n_fault[1]
    chi = (sympy.exp(-(2 * across / bridge_width) ** 6)
           * (1 + sympy.tanh((s_tip - along) / (bridge_width / 4))) / 2)
    cc = c - surface_point
    chi_c = (np.exp(-(2 * (cc @ n_fault) / bridge_width) ** 6)
             * (1 + np.tanh((s_tip - cc @ down_dip) / (bridge_width / 4))) / 2)
    bridge = chi_c > 0.5
    zone.array[:, 0, 0] = chi_c
else:
    chi = None
    zone.array[:, 0, 0] = bridge.astype(float)

stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=pr)
weak = 1 - (1 - float(p["uw_eta_w"])) * (zone.sym[0] if chi is None else chi)
set_viscoplastic(stokes, T.sym[0], float(p["uw_deta"]), float(p["uw_tau0"]), float(p["uw_tau1"]),
                 float(p["uw_yield_softness"]), weak)
stokes.constitutive_model.Parameters.yield_stress_min = -sympy.oo
stokes.bodyforce = float(p["uw_ra"]) * T.sym[0] * mesh.CoordinateSystem.unit_e_1
free_slip_walls(stokes)
stokes.add_fault_bc(0, boundary="Trench")
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = float(p["uw_tol"])
stokes.consistent_jacobian = "continuation"
stokes.newton_switch_rtol = 1e-2
set_custom_fmg(stokes, levels, field_id=0)

# every application of the velocity sub-KSP prints its converged reason and count
opts = PETSc.Options()
n0 = rotated_bc._ROT_SOLVE_COUNT
for i in range(1, 4):
    opts[f"rotfs{n0 + i}_fieldsplit_vel_ksp_converged_reason"] = None

if int(params.uw_max_it) != 50:
    _rotated_capped = rotated_bc.solve_rotated_freeslip
    rotated_bc.solve_rotated_freeslip = lambda *a, **k: _rotated_capped(
        *a, **{**k, "max_it": int(params.uw_max_it)})

wall = time.perf_counter()
stokes.solve(zero_init_guess=True, picard=0, verbose=True)
t_solve = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
blocks = timer.record()

profile = rc.slip_profile(stokes, "Trench", info, surface_point, down_dip)
near_tip = rc.top_pairs(stokes, "Trench", info, surface_point, down_dip, n_fault)

# the surface velocity at the top nodes, and the vertical velocity at depth 0.05
vc = np.asarray(v.coords)
on_top = vc[:, 1] > 1.0 - 1e-9
xs = np.concatenate(uw.mpi.comm.allgather(vc[on_top, 0]))
vxs = np.concatenate(uw.mpi.comm.allgather(np.asarray(v.array)[on_top, 0, 0]))
xs_key, first = np.unique(np.round(xs, 9), return_index=True)
x_line = np.linspace(0.005, 3.995, 400)
vy_line = np.asarray(uw.function.global_evaluate(
    v.sym[1], np.column_stack([x_line, np.full_like(x_line, 0.95)]))).ravel()

ctx = (getattr(stokes, "_rotated_linear_cache", None) or {}).get("ctx")
level_ops, smoothers = [], []
if ctx is not None:
    velpc = ctx["pc"].getFieldSplitSubKSP()[0].getPC()
    if velpc.getType() == "mg":
        smoothers = rc.level_smoothers(velpc)
        level_ops = rc.level_operators(velpc)

vel = [int(x) for x in info.get("vel_its_last") or []]
V = np.asarray(profile["V"])
s_prof = np.asarray(profile["s"])
record = {
    "problem": "B (yielding-lid box, the guide's hard state)", "row": 7, "hierarchy": "H0",
    "state": f"{run} index {params.uw_index}",
    "spacing_requested": float(params.uw_spacing), "S": S, "spine_intervals": n_fine,
    "h_b": H_B, "h_b_over_S": H_B / S,
    "depth": depth, "rings": rings, "corridor_half_width": rings * H_B if depth else 0.0,
    "h_local": h_local, "h_local_over_S": h_local / S, "h_corridor_realised": h_corridor,
    "tip_rule": tip_rule, "tip_depth_asked": tip_depth_asked, "inset_asked_elements": inset_asked,
    "tip": tip, "pairs_near_tip": near_tip, "tip_exact": int(params.uw_tip_exact),
    "bridge": {"rule": "smooth" if bridge_width > 0 else "band cells (2S)",
               "width": bridge_width if bridge_width > 0 else 2 * S, "length_down_dip": s_tip},
    "tip_depth": float(1.0 - trace[0, 1]), "trace_points": int(len(trace)),
    "bridge_cells": int(uw.mpi.comm.allreduce(int(bridge.sum()))),
    "level_cells": [rc.n_cells(m) for m in levels] + [rc.n_cells(mesh)],
    "level_ops_velocity": level_ops, "level_smoothers": smoothers,
    "mg_env": {k: val for k, val in os.environ.items() if k.startswith(("UW_FAC", "UW_CUSTOM_MG", "UW_MG"))},
    "fac_blocks": blocks,
    "tolerance": float(p["uw_tol"]), "max_it": int(params.uw_max_it),
    "converged": bool(info.get("converged")),
    "newton_iterations": info.get("nonlinear_iterations"),
    "continuation_switch_iteration": info.get("continuation_switch_iteration"),
    "outer_its": info.get("ksp_its"),
    "vel_its_last": vel, "vel_its_last_total": int(sum(vel)),
    "pres_its_last": info.get("pres_its_last"),
    "peak_slip": float(np.abs(V).max()) if len(V) else 0.0,
    "slip_integral": float(np.trapezoid(V, s_prof)) if len(V) > 1 else 0.0,
    "leak_max": profile["leak_max"],
    "slip_profile": profile,
    "surface_vx": {"x": [float(x) for x in xs[first]], "vx": [float(x) for x in vxs[first]]},
    "vy_at_depth_0.05": {"x": [float(x) for x in x_line], "vy": [float(x) for x in vy_line]},
    "t_base_s": round(t_base, 2), "t_place_s": round(t_place, 2), "t_solve_s": round(t_solve, 2),
    "np": uw.mpi.size,
    "rnorm_rel_history": [round(float(x) / float(info.get("ref") or 1.0), 6)
                          for x in (info.get("rnorm_history") or [])],
    # ru_maxrss is bytes on macOS (kilobytes on Linux)
    "peak_rss_raw_per_rank": uw.mpi.comm.allgather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    "rss_unit": "bytes" if sys.platform == "darwin" else "kB",
    "petsc": ".".join(str(i) for i in PETSc.Sys.getVersion()),
}
uw.pprint("RECORD " + json.dumps({k: val for k, val in record.items()
                                  if k not in ("slip_profile", "surface_vx", "vy_at_depth_0.05")}))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
