## Bound the barycentric builder's orphan-repair query (#893 follow-up)

The barycentric builder's orphan repair gives each coarse DOF that has no fine image the nearest
fine DOF not yet claimed, as a weight-one injection. It found these with one kd-tree query of
orphans + 8 neighbours for every orphan, an (orphans x orphans) array. That array was the #893
blow-up: 8.6 GB per rank. #890 removed it from the parallel route. The serial custom-FMG route,
the legacy `set_custom_mg` path and the public default (`repair_orphans=True`) still ran it.

Each orphan now queries 9 neighbours, and the count doubles for that orphan only while every
candidate is claimed, or while the first free candidate is at the same distance as the last
neighbour found.

**Behaviour change, exact ties only.** Where an orphan is exactly the same distance from
several fine DOFs, the claim now goes to the lower fine index. Before this, the order among
equal distances came from the size of development's query. Results are otherwise unchanged:
- every builder call in the custom-MG and placed-ribbon tests (98 calls) gives a CSR matrix
  equal entry by entry to development's;
- so does the #893 hierarchy at refinement 4 (orphans 10 and 38);
- so do 40 random 2-D and 3-D clouds.

On half-cell-offset integer grids, where four-way ties are exact, 184-788 entries differ for
n = 16-32. No bounded query can reproduce development's order there.

Test: `tests/test_0893_custom_mg_orphan_repair_memory.py` (level_1, tier_b). A fine cloud
filling the left half of a 60x60 coarse grid forces 1,770 orphans. On development's builder
the test fails at a 54.7 MB peak; with this change the peak is 4.4 MB.

Tolerances: a peak memory cap of 20 MB (tracemalloc); row sums equal to 1 within 1e-14; hard
baselines nnz 7260, 1,770 orphans repaired and 877 empty columns. The matrix comparisons are
exact.

Leaves open UNFILED 63: the repair empties columns too (1,770 empty before it, 877 after it on
the test fixture). This is pre-existing; install drops these columns.

Underworld development team with AI support from Claude Code
