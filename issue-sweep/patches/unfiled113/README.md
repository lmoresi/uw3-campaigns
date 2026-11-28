# UNFILED 113: "the fill ring crosses itself" on the dip-15 outcrop

One commit on development fbef72fa, independent of 111 (it touches only _loop_self_crossings
and adds test_0905).

Cause: a false positive in _loop_self_crossings. The ring runs along the ladder band's straight
rail through four collinear points. Two non-adjacent edges of that run had orientations of
exactly 0 and 5e-20 against each other, and the bare sign test (0 counted as "not > 0") read
that as opposite sides. look2.py finds the pair in the dumped fill inputs. The outcome turns on
round-off: the same trace built with an exact 0 instead of cos(90 deg) = 6e-17 places on
development.

Fix: proper crossings only, as the docstring always said, with |orient| <= 1e-12 * |AB| * |CD|
counted as zero. A first version also counted touchings and collinear overlaps; that broke 9
placement tests (0595, 0855, 0856, 0857), whose rings legitimately touch themselves, so it was
withdrawn.

Measured: dip 15, k 0.5-1.5 in 0.1 steps, all 11 placed as outcrop, walls labelled, split
(sweep113-final-dip15.log). Placement suite (every test file using place_*/the counter, test_0858
excluded): 92 passed.

Not this defect, for C1 to decide whether it is a row: on these outcrop placements the
smallest angle is 0.3-5.8 deg (e.g. 0.3 at k 0.8, 0.8 at k 1.4). Development's outcrop path
already gives 3.3-8.6 deg at dips 30 and 45. This is the outcrop-floor question C1 raised under
111's ruling.
