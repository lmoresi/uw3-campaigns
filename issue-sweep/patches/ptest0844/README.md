# ptest_0844 repair arm: the parent map follows the flip counts (test only)

Base: development fbef72fa. One commit (1ab28fc3), branch test/ptest-0844-maps-follow-the-flips.
The arm asserted every level's map is None after a repair. At np 3 the last pass flips 0
(3, 11, 23, 47, 17, 0), so its level keeps its map, correctly: _subsample_mg_levels sets None only
where `repaired` (n_flips > 0, a count summed over ranks) is set for the level's span. The new
assertion records the flips per pass with a wrapper around reconnect.flip_to_reduce_max_angle
(adapt calls it through the module). It asserts one map per pass, at least one pass flipped, and
the map is None exactly where the pass flipped.
Serial alignment check (laptop): 6 passes (7, 26, 35, 68, 22, 3), 6 levels, all None.
For H1: ptest_0844_reconnect_parallel.py at np 2 and 3.
