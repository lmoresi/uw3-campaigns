The JIT and the MPI supervisor leave nothing behind in the temporary directory

## What was wrong
- **JIT.** `compile_and_load` built each extension in a directory under a hard-coded `/tmp`
  (ignoring `TMPDIR`) and nothing removed it: one `fn_ptr_ext_<hash>_<pid>_<time>_<n>` per compile
  per rank, a dozen or more inodes each (sources, `.c`, `.so`, a `build/` tree).
- **Supervisor.** `scripts/mpi_supervisor.py` left a handler directory (`uw-supervisor-*`) per job
  and, without `--artifacts`, a stacks directory (`uw-stacks-*`) holding an empty placeholder per
  Python process.

On a Linux server whose `/tmp` is a tmpfs of 1,048,576 inodes these filled it and stopped every
session on the machine. A developer laptop's `/tmp` held 2,866 build directories.

## What changes
- The build directory is made by `tempfile.mkdtemp`, so `TMPDIR` is honoured, and `getext`
  removes it once the module is loaded and stored in the disk cache. The loaded module does not
  need the file: the mapped `.so` survives its unlink on Linux and macOS (a solve after the
  removal is tested). The directory is kept with `UW_JIT_KEEP_BUILD=1` (kernels unchanged) or
  `debug=True`, and after a failed build, whose error names it. The removal is rank-local,
  best-effort and decides nothing, so the ranks cannot diverge on it.
- The supervisor removes its handler directory and the empty placeholders at exit, and its own
  stacks directory if that is then empty. Dumped stacks stay. After a kill the placeholders stay
  too: an empty one records a rank that did not answer.
- Only ranks get a stack file. A process whose direct parent is an armed process, or a helper, of
  the same rank (a rank's setup.py build, say) is a helper and gets none; a rank is a child of its
  launcher and is armed under any launcher. The rank is read from `OMPI_COMM_WORLD_RANK`,
  `PMIX_RANK`, `PMI_RANK`, `MV2_COMM_WORLD_RANK` or `SLURM_PROCID`, `unknown` otherwise.
- A SIGTERM or SIGHUP to the supervisor ends the job's process tree first and waits for it
  (bounded by the kill ladder), then tidies, then dies of the same signal, so its parent sees it.
  Before, mpirun and the ranks ran on for a minute or more.
- The testing guide recommends `--basetemp` on a real disk for long suites, one per concurrent run.

## Known, not changed
- A rank killed in the middle of a compile leaves its build directory. Nothing sweeps the
  temporary directory by age: that would delete other processes' files.
- With `TMPDIR` on NFS the client renames a mapped, unlinked `.so` to `.nfsXXXX`, so one empty
  directory stays per compile. Keep `TMPDIR` on a local disk.
- After the removal a debugger reads no symbols for frames inside a kernel, and tracebacks through
  `cy_ext.pyx` lose their source lines; `UW_JIT_KEEP_BUILD=1` keeps them.

## Tolerances
- test_0903's solve: u = x^2 - y^2 on a degree-2 field, solver tolerance 1e-12, nodal error
  asserted below 1e-9. The field reproduces a quadratic, so no mesh-dependent number enters.
- No coordinate matches.

## Tests
- **test_0903** (tier B): three compiles leave a private `TMPDIR` empty, with every build
  directory made under it; a Poisson solve on kernels whose build directory is gone is exact, and
  the module reached the disk cache first; `debug=True` and `UW_JIT_KEEP_BUILD=1` keep the
  directory. It fails before the change (directories under `/tmp`, and left there).
- **test_0063**: three supervised jobs leave the temporary directory empty; a two-rank hang
  keeps the answering rank's stack and the silent rank's (it ignores SIGUSR1) empty file, and the
  rank's python subprocess gets none; a supervisor ended by SIGTERM leaves no job process, its
  parent sees -15, the job's stack file was in place until the job ended, and nothing is left.
  All three fail before the change.
- **test_0063, separately**: a commit makes the fake gdb's frame counter portable. BSD `wc` pads
  its count, so the moved-between-samples test failed on macOS every time.
- **ptest_jit_cache** removes the fake build directories its flock test makes.
- **test_0004** removes the build directories its `debug=True` compiles keep.

Serial on macOS: test_0903, test_0004 and test_jit_cache, 14 passed; the serial test_0063 tests
pass; `tests/test_00[0-4]*` and `tests/test_01*` exited 0 on the first version of the change.
Still to run on a Linux workstation at 2-4 ranks: tests/parallel/test_0842 and ptest_jit_cache.

Underworld development team with AI support from Claude Code
