# UNFILED 111: an interior ribbon beside a wall (ruling B2, interim, Louis to confirm)

One commit (0001), stacked on UNFILED 60. Apply 60's 0001-0004 on development fbef72fa, then this.
Local branches: bugfix/ribbon-wall-refusal-numbers (60), bugfix/ribbon-interior-beside-the-wall
(111, head cffdad86). PR text: PR_BODY.md.

C1's conditions:
1. Global: the rank whose cavity reaches the wall decides, from its ring and the whole skin;
   the placement's failure gather agrees the outcome. Owed: H1's np 2-3 on both paths.
2. h is the mean wall-edge length at the nearest wall vertex, held in _MIN_WALL_GAP_CELLS = 0.3,
   whose comment gives the measured angles.
3. Box corner, before the PR: p_box_corner.py, stack-logs/box-corner.log. 17 placements, all
   with walls labelled and the corner vertex kept. One refusal, a = 2, b = 4: an outcrop through
   Top whose cavity reaches Right. That is the outcrop path's existing one-band limit, untouched.
4. test_0904 checks the refused gap in cells against the geometry, within 0.05 cells.
5. The stack (this + labels70-22 0011, merged locally) is in stack-logs/:
   - H1's sweeps at dips 15/30/45, k 0-6, h 0.025, and dip 30 at h 0.0125: every g >= 0.3 h
     places, walls labelled; g 0.11-0.12 h is refused with the gap; outcrop-side outcomes unchanged;
   - the 44 placement/fault test files (test_0858 excluded): 372 passed.

Fail-first: test_0904's nine cases all fail on 60's build.
test_0865 (60's) changes: its fixture (gap 0.67 cells) now places, so the test asserts that it
places and keeps the wall's labels. 60's ribbon message no longer fires; its sheet message stands.

## Review fold-in (H1 at np 2): 0002
test_0904's box corner counted the corner vertex per rank and failed on rank 1 at np 2. It now
counts owned vertices only (ghosts excluded through the point SF, none in serial), summed over
the ranks. _inspect also reduces its counts (sum) and the smallest angle (min), so every rank
asserts the same. Serial: test_0904 + test_0865, 10 passed. Owed: H1's np 2 re-run of test_0904.

## H7's lows: 0003
L1: wall edges, and so h, come only from true domain-boundary edges (built on demand where a
ring meets the wall), so a corner chord no longer inflates h.
L2 + L3: test_0904 gains bands just past the floor, 0.31 cells (h 0.025, k 2.2) and 0.37 cells
(h 0.0125, k 2.25). Both must place with walls labelled, and the smallest angle over ALL cells
must be >= 0.5 x the deep placement's (measured 22.5 and 24.3 deg against about 38). A fixed
0.0075 mesh-unit threshold refuses the 0.37-cell case (0.0046), so H7's mutant now fails.
Serial: test_0904 + test_0865, 12 passed. The conform-path partition question waits on H1's
0.28-0.33-cell sweep.

## H1 r2 (conform hang, partition dependence): 0004, the fallback
The seam-conforming path refuses a cavity along the wall again: a RuntimeError inside the failure
gather, so no rank enters gmsh. The message names seams='gather'. 111's placement stands on the
gathered path, the default of place_thin_volume and place_fault_ribbon_2d, and of the slab
driver's -uw_fault_seams. So the science hub's case is still fixed.
MEDIUM (2): wall edges need both ends to pass _true_wall_vertex_mask (seam edges excluded). The
conform path no longer reaches _wall_gap_2d at all.
LOW: tests/parallel/test_0904_place_ribbon_beside_the_wall_parallel.py (np 2-3, theta 60, k
2.196 and 2.5) checks that gather places, conform refuses with the remedy, and every rank agrees.
It is in scripts/test.sh. Serially (np 1, where conform takes the gathered route) both place.
Serial test_0904 + test_0865: 12 passed.
For a new row: the conform-path defects (the 5.4-cell chord at the seam; theta 15 partition
dependence; seam faces in _boundary_edges).
