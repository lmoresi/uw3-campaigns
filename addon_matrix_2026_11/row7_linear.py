"""Add-on matrix row 7, the UWTN 2026-022 fixture (problem A): does a finer ladder do
physical work, and does refining the base under the fault corridor give the slip
resolution instead? (dev hub, 2026-11-01)

The fixture: unit box, unit viscosity, simple shear v = (y - 1/2, 0) on every wall, a
straight frictionless fault from (0.30, 0.45) to (0.70, 0.55) (length 0.4123). Base:
UnstructuredSimplexBox(cellSize=1/8, refinement=2), so h_b = 1/32. Hierarchy H0 only:
the welded base levels, then the solver mesh, the ladder at S placed in the base (or
in the corridor child) and split, with the FAC LU patch on it. The cover gate is
forced open (UW_FAC_COVER=1.01, #918), so every arm takes the patch.

Two arms:
    depth 0      the ladder at S = L / n_rungs in the base: h_b/S = 1, 2, ... 48
    depth k > 0  the base refined k times (nested NVB, mesh.adapt) in the corridor of
                 half-width rings * h_b around the fault, h = h_b / 2^k there, then the
                 ladder at S in the child; the levels are the base's, one per doubling,
                 then the child, then S

The record carries the slip profile (s from the fault's end at (0.30, 0.45), V the
tangential jump), the velocity on a line across the fault's midpoint, the Newton and
velocity iterations (summed over the second solve's velocity applications, as rows 3-5
report them), the times, the FAC patch's rows and its blocks' set-up and solve
time, and the peak resident memory per rank.

    python row7_linear.py -uw_n_rungs 26 -uw_depth 1 -uw_rings 1 -uw_out records/A7_n26_d1_r1.json
"""
import json
import os
import resource
import sys
import time

import numpy as np
import underworld3 as uw
from petsc4py import PETSc
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import row7_common as rc  # noqa: E402

params = uw.Params(
    uw_n_rungs=26,            # spine intervals at S; L/h_b = 13.19, so 13 is h_b/S 0.99
    uw_depth=0,               # corridor refinement levels (0: the base as it is)
    uw_rings=1,               # corridor half-width in base cells h_b
    uw_tol=1.0e-6,            # Stokes solver tolerance (the note's)
    uw_out="records/A7.json",
)
os.environ.setdefault("UW_FAC_COVER", "1.01")          # the gate forced open (#918)
timer = rc.FacBlockTimer()

FAULT = "Fault"
A, B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
H_B = 1.0 / 32
n = int(params.uw_n_rungs)
L = float(np.linalg.norm(B - A))
T_HAT = (B - A) / L
S = L / n
trace = A + (np.arange(n + 1) * S)[:, None] * T_HAT
depth, rings = int(params.uw_depth), float(params.uw_rings)

wall = time.perf_counter()
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 8,
                                         regular=False, qdegree=2, refinement=2)
host = rc.corridor_child(base, np.array([A, B]), H_B, rings, depth)
levels = list(host.multigrid_levels)            # base 1/8, 1/16, 1/32 [, corridor levels]
t_base = time.perf_counter() - wall
h_corridor = rc.cell_sizes_near(host, np.array([A, B]), 0.5 * H_B)
h_local = H_B / 2 ** depth


def ladder(host_mesh):
    """The ladder at S placed in ``host_mesh``, 2S wide, split."""
    for clearance in (0.7, 0.5):
        try:
            return place_fault_ribbon_2d(host_mesh, [(FAULT, trace)], 2 * S, margin_rings=1,
                                         clearance=clearance, split=True, mesher="ladder")[0]
        except RuntimeError as err:
            last = err
    raise last


wall = time.perf_counter()
mesh = ladder(host)
t_place = time.perf_counter() - wall

x, y = mesh.X
v = uw.discretisation.MeshVariable("v", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("p", mesh, 1, degree=1, continuous=True)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = [0.0, 0.0]
for wall_name in ("Bottom", "Top", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), wall_name)
stokes.add_fault_bc(0, boundary=FAULT)
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = float(params.uw_tol)

wall = time.perf_counter()
set_custom_fmg(stokes, levels, field_id=0)
t_fmg = time.perf_counter() - wall

wall = time.perf_counter()
stokes.solve()
t_solve = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
block_first = timer.record()

ctx = (getattr(stokes, "_rotated_linear_cache", None) or {}).get("ctx")

# the same solve again from zero on the cached operators: the solve alone, with every
# application of the velocity sub-KSP counted (rows 3-5 and the probes report this sum)
work = {"applications": 0, "iterations": 0}


