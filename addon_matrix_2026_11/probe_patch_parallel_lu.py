"""Phase 3 probe: does solving the FAC patch as ONE distributed problem, with a
parallel direct solver over every rank, keep the serial convergence at any rank
count and spread the factorisation?

custom_mg installs the finest level's patch as PCASM blocks. A PCASM block is a
sequential matrix on one rank: its rows are gathered there, factored and solved,
and the correction is added back. Before #925 each rank's share of the patch was
its own block, so the partition drew the block boundaries and the velocity
iterations grew with the rank count (row 5, no zone, n_rungs 320: 67 serially,
445 at np 16). Since #925 the patch is gathered into one block on the rank that
owns most of its rows: 67-86 iterations at np 1-16, but one rank factors it.

This probe replaces the composite smoother's ASM member (the member after
whole-level SOR) with a PC that takes each block's rows, plus PCASM's overlap
layer, as a submatrix distributed over every rank, factors it with MUMPS or
SuperLU_dist, and adds the correction back. That is the same additive Schwarz
correction as the library's, computed in parallel. Nothing else changes. It runs
the row 5 driver (row5_networks.py) with its own arguments.

    PROBE_PATCH=mumps mpirun -np 8 python probe_patch_parallel_lu.py \\
        -uw_case ti -uw_zone none -uw_n_rungs 320 -uw_out records/x.json

PROBE_DRIVER         the driver to run (row5_networks.py; sheet3d_addon.py for 3-D)
PROBE_PATCH          library (no change, the control), mumps or superlu_dist, or
                     krylov: an inexact iterative block solve, CG with GAMG by
                     default (-probe_patch_ksp_type, -probe_patch_pc_type ...
                     override), its preconditioner set up once per operator and
                     reused by every application, zero initial guess
PROBE_PATCH_OVERLAP  overlap layers added to each block (1, as the library)
PROBE_PATCH_RTOL     krylov: the block solve's relative tolerance (1e-2)
PROBE_PATCH_MAXIT    krylov: its iteration cap (50)
PROBE_PATCH_WARM     krylov: 1 starts each block solve from that block's previous
                     solution instead of zero

Options reach the parallel factorisation under the prefix probe_patch_, for
example -probe_patch_mat_mumps_icntl_24 1 (MUMPS null-pivot detection). The
probe prints one PROBEPATCH line after the driver's RECORD: the factor and apply
times (max over ranks), the block sizes and each rank's rows of each block.
"""
import inspect
import json
import os
import runpy
import sys
import time

import numpy as np
from mpi4py import MPI
from petsc4py import PETSc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(HERE, os.environ.get("PROBE_DRIVER", "row5_networks.py"))

from underworld3.utilities import custom_mg  # noqa: E402

MODE = os.environ.get("PROBE_PATCH", "mumps")
if MODE not in ("library", "mumps", "superlu_dist", "krylov"):
    raise ValueError(f"PROBE_PATCH={MODE}: expected library, mumps, superlu_dist or krylov")
OVERLAP = int(os.environ.get("PROBE_PATCH_OVERLAP", "1"))
RTOL = float(os.environ.get("PROBE_PATCH_RTOL", "1e-2"))
MAXIT = int(os.environ.get("PROBE_PATCH_MAXIT", "50"))
WARM = os.environ.get("PROBE_PATCH_WARM", "0") == "1"
STATS = {"setups": 0, "t_setup": 0.0, "applies": 0, "t_apply": 0.0,
         "failed_solves": 0, "inner_its": 0, "inner_its_max": 0, "inner_at_cap": 0,
         "blocks": [], "rows_here": []}
PARALLEL_LEVELS = set()


def _overlapped(P, rows, layers):
    """``rows`` (global, the same on every rank) grown by ``layers`` layers of P's
    sparsity, as MatIncreaseOverlap grows a PCASM subdomain."""
    r0, r1 = P.getOwnershipRange()
    comm = P.getComm().tompi4py()
    for _ in range(layers):
        mine = rows[(rows >= r0) & (rows < r1)]
        cols = [np.asarray(P.getRow(int(r))[0], dtype=np.int64) for r in mine]
        local = np.unique(np.concatenate(cols)) if cols else np.zeros(0, np.int64)
        rows = np.union1d(rows, np.concatenate(comm.allgather(local)).astype(np.int64))
    return rows


