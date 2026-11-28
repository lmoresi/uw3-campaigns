# Row 123: parallel defects that only np 3 shows, and how CI could reach them

DRAFT (W1, 2026-11-29). Wall times are pending from H1 (walltimes.txt here); TBD marks them.

## What CI runs today (development)
- Every tests/parallel/test_*.py runs at np 2 (shards 4 and 6). The ptest_* files that are pytest
  files run at np 2 on shard 2.
- np 3 and 4 run only with --full-parallel, which CI does not pass: the runner (ubuntu-latest) has
  2 cores, so np 3 is oversubscribed (#573).
- Shard 6 already runs a short always-on list at np 3/4, about 3.4 min. Each entry is a file
  whose case needs an odd split or an empty rank, started with OMPI_MCA_rmaps_base_oversubscribe=1.
- Script-style ptest files (21, including ptest_0848) are not collected by pytest at any np.
- The workflow triggers on push, pull_request and workflow_dispatch. There is no schedule.

## Defects seen at np 3 and not at np 2
| file | defect | in CI now | np 3 wall time |
|---|---|---|---|
| ptest_0848_fault_split_3d_parallel.py | row 122: the 3-D seam gate | never (script style) | TBD |
| tests/parallel/test_0912 (row 122's pytest form) | the same, hand-built partition | new | TBD |
| ptest_0844_reconnect_parallel.py | repair arm assumed every pass flips | np 2 | TBD |
| tests/parallel/test_1114_mg_coarse_gamg_parallel.py [rotated] | UNFILED 67 | np 2 | TBD |
| tests/parallel/test_0904 (placement stack) | wall-gap refusal message | np 2 | TBD |
| tests/parallel/test_0907 (placement stack) | sliver warning's reduction | always-on np 3 (115) | TBD |
| (others from H1) | | | |

Added to every CI run by the always-on entries: TBD min on shard 6, which has about 4 min of
headroom under its time limit (test.sh comment).

## Draft scripts/test.sh lines (in shard 6's always-on block, after test_0907's entry)
```bash
    # The 3-D split's seam gate: a patch whose cell star reaches the seam off the
    # fault facets is repartitioned, not refused. The default partition at np 3 is
    # where it was found; the test builds the partition by hand (row 122).
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/test_0912_3d_split_gate_tests_the_cell_star_parallel.py || status=1

    # A repair pass that flips nothing keeps its level's parent map; at three ranks
    # the last pass flips none, at two every pass flips.
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/ptest_0844_reconnect_parallel.py || status=1

    # The rotated coarse-GAMG case fails at three ranks only (UNFILED 67). Its recorded
    # answers are np 2's (the file says so), so the entry waits until UNFILED 67 says
    # whether np 3 is a defect or needs its own record.
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      "tests/parallel/test_1114_mg_coarse_gamg_parallel.py::test_gamg_on_the_coarse_level_when_asked_for[rotated]" || status=1

    # The seam-conforming placement's refusals, at three ranks where the seam
    # crosses the band (row 118 / 111).
    OMPI_MCA_rmaps_base_oversubscribe=1 $SUPERVISE mpirun -n 3 python -m pytest --with-mpi \
      tests/parallel/test_0904_place_ribbon_beside_the_wall_parallel.py || status=1
```
Runner: 2 cores. np 3 oversubscribes by one rank; the existing always-on entries already do this.
The supervisor's silence timer (300 s) bounds a hang. Lines for 0904 and 0912 only make sense once
their branches merge.

## A scheduled full-parallel run in place of more per-PR entries
A weekly `schedule:` job (and workflow_dispatch) running `./scripts/test.sh --p 2 --full-parallel`
on one larger runner, or sharded as now, would run every parallel file at np 3 and 4. That
catches the class this row is about, odd and uneven splits and ranks without cells or faces,
across all files rather than only the ones named after a failure. The always-on list only covers a
defect after it has been found once.
- Cost: TBD (np 3 + np 4 passes of every parallel file: about 2x the np 2 phase, oversubscribed on
  2 cores; a 4-core runner removes the oversubscription).
- Its failures reach no PR; someone has to read them. The always-on list stays for the cases
  that must gate.
Also: the 21 script-style ptest files run nowhere. Converting ptest_0848 to pytest (or retiring it
for test_0912) is a separate item.
