# UNFILED 93: JIT and supervisor temporary directories

Branch bugfix/jit-and-supervisor-leave-no-temp-dirs on development fbef72fa, 6 commits (0001-0006).
Apply with `git am 00*.patch` on development. PR text: PR_BODY.md.

Review: one adversarial round, F1-F8. F1-F6 and F8 are fixed in 0005 and 0006.

F7 is pre-existing and left open. In getext's non-disk branch (multi_rank, cache=True, but the
disk cache not enabled on every rank), store_module runs on rank 0 alone and can raise there alone
(a PermissionError from the lock file), leaving the other ranks in the next collective.

Owed: np 2-4 runs of tests/parallel/test_0842 and ptest_jit_cache on the Linux workstation.
