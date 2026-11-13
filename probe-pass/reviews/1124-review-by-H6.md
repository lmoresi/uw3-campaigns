## Adversarial review of #1124

**Verdict: ready with listed changes.** The four fixes are correct and each is reached by a test that fails on `development`. One change is needed before merge: the #868 cleanup makes every new mesh variable about seven times slower, in serial as well, where there is nothing to clean. A two-line variant removes the cost and keeps the result.

Reviewed at head 1d8a793e against `development` 01dec8d2 (the PR's merge base; one commit). Run by the reviewing desk (the curved-walls desk, standing in for the usual second review desk) on a 96-thread Linux workstation, single system image, Intel Xeon Gold 6240R, MPICH, PETSc int32. CI is green on all six shards at this head.

### Findings

1. **Medium. The cleanup costs a full Python collection on every new variable, on one rank too.** `_setup_ds` now calls `mpi._free_petsc_garbage`, which runs `gc.collect()` and then `PETSc.garbage_cleanup`. On a 1/32 box that already carries a Stokes model (239,356 live Python objects), adding 12 P2 variables takes:

   | | np 1 | np 2 |
   |---|---|---|
   | `development` | 0.165 s (13.7 ms each) | 0.127 s (10.6 ms each) |
   | this branch | 1.242 s (103.5 ms each) | 1.153 s (96.1 ms each) |
   | variant below | 0.144 s (12.0 ms each) | 0.134 s (11.2 ms each) |

   Twelve bare `gc.collect()` calls on that state take 0.726 s; twelve `PETSc.garbage_cleanup` calls take 0.0001 s. So the cost is the Python collection, and it grows with the model. On one rank the deferred list is never used (0 entries on both builds), so serial users pay it for nothing.
   **Variant, measured:** call `PETSc.garbage_cleanup(comm)` directly, and only when the communicator has more than one rank. At np 2 the deferred count is the same as this branch (2, 4, 4 after 1, 6, 12 variables; 4 after 40), values are kept, the Poisson solve is exact, and the cost returns to `development`'s. Caveat: our counter collects before it reads, so the variant was measured with a Python collection between variables; without one, objects in reference cycles reach the list when Python next collects and are emptied at the next rebuild.

2. **Low. The claim "nothing in use is destroyed" is not what the new tests check.** A mutant that destroys the old DM eagerly after the swap (the #492 defect) passes all five new tests, serial and np 2. The tests keep the variables, not a handle to the old DM or vectors. The property does hold: the existing `test_0858_dm_rebuild_lifecycle.py` (4 passed) and `ptest_0011_dm_rebuild_held_handles.py` (np 2 and np 3: "held DM handle valid after rebuild") pass on this head, and our held-handle probe below agrees. Either say in the PR that #492's own tests carry this, or hold `mesh.dm` and `var.vec` across the loop in the new test.

3. **Low. The serial #868 test cannot fail on its bug.** `test_twelve_variables_on_one_mesh_keep_their_values_and_a_solve_runs` passes on `development`. It is a guard, and the PR says so; it should not be counted among the tests "shown failing first".

4. **Low. The added `scripts/test.sh` line does nothing.** `batch 3 tests/parallel/test_1164_…_parallel.py` runs the file on one rank, where `mpi(min_size=2)` skips it ("1 skipped"). The test runs, and is reached, through the `tests/parallel/test_*.py` glob in the parallel phase. Drop the line (Charter §5), and the PR body's "listed in `scripts/test.sh` on shard 3".

5. **Low. The #866 test calls the private helper, not a remesh.** It applies `_mark_reinit_stale` to the proxy's entry in `mesh.vars`, which is what the remesh pass does, and fails on `development` for the right reason. It would not notice if the remesh pass stopped selecting that variable. Acceptable for this fix.

6. **Low, process.** The commit message ends with a `Co-Authored-By:` line naming a model, and the PR body ends with an emoji "Generated with" line. The project's attribution rule is the single "Underworld development team with AI support from Claude Code" line, with neither.

### What holds

- **Fails on `development`, passes here.** Serial file on `development`: 3 failed (ShapeError (2, 1) + (1, 2); `_proxy_stale` False; the swarm still registered on the mesh it left), 1 passed (finding 3). On this head: 4 passed, and 4 passed on both ranks at np 2. Parallel file at np 2: fails on `development` (`assert 310 <= 20`), passes here; passes at np 3.
- **The #868 numbers reproduce.** 1/32 box, P2 variables added one at a time, deferred entries after 1, 6 and 12:

  | | np 1 | np 2 | np 3 |
  |---|---|---|---|
  | `development` | 0, 0, 0 | 2, 82, 310 | not run |
  | this branch | 0, 0, 0 | 2, 4, 4 | 3, 6, 6 |

  Every variable keeps its values; the Poisson solve on the twelfth gives max |T − y| = 1.3e-11 (np 1), 1.2e-11 (np 2), 3.4e-11 (np 3). Max-rank peak memory at np 2: 383.2 MB on `development`, 371.8 MB here. Over 40 variables at np 2 the list reaches 3,442 entries on `development` and stays at 4 here.
- **Not a solver default.** #1034 changes the shape of a zero default body force in `SNES_NavierStokes` from a column to a row; the only path it alters is one that raised. The other three touch no solver.

### Attacks that failed

Each ran at np 1 and np 2 on both builds, with the same answer on both to the digits shown.
- A solver built and solved, six variables added under it, the solver re-solved, a second solver on the newest variable, the first solved again: errors 4.3e-12 to 1.1e-11 throughout.
- A user holding the old DM, an old vector and a data view across five rebuilds: the old DM still answers (1 field, its cells), the old vector keeps its size and norm, the variable keeps its values.
- Two meshes: variables of the first dropped and collected, the first mesh and its solver deleted, while the second gains variables and solves: errors 1.5e-12 to 5.7e-12.
- A swarm variable's proxy on a mesh that gains five variables: its integral is 0.500000.
- Stokes solved, five variables added, solved warm and cold: energy 3.699725993777e-06 before and after (np 1), 3.699725992372e-06 (np 2).
- Cleanup on rank 0 only (a mutant): aborts with a PETSc error in `PetscGarbageKeySortedIntersect` (exit 63), it does not hang. In the branch every rank reaches the call, since the rebuild itself is collective.
- Mutants: the #1034, #866 and #867 fixes reverted are each `development`'s code, and their tests fail there. Removing the pre-existing callback on the wrapper (keeping the new one on the base variable) changes no test.
- Every run exited cleanly at interpreter shutdown.
- Neighbours on this head: the swarm test files 0750 and 0751, 32 passed, 3 expected failures.
- Markers (level on the module, tier on each test), CI reach (all 447 test files reachable) and the style gate are in order. The PR body names the machine by what it is and has no local paths.

### Issues

- #1034, #866, #867, #868: fixed by this branch, each on a probe above. #866 at the level of the callback reaching the base variable; we did not run a full adapt.
- #492: untouched and still holding (finding 2).

### Merge conditions

- Remove the Python collection from the rebuild path, or show it is needed: `PETSc.garbage_cleanup(comm)` alone, on more than one rank, gave the same counts at the old cost.
- Drop the `batch 3` line.
- Say which tests guard "nothing in use is destroyed", or make the new one hold a handle.

### Not tested

More than three ranks; a mesh on a one-rank communicator inside a parallel run; a full `adapt` for #866; long time-stepping runs that create variables every step; the swarm, transport and model suites beyond the two files named (the PR reports 344 passed, and CI is green); 64-bit-index PETSc.

Underworld development team with AI support from Claude Code
