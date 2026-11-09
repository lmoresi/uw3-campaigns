"""#895 stage 1: the FAC patch as ONE structural block (#934, development's default) against
PER-RANK pieces, in parallel, with qmd ordering (#1022) on both.

The UWTN 2026-022 problem A box (unit box, unit viscosity, simple shear v = (y - 1/2, 0)
on every wall, base UnstructuredSimplexBox(cellSize=1/8, refinement=2), h_b = 1/32),
H0 hierarchy (the welded base levels, then the split S level with the structural LU
patch). Cases:

    apart     two equal faults far apart, (0.08, 0.20)-(0.48, 0.30) and
              (0.52, 0.70)-(0.92, 0.80), each the main fault's length: placed per fault
              (partition_addon gives each region to its own majority rank), so at np >= 2
              they can sit on DIFFERENT ranks, and one block then puts one rank in charge of
              both faults' rows
    single    the UWTN 2026-022 linear fixture's one fault (the baseline; one rank either way)
    pair      the row-5 pair: the main fault (0.30, 0.45)-(0.70, 0.55) and a parallel
              one 0.08 below it (likely one rank)
    junction  the row-5 stop-short junction (gap uw_gap S)

Arms (uw_blocks):

    one       development: _gathered_patch_blocks cuts the structural patch into ONE block,
              sent to the rank owning most of its rows
    per_rank  each rank's own structural rows and halo as its block (the pre-#934 cut), no
              coarse space: the control

The record: band cells per rank (is the fixture what it claims?), the ASM block rows per
rank, MatLUFactorNum flops and time per rank, MatLUFactorSym and MatSolve time per rank,
peak RSS per rank, set-up and solve times, velocity iterations, and each fault's slip
(gathered, sorted by along-fault coordinate) to compare arms.

    mpirun -np 4 python stage1_blocks.py -uw_case apart -uw_blocks one -uw_out records/x.json
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
from underworld3.utilities import custom_mg
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

PETSc.Log.begin()
params = uw.Params(
    uw_case="apart",          # apart, pair, junction or single
    uw_blocks="one",          # one (development) or per_rank (the control)
    uw_hier="H0",             # H0 or H1
    uw_n_rungs=320,           # main-fault intervals at S (h_b / S = 24 at 320)
    uw_zone="none",           # ti case: none, ti or both
    uw_gap=8,                 # junction case: the stop-short gap in S
    uw_tol=1.0e-6,
    uw_out="records/stage1.json",
)
case, hier, zone_key = params.uw_case, params.uw_hier, params.uw_zone
A, B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
L = float(np.linalg.norm(B - A))
n = int(params.uw_n_rungs)
assert n % 8 == 0
S = L / n
t_hat = (B - A) / L
n_hat = np.array([t_hat[1], -t_hat[0]])          # the main fault's normal, pointing down


def sampled(P, Q):
    """P to Q at about S, the interval count a multiple of 4."""
    m = max(4, 4 * int(round(np.linalg.norm(Q - P) / (4 * S))))
    return P + np.linspace(0.0, 1.0, m + 1)[:, None] * (Q - P)


main = A + (np.arange(n + 1) * S)[:, None] * t_hat
second = None
if case == "single":
    pass
elif case == "junction":
    P0, M = np.array([0.45, 0.20]), 0.5 * (A + B)
    d = M - P0
    # stop where the branch is uw_gap S from the main trace (distance along n_hat)
    s_stop = 1.0 - float(params.uw_gap) * S / abs(d @ n_hat)
    second = ("Branch", sampled(P0, P0 + s_stop * d))
elif case == "pair":
    second = ("Second", sampled(A + 0.08 * n_hat, B + 0.08 * n_hat))
elif case == "apart":
    shift_1, shift_2 = np.array([-0.22, -0.25]), np.array([0.22, 0.25])
    main = main + shift_1
    second = ("Second", A + shift_2 + (np.arange(n + 1) * S)[:, None] * t_hat)
else:
    raise ValueError(case)
spines = [("Fault", main)] + ([second] if second else [])
cut = spines

wall = time.perf_counter()
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 8,
                                         regular=False, qdegree=2, refinement=2)
base_levels = base._coarse_level_meshes()[:-1] + [base]
t_base = time.perf_counter() - wall


def ladder(host, k):
    """Every strand's ladder at 2^k S (every 2^k-th point), 2^(k+1) S wide, in host."""
    c = 2 ** k
    sp = [(lab, P[::c]) for lab, P in spines]
    tr = [(lab, P[::c]) for lab, P in cut]
    last = None
    for clearance in (0.7, 0.5):
        try:
            return place_fault_ribbon_2d(host, tr, 2 * S * c, spines=sp, margin_rings=1,
                                         clearance=clearance, split=True, mesher="ladder")[0]
        except RuntimeError as err:
            last = err
    raise last