class ParallelPatch:
    """y = sum_k R_k^T A_k^-1 R_k x, each A_k the block's rows of the level
    operator as a matrix distributed over every rank, factored in parallel."""

    def __init__(self, blocks):
        self.blocks = blocks          # each block's global rows, the same on every rank
        self.parts = []

    def _destroy(self):
        for part in self.parts:
            for obj in part:
                obj.destroy()
        self.parts = []

    def setUp(self, pc):
        wall = time.perf_counter()
        self._destroy()
        _A, P = pc.getOperators()
        r0, r1 = P.getOwnershipRange()
        template = P.createVecRight()
        sizes, here = [], []
        for rows in self.blocks:
            rows = _overlapped(P, rows, OVERLAP)
            mine = rows[(rows >= r0) & (rows < r1)]
            is_k = PETSc.IS().createGeneral(mine.astype(PETSc.IntType), comm=P.getComm())
            A_k = P.createSubMatrix(is_k, is_k)
            ksp = PETSc.KSP().create(comm=P.getComm())
            ksp.setOptionsPrefix("probe_patch_")
            ksp.setOperators(A_k)
            if MODE == "krylov":
                ksp.setType("cg")
                ksp.getPC().setType("gamg")
                ksp.setTolerances(rtol=RTOL, max_it=MAXIT)
                ksp.setInitialGuessNonzero(WARM)
            else:
                ksp.setType("preonly")
                ksp.getPC().setType("lu")
                ksp.getPC().setFactorSolverType(MODE)
            ksp.setFromOptions()
            ksp.setUp()
            xs, ys = A_k.createVecs()
            ys.set(0.0)
            scatter = PETSc.Scatter().create(template, is_k, xs, None)
            self.parts.append((ksp, scatter, xs, ys, A_k, is_k))
            sizes.append(int(rows.size))
            here.append(int(mine.size))
        template.destroy()
        STATS["setups"] += 1
        STATS["t_setup"] += time.perf_counter() - wall
        STATS["blocks"], STATS["rows_here"] = sizes, here

    def apply(self, pc, x, y):
        wall = time.perf_counter()
        y.set(0.0)
        for ksp, scatter, xs, ys, _A, _is in self.parts:
            scatter.scatter(x, xs, PETSc.InsertMode.INSERT_VALUES,
                            PETSc.ScatterMode.FORWARD)
            ksp.solve(xs, ys)
            reason = ksp.getConvergedReason()
            if MODE == "krylov":
                its = ksp.getIterationNumber()
                STATS["inner_its"] += its
                STATS["inner_its_max"] = max(STATS["inner_its_max"], its)
                if reason == PETSc.KSP.ConvergedReason.DIVERGED_MAX_IT:
                    STATS["inner_at_cap"] += 1
                elif reason < 0:
                    STATS["failed_solves"] += 1
            elif reason < 0:
                STATS["failed_solves"] += 1
            scatter.scatter(ys, y, PETSc.InsertMode.ADD_VALUES,
                            PETSc.ScatterMode.REVERSE)
        STATS["applies"] += 1
        STATS["t_apply"] += time.perf_counter() - wall


def _probe_configure(pc, Ps, *args, **kwargs):
    fac_keys = _configure(pc, Ps, *args, **kwargs)
    if MODE == "library":
        return fac_keys
    patch_rows = _signature.bind(pc, Ps, *args, **kwargs).arguments.get("patch_rows") or []
    comm = pc.getComm().tompi4py()
    for level, entry in enumerate(patch_rows):
        if level == 0:
            continue
        pairs = [] if entry is None else entry if isinstance(entry, list) else [entry]
        mine = [np.asarray(sub, dtype=np.int64) for _own, sub in pairs]
        # every rank takes part, whether or not it holds a block of this level
        blocks = [b for rank in comm.allgather(mine) for b in rank if b.size]
        if not blocks:
            continue
        member = pc.getMGSmoother(level).getPC().getCompositePC(1)
        member.setType("python")
        member.setPythonContext(ParallelPatch(blocks))
        PARALLEL_LEVELS.add(level)
    return fac_keys


def _probe_set_up(pc, fac_keys):
    """The library's set-up of the ASM blocks, for the levels this probe left alone."""
    keep = [k for k in (fac_keys or [])
            if not any(k.startswith(f"mg_levels_{l}_") for l in PARALLEL_LEVELS)]
    return _set_up(pc, keep)


_configure = custom_mg._configure_pcmg
_signature = inspect.signature(_configure)
_set_up = custom_mg._set_up_fac_smoothers
custom_mg._configure_pcmg = _probe_configure
custom_mg._set_up_fac_smoothers = _probe_set_up
runpy.run_path(sys.argv[0], run_name="__main__")

comm = MPI.COMM_WORLD
everyone = comm.gather(dict(STATS), root=0)
if comm.rank == 0:
    print("PROBEPATCH " + json.dumps({
        "mode": MODE, "overlap": OVERLAP, "np": comm.size,
        "levels": sorted(PARALLEL_LEVELS),
        "blocks": everyone[0]["blocks"],
        "rows_per_rank": [e["rows_here"] for e in everyone],
        "setups": everyone[0]["setups"], "applications": everyone[0]["applies"],
        "t_factor_s_max": round(max(e["t_setup"] for e in everyone), 2),
        "t_apply_s_max": round(max(e["t_apply"] for e in everyone), 2),
        "failed_solves": sum(e["failed_solves"] for e in everyone),
        "rtol": RTOL if MODE == "krylov" else None, "warm": WARM,
        "inner_its": everyone[0]["inner_its"], "inner_its_max": everyone[0]["inner_its_max"],
        "inner_at_cap": everyone[0]["inner_at_cap"],
    }), flush=True)
