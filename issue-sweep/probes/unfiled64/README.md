# UNFILED 64: test_1157's serial run-to-run difference is PETSc's VecMDot gemv path

The fixture is test_1157::test_a_genuine_warm_correction_at_low_viscosity_is_solved, the cold
solve, on macOS (12-core Apple M4) with conda-forge PETSc 3.25.3 and OpenBLAS 0.3.30, serial,
OMP_NUM_THREADS=1. The last application of the velocity sub-solve takes 78 iterations or hits
its cap of 200, from run to run on one build.

## Where the 200 comes from
It is the velocity fieldsplit sub-KSP `rotfs1_fieldsplit_vel_`: FGMRES, rtol 3.3e-8, atol
1e-50, max_it 200. `vel_its_last` samples only its last application, the 36th in this solve
(verbose1157.py). Those solves stagnate. In the 36th, the residual falls from 6.4e-3 to 9.1e-9 in
3 iterations, then creeps toward its target of 2.1e-10. Whether it reaches the target by
iteration 78 or runs to 200 depends on round-off.

## The varying input
- C1's three candidates do not make it repeatable (10 runs each):
  - PYTHONHASHSEED=0: 78 in 1 of 10;
  - OMP and all BLAS thread counts at 1: 2 of 10;
  - cKDTree `workers`: nothing in src/underworld3 passes it.
- Every input of the rotated solve is bit-identical across runs (hash1157.py): the operator, the
  right-hand side, the rotation Q, the custom transfers, Mp, the null-space vectors, the
  projected null mode, and every MG level's operator and interpolation. So nothing upstream
  varies, which includes any uw ckdtree use (UNFILED 65's stale heap memory would show here).
- There are exactly two outcomes, each bit-identical within its class: two solution hashes over
  19 runs. That holds under `-malloc_debug` too (8 runs) and with OPENBLAS_CORETYPE=ARMV8
  (10 runs; I could not confirm the forced core took effect).
- The first velocity-PC application's input already differs between the classes (apply1157.py):
  690 of 2,752 entries by about one ulp, not a uniform scale. So the difference is computed
  inside the outer KSP, in PETSc's C code.
- `VecMDot` of identical data gives one of two results depending on where the vectors' arrays sit
  in memory, 7.1e-14 apart on dots of order 50 (align_gemv.py). `dnrm2`, `ddot` and `dgemv` do
  not depend on the offset (align_norm.py). PETSc 3.25 computes `VecMDot` through BLAS gemv when
  the vectors happen to be adjacent in memory (`-vec_mdot_use_gemv`, on by default), and
  through its own loops otherwise. Allocation placement, which changes from run to run, picks
  the path.
- Proof, rerunning the test's case:

  | options | runs | outcomes |
  |---|---|---|
  | `-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0` | 10 | one class, bit-identical |
  | `-vec_mdot_use_gemv 0` alone | 6 | one class, bit-identical |
  | `-vec_maxpy_use_gemv 0` alone | 6 | both classes (78 three times) |

  With mdot-gemv off, every run takes 200: the deterministic path is the capped one.

## What it means
- Any KSP whose orthogonalisation uses VecMDot (GMRES, FGMRES) is reproducible here only to
  round-off from run to run, serial included. A stagnating sub-solve turns that round-off into
  iteration counts. The final answer agrees: |v| was identical to 16 digits in all 30 sweep
  runs.
- The underlying weakness is the stagnation itself: the velocity sub-solve hits its 200 cap in
  most runs of this fixture, and the test passes regardless.

## Options (C1 and Louis decide)
1. Accept it, and state in tests that sub-solve counts are reproducible only to round-off.
2. Put `-vec_mdot_use_gemv 0` in underworld3's default options. That makes serial runs
   repeatable at the cost of the gemv speed-up; the cost is not measured here.
3. Look at the velocity sub-solve's stagnation on this fixture (floor ~1.4e-6 relative against
   3.3e-8).