wall = time.perf_counter()
if hier == "H0":
    levels = list(base_levels)
elif hier == "H1":
    levels = base_levels[:-2] + [ladder(base_levels[-2], 2), ladder(base_levels[-1], 1)]
else:
    raise ValueError(hier)
mesh = ladder(base, 0)
t_place = time.perf_counter() - wall

x, y = mesh.X
v = uw.discretisation.MeshVariable("v", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("p", mesh, 1, degree=1, continuous=True)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
band_main = np.asarray(mesh.cells_labelled("Band", 71), dtype=bool)
band_second = np.asarray(mesh.cells_labelled("Band", 72), dtype=bool)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = [0.0, 0.0]
for wall_name in ("Bottom", "Top", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), wall_name)
for lab, _P in cut:
    stokes.add_fault_bc(0, boundary=lab)
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = float(params.uw_tol)

fac_zone = None
blocks_arm = params.uw_blocks
_one_block = custom_mg._gathered_patch_blocks


def _per_rank_blocks(zones, structural, max_rows, rstart, comm):
    """The control: each rank's own structural rows and halo as its block, as before
    #934 (the same branch on every rank: no zone is keyed here)."""
    if zones:
        return _one_block(zones, structural, max_rows, rstart, comm)
    if structural is None or len(structural[0]) == 0:
        return []
    owned, sub = structural
    return [(np.asarray(owned, dtype=np.int64), np.asarray(sub, dtype=np.int64))]


if blocks_arm == "per_rank":
    custom_mg._gathered_patch_blocks = _per_rank_blocks
elif blocks_arm != "one":
    raise ValueError(blocks_arm)
wall = time.perf_counter()
set_custom_fmg(stokes, levels, field_id=0)
t_fmg = time.perf_counter() - wall

wall = time.perf_counter()
stokes.solve()
t_solve_first = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
peaks = {}
for lab, _P in cut:
    _, slip, _ = fault_slip(stokes, lab, info)
    peaks[lab] = uw.mpi.comm.allreduce(float(np.abs(slip).max()) if len(slip) else 0.0, op=max)


def level_smoothers(velpc):
    """Each velocity MG level's smoother as installed; for a FAC patch level (PC
    composite = whole-level SOR, then ASM over the patch blocks) the ASM blocks, their
    rows summed over the ranks, the largest block and the block solver."""
    out = []
    for lev in range(velpc.getMGLevels()):
        ksp = velpc.getMGSmoother(lev)
        pc = ksp.getPC()
        entry = {"level": lev, "ksp": ksp.getType(), "pc": pc.getType()}
        asm = None
        if pc.getType() == "composite":
            subs = [pc.getCompositePC(i) for i in range(2)]
            entry["composite"] = [s.getType() for s in subs]
            asm = next((s for s in subs if s.getType() == "asm"), None)
        elif pc.getType() == "asm":
            asm = pc
        if asm is not None:
            sub_ksps = asm.getASMSubKSP()
            entry["asm_blocks"] = int(uw.mpi.comm.allreduce(len(sub_ksps)))
            entry["asm_rows"] = int(uw.mpi.comm.allreduce(
                sum(k.getOperators()[0].getSize()[0] for k in sub_ksps)))
            entry["asm_block_rows_max"] = max(uw.mpi.comm.allgather(
                max((k.getOperators()[0].getSize()[0] for k in sub_ksps), default=0)))
            entry["asm_sub_pc"] = sorted(set().union(*uw.mpi.comm.allgather(
                {k.getPC().getType() for k in sub_ksps})))
            entry["asm_blocks_per_rank"] = uw.mpi.comm.allgather(len(sub_ksps))
            entry["asm_rows_per_rank"] = uw.mpi.comm.allgather(
                int(sum(k.getOperators()[0].getSize()[0] for k in sub_ksps)))
        out.append(entry)
    return out


