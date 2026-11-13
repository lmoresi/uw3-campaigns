static char help[] = "DMPlexComputeJacobianByKey() with a Jacobian and a Jacobian preconditioner, on a mesh that leaves a rank without cells.\n\
  -assemble_on_empty_ranks : ranks without cells assemble the Jacobian once more after SNESComputeJacobian()\n\
  -boundary                : add boundary kernels for the Jacobian and for the preconditioner\n\n";

/*
  Two P1 scalar fields on the default box mesh. The Jacobian is the mass matrix of
  each field and the Jacobian preconditioner is twice that, so on any number of
  ranks |P| = 2 |J|.

    mpiexec -n 1 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
    mpiexec -n 2 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 1,1
    mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
    mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1 -assemble_on_empty_ranks
    mpiexec -n 1 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1 -boundary

  One quadrilateral cell on two ranks, or two on four, leaves a rank without a cell.
  (Quadrilaterals need no mesh generator, which conda-forge's PETSc does not have.)
*/

#include <petscdmplex.h>
#include <petscsnes.h>
#include <petscds.h>

static void g0_jac(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, PetscReal u_tShift, const PetscReal x[], PetscInt numConstants, const PetscScalar constants[], PetscScalar g0[])
{
  g0[0] = 1.0;
}

static void g0_pre(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, PetscReal u_tShift, const PetscReal x[], PetscInt numConstants, const PetscScalar constants[], PetscScalar g0[])
{
  g0[0] = 2.0;
}

static void g0_bd_jac(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, PetscReal u_tShift, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar g0[])
{
  g0[0] = 10.0;
}

static void g0_bd_pre(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, PetscReal u_tShift, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar g0[])
{
  g0[0] = 20.0;
}

int main(int argc, char **argv)
{
  DM          dm;
  PetscDS     ds;
  SNES        snes;
  Mat         J, P, K;
  Vec         X;
  PetscInt    dim, cStart, cEnd;
  PetscBool   simplex, patch = PETSC_FALSE, boundary = PETSC_FALSE;
  PetscReal   nJ, nP, nD;
  PetscMPIInt rank;

  PetscFunctionBeginUser;
  PetscCall(PetscInitialize(&argc, &argv, NULL, help));
  PetscCallMPI(MPI_Comm_rank(PETSC_COMM_WORLD, &rank));
  PetscCall(PetscOptionsGetBool(NULL, NULL, "-assemble_on_empty_ranks", &patch, NULL));
  PetscCall(PetscOptionsGetBool(NULL, NULL, "-boundary", &boundary, NULL));

  PetscCall(DMCreate(PETSC_COMM_WORLD, &dm));
  PetscCall(DMSetType(dm, DMPLEX));
  PetscCall(DMSetFromOptions(dm));
  PetscCall(DMGetDimension(dm, &dim));
  PetscCall(DMPlexIsSimplex(dm, &simplex));
  for (PetscInt f = 0; f < 2; ++f) {
    PetscFE fe;

    PetscCall(PetscFECreateLagrange(PETSC_COMM_SELF, dim, 1, simplex, 1, PETSC_DETERMINE, &fe));
    PetscCall(DMSetField(dm, f, NULL, (PetscObject)fe));
    PetscCall(PetscFEDestroy(&fe));
  }
  PetscCall(DMCreateDS(dm));
  PetscCall(DMGetDS(dm, &ds));
  for (PetscInt f = 0; f < 2; ++f) {
    PetscCall(PetscDSSetJacobian(ds, f, f, g0_jac, NULL, NULL, NULL));
    PetscCall(PetscDSSetJacobianPreconditioner(ds, f, f, g0_pre, NULL, NULL, NULL));
  }
  if (boundary) {
    DMLabel        label;
    PetscWeakForm  wf;
    PetscInt       bd;
    const PetscInt id = 1;

    PetscCall(DMGetLabel(dm, "marker", &label));
    PetscCall(DMAddBoundary(dm, DM_BC_NATURAL, "wall", label, 1, &id, 0, 0, NULL, NULL, NULL, NULL, &bd));
    PetscCall(PetscDSGetBoundary(ds, bd, &wf, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL));
    PetscCall(PetscWeakFormSetIndexBdJacobian(wf, label, id, 0, 0, 0, 0, g0_bd_jac, 0, NULL, 0, NULL, 0, NULL));
    PetscCall(PetscWeakFormSetIndexBdJacobianPreconditioner(wf, label, id, 0, 0, 0, 0, g0_bd_pre, 0, NULL, 0, NULL, 0, NULL));
  }
  PetscCall(DMPlexSetSNESLocalFEM(dm, PETSC_FALSE, NULL));

  PetscCall(SNESCreate(PETSC_COMM_WORLD, &snes));
  PetscCall(SNESSetDM(snes, dm));
  PetscCall(DMCreateMatrix(dm, &J));
  PetscCall(DMCreateMatrix(dm, &P));
  PetscCall(DMCreateMatrix(dm, &K));
  PetscCall(DMCreateGlobalVector(dm, &X));
  PetscCall(VecZeroEntries(X));

  PetscCall(DMPlexGetHeightStratum(dm, 0, &cStart, &cEnd));
  PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "[%d] cells %" PetscInt_FMT "\n", rank, cEnd - cStart));
  PetscCall(PetscSynchronizedFlush(PETSC_COMM_WORLD, PETSC_STDOUT));

  /* Two matrices: a rank with cells assembles J and P inside DMPlexComputeJacobianByKey(),
     a rank without cells assembles P only */
  PetscCall(SNESComputeJacobian(snes, X, J, P));
  if (patch && cEnd == cStart) {
    PetscCall(MatAssemblyBegin(J, MAT_FINAL_ASSEMBLY));
    PetscCall(MatAssemblyEnd(J, MAT_FINAL_ASSEMBLY));
  }
  PetscCall(MatNorm(J, NORM_FROBENIUS, &nJ));
  PetscCall(MatNorm(P, NORM_FROBENIUS, &nP));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "two matrices:        |J| = %.12e  |P| = %.12e\n", (double)nJ, (double)nP));

  /* One matrix passed twice: the cell loop adds the Jacobian kernels only, the
     boundary loop adds the Jacobian and the preconditioner kernels */
  PetscCall(SNESComputeJacobian(snes, X, K, K));
  PetscCall(MatNorm(K, NORM_FROBENIUS, &nP));
  PetscCall(MatAXPY(K, -1.0, J, SAME_NONZERO_PATTERN));
  PetscCall(MatNorm(K, NORM_FROBENIUS, &nD));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "one matrix twice:    |K| = %.12e  |K - J| = %.12e\n", (double)nP, (double)nD));

  PetscCall(VecDestroy(&X));
  PetscCall(MatDestroy(&K));
  PetscCall(MatDestroy(&P));
  PetscCall(MatDestroy(&J));
  PetscCall(SNESDestroy(&snes));
  PetscCall(DMDestroy(&dm));
  PetscCall(PetscFinalize());
  return 0;
}
