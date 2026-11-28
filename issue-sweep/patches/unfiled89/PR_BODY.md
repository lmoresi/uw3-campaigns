## Rotated free slip: a deterministic constraint-row diagonal scale

**Base:** development (fbef72fa). It is independent of #1058's branch: `_velocity_diag_scale` is untouched there, so either can merge first.

### The defect
`_velocity_diag_scale` is the mean |diag| of the rotated velocity block. The rotated route writes it on the eliminated wall-normal rows (`zeroRowsColumns`), in the forward operator and in the adjoint operator, and it scales the rigid-rotation gauge test. It was computed as `NORM_1` of a sub-vector, and PETSc computes `NORM_1` with BLAS dasum.

On a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH; conda-forge PETSc 3.25.3 and OpenBLAS), dasum of the same data gives one of two results an ulp apart, depending on where the array sits in memory. It differs by offset for 89 of 90 random vectors (n = 384, 1536 and 20011), and each offset's result is reproducible. Fresh `NORM_2`, `VecDot`, `VecSum` and `NORM_INFINITY` showed no offset dependence on the same vectors. `getSubVector` returns an array placed somewhere new on each call, so the scale changed from run to run, and even between calls in one process.

The ulp went into the operator. On a rotated free-slip annulus (cell 0.2, viscosity 1 + T), a warm re-solve after T goes from 0 to 1 gave a pressure sub-solve of 12, 13 or 200 iterations (its cap) from run to run at np 2. The answer was the same each time.

### How it was traced
- **Inputs:** the mesh partition, the Jacobian, the rotation Q and the constrained rows were bit-identical across runs, and so was a fresh `J.ptap(Qt)`.
- **The operator:** after `zeroRowsColumns` it fell into two classes, which mapped one-to-one onto the iteration counts. With a fixed diagonal value, `zeroRowsColumns` was deterministic.
- **The scale:** each rank's local |diag| sum was identical every time, but PETSc's global `NORM_1` was not.
- **PETSc's gemv switch:** `-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0`, which made an earlier serial case bit-identical, did not make this one repeatable (still 12, 13 or 200).

### The change
`_sum_abs_deterministic` sums |values| with `math.fsum`, which rounds once from the exact sum and so is independent of order and alignment. `_velocity_diag_scale` uses it per rank, gathers the ranks' sums on the operator's communicator, and sums them the same way. The result is deterministic: bit-identical from run to run at a given rank count. It is not the correctly rounded mean, since fsum of per-rank fsums divided by n rounds more than once. A grep of `src` finds no other `NORM_1`; the other vector norms are `NORM_2` and `NORM_INFINITY`.

This makes the rotated operator bit-identical from run to run. It does not make every reduction in the solve alignment-free: PETSc's `VecMDot` gemv path is alignment-dependent too (`-vec_mdot_use_gemv`), and that still varies Krylov round-off.

### Tests
- `tests/test_1089_velocity_diag_scale_is_bit_identical.py`:
  - the per-rank sum of the same data at 8 memory offsets (n = 384, 1536 and 20011) must give one value. A `NORM_1` version of the helper fails this every time on the review machine, with 2 or 3 distinct values per size;
  - the scale on 10 freshly assembled operators, 3 calls each, must give one value, and every call must go through the helper (counted). A scale rewired back to `NORM_1` fails this serially (0 calls against 30).
  It passes at np 1, 2 and 3.
- The fixture above, np 2, 10 runs, without the gemv switch: development gave 13 iterations in 8 runs and 200 in 2. This branch gives 13 in all 10, with one operator hash and one answer.
- The rotated free-slip suite (38 files, serial) and the parallel rotated files at np 2 pass.

### Is the fixture's pressure tolerance below its attainable floor?
Yes, just: the same shape as the earlier stagnation cases.
- **Target:** the warm solve's pressure equations already hold, so the pressure sub-solve starts at a residual of 5.6e-11. Its tolerance (rtol 1e-9) sets a target of 5.6e-20.
- **The 13-iteration class** reaches 4.3e-20, under the target by a factor of 1.3.
- **The 200-iteration class** stagnates at 1e-19 to 1.6e-18 from about iteration 13 on, just above it, and runs to the cap.

So the target sits on the round-off floor, and an ulp in the operator decides whether it is met. This change makes the outcome repeatable, and at np 2 on this mesh it lands on the good side. It does not move the target off the floor: at np 3 the same fixture hits the 200 cap in every run, on development and on this branch alike (measured twice, independently). The round-off test meant to stop a sub-solve asked to resolve round-off did not fire here at np 2: its ratio sits near the threshold and moves with the partition. That fragility is its own item, not this branch's.

Underworld development team with AI support from Claude Code
