# Re-check of PR #1146 at 0d9135fe against the two merge conditions

From the reviewing desk (H6, the curved-walls session, which reviewed this PR at d1acb3de). Scope: the two merge conditions of that review, the author's additions for its two low findings, and regressions. One new commit since the review, touching `checkpoint/disk_snapshot.py` and the PR's parallel test.

Machine: a 96-thread Linux workstation, single system image, Intel Xeon Gold 6240R, MPICH. A separate build of the PR head; MPI runs under `scripts/mpi_supervisor.py`, one at a time, np 1 to 4.

## Verdict

**Condition 1 (the pre-check cannot raise on one rank): MET.**
**Condition 2 (the variable set is checked both ways): MET.**
Ready to merge from this desk. One test gap (item 1 below) is worth a line in the test file, now or in a follow-up; it does not block.

## Condition 1

- The two faults that hung at d1acb3de, on the last rank's sidecar, at np 2 and np 3 (4 runs): `coordinates` replaced by a scalar dataset, and variable `s` replaced by an HDF5 group. Every rank raises the same `ValueError` naming the faulty rank ("coordinates have shape (); this swarm's particles have 2 coordinates"; "variable 's' is not a dataset"). On every rank the particle count and the hashes of the mesh variable, coordinates and both swarm variables are as before the call, and the sidecar files are unmodified. No hang (supervisor exit 0).
- The diff: `_read_swarm_sidecar_checked` is now a wrapper that calls `_read_and_check_swarm_sidecar` (the read and every check) inside `try ... except Exception`, so the guard is around both. The block carries its sanctioned failure mode ("reported into the collective verdict"), and the docstring says why a raise there would leave the other ranks waiting. Reading the sidecar pattern from the snapshot is guarded the same way.
- Further damages of our own to rank 1's sidecar at np 2, each refused on both ranks with the same error and the model untouched: coordinates with a compound dtype; a variable with a compound dtype; a zero-length file (`OSError`, reported); coordinates of shape (n, 2, 1); a variable of shape (n, 1, 1); a variable-length string variable; a complex variable; a `mpi_rank` attribute that is not a number (`ValueError` from `int()`, reported through the general guard).
- The PR's test now runs four damages (a row dropped, scalar coordinates, a variable made a group, a variable missing) and passes at np 2, 3 and 4. For d1acb3de we rely on our first review: the scalar and group cases hang there, and the missing variable is accepted there.

**1. Low, a test gap: no case in the test reaches the general guard.** Each of the four damages is now caught by an explicit check before anything can raise. Narrowing the guard back to `except (OSError, KeyError)` (a mutant in our own build, restored afterwards byte for byte) leaves the `scalar_coordinates` case passing at np 2; with the same mutant, a non-numeric `mpi_rank` attribute on rank 1 hangs at np 2 (rank 0 in the agreement; ended by the supervisor, exit 124), and is refused on both ranks without the mutant. One more damage in the test's table (`f.attrs["mpi_rank"] = "not a number"`, expected text "could not be read") would hold the guard itself.

## Condition 2

Variable `s` deleted from one rank's sidecar: refused on every rank with "lacks swarm variable 's'; restore requires the same variable set", model untouched, at np 2 with the fault on rank 1, at np 2 with the fault on rank 0, and at np 1. An extra variable is still refused. The reader's rule for which variables must be present (all but PETSc's own `DMSwarm*`) is the writer's rule. The PR body's round-1 section states this as the behaviour is.

## The additions for the low findings

- A string-typed variable on one rank (np 1, np 2, np 3): refused before the agreement on every rank ("sidecar dtype |S1 cannot be written into float64"), model untouched. At d1acb3de this left the faulty rank raising with its particles cleared.
- Three-column coordinates on a 2-D mesh (np 1, np 2, np 3): refused on every rank ("coordinates have shape (n, 3)"), model untouched. At d1acb3de this aborted in PETSc.
- An integer-typed variable for a float one is accepted and restored (a same-kind cast); stated here only so the boundary of the dtype check is on record.
- `timeout(300, method="thread")`: it fires. With the agreed verdict computed but not used (our mutant that previously ended only by the supervisor), the test at np 2 now fails by the pytest timeout after 308 s, exit 1, with the supervisor's silence limit set well above it (420 s) and not reached.

## Regressions

- The PR's test file: 4 skipped at np 1 (it needs two ranks); 4 passed on every rank at np 2, 3 and 4.
- The good path: a valid snapshot restores to exactly the saved state (hashes, particle counts) on every rank at np 1, 2 and 3.
- The 20 serial snapshot test files: 210 passed, 1 failed in a copy of the tests directory; the one failure is `test_1079_diffusion_disk_restart`, which launches a helper by its path in the repository and fails the same way in a copy at d1acb3de. Run in the repository it gives 2 passed, 1 xfailed. The same as at d1acb3de.
- CI on the head: style gates and all six shards pass.

## One line each

- Elsewhere in the diff: nothing beyond the above; the test's helper is renamed for the four damages.
- Commit trailer present. The commit message and the PR body name a session by its code alone ("H6's review", "Review round 1 (H6)"); a gloss ("the reviewing desk") would be better in the body.

## Not checked

More than four ranks; more than one swarm; proxy variables; 3-D; a parallel filesystem; d1acb3de was not rebuilt.

Underworld development team with AI support from Claude Code
