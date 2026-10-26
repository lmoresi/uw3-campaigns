"""Wall-clock phases and partition of a faulted-mesh (add-on) rebuild: measurement runs only.

``install()`` wraps the library calls a FaultedMesh build and its first solve go through
(monkeypatched module attributes, nothing edited in the library) with an EXCLUSIVE-time
clock: every wall second between install and the end goes to the innermost wrapped call
running on this rank, as a (phase, label) pair, so nested calls (a gather inside the
add_fault redistribution, a gmsh fill inside the carve) are not double counted. Phases:

  conform_split  placement of the band (carve, gmsh fill of the cavity, sew), the Mesh
                 wrap, adopt_hierarchy's bookkeeping, the cut along the trace and the split
  partition      every redistribution: place_surface._gather_regions (the placement's
                 gather of the band's star onto one rank), fault_split._redistribute_fault_interior
                 (add_fault's pre-split gather when the cut touches a seam),
                 custom_mg._colocate_level (adopt_hierarchy moving the base tail onto the
                 placed mesh's ranks), fault_mg.colocate_split_level
                 (fault_mg.split_tail_levels, add_fault replaying the cut on a mesh-owned
                 add-on tail level, counts as conform_split)
  refine         any uniform/adaptive refinement (Mesh._build_refined_hierarchy, sbr/nvb
                 refine): none is expected on a rebuild; zero when not called
  solver_setup   the rest of FaultedMesh.__init__ (MeshVariables, Stokes, set_custom_fmg
                 registration, projections, diagnostics) and, inside the first solve, the
                 lazy setup: JIT of the pointwise functions, the discretisation, the SNES/KSP,
                 the rotation, the custom-MG transfers (build_transfers)
  solve          the rest of FaultedMesh.solve: the field transfer (T, gamma, markers by
                 global_evaluate; the driver times it as "transfer") and the Newton loop
  instr          this module's own collectives (cell counts), excluded from everything

Each rank keeps its own clock; the records hold rank 0's and the max over ranks.
"""
import functools
import json
import os
import time
from collections import defaultdict
from contextlib import contextmanager

import numpy as np
from mpi4py import MPI


class Clock:
    def __init__(self):
        self.stack = [("other", "other")]
        self.mark = time.perf_counter()
        self.phase = defaultdict(float)
        self.label = defaultdict(float)
        self.calls = defaultdict(int)
        self.events = []           # partition / transfer events, in order

    def _flush(self):
        now = time.perf_counter()
        ph, lb = self.stack[-1]
        self.phase[ph] += now - self.mark
        self.label[lb] += now - self.mark
        self.mark = now

    def push(self, phase, label):
        self._flush()
        self.stack.append((phase or self.stack[-1][0], label))
        self.calls[label] += 1

    def pop(self):
        self._flush()
        self.stack.pop()

    @contextmanager
    def section(self, phase, label):
        self.push(phase, label)
        try:
            yield
        finally:
            self.pop()

    def snapshot(self):
        self._flush()
        return dict(self.phase), dict(self.label), dict(self.calls), len(self.events)

    def since(self, snap):
        ph0, lb0, c0, e0 = snap
        ph1, lb1, c1, _ = self.snapshot()
        return ({k: v - ph0.get(k, 0.0) for k, v in ph1.items() if v - ph0.get(k, 0.0) > 0},
                {k: v - lb0.get(k, 0.0) for k, v in lb1.items() if v - lb0.get(k, 0.0) > 0},
                {k: v - c0.get(k, 0) for k, v in c1.items() if v - c0.get(k, 0) > 0},
                self.events[e0:])


CLK = Clock()
COMM = MPI.COMM_WORLD


def _cells(dm):
    """(local cells, owned cells) of a DMPlex on this rank."""
    cS, cE = dm.getHeightStratum(0)
    n = cE - cS
    try:
        _nr, leaves, _rem = dm.getPointSF().getGraph()
        leaves = np.asarray(leaves if leaves is not None else [], dtype=np.int64)
        ghost = int(((leaves >= cS) & (leaves < cE)).sum())
    except Exception:
        ghost = 0
    return int(n), int(n - ghost)


def per_rank_cells(dm):
    """Owned cells of ``dm`` on every rank (collective), and the local count incl. ghosts."""
    n, owned = _cells(dm)
    return [int(x) for x in COMM.allgather(owned)], [int(x) for x in COMM.allgather(n)]


def wrap(module, name, phase, label, post=None):
    fn = getattr(module, name)
    if getattr(fn, "_addon_wrapped", False):
        return

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        within = CLK.stack[-1][1]
        CLK.push(phase, label)
        try:
            result = fn(*args, **kwargs)
        finally:
            CLK.pop()
        if post is not None:
            with CLK.section("instr", "instr"):
                CLK.within = within
                post(result, args, kwargs)
        return result

    wrapper._addon_wrapped = True
    setattr(module, name, wrapper)


