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
