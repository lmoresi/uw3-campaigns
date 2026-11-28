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
