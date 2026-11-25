# Projection solver defaults: four configurations (UNFILED 45; Louis's decision 9)

H4, 2026-11-25, for C1. Measured locally under the GitHub pause.
- **Build:** #1298's branch with development merged (9013e929); the increment rule is in force.
- **Machine:** hyperion, a 96-thread Linux workstation (Xeon Gold 6240R, MPICH).
- **Method:** every projection was overridden by H4's audit hook (env `PROJ_TOL`, `PROJ_KSP`, `PROJ_PC`), so library code was unchanged. Logs and scripts are in hyperion `runs/2026-11-10-h4/projaudit/` (`four.sh`, `four_*.jsonl`, `ve/ve_box.py`, `illcond*.py`).

## The four configurations

Today's default is GMRES+GAMG at each projection's own tolerance (1e-3 for the history projections, 1e-4 or 1e-6 elsewhere).

**The 36 time-loop files** (VE Stokes and stress transport, the stress histories, semi-Lagrangian and SLCN, the free surface, transient Darcy and Richards, slip surfaces), serial, `-n 4`, tier C excluded. All four configurations pass the same 364 tests.

| configuration | wall | projection solves | Newton its | linear its |
|---|---|---|---|---|
| GMRES+GAMG, default tolerances (today) | 526 s | 1577 | 1635 | 2679 |
| GMRES+GAMG, 1e-10 | 537 s | 1575 | 1436 | 5728 |
| CG+Jacobi, default tolerances | 520 s | 1577 | 1650 | 6453 |
| CG+Jacobi, 1e-10 | 515 s | 1575 | 1436 | 17644 |

Wall time is within noise across all four (515 to 537 s). The projections are small mass-matrix solves, so their linear iterations, even six times as many, do not show at this scale.

**The VE box** is H1's UNFILED 45 case, rebuilt from its description: a simplex box at cell 1/12, P2/P1, Maxwell with η = 1 + 99 exp(−r²/0.02) at (0.2, 0) and G = 1, BDF-1 at dt 0.1, solve tolerance 1e-10, 3 steps. The values are max |Δ| / max |ref| over 77 points.

| configuration | np 1 vs np 2, step 1 v / stress | step 2 | step 3 | serial error vs the tightest, step 2 v / stress |
|---|---|---|---|---|
| GMRES+GAMG, default | 1.6e-11 / 5.9e-4 | 8.7e-4 / 2.9e-4 | 1.2e-4 / 2.3e-4 | 1.4e-3 / 3.4e-4 |
| GMRES+GAMG, 1e-10 | 1.6e-11 / 8.9e-11 | 7.0e-11 / 7.4e-11 | 2.8e-11 / 7.2e-11 | 3.2e-11 / 9.5e-12 |
| CG+Jacobi, default | 1.6e-11 / 9.5e-11 | 7.1e-11 / 7.6e-11 | 2.7e-11 / 7.3e-11 | **2.6e-3 / 6.3e-4** |
| CG+Jacobi, 1e-10 | 1.6e-11 / 9.5e-11 | 7.1e-11 / 7.6e-11 | 2.7e-11 / 7.3e-11 | (the reference) |

(The serial-error reference is CG+Jacobi at 1e-10, np 1.)

**Two separate effects:**
- **Partition dependence comes from GAMG.** Its aggregation follows the partition, so the residual it leaves at 1e-3 or 1e-4 differs between rank counts. CG with Jacobi is partition-free by construction: Jacobi is pointwise, and CG only reduces. At its default tolerance it already gives np 1 = np 2 to 7e-11. That matches H7's finding.
- **Accuracy comes from the tolerance alone.** CG+Jacobi at the default tolerance is reproducible but no more accurate than today. Its serial error is 2.6e-3 in v and 6.3e-4 in the stress at step 2, a little worse than GMRES+GAMG's 1.4e-3 / 3.4e-4 at the same tolerance. At 1e-10 either solver is accurate to about 1e-11.

