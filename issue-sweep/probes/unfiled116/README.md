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
