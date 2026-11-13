## Adversarial review of #1146 at d1acb3de

Independent review by the reviewing desk for this PR (a session that did not write it), against `development` (merge base d66c7da0; the comparison build is 01dec8d2, and `checkpoint/` is unchanged between the two). Run on a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH), PETSc int32.

**Verdict: ready with listed changes.** The fix does what it says for every fault the old code checked: the refusal is raised on every rank, with one message, before anything is restored. One change is needed: the new pre-check can itself raise on one rank only, ahead of the agreement, and the job then hangs.

### Findings

**1. Medium, to fix: the pre-check raises on one rank for faults outside `(OSError, KeyError)`, and the other ranks wait in the agreement.** `_read_swarm_sidecar_checked` catches `OSError` and `KeyError` around the read; anything else propagates from the rank that holds the bad sidecar, before `_agreed_problem`. Two sidecars damaged by hand on rank 1 at np 2:

| fault on rank 1's sidecar | serial | np 2 |
|---|---|---|
| `coordinates` replaced by a scalar dataset | `IndexError: tuple index out of range` | hang (supervisor exit 124; rank 0 in the agreement's `Allgather`) |
| variable `s` replaced by an HDF5 group | `TypeError` from h5py | hang (exit 124) |

This is the failure #974 describes, moved into the pre-check. Whatever reading or checking a sidecar raises should become that rank's `problem`, so that every rank reaches the agreement (a guarded read with its sanctioned failure stated, or explicit checks of rank and type), with a test.

**2. Medium, not introduced here: a sidecar that lacks a variable is accepted, and that rank's variable is left unrestored.** The variable set is checked in one direction only (every sidecar variable must exist on the swarm). With `s` deleted from rank 1's sidecar at np 2, `load_state` returns on both ranks; rank 0 is as saved and rank 1's `s` is not. `development` does the same. The PR body says the variable set is checked; it is half checked.

**3. Low: two faults still fail after the agreement, on one rank.** The pre-check does not look at the coordinate array's shape beyond its length, or at a variable's type. A string-typed `s` on rank 1 at np 2: rank 0 returns, rank 1 raises `ValueError: could not convert string to float` with its particles already cleared (the same on `development`). Coordinates with three columns on a 2-D mesh abort in PETSc (error 83) during the restore, serially. Both are far from normal use; a shape check of `(n, cdim)` and a cast check in the pre-check would close them.

**4. Low: the test's `timeout(300)` does not fire on the failure it guards.** Under two of our mutants the job blocks in a collective and it is the supervisor's silence limit that ends it (exit 124), not the pytest timeout. CI runs under the same supervisor, so a regression still fails.

### What holds (run)

- **The claim.** The new test fails on `development` at np 2 with `[None, "swarm variable 's' shape mismatch ..."]` and passes on the head at np 2, 3 and 4.
- **Refusal on every rank, nothing changed.** One row dropped from the last rank's sidecar at np 2, 3 and 4: every rank raises the same `ValueError`, naming the faulty rank; mesh variable, particle coordinates, both swarm variables and the particle count hash the same as before the call on every rank; the sidecar files are not modified. On `development` the same input leaves rank 0 restored and the faulty rank raising with its model changed (and in serial, raising with the model changed).
- **Every fault the old code checked**, serially on the head, is refused with the model untouched: a row dropped or added; fewer coordinates; an extra variable; wrong component count; wrong rank, rank count or mesh name in the attributes; a truncated file; a file that is not HDF5; a missing file; `coordinates` deleted. A missing or truncated sidecar on rank 1 at np 2 is refused on both ranks.
- **Two ranks, different faults.** Rank 0 with a dropped row and rank 1 with `coordinates` deleted (np 2); rank 1 with an extra variable and rank 2 with a dropped row (np 3): every rank reports the lowest faulty rank's message. Deterministic, as `_agreed_problem` takes the first.
- **Empty ranks.** With particles only in x < 0.15, rank 0 holds none at np 3 and ranks 0 and 1 hold none at np 4: a good snapshot restores to the saved state on every rank, and an extra variable in the empty rank's sidecar is refused on all three ranks.
- **The good path.** A valid snapshot restores to exactly the saved state (hashes of the mesh variable, coordinates and both swarm variables) at np 1, 2 and 3 on the head, and at np 1 and 2 on `development`.
- **A different rank count.** A snapshot written at np 2 is refused at np 1 and on all three ranks at np 3, by the existing check at the top of `read_snapshot`, with nothing changed.
- **Mutants**, against the PR's test at np 2: the swarm check moved after the agreement (hang, exit 124); the check made on rank 0 only (fails); the shape check removed (fails); the verdict gathered and not used (hang, exit 124). All four are killed. The installed file was restored byte-for-byte.
- **Serial snapshot files** (the 20 test files using `save_state`, `load_state` or `disk_snapshot`): 210 passed; `test_1079_diffusion_disk_restart`, which launches a helper by path, was run in the repository: 2 passed, 1 xfailed.
- **Gates.** All 447 test files reachable; the style gate passes; the test carries a level and a tier; the commit and PR body end with the repository line and name no machine.

### Issues

- #974: fixed by this branch for the fault it names (a shape mismatch on one rank) and for the other checks that were rank-local; finding 1 is the same failure for two further faults and should be closed here.
- #1041: nothing reopened; its pre-check is extended, and its own refusals precede the swarm check unchanged.

### Merge conditions

- Make the sidecar read and check unable to raise on one rank (finding 1), with a test of one such fault at np 2.
- Either check the variable set in both directions or correct the sentence in the body (finding 2).

### Not tested

More than four ranks; more than one swarm in a model; a swarm with a proxy variable; a snapshot restored twice; 3-D; a parallel filesystem. Faults were made by editing the sidecar with h5py, not by interrupting a write.
