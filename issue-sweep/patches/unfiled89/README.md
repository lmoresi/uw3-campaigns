# UNFILED 89: the rotated constraint-row diagonal scale is deterministic

H4, 2026-11-28. **Branch:** local/diag-scale-deterministic-u89 on underworld3 development fbef72fa. Three commits, local because of the GitHub pause; apply in order with `git am`:
1. `0001` 7d2e808a: the fix. `_velocity_diag_scale` uses math.fsum per rank, then gathers and fsums on the operator's comm, in place of NORM_1 (BLAS dasum).
2. `0002` fb11a062: review round 1. A helper tested at 8 memory offsets, fresh-ptap calls, "deterministic" not "exact".
3. `0003` 3cb23ef3: review lows. The helper's calls are counted, so a NORM_1 rewire fails serially; no session code in the test; "must not copy".

H1: READY TO MERGE ON GREEN at fb11a062 (campaigns 760b2f1); lows folded in at 3cb23ef3. **Needs no ruling from Louis.** It is independent of row 32 (issue-sweep/patches/row32/), which applies on top of it.

**Evidence** (hyperion runs/2026-11-10-h4/u89/; PR_BODY.md here):
- **dasum is alignment-dependent on AVX-512 OpenBLAS.** The same data at 8 offsets gives different NORM_1 for 89 of 90 random vectors (n = 384, 1536, 20011), while fresh NORM_2, VecDot, VecSum and NORM_INFINITY give one value each (`dasum_alignment.py`, align5).
- **Traced on the fixture** (annulus cell 0.2, viscosity 1 + T, warm re-solve, np 2; `fixture_np2.py`):
  - the partition, J, Q, the normal rows and a fresh `J.ptap(Qt)` are bit-identical run to run;
  - the operator after `zeroRowsColumns(diag=diag_scale)` falls into two classes, mapping one-to-one onto 12 and 13 pressure iterations;
  - `diag_scale` takes two values one ulp apart (…357p+2 and …358p+2), even within one process;
  - each rank's local sum is identical every run, while PETSc's global NORM_1 varies (…961, …963, …964).
- **Counts, 10 runs at np 2:**
  - development, default: 13 x8 and 200 x2;
  - development with `-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0`: 12/13/200 (4/5/1, then 6/3/1). The GEMV switch alone does not make it repeatable;
  - 89, no switch: 13 x10, one operator hash, one answer.
- **Test:** test_1089. The NORM_1 helper mutant fails 3/3, the NORM_1 rewire fails serially 3/3 (0 calls against 30), and the test passes at np 1, 2 and 3. The rotated suite has 372 passed; the parallel 1131, 1156 and 1088 pass at np 2.
- **What 89 does not fix:** the fixture's pressure target sits on the round-off floor (5.6e-20 against a reachable 4.3e-20 to 1.6e-18), so at np 3 it hits the 200 cap every run, deterministically. That's row 32.
