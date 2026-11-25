## The ribbon's wall refusal says how much clearance is missing

When a placed ribbon's cavity reaches the domain wall, the placement refuses it (#549, #670).
The message said only that "the volume must be interior, with clearance to spare". It now
gives:
- the wall vertex the cavity touched;
- how far the cavity reaches from the band's skin;
- how far the nearest wall vertex is from the skin;
- the two terms of the carve's reach there, clearance x h and 0.6 x width;
- roughly how far to move the band, and which parameter to change, chosen by whichever term
  governs.

The check is unchanged, and so is the phrase "reached the domain wall", which drivers match
to retry with other margins.

Test: `tests/test_0865_place_ribbon_wall_refusal_numbers.py` (level_1, tier_b). The fixture is
an interior ribbon 0.1 from the outer wall of an annulus with cells of 0.05. The test fails on
development, whose message has no numbers. It asserts the printed reach (0.112) and wall
distance (0.0335) exactly as printed, to 3 significant figures; there are no other tolerances.

`place_sheet` (3-D) gets the same treatment. Its "the sheet's cavity reached the domain wall away
from the outcrop" now gives:
- the wall vertex touched;
- the cavity's reach from the sheet;
- the nearest wall vertex's distance from the sheet;
- the carve's two reaches there (clearance x h, and 0.6 x the cell diameter for the centroid
  rule);
- any growth rounds the shell took;
- the lever, either clearance or the mesh's cell size.

On a unit box with cells of 0.11, a flat sheet 0.13 below the top wall is refused. The message
now says that the cavity reaches 0.227 and that the cells, not clearance, set the carve. Test:
`tests/test_0868_place_sheet_wall_refusal_numbers.py` (level_1, tier_b), which fails on
development. It asserts the printed reach (0.227) and wall distance (0.13) exactly as printed,
to 3 significant figures. The shared shell builder keeps its text, so the 3-D thin volume's
refusal is unchanged.

The suggested move is a rough guide that errs on the safe side, and the message says "about".
With the sheet at z = 0.80 it asks for 0.061 more clearance, which puts the sheet at z = 0.74; a
sheet at z = 0.76 already places.

Not changed: the 3-D thin volume, the removal, and the stranded-wall-vertex refusals.

Underworld development team with AI support from Claude Code
