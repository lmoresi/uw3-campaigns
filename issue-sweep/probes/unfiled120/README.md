# Row 120: a rotated solve whose final residual takes one of two values, per process

Fixture: test_1111's shell case, the third rotated solve (rotfs3). Development fbef72fa, serial,
macOS arm64, OpenBLAS 0.3.30.

1. Not hash ordering, not threads (split.txt): 5 runs each of PYTHONHASHSEED 0 / random x
   OMP_NUM_THREADS / OPENBLAS_NUM_THREADS 1 / unset. Both values appear in every configuration.
2. Not the JIT: fresh per-run JIT caches build the same 10 modules (same source hashes) and the
   value still alternates.
3. Where it enters (inputs.py): the KSP operator (CSR values) is identical in every run; only
   the right-hand side differs. It differs in 104 of 622 entries (every third, the shell's 3-D
   component), by at most 5.6e-17 absolute (2.4e-18 relative to the norm). The entries are
   about 1e-9, so this is a last-bit difference in O(1) terms that cancel.
4. Which step (nsp.py): the right-hand side is projected against the rigid-rotation null space
   (nsp.remove(bhat)). The input to NullSpace.remove and its basis are byte-identical in every
   run, 64-byte aligned, of type seq, yet the output takes one of the two values. The first
   removal of the file (the annulus) varies the same way.
5. Not PETSc arithmetic alone (replay.py): the saved input and basis, replayed through
   NullSpace.remove in a fresh petsc4py-only process, give the same bits 10 of 10 times.
6. The import (replay_uw.py): the same replay after `import underworld3` gives the other value
   in 1 of 8 runs. So process state created by importing underworld3 makes a pure-PETSc
   NullSpace.remove nondeterministic. The import adds only `options_left` to the PETSc options.
7. Not OpenBLAS's kernel choice: with OPENBLAS_CORETYPE forced to VORTEX or ARMV8, both values
   still appear.
H1 sees the same two-state round-off at np 2 on development, so it is not serial-only.

## Correction and the source (later the same day)
- Item 6 above was wrong. petsc4py alone also flips: 1 of 40 fresh processes (import_bisect.py,
  bisect.txt). The earlier 10/10 was too small a sample. gmsh 3/40 and underworld3 0/20 sit in the
  same noise, so it is not the import.
- prims.py: in the replay it is VecMDot that varies. The second coefficient is -0x1.7fcp-53 in
  39 runs and -0x1.d027d85cd239dp-52 in 1. VecDot one at a time and numpy give -0x1.1027d85cd239dp-52
  in every run. The coefficient is round-off: the right-hand side is already orthogonal to that
  rotation.
- The GEMV path (prims_opt.py, and test_1111 itself through PETSC_OPTIONS, 10 runs each):
  - unset (the default): two values, 6/4;
  - -vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0: one value, 10/10 (a third value);
  - -vec_mdot_use_gemv 1 -vec_maxpy_use_gemv 1: two values, 6/4.
  So the nondeterminism is PETSc's GEMV path for VecMDot/VecMAXPY (the default here), which calls
  OpenBLAS dgemv. The loop path is deterministic.
- Scope: FGMRES orthogonalisation also uses VecMDot/VecMAXPY, so every Krylov solve is exposed,
  not only the rotated null-space projection.

## (a) Timing the GEMV path off (for H1, hyperion)
gemv_timing.py times four cases; run_gemv_timing.sh runs it with PETSC_OPTIONS unset and with
`-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0`, every thread variable 1, then
gemv_timing_compare.py prints the median wall times, the off/default ratio, and whether
iterations are equal.
- Cases: rotated FMG annulus, 3-D shell Stokes (rotated free slip), a VEP box step (velocity
  GMRES restart 30; each repeat a fresh solver's first step, since a step advances the elastic
  history), an advection-diffusion step. 5 timed repeats after a warm-up.
- Laptop smoke test (scale 0.5, 2 repeats, serial): iterations equal; ratio 0.997-1.03.
- Seen while writing it: on the VEP box, a SECOND step from the evolved history had different
  iteration counts with and without the GEMV path (39/691 against 45/519 Newton/linear). That
  nonlinear solve is sensitive to the last-bit difference.
