# ptest_0844 repair arm: the parent map follows the flip counts (test only)

Base: development fbef72fa. Commits e544cefc, b79c5d99, branch test/ptest-0844-maps-follow-the-flips.
The arm asserted every level's map is None after a repair. At np 3 a late pass can flip nothing,
so its level keeps its map, correctly. The map is kept only on levels whose pass made no flips; which
levels those are depends on the mesh, metric and rank count (H1: the counts repeat exactly at np 3 over
10 and 5 runs): _subsample_mg_levels sets None only
where `repaired` (n_flips > 0, a count summed over ranks) is set for the level's span. The new
assertion records the flips per pass with a wrapper around reconnect.flip_to_reduce_max_angle
(adapt calls it through the module). It asserts one map per pass, at least one pass flipped, and
the map is None exactly where the pass flipped.
Serial alignment check (laptop): one map per pass; every pass flipped there, so all None.
For H1: ptest_0844_reconnect_parallel.py at np 2 and 3.

## 0002 (2026-11-29, H1/C1 review): the subsampler's guard tested alone; comment without counts
tests/test_0844_reconnect_repair.py gains a serial test calling _subsample_mg_levels directly on a captured unrepaired hierarchy with recorded maps blanked: unmarked -> derived maps; all repaired -> none; one marked -> only it goes. A guard-removed mutant fails it; the file passes 15/15. The ptest comment no longer quotes pass counts. 

## Reworded (2026-11-29)
Both commit messages reworded to drop pass counts (the earlier numbers came from a probe centred at (0.5, 0.5), not the test's (0.4, 0.55)). Content unchanged: `git patch-id --stable` is identical (c0c7e34cc4ae, 62f48a2ea989) and the tree matches the old head, so H1's READY carries over. New SHAs e544cefc (0001), b79c5d99 (0002); old 1ab28fc3, 0b5d2d9d.
