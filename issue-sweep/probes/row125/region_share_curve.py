"""Row 125: the add-on fault region's share of the finest cells, against h, k and width.

add_fault partitions with partition_addon(mesh, mark_polylines([trace]), layers=1):
the unit is a cell of the coarsest add-on level with all its descendants, a
unit is in the region if any of its cells on any level is in that level's
region (the trace's marked vertices' star plus one layer), and the owner
holds every region unit. This repeats that computation in serial (the
helpers partition_addon uses, its weight and unit rules) and prints the
region's weight over the total: the share the owner holds at every np, and
1/share, the solve's speed-up ceiling while the owner's cells bound it.

The fixture is that of empty_rank_probe.py / split_solve_timing.py: unit box,
cellSize h, refinement 1, adapt toward the trace with h_near = h/2/2**k,
h_far = h/2, the metric's refinement width uw_width.

    python region_share_curve.py -uw_cellsize 0.1 -uw_k 3 -uw_width 0.08

Check: h 0.1, k 3, width 0.08 gives 873 of 1764, the owner's count in H1's
region arm at np 4 and 8.
"""
import numpy as np

import underworld3 as uw
from underworld3.utilities.addon_partition import (_levels_of, _parent_cells_local,
                                                   mark_polylines)
from underworld3.utilities.place_surface import _region_cells

params = uw.Params(
    uw_cellsize=uw.Param(0.1, description="base cell size"),
    uw_k=uw.Param(3, description="add-on levels toward the trace"),
    uw_width=uw.Param(0.08, description="metric refinement width"),
)
H, K, WIDTH = float(params.uw_cellsize), int(params.uw_k), float(params.uw_width)
TIP_A, TIP_B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
TRACE = np.vstack([TIP_A, TIP_B])

base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=H, refinement=1, qdegree=2)
pts = np.column_stack([np.linspace(TIP_A[0], TIP_B[0], 9),
                       np.linspace(TIP_A[1], TIP_B[1], 9), np.zeros(9)])
guide = uw.meshing.Surface("guide", base, pts)
guide.discretize()
mesh = base.adapt(guide.refinement_metric_function(
    h_near=H / 2 / 2**K, h_far=H / 2, width=WIDTH, profile="linear"), max_levels=K)

_base, _static, addon = _levels_of(mesh)
levels = addon + [mesh]
unit_of = [np.arange(levels[0].dm.getHeightStratum(0)[1]
                     - levels[0].dm.getHeightStratum(0)[0], dtype=np.int64)]
for l in range(1, len(levels)):
    unit_of.append(unit_of[l - 1][_parent_cells_local(levels[l - 1], levels[l])])
n_units = len(unit_of[0])
weight = np.bincount(unit_of[-1], minlength=n_units).astype(float)

marks = mark_polylines([TRACE])
in_region = np.zeros(n_units, dtype=bool)
for l, lev in enumerate(levels):
    cell_region, _canon, _regions = _region_cells(
        lev.dm, np.asarray(marks(lev.dm), dtype=np.int32), layers=1)
    in_region[unit_of[l][np.flatnonzero(cell_region)]] = True

region, total = int(weight[in_region].sum()), int(weight.sum())
share = region / total
uw.pprint(f"RES h={H} k={K} width={WIDTH} addon_levels={len(addon)} "
          f"region={region} of {total} share={100 * share:.1f}% ceiling={1 / share:.2f}x")