def _dm_of(x):
    return getattr(x, "dm", x)


def install():
    import underworld3 as uw
    from underworld3.utilities import custom_mg, fault_mg, fault_split, line_cut, place_surface, rotated_bc

    def caller():
        return getattr(CLK, "within", None)

    def post_gather(result, args, kwargs):
        work, n_region, n_moved, owner, _canon = result
        before, _ = per_rank_cells(args[0])
        after, _ = per_rank_cells(work)
        CLK.events.append({"event": "gather_regions", "within": caller(), "n_region_cells": int(n_region),
                           "n_moved": int(n_moved), "owner": {str(k): int(v) for k, v in owner.items()},
                           "cells_before": before, "cells_after": after})

    def post_colocate(result, args, kwargs):
        coarse, fine = args[0], args[1]
        moved = result is not coarse
        before, _ = per_rank_cells(_dm_of(coarse))
        after, _ = per_rank_cells(_dm_of(result)) if moved else (before, None)
        CLK.events.append({"event": "colocate_level", "within": caller(), "moved": bool(moved),
                           "cells_before": before, "cells_after": after})

    def post_redistribute(result, args, kwargs):
        CLK.events.append({"event": "redistribute_fault_interior", "within": caller()})

    def post_zero(result, args, kwargs):
        CLK.events.append({"event": "transfer_zero_columns", "within": caller(), "n_zero": int(result)})

    def post_split_tail(result, args, kwargs):
        CLK.events.append({"event": "split_tail_levels", "within": caller(), "n_levels": len(result)})

    # partition
    wrap(place_surface, "_gather_regions", "partition", "gather_regions", post_gather)
    wrap(fault_split, "_redistribute_fault_interior", "partition", "redistribute_fault_interior",
         post_redistribute)
    wrap(custom_mg, "_colocate_level", "partition", "colocate_tail_level", post_colocate)
    wrap(fault_mg, "colocate_split_level", "partition", "colocate_split_level")
    # conform + split
    wrap(place_surface, "_place_thin_volume_2d", "conform_split", "carve_fill_sew")
    wrap(place_surface, "_gmsh_fill_2d", None, "gmsh_cavity_fill")
    wrap(place_surface, "_rebuild_sewn", None, "rebuild_sewn")
    wrap(custom_mg, "adopt_hierarchy", "conform_split", "adopt_hierarchy")
    wrap(fault_split, "add_fault", "conform_split", "cut_and_split")
    wrap(fault_split, "split_fault", None, "split_fault")
    wrap(line_cut, "cut_along_lines", None, "cut_along_lines")
    wrap(line_cut, "pull_vertex_onto", None, "pull_vertex_onto")
    wrap(fault_mg, "split_tail_levels", "conform_split", "split_tail_levels", post_split_tail)
    # refinement: none is expected on a rebuild (the base hierarchy is built once at
    # start-up); these would show it if any were called
    wrap(uw.discretisation.Mesh, "_build_refined_hierarchy", "refine", "build_refined_hierarchy")
    wrap(custom_mg, "sbr_refine", "refine", "sbr_refine")
    wrap(custom_mg, "nvb_refine", "refine", "nvb_refine")
    # solver setup inside the first solve
    wrap(custom_mg, "build_transfers", "solver_setup", "build_transfers")
    wrap(custom_mg, "_build_crosspart_transfer", None, "crosspart_transfer")
    wrap(custom_mg, "_count_zero_columns_parallel", None, "count_zero_columns", post_zero)
    wrap(rotated_bc, "build_rotation", "solver_setup", "build_rotation")
    wrap(rotated_bc, "_build_rotated_custom_Pl", "solver_setup", "rotated_custom_Pl")
    wrap(fault_mg, "rotated_split_transfers", "solver_setup", "rotated_split_transfers")
    Stokes = uw.systems.Stokes
    for meth, lab in (("_setup_pointwise_functions", "jit_pointwise"),
                      ("_setup_discretisation", "setup_discretisation"),
                      ("_setup_solver", "setup_solver")):
        wrap(Stokes, meth, "solver_setup", lab)
    # a label (no phase change) on every Mesh construction
    wrap(uw.discretisation.Mesh, "__init__", None, "Mesh.__init__")
    return CLK


def reduce_over_ranks(d):
    """{key: value} on every rank -> {key: [rank0, max]}."""
    keys = sorted(set().union(*COMM.allgather(set(d))))
    vals = np.array([d.get(k, 0.0) for k in keys], dtype=float)
    mx = np.empty_like(vals)
    COMM.Allreduce(vals, mx, op=MPI.MAX)
    r0 = COMM.bcast(vals, root=0)
    return {k: [round(float(a), 4), round(float(b), 4)] for k, a, b in zip(keys, r0, mx)}


RECORDS = []


def dump(out):
    if COMM.rank == 0:
        with open(os.path.join(out, "addon_timing.json"), "w") as f:
            json.dump(RECORDS, f, indent=1, default=str)