## The harder cases: does Jacobi stall?

The test is one projection to rtol 1e-8 against a tight GAMG or direct reference, serial.

| case | GMRES+GAMG its / rel err / time | CG+Jacobi its / rel err / time |
|---|---|---|
| box P2, cell 0.05 | 6 / 3e-10 / 0.05 s | 16 / 7e-9 / 0.04 s |
| box P3, qdegree 8 | 6 / 1e-10 / 0.22 s | 20 / 5e-9 / 0.21 s |
| box P4, qdegree 8 | 6 / 3e-10 / 0.39 s | 21 / 1e-8 / 0.34 s |
| annulus P2, cell 0.05 | 6 / 3e-10 / 0.10 s | 16 / 7e-9 / 0.08 s |
| spherical shell P2, cell 0.15 | 7 / 2e-9 / 0.75 s | 32 / 7e-9 / 0.61 s |
| graded adapt child, h 0.004 to 0.1, P2 | 1 / 3e-15 / 0.43 s | 17 / 6e-9 / 0.07 s |
| box P2, `smoothing_length` 0.01 | 6 / 4e-10 / 0.09 s | 16 / 3e-9 / 0.09 s |
| box P2, `smoothing_length` 0.05 | 8 / 3e-9 / 0.10 s | 64 / 1e-9 / 0.10 s |
| box P2, `smoothing_length` 0.2 | 14 / 7e-11 / 0.16 s | 191 / 9e-11 / 0.11 s |

- **No stall.** CG+Jacobi converges everywhere, in equal or less time. Curvature and grading do not hurt it: Jacobi removes the diagonal scaling.
- **Smoothing raises its iteration count.** A screened-Poisson projection is a Laplacian-dominated operator as L/h grows (191 iterations at L = 0.2, h = 0.05). On large meshes with strong smoothing, GAMG may win on time. Projections with `smoothing_length` set could keep GAMG.

## A separate defect found on the way: under-integrated projections are singular

A projection of degree 3 or 4 on a mesh with the default `qdegree` (2 for `UnstructuredSimplexBox`) assembles a singular mass matrix. Too few quadrature points for the basis leave the P3 matrix with 1 zero eigenvalue and P4 with 59 (cell 0.25).
- **LU** fails (zero pivot; it returns zeros).
- **GMRES+GAMG** returns one of many solutions, and looks fine.
- **CG+Jacobi** reports convergence (reason 2) with an answer 39 to 45% off.

With `qdegree` 8 the matrices are SPD and both solvers agree to 1e-8. Today's default hides the problem rather than solving it, and a switch to CG would make it visible as a wrong answer. So a projection whose degree needs more quadrature than the mesh has should be refused, or should raise its own quadrature. This needs no decision: it should be its own fix and test, owner to assign.

## Proposal for Louis (decision 9, widened)

1. **Projection solver default: CG + Jacobi** (`snes ksponly`, as `SNES_Projection.linear_solver()` already offers opt-in, #800), for every projection class. It is partition-free, and as fast or faster here. A projection with `smoothing_length` set could keep GMRES+GAMG.
2. **History-projection tolerance: 1e-10**, for the projections whose result feeds the next step (stress-history commit, flux and forcing, the VE and ψ\* histories, the SLCN commit, the free surface's velocity). It costs nothing measurable at these sizes (515 against 526 s for the 36 files), and gives step-2 accuracy of about 1e-11 against 1e-3 today.
3. **Prerequisite for (1): the under-integration fix above,** so that CG never reports convergence on a singular matrix.

Either (1) or (2) alone removes UNFILED 45's partition dependence. Only (2) improves accuracy. (1) without (3) would turn a hidden defect into a visible wrong answer on under-integrated P3+ projections.

Not measured: parallel runs of the 36 files (np 1 against np 2 was measured on the VE box only), meshes over about 1e5 nodes, and 3-D at high degree.
