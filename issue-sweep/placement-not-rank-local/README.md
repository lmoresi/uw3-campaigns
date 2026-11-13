# A parallel fault placement refused as "not rank-local"

Not filed as an issue: it has not been reproduced on `development`.

## What was seen

A 2-D split fault placed with `uw.meshing.FaultNetwork.build(..., realisation="split",
mesher="ladder", max_levels=0, margin_rings=1, carve_clearance=0.7, seams="gather")` on a
focused annulus (4 km cells in a 1,500 x 700 km box, 304,064 cells, 26 ranks, a Linux
cluster under Slurm) stopped with

    addon_partition: 2 cell(s) of a surgery's result lie in no local cell of the mesh
    it was made from; the surgery was not rank-local.

The library was underworld3 at 80d3ebe9 (2026-11-08). The same fault placed with a wider
band or a second margin ring, and the campaign driver retries on this message.

## What reading the code gives (nothing here was run at more than one rank)

- The message comes from `addon_partition.inherit_provenance(child, host)`. It locates
  every cell centroid of the result in the local cells of the mesh the surgery started
  from, and it runs only when `partition_addon` moved cells beforehand.
- Three calls on this path can raise it: after the band placement
  (`place_surface.place_fault_ribbon_2d`), after the cut (`fault_split.add_fault`) and
  after the split (`fault_split.split_fault`). The last two run again for each coarse
  level the split is replayed on. The cut partitions a second time before it starts.
- The band placement partitions first (`partition_addon` with `mark_band`, two layers) so
  that the placement's own gather (one layer) moves nothing. By reading, the placement's
  marks lie inside the partition's: the placement marks vertices within
  `max(clearance h, 0.6 width) + h` of the band's skin, the partition within that plus one
  band width of the band's path, and the cell size `h` at a vertex is reconciled across
  ranks. So reading does not give a mechanism.
- 80d3ebe9 is older than four changes to this path that are on `development`: the pull of
  a vertex onto the trace near the domain boundary (#1089), the as-built record that
  rewrote `inherit_provenance` (#1091), the second `add_fault` (#1099) and the collective
  failures of the winding vote (#874, in part).

## The trace

`trace_placement.py` wraps four library functions in memory (no library edit) and prints,
in order: each partition and what it moved; each gather and what it moved, and, when a
gather after a partition moves cells, the vertices it marks that the partition's rule does
not; each redistribution; and, before a check that would refuse, each refused cell with
its rank, centroid and vertices, the rank whose host cell holds it, and whether that host
cell is the same cell or a different one.

    import trace_placement
    trace_placement.install()      # on every rank, before FaultNetwork.build

It answers:

1. Which of the three checks refused.
2. Whether any gather or redistribution ran between the partition and the check, and how
   many cells it moved. By design none should.
3. Whether each refused cell changed rank (the same cell is in the host on another rank)
   or is a new or reshaped cell whose centroid fell across a rank boundary.
4. With the same script on current `development`: whether it still refuses.

Checked on one rank only (macOS, 12-core Apple M4, conda-forge PETSc 3.25.3): the
placement builds the same mesh with and without the trace (444 cells, 256 vertices on the
small box of `tests/test_0858`), and both reports run. On one rank no cell is ever
refused and nothing is moved, so the reports' content at more than one rank is untested.

Underworld development team with AI support from Claude Code
