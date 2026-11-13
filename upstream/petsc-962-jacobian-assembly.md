# Draft upstream report: PETSc, #962

*Status: READY FOR LOUIS (complete 2026-11-13): DRAFT for Louis to send in his name (where: PETSc's GitLab issues or petsc-maint). Drafted by
H1 (the parallel review desk) from the PETSc source, 2026-11-13; placed here by the dev hub. The
reproducer is W1's (the integration session; macOS, 12-core Apple M4, serial runs only), run there on one rank;
H1 ran it at np 1, 2 and 4 on 3.25.3 (Linux workstation, MPICH); its results are in the reproducer section. The second observation below the
line is W1's, measured on one rank.*

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

**Reproducer:** `petsc-962-reproducer.c` (beside this file; PETSc only, about 130 lines). Two P1 scalar
fields on the default box mesh; the Jacobian is each field's mass matrix (`PetscDSSetJacobian`, g0 = 1)
and the Jacobian preconditioner is twice that (`PetscDSSetJacobianPreconditioner`, g0 = 2); then
`DMPlexSetSNESLocalFEM` and one `SNESComputeJacobian(snes, X, J, P)` on two matrices from `DMCreateMatrix`.

```
mpicc petsc-962-reproducer.c -o petsc-962-reproducer -I$PETSC_DIR/include -L$PETSC_DIR/lib -lpetsc -lm
mpiexec -n 1 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
mpiexec -n 2 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 1,1
mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1 -assemble_on_empty_ranks
```

One quadrilateral cell on two ranks, or two cells on four, leaves a rank without a cell. On one rank
(macOS arm64, conda-forge PETSc 3.25.3, Open MPI) the program prints:

```
-dm_plex_box_faces 1,1    [0] cells 1    two matrices:  |J| = 3.928371006592e-01  |P| = 7.856742013184e-01
-dm_plex_box_faces 2,1    [0] cells 2    two matrices:  |J| = 3.286710990611e-01  |P| = 6.573421981222e-01
```

On more than one rank (PETSc 3.25.3, conda-forge build, MPICH; Linux, Intel Xeon), every run that leaves a
rank without a cell returns a Jacobian of norm zero from `SNESComputeJacobian(snes, X, J, P)`, on every
rank including the one that holds the cell, while P is correct. The job then hangs and has to be killed.
Making the ranks without cells assemble J once more after the call restores the one-rank norms, and the
job exits cleanly:

```
$ mpiexec -n 1 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
[0] cells 2
two matrices:        |J| = 3.286710990611e-01  |P| = 6.573421981222e-01
one matrix twice:    |K| = 3.286710990611e-01  |K - J| = 0.000000000000e+00        (exit 0)

$ mpiexec -n 2 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 1,1
[0] cells 0
[1] cells 1
two matrices:        |J| = 0.000000000000e+00  |P| = 3.928371006592e-01
one matrix twice:    |K| = 0.000000000000e+00  |K - J| = 3.928371006592e-01
(hangs after this; killed by the timeout)

$ mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1
[0] cells 0
[1] cells 0
[2] cells 0
[3] cells 2
two matrices:        |J| = 0.000000000000e+00  |P| = 3.286710990611e-01
one matrix twice:    |K| = 0.000000000000e+00  |K - J| = 3.286710990611e-01
(hangs after this; killed by the timeout)

$ mpiexec -n 4 ./petsc-962-reproducer -dm_plex_simplex 0 -dm_plex_box_faces 2,1 -assemble_on_empty_ranks
[0] cells 0   [1] cells 0   [2] cells 0   [3] cells 2
two matrices:        |J| = 3.286710990611e-01  |P| = 6.573421981222e-01
one matrix twice:    |K| = 3.286710990611e-01  |K - J| = 0.000000000000e+00        (exit 0)
```

So the call returns, with a wrong J; the hang comes later, from the collective left unpaired. (With
`-boundary` at np 2, |P| comes out as 1.4407e+01, the one-rank |J| rather than the one-rank |P| of
2.8814e+01, which suggests the cell rank's J assembly paired with the empty rank's P assembly; not traced.)

**How we met it:** Stokes solves in Underworld3 (a separate pressure-Schur preconditioner matrix) on meshes
where a rank holds no cells, which happens routinely for extracted submeshes and for coarse refined bases
at high rank counts.

---

**A second observation, a question rather than a report** (measured on one rank with the same
program and `-boundary`, which adds a natural boundary on the `marker` label with a boundary Jacobian
kernel, g0 = 10, and a boundary Jacobian-preconditioner kernel, g0 = 20, on field 0).

When the same matrix is passed as J and P, `DMPlexComputeJacobianByKey` adds the Jacobian kernels only
("user passed in the same matrix, avoid double contributions and only assemble the Jacobian").
`DMPlexComputeBdJacobianSingleByLabel` has no such test, so it adds the boundary Jacobian kernels and the
boundary preconditioner kernels into the one matrix. With K from `SNESComputeJacobian(snes, X, K, K)` and
J from the two-matrix call:

| mesh | \|J\| | \|K\| | \|K - J\| |
|---|---|---|---|
| 1 cell, no boundary kernels | 3.928371006592e-01 | 3.928371006592e-01 | 0 |
| 2 cells, no boundary kernels | 3.286710990611e-01 | 3.286710990611e-01 | 0 |
| 1 cell, `-boundary` | 1.440700275543e+01 | 4.268930244464e+01 | 2.828427124746e+01 |
| 2 cells, `-boundary` | 1.197670063184e+01 | 3.554492028440e+01 | 2.357022603955e+01 |

Is that intended? We met it through a penalty boundary term that we register for both matrices: a
single-matrix Jacobian call then carries the boundary term twice.
