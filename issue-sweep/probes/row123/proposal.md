# Row 123: parallel defects that CI does not reach, and a proposal

W1, 2026-11-29. Wall times and results are H1's measurements on development fbef72fa (placement
stack 5a9f9ab7 where marked). They were taken on a 96-thread Xeon with 3 dedicated cores, threads
pinned to 1, no oversubscription, one mpirun per file under the MPI supervisor with a 300 s
silence window. Each is the whole file's time, launch and import included.

## What CI runs today
- Each tests/parallel/test_*.py runs at np 2 (shards 4 and 6). The 17 ptest_* files in
  PTEST_FILES run at np 2 on shard 2.
- np 3 and 4 run only with `--full-parallel`, which CI does not pass, because the runner
  (ubuntu-latest) has 2 cores (#573).
- Shard 6 runs a short always-on list at np 3/4 (about 3.4 min), with
  `OMPI_MCA_rmaps_base_oversubscribe=1`.
- 21 ptest files are run at no np. 19 are script-style (no test functions); 0863 is deferred as
  too slow; 0763 skips its one test unconditionally.
- The workflow triggers on push, pull_request and workflow_dispatch. It has no schedule.

## 1. Defects only np 3 shows, and the always-on entries that would gate them
| file | defect | in CI now | np 2 / np 3 (s) | at np 3 |
|---|---|---|---|---|
| ptest_0844_reconnect_parallel | repair arm assumed every pass flips (fix filed) | np 2 | 10 / 10 | fail |
| ptest_0848_fault_split_3d_parallel | row 122, the 3-D seam gate | never (script style) | 5 / 3 | fail |
| tests/parallel/test_0912 (row 122, pytest form, hand-built partition) | same | new | not timed (~5 est.) | fails before the fix |
| test_1114_mg_coarse_gamg_parallel [rotated] | UNFILED 67: asserts its (4, 10) against a bound of 9 | np 2 | 8 / 7 | fail |
| test_0904 parallel (placement stack) | message contract of the conform refusal | np 2 | 12 / 12 | pass |
| test_0907 parallel (placement stack) | sliver warning's reduction | always-on np 3 | 10 / 10 | pass |

H1 found no other file that fails at np 3 only. test_0855_mesh_smoothing was not run at np 3, since it spawns a child process.

Adding test_0912, ptest_0844 and test_0904 to the always-on block costs about 27 s of np 3 time
on dedicated cores. On the 2-core runner, oversubscribed, that is perhaps 1 to 1.5 min. Shard 6 has
about 4 min of headroom. test_1114[rotated] should wait: its bound is an iteration count recorded
at np 2, so UNFILED 67 first decides whether 10 at np 3 is a defect or needs its own record.

```bash
    # The 3-D split's seam gate (row 122): a patch whose cell star reaches the seam
    # off the fault facets is repartitioned, not refused. The test builds the
    # partition by hand; np 3 is where the default partition first showed it.
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/test_0912_3d_split_gate_tests_the_cell_star_parallel.py || status=1

    # A repair pass that flips nothing keeps its level's parent map: at three ranks
    # the last pass flips none, at two every pass flips.
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/ptest_0844_reconnect_parallel.py || status=1

    # The seam-conforming placement's refusals carry one name; at three ranks the
    # connector refusal fires first.
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/test_0904_place_ribbon_beside_the_wall_parallel.py || status=1
```
The entries for test_0912 and test_0904 go in with their branches (row 122; the placement stack).

## 2. The 21 files that run nowhere
Five files failed on development in H1's run: 000c, 000d, 001a, 0848 and 0863. All five are among
the 21. Four are script-style; 0863 is the slow one, and passes in 576 s with a 900 s window. A
script that asserts fails by its exit code. A print-only script only fails by crashing. "exit 0" below
means the file is not among H1's failures.

| file | asserts | dev result | recommendation |
|---|---|---|---|
| 0004 checkpoint_fmg_hierarchy | 3 | exit 0 | convert to pytest |
| 0007 snapshot_inmemory | 5 | exit 0 | convert |
| 0008 mesh_radii_accessors | 6 | exit 0 | convert |
| 0010 snapshot_disk | 6 | exit 0 | convert |
| 0011 dm_rebuild_held_handles | 7 | exit 0 | convert |
| 0202 warmstart_homotopy | 13 | exit 0 | convert |
| 0203 wallclock_guard | 10 | exit 0 | convert |
| 1020 fmg_single_field | 8 | exit 0 | convert |
| 1079 diffusion_disk_restart | 1 | exit 0 | convert |
| 0848 fault_split_3d | 1 + a FAIL list | fail (row 122) | convert. test_0912 covers only the seam gate; 0848 also checks the split's census, SF drift and a P2 solve |
| 000 petsc4py, 000a uw, 000b uw_petsc4py, 001 start_stop | 0 | exit 0 | retire: every parallel test starts uw and PETSc |
| 001a start_stop_petsc4py | 0 | hangs (#900), silence-ended | retire, or move #900's case into a pytest file with a timeout |
| 000c uw_petsc4py_h5, 000d uw_petsc4py_swarm | 0 | fail: they read annulus_example.msh, which nothing makes | retire, or convert with a mesh the test builds |
| 002 projection, 003 swarm_projection | 0 | exit 0 | convert with an assertion against the serial answer, or retire if a test_* file covers it (not checked) |
| 0863 fault_network_3d_width | 15 (3 test fns) | 576 s; silence-ended at 300 s | run in the weekly job with a 900 s window |
| 0763 mesh_adapt_transfer | 2 (skipped) | skip | retire: it needs mmg's adaptMetric |

## 3. A weekly full-parallel run
Add a `schedule:` trigger (weekly) to the existing workflow, with a job running
`./scripts/test.sh --p 2 --full-parallel`, sharded as now. Also run the remaining script-style
files as scripts, where a non-zero exit fails the job. This catches the class across every file:
odd and uneven splits, ranks without cells or faces, collectives entered by some ranks only (#609,
#611 hung at np 4 only). The always-on list only covers a defect after it has been found once. On
development today it would have shown six: ptest_0844 and test_1114[rotated] at np 3, and, as
scripts, 000c, 000d, 0848 and 001a's hang.

Cost, from H1's times on dedicated cores:
- np 3 adds 2304 s of test_* and 288 s of PTEST_FILES (about 43 min); np 4 about the same again.
- The scripts add about 12 min, including the two 300 s silence windows.
- So about 1.6 hours of rank time on dedicated cores. Oversubscribed on 2-core runners, perhaps
  twice that, spread over the shards. A 4-core runner removes the oversubscription.

It gates no PR, so someone has to read its result each week. The always-on list stays for the
cases that must gate.
