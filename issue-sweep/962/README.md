# Issue 962: the two-call Jacobian (underworld3 PR 1156)

Probes behind the pull request that works around PETSc leaving a rank without
cells out of the Jacobian's assembly. All runs: macOS, 12-core Apple M4, one
rank, conda-forge PETSc 3.25.3. Paths in scripts and logs are placeholders
(UW3_WORKTREE, PROBE_DIR).

- `two_call/matequal_plugin.py`: a pytest plugin that assembles J and P with the
  branch's routine and with PETSc's one pass at every Stokes-family solve and
  compares them with MatEqual. `table_f1ff675c_summary.txt` is the final table
  (164 files, 2,522 solves compared, 0 differing); `table_d3ad12c0_summary.txt`
  is the first one; `reruns_summary.txt` has the files that fail under the
  plugin, run without it.
- `two_call/mutate.py`, `run_mutants.sh`, `mutants.log`: six mutants of the C
  routine, each built and run against the serial comparison test.
- `cost/`: one 3-D Stokes solve under each routine (flops, counts, times).
- `leak/malloc_dump.py`: PETSc's unfreed-memory dump after 5 and after 50
  Jacobian evaluations (14,649 blocks both times; the dumps are not kept here).
- `box_fixture/box_one_rank.py`: the one-rank value of the two-cell box.
- `review_r2/`: the probes of the second adversarial review.
- The upstream report draft is `upstream/petsc-962-jacobian-assembly.md`.
