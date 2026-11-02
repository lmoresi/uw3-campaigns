"""Iterative FAC patch probe (dev hub, 2026-11-01), the linear fixture: does the patch
need an exact LU, and can tiny local solves plus the slip coarse space replace it?

UWTN 2026-022 problem A (unit box, simple shear, the straight frictionless fault from
(0.30, 0.45) to (0.70, 0.55), base h_b = 1/32), hierarchy H0 only: the welded base,
then the split S level with the FAC patch, the cover gate forced open. The patch's
block solver and cutting come from patch_probe.py (see its spec). The reference arm
is one LU block (the defaults): 66-67 velocity iterations at band ratios 24-97.

    python iterative_patch_linear.py -uw_n_rungs 640 -uw_block fgmres -uw_block_pc ilu \
        -uw_ilu_levels 1 -uw_rtol 1e-2 -uw_out records/A_r640_fgmres_ilu1_rtol1e-2.json
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
from underworld3.utilities.fault_contact import fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_probe  # noqa: E402

params = uw.Params(
    uw_n_rungs=320,           # spine intervals at S: 320, 640, 1280 (h_b/S 24, 48, 97)
    uw_tol=1.0e-6,            # Stokes solver tolerance
    uw_block="lu",            # lu or fgmres (patch_probe spec)
    uw_block_pc="ilu",        # ilu or gamg
    uw_ilu_levels=1,
    uw_rtol=1.0e-2,           # 0: exactly max_it steps
    uw_max_it=200,
    uw_cut=0,                 # 1: pieces of 2000 rows
    uw_strip=0,               # >0: strips of this many rung spacings
    uw_slip=0,                # 1: the slip coarse space
    uw_out="records/A.json",
)
spec = {k: getattr(params, "uw_" + k) for k in
        ("block", "block_pc", "ilu_levels", "rtol", "max_it", "cut", "strip", "slip")}

FAULT = "Fault"
A, B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
H_B = 1.0 / 32
n = int(params.uw_n_rungs)
assert n % 8 == 0, "the spine count must be a multiple of 8"
L = float(np.linalg.norm(B - A))
S = L / n
trace = A + (np.arange(n + 1) * S)[:, None] * (B - A) / L

wall = time.perf_counter()
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 8,
                                         regular=False, qdegree=2, refinement=2)
base_levels = base._coarse_level_meshes()[:-1] + [base]           # h = 1/8, 1/16, 1/32
t_base = time.perf_counter() - wall


def ladder(host, k, widen=True):
    """The fault's ladder at 2^k S (every 2^k-th spine point) placed in ``host``, split."""
    c = 2 ** k
    width = 2 * S * (c if widen else 1)
    for clearance in (0.7, 0.5):
        try:
            return place_fault_ribbon_2d(host, [(FAULT, trace[::c])], width, margin_rings=1,
                                         clearance=clearance, split=True, mesher="ladder")[0]
        except RuntimeError as err:
            last = err
    raise last


def graded_depth():
    """The smallest j with h_b / (2^j S) <= 4."""
    j = 1
    while H_B / (2 ** j * S) > 4.0:
        j += 1
    return j


hier = "H0"
wall = time.perf_counter()
levels, names = list(base_levels), ["1/8", "1/16", "1/32"]
mesh = ladder(base, 0)
names.append("S in 1/32 (solver mesh)")
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

patch_probe.configure_patch(spec, S)
wall = time.perf_counter()
set_custom_fmg(stokes, levels, field_id=0, slip_coarse_space=bool(int(spec["slip"])))
t_fmg = time.perf_counter() - wall


wall = time.perf_counter()
stokes.solve()
t_solve_first = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
record_info = {k: info.get(k) for k in ("converged", "nonlinear_iterations", "ksp_its",
                                        "vel_its_last", "pres_its_last", "velocity_pc")}
_, slip, _ = fault_slip(stokes, FAULT, info)
peak = uw.mpi.comm.allreduce(float(np.abs(slip).max()) if len(slip) else 0.0, op=max)

def level_smoothers(velpc):
    """The smoother each velocity multigrid level runs, as installed: KSP and PC type;
    for a FAC patch level (custom_mg, #629: PC composite = whole-level SOR, then ASM
    over the band blocks) the ASM blocks and their rows summed over the ranks, the
    largest block's rows, and the block solver. Level 0 is the coarse solve."""
    out = []
    for lev in range(velpc.getMGLevels()):
        ksp = velpc.getMGSmoother(lev)
        pc = ksp.getPC()
        entry = {"level": lev, "ksp": ksp.getType(), "pc": pc.getType()}
        asm = None
        if pc.getType() == "composite":
            subs = [pc.getCompositePC(i) for i in range(2)]     # custom_mg adds sor, asm
            entry["composite"] = [s.getType() for s in subs]
            asm = next((s for s in subs if s.getType() == "asm"), None)
        elif pc.getType() == "asm":
            asm = pc
        if asm is not None:
            sub_ksps = asm.getASMSubKSP()
            rows = sum(k.getOperators()[0].getSize()[0] for k in sub_ksps)
            entry["asm_blocks"] = int(uw.mpi.comm.allreduce(len(sub_ksps)))
            entry["asm_rows"] = int(uw.mpi.comm.allreduce(rows))
            # the largest block (overlap included), against fac_block_rows (2000)
            entry["asm_block_rows_max"] = max(uw.mpi.comm.allgather(
                max((k.getOperators()[0].getSize()[0] for k in sub_ksps), default=0)))
            entry["asm_sub_pc"] = sorted(set().union(*uw.mpi.comm.allgather(
                {k.getPC().getType() for k in sub_ksps})))
        out.append(entry)
    return out


