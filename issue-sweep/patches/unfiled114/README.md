# UNFILED 114: the assembly area check at a curved wall

One commit on development fbef72fa, independent of 111 and 113.

Measured (area_rec.py; rec-dip*.json): 296 ladder assemblies on H1's annulus fixture, at dips
10/15/20/30/45 and k 0-3 in 0.05 steps. |mesh - CAD| / CAD is at most 8.3e-16 for all but one:
dip 15, k = 0, at 2.0e-8.

Located (hunt.py, C1's condition): assembly vertex v17 sits at (-4.6e-9, 1.0), the trace's top on
the wall, 4.6e-9 from the CAD's point there. The sliver it adds (base 4.6e-9, height about 0.07)
is the 1.7e-10 excess. It is only in the intermediate assembly: _collapse_boundary_imprints
removes it, and every final outer-wall vertex lies on the base wall polygon to round-off (largest
signed distance outside +1.4e-17; r - 1 = -7.8e-5 is the chords' sagitta). So decision 28's wall
contract holds.

Fix: _check_assembly_area allows max(1e-3 x smallest triangle, 1e-9 x CAD); the comment gives both
distributions. split=False now places the outcropping zone; split=True reaches the split's "the
fault touches the domain boundary".

test_0906 (tier B): the zone places and reaches the wall; the fault gets the split's refusal
(both fail first on development); the check accepts 1e-4 of a triangle and refuses one missing
triangle. Placement suite: 91 passed.

Notes (not rows): dip 10 k <= 0.45 "fewer than two rungs inside the domain"; dips 15/20 k 0.05
pull_vertex_onto boundary-vertex refusal. When 111 lands, check whether its gap message or the
pull's fires at k 0.05, and that the user gets a remedy either way (C1).

## H7 MEDIUM: 0002
The allowance is now perimeter x 3e-9 x diameter, plus a check that no edge borders more than two
triangles (a doubled cell). perim.py measures the window. The annulus excess (1.731e-10,
perimeter 0.4776, diameter 0.2197) needs delta >= 1.65e-9 x diameter. H7's strip (missing 1e-6
sliver, perimeter 18, diameter 8.06) is refused only for delta < 6.89e-9 x diameter. 3e-9 is
inside, about 2x from each side. C1's suggested 1e-8 would accept the missing sliver. A full
topological check (every boundary edge on the CAD outline) needs the outline, which this check
does not have without redoing the CAD; not added. The edge-multiplicity check covers doubling.
Mutants: the smallest-triangle allowance and 1e-3 x CAD both fail test_a_missing_sliver_is_refused.
test_0906: 5 passed. Placement suite: 93 passed.

## C1's length check, measured, and what was done instead: 0003
The boundary-length check needs the CAD perimeter, which no assembly returns (three functions and
their tests unpack (pts, tris, area)). It also misses a missing BOUNDARY sliver, whose length
change is second order like a displaced vertex. Instead, the Euler characteristic (euler.py,
euler_annulus.py):
- every real annulus assembly measured has V - E + F = 1;
- the strip is 1; the strip with the interior sliver removed is 0;
- a notch (a boundary cell removed) stays at 1.
So for ladder assemblies (outlines without holes) V - E + F == pieces is exact for any missing
interior cell. The edge multiplicity covers doubling. The area check is the backstop for notches,
loosened to perimeter x 1e-8 x diameter (wall excess 1.7e-10 against 1.0e-9). The network mesher
is not checked for holes; its fused outlines may enclose them.
test_0906: 6 passed (adds a missing interior triangle touching the boundary at one vertex).
Placement suite: 94 passed.
