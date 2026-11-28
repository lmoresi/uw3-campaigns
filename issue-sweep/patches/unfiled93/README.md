# UNFILED 93: JIT and supervisor temporary directories

Branch bugfix/jit-and-supervisor-leave-no-temp-dirs on development fbef72fa, 6 commits (0001-0006).
Apply with `git am 00*.patch` on development. PR text: PR_BODY.md.

Review: one adversarial round, F1-F8. F1-F6 and F8 are fixed in 0005 and 0006.

F7 is pre-existing and left open. In getext's non-disk branch (multi_rank, cache=True, but the
disk cache not enabled on every rank), store_module runs on rank 0 alone and can raise there alone
(a PermissionError from the lock file), leaving the other ranks in the next collective.

Owed: np 2-4 runs of tests/parallel/test_0842 and ptest_jit_cache on the Linux workstation.

## Round 2 (H7, H1): 0007
M1 fixed: SIGTERM/SIGHUP ends the job's tree first, waits, tidies, then re-raises (parent sees -15).
L1: the hang test has a rank that ignores SIGUSR1; its empty file survives the kill.
L2: only ranks are armed. A process whose direct parent is armed (or a helper) with the same rank
is a helper and gets no file, so a rank's build subprocesses don't. Ranks are children of their
launcher, so they are armed under any launcher. Keyed on OMPI_COMM_WORLD_RANK, PMIX_RANK,
PMI_RANK, MV2_COMM_WORLD_RANK, SLURM_PROCID ('unknown' otherwise).
L3: ptest_jit_cache removes uw_jit_fake_rank* dirs.
L4: accepted and documented in PR_BODY: a rank killed mid-compile leaves its build dir; no
age-based sweep.
New tests fail first against 0006's supervisor (L1/L2: helper's empty rank_0 file; M1: 143 not -15).
Serial test_0063 (excluding mpirun cases): 8 passed.
Owed: H1's np 3 kill test, H7's serial re-check.
112 rebased onto 0007 (one commit, unchanged).
