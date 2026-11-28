"""Row 125: how much of the mesh a placed ribbon's region is.

place_fault_ribbon_2d(seams="gather") partitions the host with partition_addon
for the bands' region (_ribbon_region_marks, layers=2) and the placement then
moves nothing. Here, in serial, the same marks and the same growth layers on the
science hub's annulus (zg95_lid_regimes: unit depth, r_i / r_o = 0.55, cellSize
uw_cell with uw_refinement levels, rung spacing S = one base cell, band width
W = 2 S, clearance 0.7, margin_rings 1), with a straight trace dipping
uw_dip degrees from 3 S below the surface to uw_depth. Prints the region's
share of the finest cells: the share the owner rank must hold however many
ranks there are.

    python placement_region_fraction.py -uw_refinement 5 -uw_faults 1
"""
import numpy as np

import underworld3 as uw
from underworld3.utilities.place_surface import (_extend_polyline_2d, _region_cells,
                                                 _ribbon_region_marks)

params = uw.Params(
    uw_cell=uw.Param(0.5, description="base cellSize (layer depths)"),
    uw_refinement=uw.Param(5, description="refinement levels"),
    uw_dip=uw.Param(45.0, description="trace dip (degrees)"),
    uw_depth=uw.Param(0.35, description="lower tip depth (layer depths)"),
    uw_faults=uw.Param(1, description="traces, 20 degrees apart"),
    uw_gap=uw.Param(20.0, description="angle between traces (degrees)"),
)
RATIO = 0.55
r_o, r_i = 1.0 / (1.0 - RATIO), RATIO / (1.0 - RATIO)
mesh = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=float(params.uw_cell),
                          refinement=int(params.uw_refinement), qdegree=3)
S = float(params.uw_cell) / 2 ** int(params.uw_refinement)
W = 2.0 * S


def trace(theta0):
    """From 3 S below the surface at theta0, dipping into the annulus, to uw_depth."""
    dip = np.deg2rad(float(params.uw_dip))
    depth = np.arange(3 * S, float(params.uw_depth) + 0.5 * S, S * np.sin(dip))
    r = r_o - depth
    # horizontal run along the arc: depth / tan(dip), as an angle at each radius
    theta = theta0 + (depth / np.tan(dip)) / r
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])


paths = [trace(np.deg2rad(90.0 + k * float(params.uw_gap)))
         for k in range(int(params.uw_faults))]
extended = [_extend_polyline_2d(P, 1) for P in paths]
spacing = [float(np.linalg.norm(np.diff(P, axis=0), axis=1).mean()) for P in paths]
marks = _ribbon_region_marks(mesh.dm, extended, W, 0.7, spacing, "ladder")(mesh.dm)
cell_region, _canon, _regions = _region_cells(mesh.dm, marks, layers=2)
cS, cE = mesh.dm.getHeightStratum(0)
n = cE - cS
for k in sorted(set(cell_region[cell_region > 0].tolist())):
    m = int((cell_region == k).sum())
    uw.pprint(f"RES refinement={params.uw_refinement} h={S:.4g} W={W:.4g} "
              f"faults={params.uw_faults} region={k} cells={m} of {n} "
              f"share={100.0 * m / n:.2f}% ranks_before_it_exceeds_the_mean={int(n / m)}")
m = int((cell_region > 0).sum())
uw.pprint(f"RES refinement={params.uw_refinement} all regions {m} of {n} "
          f"({100.0 * m / n:.2f}%)")