ctx = (getattr(stokes, "_rotated_linear_cache", None) or {}).get("ctx")
level_ops, smoothers = [], []
if ctx is not None:
    velpc = ctx["ksp"].getPC().getFieldSplitSubKSP()[0].getPC()
    if velpc.getType() == "mg":
        smoothers = level_smoothers(velpc)
        for lev in range(velpc.getMGLevels()):
            Amat = velpc.getMGSmoother(lev).getOperators()[0]
            level_ops.append({"rows": int(Amat.getSize()[0])})

work = {"applications": 0, "iterations": 0}


def count_velocity_work(_ksp, its, _rnorm):
    if its == 0:
        work["applications"] += 1
    else:
        work["iterations"] += 1


if ctx is not None:
    ctx["pc"].getFieldSplitSubKSP()[0].setMonitor(count_velocity_work)
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_solve_again = time.perf_counter() - wall
info2 = stokes._rotated_freeslip_info

h = (getattr(stokes, "_custom_mg", None) or {}).get("hierarchy")
pr = getattr(h, "level_patch_rows", None)
last = pr[-1] if pr else None


def _rows(item):
    if item is None:
        return None
    blocks = item if isinstance(item, list) else [item]
    return [int(uw.mpi.comm.allreduce(len(b[1]))) for b in blocks]


owned = mesh.dm.getCellNumbering().getIndices() >= 0


def event_per_rank(name):
    try:
        info = PETSc.Log.Event(name).getPerfInfo()
    except Exception:
        return None
    return {"flops": uw.mpi.comm.allgather(float(info.get("flops", 0.0))),
            "time_s": uw.mpi.comm.allgather(round(float(info.get("time", 0.0)), 3)),
            "count": uw.mpi.comm.allgather(int(info.get("count", 0)))}


slips = {}
for lab, _P in cut:
    s_loc, V_loc, _leak = fault_slip(stokes, lab, info2)
    s_all = np.concatenate(uw.mpi.comm.allgather(np.asarray(s_loc, dtype=float)))
    V_all = np.concatenate(uw.mpi.comm.allgather(np.asarray(V_loc, dtype=float)))
    order = np.argsort(s_all, kind="stable")
    slips[lab] = (s_all[order], V_all[order])

record = {
    "stage": 1, "case": case, "blocks": blocks_arm, "hierarchy": hier,
    "UW_FAC_STRUCTURAL": os.environ.get("UW_FAC_STRUCTURAL"),
    "UW_FAC_COVER": os.environ.get("UW_FAC_COVER"), "gap_S": float(params.uw_gap),
    "n_rungs": n, "S": S, "h_b_over_S": (1 / 32) / S,
    "strands": {lab: len(P) - 1 for lab, P in spines}, "cut": [lab for lab, _ in cut],
    "band_cells_per_rank": {"main": uw.mpi.comm.allgather(int((band_main & owned).sum())),
                            "second": uw.mpi.comm.allgather(int((band_second & owned).sum()))},
    "cells_per_rank": uw.mpi.comm.allgather(int(owned.sum())),
    "lu_num": event_per_rank("MatLUFactorNum"),
    "lu_sym": event_per_rank("MatLUFactorSym"),
    "mat_solve": event_per_rank("MatSolve"),
    "level_ops_velocity": level_ops, "level_smoothers": smoothers,
    "patch_block_rows": _rows(last),
    "converged": info.get("converged"), "ksp_its": info.get("ksp_its"),
    "vel_its_last": info.get("vel_its_last"),
    "vel_its_last_again": info2.get("vel_its_last"),
    "vel_applications_again": work["applications"],
    "vel_its_all_applications_again": work["iterations"],
    "peak_slip": peaks,
    "t_base_s": round(t_base, 2), "t_place_s": round(t_place, 2), "t_fmg_s": round(t_fmg, 2),
    "t_solve_first_s": round(t_solve_first, 2), "t_solve_again_s": round(t_solve_again, 2),
    # ru_maxrss is bytes on macOS and kilobytes on Linux
    "peak_rss_mb_per_rank": [round(m * (1 if sys.platform == "darwin" else 1024) / 2 ** 20, 1)
                             for m in uw.mpi.comm.allgather(
                                 resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)],
    "np": uw.mpi.size,
}
uw.pprint("RECORD " + json.dumps(record))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
        np.savez(os.path.splitext(out)[0] + "_slip.npz",
                 **{f"{lab}_s": s for lab, (s, _V) in slips.items()},
                 **{f"{lab}_V": V for lab, (_s, V) in slips.items()})
