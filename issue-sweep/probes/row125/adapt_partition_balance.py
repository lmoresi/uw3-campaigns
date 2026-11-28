"""Row 125: how balanced adapt's own child partition is (no fault).

adapt keeps the child co-partitioned with the base, so the refined cells sit on
the ranks that own the trace's base cells. This prints the per-rank finest
cells of the adapted mesh and max/mean, on the fixture of region_share_curve.py.

    mpirun -n 8 python adapt_partition_balance.py -uw_cellsize 0.1 -uw_k 3 -uw_width 0.08
"""
import numpy as np

import underworld3 as uw

params = uw.Params(
    uw_cellsize=uw.Param(0.1, description="base cell size"),
    uw_k=uw.Param(3, description="add-on levels toward the trace"),
    uw_width=uw.Param(0.08, description="metric refinement width"),
)
H, K, WIDTH = float(params.uw_cellsize), int(params.uw_k), float(params.uw_width)
TIP_A, TIP_B = np.array([0.30, 0.45]), np.array([0.70, 0.55])

base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=H, refinement=1, qdegree=2)
pts = np.column_stack([np.linspace(TIP_A[0], TIP_B[0], 9),
                       np.linspace(TIP_A[1], TIP_B[1], 9), np.zeros(9)])
guide = uw.meshing.Surface("guide", base, pts)
guide.discretize()
mesh = base.adapt(guide.refinement_metric_function(
    h_near=H / 2 / 2**K, h_far=H / 2, width=WIDTH, profile="linear"), max_levels=K)
cS, cE = mesh.dm.getHeightStratum(0)
cells = uw.mpi.comm.allgather(cE - cS)
uw.pprint(f"RES h={H} k={K} width={WIDTH} np={uw.mpi.size} cells={cells} "
          f"max/mean={max(cells) / np.mean(cells):.2f}")
