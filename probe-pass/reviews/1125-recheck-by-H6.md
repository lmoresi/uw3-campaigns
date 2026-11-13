## Re-check of #1125 at ab381324

By the reviewing desk (the session that reviewed this PR at 60defae8), against the merge conditions of that review only. Run on a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH), serially.

**Result: all four conditions are met.**

The diff 60defae8..ab381324 is one file, `tests/test_1165_tensor_history_swarm_read_and_component_clamp.py` (+73/-16), in two commits. No library file changed, so the review build of 60defae8 was used unrebuilt; its installed `functions_unit_system.py` is byte-identical to the source at the new head.

### Conditions

1. **Met: the clamp tests now fail on the layout mapping.** `test_clamping_one_component_equals_that_entry_of_the_whole_clamp` asserts, for every entry of a TENSOR, a SYM_TENSOR, a VECTOR and a 2 x 3 MATRIX, that the clamp of one component equals that entry of the whole-variable clamp at 200 random interior points, with a difference of exactly 0. The three-point baseline is gone.
   - Unmutated: 8 passed.
   - Flat-index mutant (`stored_column = [_comp]` in the installed file, restored byte-for-byte afterwards): 1 failed, 7 passed. The failure is the MATRIX case, as the author says; TENSOR, SYM_TENSOR and VECTOR pass under the mutant because there the flat index is the stored column.
2. **Met: the file is serial.** Module-level `pytest.mark.skipif(uw.mpi.size > 1, reason="serial: per-rank tmp_path; rank-local clamp")`. Read, not run in parallel.
3. **Met: a units-model round trip.** `test_a_tensor_swarm_variable_round_trips_in_a_units_model` writes and reads a SYM_TENSOR swarm variable in a model with reference quantities and asserts a difference of exactly 0. On `development` 01dec8d2 it fails (`ValueError: could not broadcast input array from shape (144,3) into shape (144,2)`); on the head it passes. The PR body states it ("#984 in a units model").
4. **Met in the PR body; one commit in history is not.** The body ends with the repository attribution line and has no emoji line. Of the three commits, the first (60defae8) still carries `Co-Authored-By:` naming a model; the two new commits carry the correct trailer. A squash merge keeps that line out of `development`.

### Also checked

- **The MATRIX history test** now runs two steps and asserts each entry of the (2, 3) MATRIX history against a scalar semi-Lagrangian history of that entry under the same scheme, to 1e-12, after asserting the initialised history against the nodal field to 1e-12. It passes.
- **The whole file on the head:** 8 passed, serially. On `development`: 8 failed (the history, both swarm round trips, the four clamp cases and the units round trip).
- **Nothing else** is in the diff.

### One low note, new

The PR body says "H6's review conditions are met" and a commit subject says "review conditions (H6)": a session code with no gloss. A reader outside the project cannot tell what it names.

### Not re-run

The first review's other attacks, the 56 neighbouring files, anything in parallel.
