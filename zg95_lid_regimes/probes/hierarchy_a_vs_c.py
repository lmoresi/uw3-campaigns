"""Hierarchy A (welded coarse levels, the ladder on a copy of the base's finest) against
hierarchy C (an adapt-built add-on, every add-on level split by add_fault) on the
same hard state: the fixed-trench fault run's checkpoint 2000 (t 0.2316, M 0.70).

Same rheology, walls, fault and weak bridge in both; one Stokes solve each from rest.
Prints nonlinear iterations, velocity and pressure iterations per increment, and time.

    mpirun -np 4 python hierarchy_a_vs_c.py -uw_arm C
"""
import json
import os
import sys
import time

import numpy as np
import sympy
import underworld3 as uw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
from box_model import box_mesh, free_slip_walls, set_viscoplastic

params = uw.Params(
    uw_arm="L",                 # "A" (welded FMG), "G" (A's mesh, GAMG), "L" (split ladder chain) or "C"
    uw_run="~/+Simulations/zg95/box_faults/runs/stagnant_tau1x1.00_fault_x2.0_dip45",
    uw_index=2000,
    uw_levels=3,                # adapt depth for C (near-fault h = base finest / 2**levels)
    uw_lean_width=1,            # M arm: band width 2 x each level's own spacing (0: 2S on every level)
)
run = os.path.expanduser(params.uw_run)
with open(os.path.join(run, f"state_{params.uw_index:05d}.json")) as f:
    state = json.load(f)
p = state["params"]
S = float(p["uw_spacing"])
W = 2 * S

base = box_mesh(p["uw_width"], p["uw_cell"], p["uw_refinement"])
T_b = uw.discretisation.MeshVariable("T", base, 1, degree=2)
T_b.read_timestep("box", "T", params.uw_index, outputPath=run)

dip = np.deg2rad(float(p["uw_dip"]))
down_dip = np.array([np.cos(dip), -np.sin(dip)])
x_t = float(p["uw_trench_x"])
top = np.array([x_t, 1.02])
length = (float(p["uw_fault_depth"]) + 0.02) / np.sin(dip)
n = int(round(length / S))
spine = np.array([top + down_dip * (length * i / n) for i in range(n + 1)])
trace = spine[spine[:, 1] <= 1.0 - 3.0 * S]

wall = time.perf_counter()
if params.uw_arm in ("A", "G"):
    from underworld3.utilities.custom_mg import set_custom_fmg
    from underworld3.utilities.place_surface import place_fault_ribbon_2d
    mesh, info = place_fault_ribbon_2d(base, [("Trench", trace)], W, spines=[("Trench", spine)],
                                       margin_rings=1, clearance=0.7, split=True, mesher="ladder")
    levels = base._coarse_level_meshes()[:-1] + [base]
elif params.uw_arm == "L":
    # C on the ladder: the same band (width W) placed on the static base at nested
    # 2:1 rung spacings 4S, 2S, S, each split along its own rungs; the coarser two
    # are the mid levels between the welded base and the finest.
    from underworld3.utilities.custom_mg import set_custom_fmg
    from underworld3.utilities.place_surface import place_fault_ribbon_2d
    n_fine = 4 * int(round(length / (4 * S)))
    fine_spine = np.array([top + down_dip * (length * i / n_fine) for i in range(n_fine + 1)])
    chain = []
    for k in (2, 1, 0):
        sp = fine_spine[::2 ** k]
        tr = sp[sp[:, 1] <= 1.0 - 3.0 * S]
        m, _inf = place_fault_ribbon_2d(base, [("Trench", tr)], W, spines=[("Trench", sp)],
                                        margin_rings=1, clearance=0.7, split=True, mesher="ladder")
        chain.append((m, tr))
    mesh, trace = chain[-1]
    levels = base._coarse_level_meshes()[:-1] + [base] + [m for m, _ in chain[:-1]]
    n_cells_levels = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                      for m in levels + [mesh]]
    uw.pprint(f"L: levels (cells) {n_cells_levels}")
