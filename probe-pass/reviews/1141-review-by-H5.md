# Review of #1141 at b2fb4141, by H5

H5: fault, multigrid and restart fixes, with parallel runs on a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH). Built at b2fb4141.

**Verdict: READY.**

## The collective emptiness test (read)

`UWNVBPointQueueEmptyCollective` is an `MPI_Allreduce(LAND)` on the DM's communicator. Both drain loops (the conforming-closure split, about line 472, and the refedge request loop, about line 1391) have the same shape:
1. one global test before the loop;
2. in the loop, a local drain, the collective `DMLabelPropagatePush`, then the global test again.

The loop condition is the Allreduce's result, the same on every rank, so every rank runs the same number of iterations and reaches the Allreduce the same number of times. A rank with an empty local queue still runs the push and the test. That is the same structure as development, with PETSc's queue swapped for the file's own.

The queue: `Create` clamps the capacity to at least 1, so the compact branch never writes into a zero-length array. `Enqueue` compacts the live range to the front when it is at most half the capacity and doubles otherwise, so it never wraps. `Dequeue` checks for an empty queue. The SF callback (`UWNVBSplitPoint`) takes the new queue type.

## Measured

- **The #1140 shell adapt** (SphericalShell, cellSize 0.5 refined once, the shell metric), each run with an empty mesh cache:

  | levels | np 1 | np 2 | np 3 | np 4 | np 5 |
  |---|---|---|---|---|---|
  | 2 | 95699 | 95699 | 95699 | 95699 | 95699 |
  | 3 | 96072 | 96072 | 96072 | 96072 | 96072 |

  The cell count does not depend on the partition.
- **The parallel files H6 did not run:** ptest_0843 (edge split), ptest_0844 (line cut, 21 tests; reconnect) and ptest_0845 (fault split).
  - np 2: 33 passed, 1 skipped; np 4 and np 5 the same.
  - np 3: 33 passed, 1 failed. The failure is `ptest_0844_reconnect::test_adapt_with_repair_runs_in_parallel`, which fails the same way on development (seen in the reviews of #1126 and #1134). It is not this PR.
- **test_1178's queue self-test:** 3 passed.

## Notes

- None blocking. The `star[128]` bound in the request loop predates this PR.
