# UNFILED 62: bounded orphan-repair query (local branch bugfix/orphan-repair-bounded-query)

Commits 99cfea1e (bounded query) and e2aa7be6 (tie-break, test renamed to test_0893) on
development fbef72fa. Not pushed (GitHub pause); handed over as format-patch files.

## Change
`barycentric_prolongation` (custom_mg.py): the orphan repair's single query of
k = orphans + 8 neighbours for all orphans is replaced by k0 = 9 per orphan, doubled for
that orphan only while all candidates are claimed. `taken` is a boolean array, not a set.
The loop stops once every fine DOF is claimed (the old code then found nothing either).
A zero-node fine cloud skips the repair (the old code raised at k = 0).
One change covers all three sites: the serial custom-FMG route (_reduced_transfer),
legacy inject_custom_mg, and the public default.

## Proof of no result change
- A/B plugin (development's builder vs this one, CSR compared entry by entry, plus
  orphans_repaired): 98 calls over test_1015/1016/1017 (both), 1020, 1022, 1111, 1113,
  1145, 1146, 1149, 1176, 0004, 1097 -- 91 passed, all identical. Only 2 calls had orphans.
- K1's #893 fixture (p_893_k1.py, refinement 4, chain 2): 5 calls, orphans 0,0,0,10,38,
  all identical; solve converged, peak 1,190 MB (same as before the change, 1,185 MB).
- 40 random 2-D/3-D clouds, a third with the fine cloud cut to x < 0.6: 0 differ.
- All of the above rerun after e2aa7be6: 98 calls (91 passed), K1 orphans 10 and 38, 40
  clouds -- all identical to development.
- Ties (e2aa7be6): equal distances go to the lower fine index, and the query widens while the
  first free candidate ties with the last neighbour found, so the claims do not depend on k.
  Development's own tie order depended on its k = orphans + 8. On half-cell-offset integer
  grids (exact four-way ties; probe_ties.py, probe_ties99.py) 99cfea1e alone already differed
  from development by 104-1,472 entries at n = 16-48; with the tie-break the differences are
  184-788 entries at n = 16-32. No bounded query reproduces development there. Grids offset by
  0 or a quarter cell, and every fixture above, have no such ties and are identical.

## Test
tests/test_0893_custom_mg_orphan_repair_memory.py (level_1, tier_b, 4 s): a 60x60 coarse
grid with a 3,600-point fine cloud in its left half, so 1,770 orphans. tracemalloc peak
under 20 MB; hard baselines orphans 1770, nnz 7260, empty columns 877, row sums 1.
On development's builder (swapped in by a plugin) it fails: 54.7 MB.

## Tolerances
Row-sum check atol 1e-14. Memory cap 20 MB (new 4.4 MB, old 54.7 MB). Matrix equality exact.

## Not done
- Dropping the repair at the serial route (C1's option 2) changes the transfer: the
  repair overwrites fine rows, and install's restrict_unreached only drops columns.
  It needs its own proof.
- test_0885 (parallel, public default) not run: no MPI on this laptop.

## Side finding
The repair can create new orphans: overwriting a fine row with a weight-one injection
removes that row's old columns. On the forced fixture, 1,770 columns are empty before the
repair and 877 after it. Development does the same; install drops them.

## Round 2 (H1 review: changes requested), commit c5a47485
1. test_0893 no longer hard-codes counts from a regular grid's non-unique Delaunay. It uses a
   seeded random cloud and compares the claims with an inline greedy reference, with the
   orphans from the repair-off build. The 20 MB cap stays.
2. It fails on a k-held-at-9 mutant (`mutant_k9.py`, `mutant_plugin.py`; the claims differ) and
   on development (59.2 MB; and IndexError with a single fine DOF). Development's claims equal
   the reference on this cloud (`dev_vs_ref.py`: 1,876 orphans), so the reference encodes the
   existing rule.
3. The PR body no longer says "tie order". It describes the cascade, with the server's counts
   next to the laptop's.
4. Lows:
   - `orphans_claimed` added, and `orphans_repaired` documented as the orphans found;
   - the n_fine = 1 fix is in the test and the body;
   - the Python loop and the per-rank False are noted in the code and the body.

Custom-MG tests 1015, 1016 and 1017: 15 passed. test_0885 is blocked by UNFILED 65, not by this
branch.
