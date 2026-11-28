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
