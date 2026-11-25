# Register row 26 (proposed): serial custom-FMG without the orphan repair

Base: underworld3 development fbef72fa. Five commits, as `git format-patch` files:
- 0001-0003 are UNFILED 62 (the bounded query, the tie-break, and round 2's reference test,
  c5a47485);
- 0004 (a5b1b623) is row 26, restacked from aa3d092c onto the fixed 62 with no conflicts. The
  change is the same;
- 0005 (c0ef3729) bounds test_0894's guard counts instead of matching them (UNFILED 64).

After the restack, test_0893, test_0894, test_1015 and test_1016 pass (14 passed). The
before/after tables were measured on aa3d092c, whose row-26 change is identical. 62's round 2
changes only its test, the build statistics and a comment.

Apply them with `git am 000*.patch` on fbef72fa. Not pushed. Merging is Louis's call.

Files:
- `PR_BODY.md`: the draft, with the summary table.
- `ITERATIONS_ALL.md`: every test with solves, before (e2aa7be6) and after (aa3d092c), solve by
  solve.
- `ITERATIONS_CHANGED.md`: the tests whose counts or solutions differ, with the largest relative
  solution difference.
- `rec_plugin.py` and `compare.py`: the recorder, run as
  `REC_OUT=dir PYTHONPATH=. pytest -p rec_plugin $(cat suite_files.txt)`, and the comparison.
- `run_graded.py`, `run_box3d.py` and `run_k1.py` (needs `issue-sweep/probes/p_893_k1.py`):
  the fixtures, with `orph_log.py` and `norepair_plugin.py`.

Recorder artifacts: test_1077::test_warm_solve_without_a_linear_solve_prints_no_banner and
test_1174::test_a_split_fault_with_no_law_is_named_at_solve fail only under the recorder, on
both builds. The recorder's fieldsplit sub-KSP query prints a PETSc error that the tests check
for. Without the plugin both pass on both builds.

For H1 (np 2-4): the same fixtures in parallel. With this change, serial and parallel should
build their node transfers the same way, so the graded fixture's serial velocity count (3)
should match what the parallel route already gives.