# the custom-MG switches read from the environment (none set: the defaults)
MG_ENV = {k: v for k, v in os.environ.items() if k.startswith(("UW_FAC", "UW_CUSTOM_MG", "UW_MG"))}

# the velocity multigrid's levels: rows and nonzeros per row of each level operator
ctx = (getattr(stokes, "_rotated_linear_cache", None) or {}).get("ctx")
level_ops, smoothers = [], []
if ctx is not None:
    velpc = ctx["ksp"].getPC().getFieldSplitSubKSP()[0].getPC()
    if velpc.getType() == "mg":
        smoothers = level_smoothers(velpc)
        for lev in range(velpc.getMGLevels()):
            Amat = velpc.getMGSmoother(lev).getOperators()[0]
            rows = Amat.getSize()[0]
            nz = Amat.getInfo(PETSc.Mat.InfoType.GLOBAL_SUM)["nz_used"]
            level_ops.append({"rows": int(rows), "nnz_per_row": round(nz / max(rows, 1), 1)})


def n_cells(m):
    """Cells owned across the ranks (the plex numbering marks the others negative)."""
    n_own = int(np.count_nonzero(m.dm.getCellNumbering().getIndices() >= 0))
    return int(uw.mpi.comm.allreduce(n_own))


# the same solve again from zero on the cached operators: the solve alone, with every
# application of the velocity sub-KSP counted (vel_its_last is the last one only)
work = {"applications": 0, "iterations": 0}


def count_velocity_work(_ksp, its, _rnorm):
    if its == 0:
        work["applications"] += 1
    else:
        work["iterations"] += 1


block_work = {}
patch = {}
if ctx is not None:
    ctx["pc"].getFieldSplitSubKSP()[0].setMonitor(count_velocity_work)
    if velpc.getType() == "mg":
        patch = patch_probe.patch_summary(velpc)
        block_work = patch_probe.count_block_work(velpc)
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_solve_again = time.perf_counter() - wall
info2 = stokes._rotated_freeslip_info

# the cover gate's verdict on the finest level: the structural patch rows the
# hierarchy kept (None: the gate declined, the level smooths whole), against the
# level's velocity rows (the finest operator's size)
_h = (getattr(stokes, "_custom_mg", None) or {}).get("hierarchy")
_pr = getattr(_h, "level_patch_rows", None)
_last = _pr[-1] if _pr else None
gate = {"cover_max": float(os.environ.get("UW_FAC_COVER", 0.75)),
        "taken": any(uw.mpi.comm.allgather(_last is not None)),
        "level_rows": level_ops[-1]["rows"] if level_ops else None}
if _last is not None:
    gate["patch_owned_rows"] = int(uw.mpi.comm.allreduce(len(_last[0])))
    gate["subdomain_rows"] = int(uw.mpi.comm.allreduce(len(_last[1])))
    if gate["level_rows"]:
        gate["subdomain_fraction"] = gate["subdomain_rows"] / gate["level_rows"]

record = {
    "problem": "A (linear, the note's fixture)",
    "hierarchy": hier,
    "levels": names,
    "level_cells": [n_cells(m) for m in levels] + [n_cells(mesh)],
    "level_ops_velocity": level_ops,
    "level_smoothers": smoothers, "mg_env": MG_ENV,
    "n_rungs": n, "S": S, "h_b": H_B, "h_b_over_S": H_B / S,
    "tolerance": float(params.uw_tol),
    **record_info,
    "vel_its_last_again": info2.get("vel_its_last"),
    "vel_applications_again": work["applications"],
    "vel_its_all_applications_again": work["iterations"],
    "peak_slip": peak,
    "t_base_s": round(t_base, 2), "t_place_s": round(t_place, 2), "t_fmg_s": round(t_fmg, 2),
    "t_solve_first_s": round(t_solve_first, 2), "t_solve_again_s": round(t_solve_again, 2),
    "np": uw.mpi.size,
    "fac_gate": gate, "spec": spec, "patch": patch,
    "block_work_again": patch_probe.reduce_work(block_work) if block_work else None,
    "t_setup_s_est": round(t_solve_first - t_solve_again, 2),
    # ru_maxrss is bytes on macOS, kilobytes on Linux
    "peak_rss_mb_per_rank": [round(m / (2 ** 20 if sys.platform == "darwin" else 2 ** 10), 1)
        for m in uw.mpi.comm.allgather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)],
    "petsc": ".".join(str(i) for i in PETSc.Sys.getVersion()),
}
uw.pprint("RECORD " + json.dumps(record))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
