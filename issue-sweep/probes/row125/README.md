# Row 125: the fault-region partition and the solve

## Question 1: does the solve inherit the owner-holds-region partition? Yes, by reading.
- add_fault (fault_split.add_fault, about line 1754 on development fbef72fa)
  calls partition_addon once, before the cut. Its docstring says "The cut and
  the splits then move nothing."
- partition_addon gives each region to one rank, the argmax of region weight
  (addon_partition.py about 930). _peel_balance then moves only free units,
  `free = unit_region == 0` (about 590).
- Nothing redistributes between the split and the solve. The base levels never
  move ("load fixes go on the child").
- The unit is a cell of the coarsest add-on level with all its descendants, and
  mark_polylines marks one local cell diameter around the trace on every level.
  So at k 3 the region takes most of the refined band. In H1's row 124 sweep it
  holds 1115 of 2006 finest cells, 56 % of the mesh. At np >= 2 no balance
  within the rule can bring that rank to the mean.

## Question 2: what does that cost? Driver split_solve_timing.py
Three arms on the same adapt k 3, h 0.1 mesh, with the same Stokes solve
(simple shear on the walls plus a buoyant blob):
- plain: as adapt partitions it;
- region: after partition_addon for the trace, the same cells;
- fault: add_fault, frictionless.
The timed solve is the second one, from zero. Counts come from solve_report on
every arm. plain against region is the partition's cost alone. fault adds the
split and the rotated solve path. That path also costs about 3.8x in serial
(0.50 s against 1.90 s here), so the fault arm is compared with its own serial
time, not with plain's.

Serial smoke runs on the laptop, k 3 h 0.1:
    plain  cells 1764 timed 0.505 s velocity 25 pressure 12
    region cells 1764 timed 0.507 s velocity 25 pressure 12
    fault  cells 2006 timed 1.903 s

## Question 3 (C1): do the science hub's placement paths share it? Same rule, small regions
- place_fault_ribbon_2d(seams="gather") calls partition_addon on the host with
  the bands' own marks (_ribbon_region_marks, layers=2), before the placement
  (place_surface.py about 9539). The region goes to one rank, the free cells
  are peeled, and nothing moves after it. So it is the same mechanism.
- The difference is the unit. The zg95 drivers place into a copy of a base
  level, which has no add-on levels below it, so a unit is one finest cell and
  the region is just the band's footprint at the host's own cell size.
- place_thin_volume called directly (3-D, or 2-D without the ribbon wrapper)
  uses _gather_regions instead. It moves only the region's cells, with no peel,
  so the owner keeps its own share plus the region.

placement_region_fraction.py: serial, annulus r_i/r_o 0.55, cellSize 0.5,
S = one base cell, W = 2 S, clearance 0.7, margin_rings 1, a 45-degree trace
from 3 S below the surface to depth 0.35:
    refinement 4 (h 0.031): one band 594 of 31744 cells = 1.87 %
    refinement 5 (h 0.016): one band 1107 of 126976 = 0.87 %
    refinement 5, four bands 20 or 11 degrees apart: four separate regions,
      0.8-1.1 % each, 3.8-3.9 % together
The share halves with each refinement, since the band is a fixed number of
cells wide. A region exceeds the mean share at about 1/share ranks: 53 at
refinement 4, about 100 at 5, about 200 at 6. The runs on 26-52 ranks are
inside that, unless one rank owns two regions.
