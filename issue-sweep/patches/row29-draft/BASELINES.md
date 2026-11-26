# Row 29 (draft): the tests whose baselines move, and the relation each should become

Row 29 restacked on labels70-22 0006 (with UNFILED 80's fix). The suite is the fault,
conforming-surface and line-cut set plus tests 0900, 0901, 1092 and 0559: **15 failed, 419
passed, 1 skipped** (`suite29_r3.log`).
- No failure is a defect.
- test_1092, which crashed on the sphere earlier, passes with UNFILED 80's fix.
- None is converted yet; each relation below is a proposal.

The rule they follow: compare A against B on the same mesh, or assert an exact identity. No
absolute number that moves when the mesh does.

| Test | Asserts now | Measured under row 29 | Proposed relation |
|---|---|---|---|
| test_0595 `add_fault_without_snap_options_makes_the_same_cut` | the default cut equals `snap_frac=0.10, snap_quality=0.15, snap_dist=0.0` | 244 vs 260 vertices | A DEFAULT moved deliberately (add_fault's snap 0.1 to 0.3). Compare against `snap_frac=fault_split._ADD_FAULT_SNAP_FRAC`, so the test names the constant it encodes. |
| test_0559 `a_sphere_fault_cuts_in_either_direction...` [forward, reversed] | the "left without a vertex" warning, and 2 shared points | no warning, 0 shared | The PREMISE is gone: row 29 pulls only the tips of this trace (0.5 cells apart). Assert that add_fault shares no point in either direction, and move the counting check onto a direct `pull_vertex_onto` call on the same samples (measured: 2 shared, forward and reversed). |
| test_1174 `two_calls_solve_as_one_call_does` | peak slip == 0.152175 at 2e-5 | 0.152151 | Two calls against ONE call, both computed in the test on the same base (the test's subject). |
| test_1174 `a_split_fault_with_no_law_is_named_at_solve` | opening == 0.016910 at 1e-4 | 0.016551 | The opening with no law on Flt against the opening with a law on both, computed in the test (the crack the warning is about). The ratio to require is still to be measured on both rules. |
| test_1174 `one_call_puts_every_fault_on_the_add_on_levels` | TAIL pairs == {Flt 31, F2 33} | {23, 25} | Each add-on level's pair count for a fault equals that level's own chain count (interior vertices of the level's labelled chain), computed live; the welded levels stay {}. |
| test_1174 `the_add_on_levels_keep_the_first_fault` | node pairs == NODE_PAIRS_ADAPT {63, 67} | 47 | Two calls against one call on the same adapt child, computed in the test. |
| test_1174 `a_conforming_surface_keeps_the_split_fault` | slip == 0.160387 at 2e-5 | 0.160355 | Slip with the conforming surface against slip with Flt alone, both computed on the same base in the test. |
| test_1120 `weak_copy_threshold_sits_in_the_measured_gap` [at-rest, moved-0.002, moved-0.015] | the gap's edges equal recorded values at 0.005, and threshold in the gap | ratios to the median copy norm, smallest first (`_WEAK_COPY` = 0.1): at rest 0, 0, **0.140**, 0.376; moved 0.002: 0, 0.343; moved 0.015: 0.341 (no copy needs repair) | Keep `needs.max() < _WEAK_COPY < sound.min()`, measured live, wherever the fixture has a weak copy; drop the recorded edges. The threshold still sits in the gap in every case, but at rest the sound edge comes down to 0.140 (was 0.255), so the margin is thinner. **A decision for the hub:** the moved-0.015 fixture has no weak copy under row 29, so that case loses its subject; it needs a fixture that still makes one, or the case goes. |
| test_1173 `cut_made_on_a_moved_mesh_reaches_the_level_below` | shared nodes >= len(X0) - 5 | 760 of 769 | Exact identity: shared == len(X0) minus the moved-mesh vertices the pull and the snap moved (row 29's snap 0.3 moves more), counted from the two coordinate arrays by vertex. |
| test_1173 `split_level_takes_over_the_reference...` | wrong <= 16 | 20 | wrong <= the number of cut cells that straddle two parents (the test's own comment names them: 8 of 2,506 at the time), counted live from the host-cell label. |
| test_1176 `split_level_solve_after_a_move_keeps_its_iterations` | counts == [6, 6, 6, 6] | [5, 5, 5, 5] | Relation: every count after a move equals the at-rest count, and that count is at most half the rebuilt-transfer count (13 in the docstring), computed in the test. |
| test_1176 `fault_cut_into_a_moved_mesh_is_read_where_it_is` | vel its == 6 | 5 | Equal to the same fixture with the child at rest, computed in the test. |

Spacing threshold (`_PULL_SPACING` = 1.1 mean edges). Every sample is pulled when the trace's
median spacing is at least 1.1 times the mean edge length near it; the light rule applies below
that. Why 1.1:
- at 0.75, regular-box lines sampled a cell apart lost vertices and were refused;
- 1.1 keeps every trace sampled at about a cell or coarser on development's behaviour.

The cell size here is the mean edge length in the trace's bounding box, grown by a tenth of its
diagonal, SUM-reduced over the ranks with an in-place Allreduce. Every rank gets the same number.

## test_1120, done in the row 29 WIP (hub's ruling)
- **What moved it:** the snap (0.1 to 0.3), not the pull. The trace has two points, and pulling
  every sample gives bit-identical ratios. An explicit snap_frac=0.1 does not restore the recorded
  edges either: the add-on levels' cuts take the snap too (`w1120.py`).
- **The moved-0.015 case** now uses the trace shifted down by 0.01, chosen from a scan of eight
  offsets (`scan1120.py`). It makes 3 weak copies (all 0), with the weakest sound copy at 0.743.
- **The relation,** in every case: the copies below the median are split at their largest
  multiplicative jump, and `needs.max() < _WEAK_COPY < sound.min()` must hold. A case that makes
  no weak copy FAILS, so a platform that meshes one away shows.
- **Measured margin at rest:** 0.140 against `_WEAK_COPY` = 0.1. The constant is not moved.
- **No mesh fixture reaches a non-zero weak copy with margin under row 29's snap.** The nearest is
  dy -0.015, at 0.090 against 0.1. So `test_the_weak_copy_comparison` tests the comparison itself
  on hand-made norms: copies at 0.5, 0.9, 1.0 and 1.5 times the threshold, strict at the
  threshold, and invariant under scaling.
