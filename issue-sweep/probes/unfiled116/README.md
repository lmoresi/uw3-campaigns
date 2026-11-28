# UNFILED 116: slivers on the outcrop path, measured

Library: a stack of 111 (0001-0003), 113 and 114 on development fbef72fa, merged locally, so that
the dip-15 outcrops place. Fixture: H1's annulus (p_nearsurface_split.py), ladder ribbon, width
2h, margin 2, clearance 0.3, split.

Sweeps (h025-dip*.log: dips 10/15/20/30/45/60, k 0.05-2.55 in 0.1 steps; h0125-dip*.log: dips
15/30/45, k 0.1-2.5 in 0.2 steps). Smallest angle over all cells, outcrop placements only:

| h, dip | outcrops | < 5 deg | < 10 deg | < 15 deg | median |
|---|---|---|---|---|---|
| 0.025, 10 | 10 | 8 | 10 | 10 | 3.6 |
| 0.025, 15 | 14 | 12 | 14 | 14 | 2.4 |
| 0.025, 20 | 16 | 7 | 15 | 16 | 5.8 |
| 0.025, 30 | 19 | 2 | 10 | 12 | 9.1 |
| 0.025, 45 | 21 | 4 | 9 | 12 | 10.9 |
| 0.025, 60 | 22 | 4 | 7 | 10 | 15.9 |
| 0.0125, 15 | 8 | 3 | 7 | 7 | 5.7 |
| 0.0125, 30 | 9 | 1 | 4 | 5 | 14.0 |
| 0.0125, 45 | 11 | 2 | 4 | 5 | 18.9 |

The angle does not follow depth or gap smoothly: neighbouring depths give 0 and 30 degrees.
Interior placements in the same sweeps stay at 20-35 degrees.

Mechanism (worst.py, the worst cell of five of the worst points): in every case, a fill cell
outside the band, with two vertices exactly on the wall polygon. One is an original wall vertex;
the other is the outcrop's new wall vertex, where the band's clipped edge meets the wall. They are
0.012-0.032 h apart (0.087 h for the 11.9-degree dip-60 case), and the third, interior vertex
closes a sliver. So the angle depends on how close the band's wall crossing falls to a kept wall
vertex, which varies erratically with depth.

## Experiment (ii), first round (exp_snap.diff on the stack, UW_EXP_SNAP=s)
- The snap aims each cap rail at a wall vertex within s local edge lengths of its crossing. With
  the snap on, cap edges on the wall also carry no interior node.
- Dip 15, h 0.025, k 0.15-1.55: s = 0.25 fires 16 times (moves 0.004-0.24 of an edge) but leaves
  the smallest angles at 0.1-9.3 deg. s = 0.5 lifts some (k 0.7: 4 -> 10 deg; k 1.2: 2.4 -> 8.1)
  but leaves 0.1-0.5 deg at k 0.15, 0.35, 0.55, 0.75.
- The remaining worst cells keep the same shape: a band vertex on the wall polygon 0.008-0.041 h
  from an original wall vertex. At dip 15, k 0.3 (dbg.txt) that vertex (x = -0.0239) is NOT a
  rail crossing: the rails cross at x = +0.081 and -0.104, and both were snapped. It is a band
  vertex between them, on the wall.
- Ruled out: _snap_to_boundary_2d (tol 1e-9); _compress_collinear_loop dropping annulus wall
  vertices (252/252 and 504/504 kept).
- Not yet known: which step puts a band vertex on the wall between the crossings, 0.04 h from a
  wall vertex.

## Experiment (ii) + rail reach + cap margin (a), margin rows only: the comparison (checks/)
compare.py places each point with the experiment off, then on (UW_EXP_SNAP 0.5, UW_EXP_CAP_CELLS
0.25, UW_EXP_MARGIN_ROWS 2), and compares them. checks/summary.txt has it per dip. In short:
- Smallest angle over all cells, outcrops: medians up (h 0.025: dip 15 9.1, dip 30 21.5, dip 45
  24.4, dip 60 28.3), but the worst cases are still 0.3 (dip 15), 0.5 (dip 20), 1.4 (dip 10) and
  2.6-5.3 (dips 30-60). No setting brings every outcrop to 20 deg.
- Wall: every vertex on the base polygon (0.0e+00), no label missing. Interior placements:
  bit-identical at every point (37 of 37).
- Fault identical (fault vertex set and pairing) wherever the trace's top row is outside the cap.
  Where the cap meshes the fault's top segment ("fault in cap"): every fault node on the trace to
  <= 5.7e-15, Plus/Minus paired exactly, node count changes by -5..+2, shortest fault edge
  0.05-1.0 cells before and 0.07-1.0 after (coarser at dips 45/60, mixed at 15-30).
- New refusals with the experiment on: dip 10 k 0.45-0.65 ("the zone meets the domain
  boundary"); k 0.05 at dips 30/45/60 (assembly / pull_vertex_onto). These are side effects of
  the rail reach or cap changes, not investigated.
- Not identified: the mechanism of the residual worst cells (below about 15 deg).

## The residual worst cells (C1, 2026-11-28; residual.py on the experiment stack)
The three worst outcrops after snap + rail reach + margin-row cap margin were unchanged by the
experiment: dip 15 k 0.15 (0.32 deg), dip 20 k 0.95 (0.53), dip 10 k 0.85 (1.40). Each worst cell
is the same construction:
- two consecutive BASE wall vertices (a wall edge, length 1.0 h);
- the rail+ point of a TRACE row of the ladder (rows 6, 2 and 3), 0.005 / 0.006 / 0.020 cells
  inside the wall, near the middle of that edge.
The fill joins the rail point to the wall edge beneath it: a triangle with angles about 1, 178 and
0.3-1.4 degrees. This is cause 3 (a rung on the wall), on a trace row. The margin-row restriction
(kept so the fault's vertices do not change) excludes it.
