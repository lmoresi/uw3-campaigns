# Review of #1131 at e95fe4ec, by H5

H5: fault, multigrid and restart fixes, with parallel runs on a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH). Built at e95fe4ec. Development is a7297194.

**Verdict: NOT READY on F1, a small change. Everything else holds.**

## What holds (measured)

- **Every generator that goes through the conversion**, at np 1 to 5, each parallel run with an empty mesh cache so the gmsh conversion really runs: UnstructuredSimplexBox, StructuredQuadBox, Annulus, AnnulusInternalBoundary, AnnulusWithSpokes, BoxInternalBoundary, SphericalShell, SphericalShellInternalBoundary, SegmentedSphericalShell, SegmentedSphericalBall.
  - All 10 build at every rank count, with the same global cell count as serial: 66, 16, 144, 422, 177, 256, 570, 1087, 507, 413.
  - The world-communicator generators keep their barrier: `comm` is not COMM_SELF.
- **The PR's tests:**
  - test_1176_rank0_generators_parallel: 3 passed at np 2, 3, 4 and 5, with a fresh cache each time;
  - test_1177_spherical_generator_fixes: 2 passed serially.
- **test_0858 at np 3 and np 5**, in the repository: 2 passed.
- **On development**, test_1176's `segmented_ball` and `annulus_with_spokes` cases at np 2 hang. Each was killed by an outer 480 s guard, with no pytest output; `segmented_shell` passes (F4).
- **The shell radius tolerance** (a quarter of the smaller gap between the radii) is sound: the OCC radii are exact, and half a cell was the whole gap on a coarse shell.

## Findings

**F1 (medium, blocking): the file rank 0 writes is read by every rank with nothing ordering the two.** In SegmentedSphericalShell, SegmentedSphericalBall, the segmented surface and AnnulusWithSpokes:
- rank 0 writes `uw_filename + ".h5"` through `PETSc.ViewerHDF5().create(..., "w", comm=COMM_SELF)` and `viewer(plex)` inside its rank-0 block;
- every rank then calls `Mesh(uw_filename + ".h5")`, a collective read on COMM_WORLD.

The viewer is never destroyed, so rank 0's HDF5 file can still be open for writing, and unflushed, when the others open it. No barrier follows the block either.

The removed world barrier was, by its own comment, the guarantee that "every rank sees the complete file". It never worked in parallel, because only rank 0 reached it. With the hang gone, this path now runs, and nothing orders the write before the read.

It passed here: one node, shared page cache. On a parallel filesystem (Lustre) an unflushed write read by another node is exactly the case that bites.

Fix, in each of these generators: `viewer.destroy()` inside the rank-0 block, then `uw.mpi.barrier()` after the block, reached by every rank. That restores what the removed barrier meant, in a place every rank reaches.

**F2 (low): `comm != PETSc.COMM_SELF` tests identity, not size.** A caller that passes mpi4py's `MPI.COMM_SELF` or a duplicated self-communicator still takes the barrier and hangs. I read this, but no current caller does it: all three pass `PETSc.COMM_SELF`. `comm is not None and comm.getSize() == 1` (or the mpi4py equivalent) says what is meant.

**F3 (low): the timeout marker does not make the regression fail.**
- The comment says "The timeout is the regression's failure". On development the `segmented_ball` case blocked past 480 s, with `timeout(300)` set, and pytest never reported: a rank blocked in `MPI_Barrier` does not run the signal-method handler.
- What fails it in CI is the supervisor around the parallel batches (`--silence 300`, which exits 124), and that is enough.
- Either reword the comment, or use `pytest.mark.timeout(300, method="thread")`, which dumps the stacks and exits even when a rank is blocked in C.

**F4 (low): one of the three cases does not guard on MPICH.** On development, `segmented_shell` passes at np 2 in 11 s. Rank 0's stray world barrier was matched by a collective inside the other ranks' read, which is erroneous MPI that MPICH lets through. `segmented_ball` hangs. The test still catches the regression through the ball, but say in the docstring that the shell case may pass on some MPI builds.

## Not checked

- The rank-0 write on a parallel filesystem (F1 is by reading).
- Any MPI other than MPICH.

## Re-check at 17eaebb4: READY

- **F1 fixed.** All four generators (the three segmented ones and AnnulusWithSpokes) destroy the viewer inside the rank-0 block, and a `uw.mpi.barrier()` at function level, reached by every rank, comes before the collective `Mesh(... .h5)` read.
  - Measured: every generator that goes through the conversion, at np 2, 3, 4 and 5, each with an empty mesh cache: all 10 build, with the same cell counts as serial (66, 16, 144, 422, 177, 256, 570, 1087, 507, 413).
  - test_1176: 3 passed at np 2, 3, 4 and 5.
- **F2 fixed:** `comm is None or comm.getSize() > 1`. One note, not blocking: `getSize` is petsc4py's spelling, so an mpi4py communicator would raise AttributeError here. Every current caller passes a PETSc communicator.
- **F3 and F4:** the comment and the docstring now say what was measured.