def count_velocity_work(_ksp, its, _rnorm):
    if its == 0:
        work["applications"] += 1
    else:
        work["iterations"] += 1


if ctx is not None:
    ctx["pc"].getFieldSplitSubKSP()[0].setMonitor(count_velocity_work)
timer.reset()
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_solve_again = time.perf_counter() - wall
info2 = stokes._rotated_freeslip_info
block_again = timer.record()

profile = rc.slip_profile(stokes, FAULT, info2, A, T_HAT)

# the velocity on the line through the fault's midpoint along its normal, offset so
# that no sample lies on the fault (a coincident pair has two values there)
mid = 0.5 * (A + B)
N_HAT = np.array([-T_HAT[1], T_HAT[0]])
offsets = np.linspace(-0.2, 0.2, 200)
line = mid + offsets[:, None] * N_HAT
v_line = np.asarray(uw.function.global_evaluate(v.sym, line)).reshape(-1, 2)

level_ops, smoothers = [], []
if ctx is not None:
    velpc = ctx["ksp"].getPC().getFieldSplitSubKSP()[0].getPC()
    if velpc.getType() == "mg":
        smoothers = rc.level_smoothers(velpc)
        level_ops = rc.level_operators(velpc)

# the cover gate's verdict on the finest level (None: declined)
_h = (getattr(stokes, "_custom_mg", None) or {}).get("hierarchy")
_pr = getattr(_h, "level_patch_rows", None)
_last = _pr[-1] if _pr else None
gate = {"cover_max": float(os.environ.get("UW_FAC_COVER", 0.75)),
        "taken": any(uw.mpi.comm.allgather(_last is not None)),
        "level_rows": level_ops[-1]["rows"] if level_ops else None}
_patch = rc.patch_rows_global(_last)       # one collective on every rank
if _patch["taken"]:
    gate["patch_owned_rows"] = _patch["patch_owned_rows"]
    gate["subdomain_rows"] = _patch["subdomain_rows"]

V = np.asarray(profile["V"])
s_prof = np.asarray(profile["s"])
record = {
    "problem": "A (linear, the UWTN 2026-022 fixture)", "row": 7, "hierarchy": "H0",
    "n_rungs": n, "S": S, "h_b": H_B, "h_b_over_S": H_B / S,
    "depth": depth, "rings": rings, "corridor_half_width": rings * H_B if depth else 0.0,
    "h_local": h_local, "h_local_over_S": h_local / S, "h_corridor_realised": h_corridor,
    "level_cells": [rc.n_cells(m) for m in levels] + [rc.n_cells(mesh)],
    "level_ops_velocity": level_ops, "level_smoothers": smoothers,
    "mg_env": {k: val for k, val in os.environ.items() if k.startswith(("UW_FAC", "UW_CUSTOM_MG", "UW_MG"))},
    "fac_gate": gate,
    "fac_blocks_first": block_first,          # the first solve: set-up (LU) and solve
    "fac_blocks_again": block_again,          # the second solve: block solves only
    "tolerance": float(params.uw_tol),
    "converged": bool(info.get("converged")),
    "newton_iterations": info.get("nonlinear_iterations"),
    "outer_its": info.get("ksp_its"),
    "vel_its_last": info.get("vel_its_last"), "pres_its_last": info.get("pres_its_last"),
    "vel_applications_again": work["applications"],
    "vel_its_all_applications_again": work["iterations"],
    "peak_slip": float(np.abs(V).max()) if len(V) else 0.0,
    "slip_integral": float(np.trapezoid(V, s_prof)) if len(V) > 1 else 0.0,
    "leak_max": profile["leak_max"],
    "slip_profile": profile,
    "velocity_across_mid": {"offset": [float(o) for o in offsets],
                            "v_t": [float(x) for x in v_line @ T_HAT],
                            "v_n": [float(x) for x in v_line @ N_HAT]},
    "t_base_s": round(t_base, 2), "t_place_s": round(t_place, 2), "t_fmg_s": round(t_fmg, 2),
    "t_solve_first_s": round(t_solve, 2), "t_solve_again_s": round(t_solve_again, 2),
    "np": uw.mpi.size,
    # ru_maxrss is bytes on macOS (kilobytes on Linux)
    "peak_rss_raw_per_rank": uw.mpi.comm.allgather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    "rss_unit": "bytes" if sys.platform == "darwin" else "kB",
    "petsc": ".".join(str(i) for i in PETSc.Sys.getVersion()),
}
uw.pprint("RECORD " + json.dumps({k: val for k, val in record.items()
                                  if k not in ("slip_profile", "velocity_across_mid")}))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
