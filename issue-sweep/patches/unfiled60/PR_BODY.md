## The placement's wall refusals say how much clearance is missing

When the cavity carved around a placed ribbon (2-D) or sheet (3-D) reaches the domain wall, the
placement refuses it (#549, #670). The message said only that "the volume must be interior, with
clearance to spare" or that "the sheet must clear the other walls". It now gives, in mesh units:
- the wall vertex the cavity touched;
- how far the cavity reaches from the band's skin or the sheet;
- how far the nearest wall vertex is from it;
- the two terms of the carve's reach at the touched vertex;
- what to change: a move of "at least about" a distance, or the governing term's lever (narrow
  the band, reduce clearance, or refine the mesh). For the ribbon, the message names the width
  below which clearance x h takes over as the carve.

The check is unchanged. The original phrase leads both messages, because drivers match "domain
wall" to retry with other margins and `add_fault` matches "wall". An empty set of wall vertices,
or none within the bounded distance, is reported in words, so the phrase survives. At np 2 and 3
the message is identical on every rank (Linux server review): it is formatted on the surgery rank
and all-gathered.

The suggested move is a guide, not a guarantee: the cavity is re-cut at the new position, and its
reach changes. Followed step by step (`follow.py`, moving away from the wall each message names):
- the sheet places in two moves, 0.87 to 0.773 to 0.748 (on the Linux server 0.773 is refused
  too, and the second message places it);
- the ribbon at width 0.1 does not place by moving alone. Moving away from one wall carries the
  cavity onto the wall across the band (0.9 to 0.821 is refused at the inner wall). When a wall
  far from the touched one lies within the cavity's reach plus the suggested move, the message
  says so and says to narrow the band first, to the width where clearance x h takes over the
  carve (0.058 here, 0.0572 on the Linux server, whose clearance x h is 0.0343 against 0.0348).
  Narrowed once and then moved 0.036 away from the outer wall (top 0.864), it places. Followed
  literally, the second message asks to narrow again (to 0.0507 on the Linux server), because the
  cell size at the new touched vertex is smaller. That step does not shrink the reach, and the
  move after it places the band, so the literal path takes three steps.

No predicted target is given for the width or the cell size: predictions were tried and missed
(a ribbon narrowed to 0.025-0.03, and a sheet with cells of 0.08, were still refused). The
numbers above are examples from the test fixtures.

Tests:
- `tests/test_0865_place_ribbon_wall_refusal_numbers.py`: an interior ribbon about 0.03 from the
  outer wall of an annulus;
- `tests/test_0868_place_sheet_wall_refusal_numbers.py`: a flat sheet 0.13 below the top of a box.

Both are level_1, tier_b, and both fail on development, whose messages carry no numbers. They
assert relations rather than one mesher's numbers. Gmsh on Linux places the annulus's wall vertices
about 1.5 % differently, and the reach reads 0.107 there against 0.112 on macOS. The relations:
- the reach exceeds the wall distance;
- the wall distance lies within a band (0.02-0.05 for the ribbon; 0.13 to 1e-3 for the sheet,
  whose wall vertices lie at z = 1 on any mesh);
- the reach is at least the largest carve term;
- the lever's text.

Tolerances: the bands above. The touched vertex and the carve terms, which differ between rank
counts, are not asserted.

Not changed: the 3-D thin volume, the removal, and the "strand a domain-wall vertex" refusals.

Underworld development team with AI support from Claude Code
