# Draft upstream report: PETSc, #962

*Status: DRAFT for Louis to send in his name (where: PETSc's GitLab issues or petsc-maint). Drafted by
H1 (the parallel review desk) from the PETSc source, 2026-11-13; placed here by the dev hub. The
reproducer section is to be filled from W1's standalone reproducer, run by H1 at np 2 and 4 on 3.25.3.
W1 adds the second, boundary-routine observation below the line if it is confirmed.*

---

**Title:** DMPlexComputeJacobianByKey skips the Jacobian's assembly on a rank with no cells when J != P (collective mismatch)

PETSc 3.25.3, 3.26.1 and main (src/dm/impls/plex/plexfem.c, `DMPlexComputeJacobianByKey()` and `DMPlexComputeJacobianByKeyGeneral()`).

When a rank owns no cells, the function jumps to `end` before reading `hasJac` and `hasPrec` from the cell DS, so both stay false on that rank. At `end` the Jacobian is assembled only `if (hasJac && hasPrec)`, which is the local value. With a separate preconditioner matrix (J != P), every rank with cells calls `MatAssemblyBegin/End(Jac)` and the rank without cells does not. The collectives then pair one step out: an `MPI_ERR_TRUNCATE` abort, or a hang, a few collectives later (seen in `MatPtAP` and `PCSetUp`).

In 3.25.3 the flag was reduced (`MPIU_Allreduce(&assOp, &gassOp, ..., MPI_LOR, ...)`) but the reduced `gassOp` was never used. Commit 054f31b90d (clang-format-23) removed that unused reduction, so 3.26.1 and main make no reduction at all.

Suggested fix, in both functions:
```c
end: {
  PetscBool assOp = hasJac && hasPrec ? PETSC_TRUE : PETSC_FALSE;

  if (dmAux) PetscCall(DMDestroy(&plex));
  PetscCallMPI(MPIU_Allreduce(MPI_IN_PLACE, &assOp, 1, MPI_C_BOOL, MPI_LOR, PetscObjectComm((PetscObject)dm)));
  if (assOp) {
    PetscCall(MatAssemblyBegin(Jac, MAT_FINAL_ASSEMBLY));
    PetscCall(MatAssemblyEnd(Jac, MAT_FINAL_ASSEMBLY));
  }
}
```

**Reproducer:** [W1's standalone DMPlex with more ranks than cells, a two-field DS with a Jacobian
preconditioner, `SNESComputeJacobian` with J != P; results at np 2 and 4 on 3.25.3 to be added].

**How we met it:** Stokes solves in Underworld3 (a separate pressure-Schur preconditioner matrix) on meshes
where a rank holds no cells, which happens routinely for extracted submeshes and for coarse refined bases
at high rank counts.

---

*Possible second item (W1, to confirm before sending):* `DMPlexComputeBdJacobianSingleByLabel` with the
same matrix passed as J and P adds both the Jacobian and the Jacobian-preconditioner boundary kernels into
it (no same-matrix guard); ask whether that is intended.
