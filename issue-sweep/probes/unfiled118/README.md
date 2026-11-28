# Row 118: the fill ring dumped from the seam-conforming hang (UNFILED 111 round 2)

`fill_rank1_0.npz` holds the inputs that the rank which hung handed to `_gmsh_fill_2d`: `Xall` (vertex coordinates), `ring` (the cavity ring, 30 vertices) and `holes` (one hole, the band skin, 24 vertices). `fill_rank0_0.npz` is rank 0's fill from the same run (ring 11, no holes), kept for comparison.

**Where it came from.** UNFILED 111 round 2, head 03730af5 (0001-0003 on UNFILED 60 at 02f34664), seam-conforming path (`mesher="network"`, `seams="conform"`). np 3, dip 30, cellsize 0.05 (h = 0.025), top at theta 60 degrees, k = 2.5 (a gap of 0.61 cells). Rank 1 hung in gmsh (`GFaceInitialMesh` / `robustPredicates::orient2d`) while ranks 0 and 2 waited in an Allgather. `dump-run.log` is the run's log, with the supervisor's report. The same hang occurred at k = 2.196, but that run was not dumped.

**What it shows** (`analyse_fill.py fill_rank1_0.npz`):
- the ring does not cross itself, and neither does the hole (`_loop_self_crossings` = 0);
- the ring and the hole share no vertex;
- one ring edge, (39, 1356), a chord from a wall vertex at r = 1, crosses two edges of the hole: (1833, 1801) and (1820, 1821).

**Command.** Reconstructed from the run scripts: the run used the dump variant of the probe, which wraps `_gmsh_fill_2d` and saves its inputs to `$DUMP_FILL`. Run from a working directory, with the UNFILED 111 round-2 overlay first on `PYTHONPATH`:

    DUMP_FILL=<dir> python scripts/mpi_supervisor.py --silence 180 -- \
      mpirun -n 3 --bind-to none python -X faulthandler p_nearsurface_split_dump.py \
      --dip 30 --cellsize 0.05 --k 2.5 --mesher network --seams conform --theta 60

The job hangs. The dump is written before the fill, so the supervisor or an outer `timeout` ends the job afterwards.

Underworld development team with AI support from Claude Code

## W1's reading of the dump (2026-11-28)
- The ring (30 vertices) contains NO band vertex (band ids are 1801 and up; the ring's
  largest is below that). So the skin was not spliced into this rank's ring: no crossing
  span was paired with skin run ends.
- The chord (39, 1356) joins two OLD vertices: 39 on the wall (r = 1), 1356 inside
  (r = 0.872). It is 0.135 long, 5.4 times the median ring edge. It is therefore the
  straight connector `_conform_fill_loops_2d` puts across a span it judged NOT crossed by the
  band (`link(v1, v2)`): the seam span from 39 to 1356, whose vertices were victims.
- Mechanism: the crossing test (`_edge_meets_band`) runs only on the span's seam edges.
  The seam path skirts the band's tip without crossing it (its vertices within the carve's
  reach, so deleted), and the straight connector between the span's surviving ends cuts
  across the tip: the two hole-edge crossings H1 found. Nothing in this needs a wall; any
  band tip near a seam can do it. 111's wall rings made it reachable here.
