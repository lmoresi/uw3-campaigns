"""Shared set-up for the iterative FAC patch probes (dev hub, 2026-11-01): the finest
level's patch block solver, the patch's cutting, and what the record reads back.

The patch is the composite smoother's ASM member on the finest velocity MG level.
Its blocks read their KSP and PC from the options database when the ASM sets up,
inside ``custom_mg._set_up_fac_smoothers``, under the rotated solve's per-solve
prefix ``rotfs<N>_fieldsplit_vel_mg_levels_<l>_sub_1_sub_``. The prefix is not known
before the solve, so the keys are written for the next few solve counts and levels.

Spec (the drivers' uw.Params):

    block      lu (preonly + LU, the production default) or fgmres
    block_pc   ilu or gamg, for fgmres
    ilu_levels ILU fill levels
    rtol       the block solve's relative tolerance; 0 runs exactly max_it steps
               (convergence test "skip": a fixed number of Krylov steps)
    max_it     the block solve's iteration cap (with rtol > 0, a safety cap)
    cut        1: the structural patch cut along strike into pieces of 2000 rows
    strip      >0: cut into strips of this many rung spacings instead
    slip       1: the slip coarse space on top (set_custom_fmg(slip_coarse_space=True))
"""
import os

import numpy as np
import underworld3 as uw
from petsc4py import PETSc
from underworld3.utilities import rotated_bc


def configure_patch(spec, rung_spacing):
    """Set the environment knobs and option keys for the next rotated solves."""
    os.environ["UW_FAC_COVER"] = "1.01"            # the gate forced open (#918)
    if int(spec["cut"]):
        os.environ["UW_FAC_SEGMENT_STRUCTURAL"] = "1"
        os.environ["UW_FAC_BLOCK_ROWS"] = "2000"
    if float(spec["strip"]) > 0:
        os.environ["UW_FAC_STRIP_WIDTH"] = repr(float(spec["strip"]) * rung_spacing)
    if spec["block"] == "lu":
        return
    os.environ["UW_FAC_SUB_PC"] = spec["block_pc"]
    opts = PETSc.Options()
    n0 = rotated_bc._ROT_SOLVE_COUNT
    rtol = float(spec["rtol"])
    for n in range(n0 + 1, n0 + 6):
        for lev in range(1, 7):
            p = f"rotfs{n}_fieldsplit_vel_mg_levels_{lev}_sub_1_sub_"
            opts[p + "ksp_type"] = spec["block"]
            opts[p + "ksp_max_it"] = int(spec["max_it"])
            if rtol > 0:
                opts[p + "ksp_rtol"] = rtol
                opts[p + "ksp_atol"] = 0.0
            else:
                # exactly max_it steps, reported converged (a capped block solve
                # that reports DIVERGED_ITS can fail its PCASM)
                opts[p + "ksp_convergence_test"] = "skip"
            if spec["block_pc"] == "ilu":
                opts[p + "pc_factor_levels"] = int(spec["ilu_levels"])


def finest_patch(velpc):
    """The finest FAC level's ASM (the composite's second member), or None."""
    for lev in range(velpc.getMGLevels() - 1, 0, -1):
        pc = velpc.getMGSmoother(lev).getPC()
        if pc.getType() == "composite":
            return pc.getCompositePC(1)
        if pc.getType() == "asm":
            return pc
    return None


def patch_summary(velpc):
    """Blocks, their rows summed over the ranks, the largest block, the block KSP
    and PC, and the slip coarse space's columns where it is on."""
    asm = finest_patch(velpc)
    if asm is None:
        return {"blocks": 0}
    subs = asm.getASMSubKSP()
    sizes = [k.getOperators()[0].getSize()[0] for k in subs]
    out = {"blocks": int(uw.mpi.comm.allreduce(len(subs))),
           "rows": int(uw.mpi.comm.allreduce(int(sum(sizes)))),
           "block_rows_max": max(uw.mpi.comm.allgather(max(sizes, default=0))),
           "block_rows_median_rank0": float(np.median(sizes)) if sizes else 0.0,
           "block_ksp": sorted(set().union(*uw.mpi.comm.allgather({k.getType() for k in subs}))),
           "block_pc": sorted(set().union(*uw.mpi.comm.allgather({k.getPC().getType() for k in subs})))}
    level_pc = velpc.getMGSmoother(velpc.getMGLevels() - 1).getPC()
    if level_pc.getType() == "composite":
        members = []
        k = 0
        while True:
            try:
                members.append(level_pc.getCompositePC(k).getType())
            except Exception:
                break
            k += 1
        out["composite"] = members
    return out


def count_block_work(velpc):
    """Attach a monitor to every block KSP of the finest patch; returns the counter
    (block applications and block iterations, this rank's)."""
    work = {"block_applications": 0, "block_iterations": 0}
    asm = finest_patch(velpc)
    if asm is None:
        return work

    def monitor(_ksp, its, _rnorm):
        if its == 0:
            work["block_applications"] += 1
        else:
            work["block_iterations"] += 1

    for k in asm.getASMSubKSP():
        k.setMonitor(monitor)
    return work


def reduce_work(work):
    return {k: int(uw.mpi.comm.allreduce(v)) for k, v in work.items()}
