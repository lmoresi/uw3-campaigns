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
