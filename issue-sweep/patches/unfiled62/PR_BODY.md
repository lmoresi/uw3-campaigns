## Bound the barycentric builder's orphan-repair query (#893 follow-up)

The barycentric builder's orphan repair gives each coarse DOF that has no fine image the nearest
fine DOF not yet claimed, as a weight-one injection. It found these with one kd-tree query of
orphans + 8 neighbours for every orphan, an (orphans x orphans) array. That array was the #893
blow-up: 8.6 GB per rank. #890 removed it from the parallel route. The serial custom-FMG route,
the legacy `set_custom_mg` path and the public default (`repair_orphans=True`) still ran it.

Each orphan now queries 9 neighbours. The count doubles for that orphan only while every
candidate is claimed, or while the first free candidate is at the same distance as the last
neighbour found. Equal distances go to the lower fine index. The loop is Python, one small query
per orphan: on a Linux server, 21,929 orphans take 11.7 s and 7.8 MB, against 419 s and 1.76 GB
before. Per-rank (parallel) callers pass `repair_orphans=False` and never run it.

**Results.** Where no two candidates are the same distance from an orphan, the claims are
development's: CSR-identical on every builder call in the custom-MG and placed-ribbon tests
(98 calls), on the #893 hierarchy at refinement 4 (orphans 10 and 38), and on 40 random 2-D and
3-D clouds. A Linux server's review matched the builder against a brute-force greedy reference
on 60 fixtures.

**Behaviour change on exact-distance ties.** With an exact tie, development's choice depended on
the size of its one large query and on the platform. The bounded query takes the lower index.
One different claim takes a fine DOF a later orphan would have had, so a tie early on cascades:
- on the server's fixtures, 17-208 orphans took a farther node on development and 32-384 with
  this change;
- on half-cell-offset integer grids, where four-way ties are exact, 168-1,720 entries differed
  for n = 16-48 on that server, and 184-788 for n = 16-32 on a 12-core Apple M4 laptop.

Both are valid greedy results. A tied custom-FMG Poisson answer moved 3.7e-11 at rtol 1e-10.

**Also fixed:** with a single fine DOF development raised (IndexError); the bounded query gives it
to the first orphan.

The build statistics gain `orphans_claimed`, the fine rows given to orphans. `orphans_repaired`
keeps its meaning, the orphans found.

Test: `tests/test_0893_custom_mg_orphan_repair_memory.py` (level_1, tier_b). A seeded random
cloud has no ties, so its greedy result is unique, and its fine half forces 1,876 orphans. The
test compares the rows the repair rewrote with an inline brute-force greedy reference, with the
orphans taken from the build without the repair. The check does not depend on how a platform's
Delaunay splits a tie. It fails on development (59 MB against the 20 MB cap), and on a mutant
whose query is held at 9 neighbours: that mutant passes every other custom-MG test, so this is
the only check on the widening. A second case is the single fine DOF.

Tolerances: a peak memory cap of 20 MB (tracemalloc); row sums equal to 1 within 1e-14. The
claims are compared exactly.

Leaves open UNFILED 63: the repair empties columns too. Register row 26, stacked on this branch,
turns the repair off on the serial custom-FMG route.

Underworld development team with AI support from Claude Code
