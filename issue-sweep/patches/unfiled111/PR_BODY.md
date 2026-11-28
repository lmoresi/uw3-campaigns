An interior ribbon whose cavity runs along a domain wall is placed; only a sliver's gap is refused

## What was wrong
`place_fault_ribbon_2d` (through `place_thin_volume`) refused a ribbon whose band ended a few
cells below a domain wall: "the ribbon's cavity reached the domain wall; the volume must be
interior, with clearance to spare". Such a band neither reached the wall, so it could not be
placed as an outcrop, nor cleared it by the carve's reach plus a cell, so it could not be placed
as interior. On an annulus with a ladder ribbon 2 cells wide, every band whose highest corner lay
between 0 and about 2 cells below the wall was refused, at dips of 15, 30 and 45 degrees and at
two cell sizes. A slab model with 10 km cells lost fault tops at about 42 and 55 km, the middle
of its dip scan.

## What changes
- **The cavity may run along the wall.** The wall's vertices are already protected from the
  carve, so the cavity's ring runs along existing wall edges, and the rebuild keeps them and their
  labels. The blanket refusal is removed on both the gathered and the seam-conforming paths.
- **A sliver's gap is still refused.** The cells filled in between the band's skin and the wall
  are a strip of the gap's width. Below 0.3 of the wall's cells (`_MIN_WALL_GAP_CELLS`) the
  placement is refused, with the gap in cells and in mesh units and both ways out: move the band
  further from the wall, or closer, so that it reaches the wall and is placed as an outcrop.
- **The reach-and-distance message** added for this refusal (`_wall_refusal_2d`) could no longer
  fire, since every such case now places or gets the gap message, so it is removed here. The 3-D
  sheet's wall message is unchanged.

## Tolerances and thresholds
- **0.3 cells.** Measured smallest angle of the cells between skin and wall, against the gap g
  (annulus, dip 30, h = 0.025): 1.0 degree at g = 0.01 h, 8.5 at 0.11 h, 15.7 at 0.21 h, 22.5 at
  0.31 h, 34.6 at 0.51 h, and 32-39 degrees (as a deep placement, 38.3) from about 0.5 h on. Dips
  15 and 45 and h = 0.0125 give the same shape.
- **The cell size h** is the mean length of the ring's wall edges at the wall vertex nearest the
  band (that vertex's own size when no ring edge lies on the wall), not the mesh's nominal size,
  so a graded mesh is judged by its cells at the wall.
- **The gap g** is the smaller of the wall vertices' distance to the skin and the skin vertices'
  distance to the ring's wall edges.
- No coordinate matches.

## Parallel
The gap and the decision are computed by the rank whose cavity reaches the wall, from that
cavity's ring and the whole band's skin (every rank holds the assembly), and a refusal goes
through the placement's existing failure gather: every rank raises the same message or none
does. On the seam-conforming path each rank decides on its own cavities and the same gather
agrees the outcome.

## Tests
- **test_0904** (tier B, level 2), annulus fixture at h = 0.025 and 0.0125:
  - bands 2.5, 3.0 and 3.5 cells below the wall are placed inside, the wall keeps its labels, the
    fault is split, and the smallest angle of the cells beside the wall is at least 0.8 of the
    same ribbon placed deep (k = 6) on the same mesh;
  - a band 1.95 cells below is refused, and the gap the message gives in cells is within 0.05
    cells of the band corner's distance from the wall;
  - a box corner, where the cavity runs along two walls, keeps both walls' labels and the corner
    vertex.
  All nine fail before the change.
- **test_0865**: its fixture (a gap of 0.67 cells) is now placed, and the wall keeps its labels.

Measured before the PR: H1's sweeps (dips 15/30/45, k 0-6, h = 0.025; dip 30 at h = 0.0125) on
this branch stacked with the cut-labelling branch; a box-corner sweep (18 placements, every wall
edge labelled, the corner vertex kept); the placement and fault suites.

## Left open
- The outcrop path on the dip-15 fixture: "the fill ring crosses itself" for bands just crossing
  the wall, and the assembly's area check against a curved wall at k = 0 (tracked separately).
- A box-corner band that outcrops through one wall while its cavity reaches the other is refused
  ("only a one-band outcrop is built"), as before.

Underworld development team with AI support from Claude Code
