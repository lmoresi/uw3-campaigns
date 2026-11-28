# Row 122: the 3-D split's seam gate tests the closure of the patch's cell star

Base: labels70-22's head 3b4f5975 (bugfix/cut-labels-chords-across-kinks, which contains development
fbef72fa). labels70-22 touches fault_split.py (add_fault and the cut's helpers, not the split or its
gate); nothing else in the held queue does (111-118, 93, 100, 89 checked).
**Apply order:** labels70-22 0001-0011, then this 0001-0002.

- 0001 (tests first):
  - tests/parallel/test_0912: hand-built partition, the star on rank 0 and the rest above by x.
    The fixture is checked: no facet point is shared, a star-closure point is. It asserts the gate
    says touch on every rank and split_fault succeeds. Expected on the base (0001 alone), at np 2
    and 3: the fixture holds, the gate is False, and every rank refuses "cell star touches the
    partition seam".
  - tests/test_0912 (serial): five cases on hand-marked shared points.
- 0002 (fix): _patch_star_touches_seam(dm, patch_verts, shared, cell_verts=None) holds the
  refusal's own test. split_along_label_3d calls it in place of its inline loop, with the same
  message and the same order. _fault_labels_touch_seam calls it in 3-D after the facet test and
  still reduces with LOR; 2-D is unchanged.
- Remedy already right: partition_addon(mark_labels, layers=1) and the extrude path's
  _gather_regions(layers=1) both make every point of a star cell unshared (their docstrings).

Laptop (serial only): test_0912 5 passed; 13 fault-split files 113 passed. A facet-only mutant of the
helper fails 2 of 5 (the off-facet and fragment cases). scripts/check_test_coverage.py OK.
For H1: tests/parallel/test_0912 at np 2 and 3 on 0001 alone (must fail) and on 0001+0002 (must
pass); ptest_0848 at np 3 on 0001+0002.

## 0003 (2026-11-29): ptest_0848 in pytest form
tests/parallel/test_0848_fault_split_3d_parallel.py: every check of the script as an assert (two tests: away from the cut; on the cut). u.data -> u.array[:, 0, 0] (same order, checked). Serial run of both test bodies passes. The old script stays. For H1: np 2 and 3 under the supervisor on labels70-22 + row122 0001-0003; on 0001 alone (no fix) np 3 is expected to fail.

## 0004 (2026-11-29, H1 HIGH + two LOWs)
- Fixture: rank 0 = star + cells with centroid x > 1.5 (far from the patch at 0.4); the rest by x over [0, 1.5]. Asserts every rank keeps cells after the split.
- Non-simplex 3-D: development's split is tetrahedra only (fault_split.py:1263 `np.empty((nc, 4))`, :1391 `setConeSize(i, 4)`), so a hex mesh raised rank-locally at :1264. The gate now refuses it collectively (LAND, an empty rank votes yes), before the per-label loop; parallel case with a 3x3x3 hex box. The helper keeps the four-wide form (no dead any-count path).
- Double closure build (gate then split): left as it is.
Serial: test_0912 5 passed; fault-split files 113 passed. For H1: test_0912 parallel at np 2 and 3.
