# UNFILED 60: the ribbon's wall refusal gives its numbers

Branch bugfix/placement-wall-clearance-message, commit 7fe58f8f on development fbef72fa.
Not pushed (GitHub pause). Patch: 0001-*.patch here.

## Change
The two ribbon sites in `_place_thin_volume_2d` (place_surface.py, the conform fill and the
per-cavity ring) now raise `_wall_refusal_2d(ring, X, on_wall, d_skin, h_vertex, clearance,
width)`. The message gives:
- the wall vertex the ring touched;
- the cavity's reach, the largest skin distance of any ring vertex;
- the nearest wall vertex's skin distance;
- the two terms of the carve's reach at that vertex;
- the move that would clear it (reach minus wall), and the lever: clearance or the cell size
  when clearance x h governs, the band width when 0.6 x width governs.

The check itself is unchanged. "reached the domain wall" is kept, because the drivers' retry
list matches it (annulus_faults.py:735, p_893_k1.py:120).

Example (cell 0.05, interior ribbon of width 0.1 whose top is at radius 0.9):
"the ribbon's cavity reached the domain wall at (0.1467, 0.9892): the cavity reaches 0.112
from the band's skin and the nearest wall vertex is 0.0335 from it. The carve takes the cells
within max(clearance x h = 0.0348, 0.6 x width = 0.06) of the skin there, ... move it about
0.0786 further from the wall, or narrow the band, whose width sets the carve here"

## Review
- Parallel: both sites are inside the surgery rank's try block, whose failure string is
  all-gathered, so the helper is rank-local with no collectives. Not run in parallel.
- The wall distance is to wall vertices, not edges, so it is an upper bound on the true
  distance by up to half a wall edge. The message says "nearest wall vertex".
- "move it about X": X assumes the cavity keeps its reach. It is a guide, not a guarantee. At
  top 0.85 the advice said 0.025; at 0.82 the trace then reached the INNER wall, and the
  message named the inner wall point (-0.049, 0.498), as it should.
- Other refusals with the same clearance wording are not touched: place_sheet (2584, 1962),
  removal (7035), 3-D (5363), the volume interior check (7909), and the "strand a domain-wall
  vertex" refusal. add_fault goes through place_sheet, so its wall refusals stay terse. That
  is the next candidate if wanted.

## Test
tests/test_0865_place_ribbon_wall_refusal_numbers.py (level_1, tier_b, 2.5 s). It fails on
development (the message has no numbers) and passes here with hard baselines reach 0.112 and
wall 0.0335, at 3 significant figures as printed. Placement tests 0853, 0855, 1090, 1091, 1022
and 1097 all pass (63 passed, 1 skipped).

## Tolerances
None beyond the printed rounding: the baselines are the message's own 3-significant-figure
numbers, compared exactly.

## Second commit, 22fb2614: place_sheet (C1: "yes to place_sheet next")
place_sheet is 3-D only; 2-D add_fault goes through line_cut. "Leave the 3-D placement" was read
as the 3-D thin volume (place_surface.py ~5363), which this commit leaves unchanged.

- `_closed_shell_3d` (shared by the sheet and the 3-D thin volume) keeps its message text. At the
  wall refusal it attaches `wall_face`, `drop` (the cavity's cells) and `rounds` to the
  exception. The 3-D thin volume is otherwise untouched (test_0855 passes).
- The sheet carve catches it and raises `_sheet_wall_refusal`. The original text leads, so
  fault_split's `"wall" in str(err)` and the tests' "domain wall" matches still hold. No campaign
  driver matches on sheet errors (grep of uw3-campaigns: the only retry lists are the 2-D
  ribbon's).
- Numbers: the cavity's reach is the largest exact sheet distance of any vertex of a dropped
  cell. The nearest wall vertex is taken over non-outcrop wall vertices, with a bounded exact
  distance (cutoff 2 x reach; the touched vertex is always inside it). The carve terms are
  clearance x h at the touched vertex and 0.6 x the largest diameter of the dropped cells
  around it. The lever is clearance if clearance x h >= 0.6 x diameter, otherwise cell size.
- Probe (p_sheet_wall.py): flat 0.4 x 0.4 sheet in a unit box, cells 0.11. It is refused at
  z = 0.98-0.80 and places at 0.76. At 0.95 / 0.87 / 0.80 the message gives a reach of
  0.245 / 0.227 / 0.261 against a wall at 0.05 / 0.13 / 0.20, and asks for 0.195 / 0.097 /
  0.061 more. 0.80 - 0.061 = 0.74, but 0.76 already places, so the advice
  over-asks by about 0.02 here. It errs on the safe side, as a guide should. Growth rounds were 0 in all three:
  the reach is the carve (0.111) plus the dropped cells' outer vertices, about one cell.
- Test: tests/test_0868_place_sheet_wall_refusal_numbers.py (level_1, tier_b, 3 s), the z = 0.87
  fixture. Baselines are reach 0.227, wall 0.13 and the lever "refine the mesh near it".
- Both new tests were run against development's place_surface.py (swapped in, rebuilt): both
  fail with the old text. Restored and rebuilt: both pass. Placement and sheet tests 0853, 0854,
  0855, 0865, 0867, 0868, 1090, 1091 and 1174: 98 passed, 1 skipped.
- Not changed: the sheet's "strand a domain-wall vertex" refusal (~1962). No fixture reaches it
  here, and changing it without a failing test is against the rule.
- For H1 at np 2 (C1's check): the message is formatted only on the surgery rank and then
  all-gathered as a string, so every rank should raise identical text. To confirm, run test_0865
  and test_0868's fixtures under mpirun -n 2 and compare str(err) across ranks.

## Round 2 (Linux server review: changes requested), commit 0a9d08fc
1. High: test_0865 failed on Linux (0.107 against 0.112). Both tests now assert relations: reach >
   wall, the wall in a band, reach >= the largest carve term, and the lever text. No
   partition-dependent term is pinned.
2. Medium: "conservative" was wrong and is gone. The move is "at least about X (a guide: the
   cavity is re-cut at the new position)". `follow.py` follows the messages to placement in two or
   three steps (numbers in the PR body). Predicted width and cell-size targets were tried
   (`check_targets.py`) and failed (a ribbon of width 0.025-0.03 and a sheet with cells of
   0.08-0.11 were still refused at the same position), so the message names the width where
   clearance x h takes over instead of predicting a target.
3. Lows:
   - empty or out-of-range wall sets are reported in words, so the phrase survives;
   - the nearest wall vertex is named as such;
   - the units are mesh units;
   - nothing partition-dependent is asserted.

Placement and sheet tests 0853, 0854, 0855, 0865, 0868, 1090, 1091: 67 passed, 1 skipped.
