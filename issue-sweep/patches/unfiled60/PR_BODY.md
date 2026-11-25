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

Not changed: the same wording in `place_sheet` (and so in `add_fault`), the 3-D placement and
the removal.

Underworld development team with AI support from Claude Code