elif params.uw_arm == "M":
    # The LEAN chain: each coarser ladder on the matching coarser base level, so the
    # mid levels are coarse (4S on the base's middle level, 2S on its finest), the
    # finest ladder (S) on the base's finest; the coarsest base level stays welded.
    from underworld3.utilities.custom_mg import set_custom_fmg
    from underworld3.utilities.place_surface import place_fault_ribbon_2d
    n_fine = 4 * int(round(length / (4 * S)))
    fine_spine = np.array([top + down_dip * (length * i / n_fine) for i in range(n_fine + 1)])
    base_levels = base._coarse_level_meshes()[:-1] + [base]
    chain = []
    for k, host in ((2, base_levels[1]), (1, base_levels[2]), (0, base_levels[2])):
        sp = fine_spine[::2 ** k]
        tr = sp[sp[:, 1] <= 1.0 - 3.0 * S]
        width = 2 * S * 2 ** k if params.uw_lean_width else W
        m, _inf = place_fault_ribbon_2d(host, [("Trench", tr)], width, spines=[("Trench", sp)],
                                        margin_rings=1, clearance=0.7, split=True, mesher="ladder")
        chain.append((m, tr))
    mesh, trace = chain[-1]
    levels = base_levels[:1] + [m for m, _ in chain[:-1]]
    n_cells_levels = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                      for m in levels + [mesh]]
    uw.pprint(f"M: levels (cells) {n_cells_levels}")
else:
    fault = uw.meshing.Surface("fault_probe", base, np.c_[trace, np.zeros(len(trace))], symbol="F")
    fault.discretize()
    h_finest = float(p["uw_cell"]) / 2 ** int(p["uw_refinement"])
    metric = fault.refinement_metric_function(h_near=h_finest / 2 ** params.uw_levels,
                                              h_far=1.5 * h_finest, width=4 * S, profile="linear")
    child = base.adapt(metric, max_levels=params.uw_levels)
    mesh = child.add_fault(("Trench", trace))
    tail = getattr(mesh, "_custom_mg_coarse_meshes", None) or []
    n_split = sum(bool(getattr(m, "_fault_point_pairs", None)) for m in tail)
    uw.pprint(f"C: tail of {len(tail)} levels, {n_split} split")
t_mesh = time.perf_counter() - wall

T = uw.discretisation.MeshVariable("Tp", mesh, 1, degree=2)
v = uw.discretisation.MeshVariable("Vp", mesh, 2, degree=2)
pr = uw.discretisation.MeshVariable("Pp", mesh, 1, degree=1, continuous=True)
zone = uw.discretisation.MeshVariable("zone_p", mesh, 1, degree=0, continuous=False)
T.array[:, 0, 0] = np.asarray(uw.function.global_evaluate(T_b.sym[0], T.coords)).ravel()

# The weak bridge: cells within a band half-width of the spine between the split's
# upper tip and the surface (the ladder arm's cap region, by distance).
c = np.asarray(zone.coords)
a, b = np.array([x_t, 1.0]), trace[0]
ab = b - a
s = np.clip(((c - a) @ ab) / (ab @ ab), 0.0, 1.0)
d = np.linalg.norm(c - (a + s[:, None] * ab), axis=1)
zone.array[:, 0, 0] = ((d < S) & (c[:, 1] > trace[0, 1] - 0.5 * W)).astype(float)

stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=pr)
weak = 1 - (1 - float(p["uw_eta_w"])) * zone.sym[0]
set_viscoplastic(stokes, T.sym[0], float(p["uw_deta"]), float(p["uw_tau0"]), float(p["uw_tau1"]),
                 float(p["uw_yield_softness"]), weak)
stokes.bodyforce = float(p["uw_ra"]) * T.sym[0] * mesh.CoordinateSystem.unit_e_1
free_slip_walls(stokes)
stokes.add_fault_bc(0, boundary="Trench")
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = float(p["uw_tol"])
stokes.consistent_jacobian = "continuation"
stokes.newton_switch_rtol = 1e-2
if params.uw_arm in ("A", "L", "M"):
    set_custom_fmg(stokes, levels, field_id=0)
elif params.uw_arm == "G":
    stokes.preconditioner = "gamg"

wall = time.perf_counter()
stokes.solve(zero_init_guess=True, picard=0, verbose=True)
t_solve = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
n_cells = int(uw.utilities.gather_data(mesh.dm.getHeightStratum(0)[1], bcast=True).sum())
uw.pprint(f"arm {params.uw_arm}: {n_cells} cells, mesh {t_mesh:.1f} s, solve {t_solve:.1f} s, "
          f"converged {info.get('converged')}, nonlinear {info.get('nonlinear_iterations')}\n"
          f"  vel {info.get('vel_its_last')}\n  pres {info.get('pres_its_last')}", clean_display=False)
