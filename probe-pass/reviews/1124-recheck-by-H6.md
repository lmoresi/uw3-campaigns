## Re-check of #1124 at 7c0c6f2d

We re-checked the three merge conditions of our review at 1d8a793e, and nothing else. Run on a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH 5.0.1, PETSc int32), on a rebuild of the new head; `development` numbers are those of the first review (01dec8d2).

**Result: all three conditions are met.**

The diff since the reviewed head is three files: the cleanup call in `discretisation_mesh_variables.py` (12 lines), the parallel test (12 lines added), and two lines removed from `scripts/test.sh`. Nothing else changed.

### Condition 1: the Python collection is off the rebuild path. Met.
- Read: the rebuild now calls `PETSc.garbage_cleanup(comm)` alone, and only when the communicator has more than one rank. No `gc.collect()` and no `_free_petsc_garbage` remain in that path.
- Cost of a new variable, 12 P2 variables added to a 1/32 box that carries a solved Stokes model, three runs each:

  | | np 1 | np 2 |
  |---|---|---|
  | `development` | 13.7 ms each | 10.6 ms each |
  | reviewed head 1d8a793e | 103.5 | 96.1 |
  | this head | 12.4, 12.1, 14.7 | 10.6, 10.5, 11.6 |

  The sevenfold cost is gone. The author's figures (11.3 and 8.4) are a little lower than ours; ours are at `development`'s level, on a shared machine.
- Deferred-destroy entries at np 2 after 1, 6 and 12 variables: 2, 4, 4 (`development`: 2, 82, 310). In serial: 0, 0, 0. Values kept; the Poisson solve on the twelfth variable is exact to 1.3e-11 (np 1) and 1.2e-11 (np 2).
- **The bound does not depend on a Python collection.** Our first counter collected before each reading, so we repeated it without: reading the list with no collection gives 2, 4, 4; with Python's automatic collector switched off as well, 2, 4, 4; over 40 variables with the collector off the list stays at 4; and on the mesh carrying the solved Stokes model, collector off, 20 variables give 2, 4, 4, 4 and the model re-solves (reason 2). The released objects reach the deferred list by reference count, as the new comment says.

### Condition 2: the `batch 3` line. Met.
The line is gone from `scripts/test.sh`; `scripts/check_test_coverage.py` passes (447 files reachable).

### Condition 3: a test that holds handles. Met.
- The parallel test now holds the DM from before the rebuilds and an old vector of the first variable, and asserts both are usable afterwards and the variable keeps its values.
- It passes at np 2 and np 3.
- Our eager-destroy mutant (the old DM destroyed straight after the swap), which passed every test at the reviewed head, now fails it at np 2 on both ranks: `assert (0 != 0)` on the held DM's handle. The mutant was made in the review build's installed file and restored byte-for-byte.

### Also confirmed
- The four tests of the serial file pass on this head.
- The PR body ends with the project's attribution line, says the serial #868 test is a guard and that the #866 test calls the helper directly, and names `test_0858` and `ptest_0011`. The new commit's trailer is correct. The first commit (1d8a793e) still carries its `Co-Authored-By` line in history.

### Not re-run
The attacks of the first review (held handles, two meshes, swarm proxy, rank-0-only cleanup), more than three ranks, and the rest of the suite: the library change is the one call above.

Underworld development team with AI support from Claude Code
