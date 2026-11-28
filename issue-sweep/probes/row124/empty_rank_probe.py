"""Row 124: can a real partition leave a rank with all its units inside a fault region?

partition_addon sends every unit of a region to the region's owner (the rank with most
of its weight) and keeps the other units where they are; _peel_balance then sheds free
units across faces to lighter neighbours. A rank whose units all lie in a region it
does not own receives nothing and touches nothing, so it ends empty (np >= 3) or the
partition refuses ("the whole add-on would sit on one rank", np 2).

This wraps _peel_balance and reports, on rank 0, one RES line per partition call:
the per-rank load (finest cells) before and after the balance, the ranks left at zero,
and whether the call refused. Run under the supervisor at each np:

    mpirun -n N python empty_rank_probe.py -uw_case adapt -uw_k 2 -uw_cellsize 0.1

Cases (the fixtures of tests/parallel/fault_fixtures.py):
  adapt   a unit box (cellSize, refinement 1), adapt-on-top of k levels toward a
          straight trace, add_fault on it
  second  the same, then a second fault parallel to the first, 0.2 away
  base    add_fault straight on the box, no add-on
"""
import numpy as np
from mpi4py import MPI

import underworld3 as uw
from underworld3.utilities import addon_partition

params = uw.Params(
    uw_case=uw.Param("adapt", description="adapt | second | base"),
    uw_k=uw.Param(2, description="add-on levels toward the trace"),
    uw_cellsize=uw.Param(0.1, description="base cell size"),
)
comm = uw.mpi.comm
CASE, K, H = str(params.uw_case), int(params.uw_k), float(params.uw_cellsize)
TIP_A, TIP_B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
SECOND = np.array([[0.30, 0.65], [0.70, 0.75]])

calls = []
real_peel = addon_partition._peel_balance


def peel(dm, unit_of_cell, assign_unit, weight, *args, **kwargs):
    size = comm.size
    before = comm.allreduce(np.bincount(assign_unit, weights=weight, minlength=size), op=MPI.SUM)
    out = real_peel(dm, unit_of_cell, assign_unit, weight, *args, **kwargs)
    after = comm.allreduce(np.bincount(out[0], weights=weight, minlength=size), op=MPI.SUM)
    calls.append((before, after))
    return out


addon_partition._peel_balance = peel


def report(stage, refused=None):
    for i, (before, after) in enumerate(calls):
        uw.pprint(f"RES case={CASE} k={K} h={H} np={comm.size} stage={stage} call={i} "
                  f"before={before.astype(int).tolist()} after={after.astype(int).tolist()} "
                  f"empty_after={[r for r in range(comm.size) if after[r] == 0]} "
                  f"refused={refused!r}")
    if not calls:
        uw.pprint(f"RES case={CASE} k={K} h={H} np={comm.size} stage={stage} "
                  f"no-peel refused={refused!r}")
    calls.clear()


base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=H, refinement=1, qdegree=2)
mesh = base
if CASE in ("adapt", "second"):
    pts = np.column_stack([np.linspace(TIP_A[0], TIP_B[0], 9),
                           np.linspace(TIP_A[1], TIP_B[1], 9), np.zeros(9)])
    guide = uw.meshing.Surface("guide", base, pts)
    guide.discretize()
    mesh = base.adapt(guide.refinement_metric_function(
        h_near=H / 2 / 2**K, h_far=H / 2, width=0.08, profile="linear"), max_levels=K)
    report("adapt")

stages = [("first", [("Flt", np.vstack([TIP_A, TIP_B]))])]
if CASE == "second":
    stages.append(("second", [("Flt2", SECOND)]))
for stage, faults in stages:
    try:
        mesh = mesh.add_fault(faults)
        report(stage)
    except RuntimeError as exc:
        report(stage, refused=str(exc)[:120])
        break
cS, cE = mesh.dm.getHeightStratum(0)
uw.pprint(f"RES case={CASE} k={K} h={H} np={comm.size} final_cells={comm.allgather(cE - cS)}")
