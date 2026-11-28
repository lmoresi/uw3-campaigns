# UNFILED 112: a JIT cache write that fails on rank 0 alone

One commit, stacked on unfiled93 (branch bugfix/jit-and-supervisor-leave-no-temp-dirs, 0001-0006).
Apply after those: `git am 0001-*.patch`.

In getext's non-disk branch (multi-rank, cache=True, the disk cache not enabled on every rank),
store_module now runs inside a try, and its outcome is agreed with _raise_if_any_rank_failed
(what="cache write"). The message reads "JIT build of <mod> succeeded but storing it in the JIT
cache failed on rank(s) [0], so it fails on every rank".

The new test is in tests/parallel/test_0842. The cache is off on ranks > 0, and rank 0's
store_module is patched to raise. Fail-first: before the change rank 0 raises alone, and the run either hangs, with the
other ranks in the solve's first collective until the test timeout or the supervisor's silence
limit, or aborts quickly. At np 2 on the Linux workstation, H1 saw rank 1 hit MPI_Abort (63) at
finalize within 4-7 s. Either way, the ranks do not raise together.

Serial: test_0903, test_0004, test_jit_cache, and test_0842 at np 1 (its np >= 2 cases skip):
15 passed, 3 skipped.
Owed, at np 2-3 on the Linux workstation: test_0842, on this head and on unfiled93's head,
to show it failing first.
