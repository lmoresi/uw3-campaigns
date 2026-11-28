# UNFILED 115: an outcrop beside a second wall, plus the outcrop sliver warning (C1's ruling after 116 was parked)

One commit, on 111's head (apply 60, then 111's 0001-0007, then this).

- The off-band refusal on the outcrop path ("only a one-band outcrop is built") becomes 111's gap
  rule toward the second wall, with 111's partial-ring gate in front.
- place_fault_ribbon_2d warns when a cell beside the wall where an outcropping band meets it has a
  smallest angle below 5 degrees (_OUTCROP_SLIVER_DEG). The minimum is taken over the ranks and
  printed once (uw.pprint), and recorded as info["outcrop_min_angle"]. A split fault's side
  vertices are excluded from the wall mask: they are boundary after the split, and a fault is
  strictly interior.
- The remedy wording was checked against 116's unsnapped table first. Moving the trace's top by
  one step (0.1 cells at h 0.025, 0.2 at h 0.0125) clears 27 of 43 sub-5-degree cases, and within
  two steps 33 of 43: nearly all at dips >= 20, about half at dips 10-15. The message says "about
  three cases in four, fewer at dips below 20 degrees".
- faults-in-convection.md (the capability guide that names place_fault_ribbon_2d) gains "A band
  near the surface": the interior gap rule, the outcrop warning, and the cap meshing the fault's
  last segment.

test_0907 (tier B):
- the corner outcrop (a = 2, b = 4) places with both walls labelled and the corner vertex kept;
  on 111's head it is refused, as measured in the box-corner sweep;
- the warning prints exactly when info["outcrop_min_angle"] < 5, a sliver-prone outcrop (dip 15,
  k 0.15) records less than a clean one (dip 45, k 1.05), and an interior placement records 180.
  On 111's head the key does not exist.

Box-corner sweep (a 1.5/2/2.5): all 9 placed, walls labelled, corner kept. Placement suite: 103
passed.
