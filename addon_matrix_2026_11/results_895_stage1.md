# #895 stage 1: one structural FAC block against per-rank pieces

Run by the kaiju dev runner (K2), 2026-11-09:
- **Build:** development b8367c40 (#1022 qmd merged), build job 4222.
- **Driver:** `stage1_895_blocks.py` @ 86d2420.
- **Jobs:** arrays 4223 (layout check), 4239 (np 1), 4227 (np 4), 4232 (np 8) and 4233 (np 16). OMP_NUM_THREADS=1, `-c 2`, on shared nodes, so times are indicative and flops exact.
- **Records:** on kaiju, branch `kaiju/895-stage1-records` 8dcbb8e (112 files, not pushed; kaiju has no GitHub credentials). The binary patch is `~/+Claude/devrun/patches/0001-895-stage-1-records-from-kaiju-56-jobs-one-block-aga.patch`, sha256 759f3462…54b3.

## Result

All 56 jobs exit 0 and converge. The per-rank arm gives the same answer as the one block: max |ΔV| ≤ 5.2e-14 in every job. Velocity iterations are the same in every job (4/4; pair and single 3/3 at some np).

- **single, pair, junction:** each sits on one rank, so the arms agree to round-off (the control checks out).
- **apart:** the two faults sit on different ranks (np 4: ranks 3 and 0; np 8: 6 and 1; np 16: 12 and 2).
  - The one block sends both faults' rows to one rank, the rank with the slightly larger share. That rank was the "second" fault's in every case; the two faults' row counts are a near-tie.
  - The per-rank arm halves the rows over the two fault ranks.

| h_b/S | np | arm | busy-rank rows | busy-rank LU flops | busy-rank MatSolve s (both solves) | first solve s | busy-rank RSS MB |
|---|---|---|---|---|---|---|---|
| 24.3 | 4 | one | 30942 | 2.65e8 | 13.54 | 12.49 | 434 |
| 24.3 | 4 | per_rank | 15642 / 15300 | 1.43e8 / 1.28e8 | 7.91 / 7.54 | 10.29 | 399 / 381 |
| 24.3 | 8 | one | 30934 | 2.59e8 | 12.40 | 11.34 | 418 |
| 24.3 | 8 | per_rank | 15642 / 15292 | 1.38e8 / 1.16e8 | 8.73 / 7.94 | 11.12 | 380 / 378 |
| 24.3 | 16 | one | 30930 | 2.68e8 | 16.39 | 14.52 | 412 |
| 24.3 | 16 | per_rank | 15642 / 15288 | 1.29e8 / 1.30e8 | 11.45 / 8.82 | 14.84 | 382 / 382 |
| 48.5 | 4 | one | 60230 | 5.99e8 | 33.65 | 30.96 | 557 |
| 48.5 | 4 | per_rank | 30882 / 29348 | 3.36e8 / 2.73e8 | 18.56 / 16.14 | 22.52 | 516 / 488 |
| 48.5 | 8 | one | 60238 | 6.32e8 | 35.47 | 32.20 | 542 |
| 48.5 | 8 | per_rank | 30882 / 29356 | 3.44e8 / 2.61e8 | 19.25 / 17.11 | 23.05 | 501 / 483 |
| 48.5 | 16 | one | 60238 | 6.16e8 | 32.93 | 28.50 | 546 |
| 48.5 | 16 | per_rank | 30882 / 29356 | 3.29e8 / 2.67e8 | 19.10 / 17.11 | 23.02 | 498 / 488 |

Quiet ranks: 246–300 MB, LU flops about 1e6.

## Reading

- **Memory.** With qmd the patch's memory is small. Splitting it lowers the busy rank's peak by 7–8 % (434 → 399 MB, 557 → 516 MB). The busy/quiet ratio stays at about 1.5–2 in both arms, so the imbalance is the fault region the rank holds, not the LU block.
- **Time.** The patch's triangular solves are the critical path: on the busy rank, MatSolve time is close to the whole solve time. Splitting the block over the fault ranks cuts the busy rank's LU flops and MatSolve time by 1.8–2×, and the first solve by up to 28 % (most at h_b/S 48: 31.0 → 22.5 s at np 4, 32.2 → 23.1 s at np 8). Iterations and answer are unchanged.
- **Coarse space.** No coarse space was needed for this: the pieces are whole faults, so nothing couples across a piece. The two-level form's case rested on memory and on splitting one fault's block; qmd has removed the first, and the second does not arise while each fault is rank-interior.
- **Partition differences.** Against np 1 the slip differs by 4e-8 to 2.9e-6 in both arms alike, from the partition at solver tolerance 1e-6. It is not an arm effect.
