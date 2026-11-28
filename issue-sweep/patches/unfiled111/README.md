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
