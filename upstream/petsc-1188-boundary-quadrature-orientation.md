# Draft upstream report: PETSc, #1188 (second item for Monday, with #962)

*Status: NOT READY (C1 sets it). W1 added the C reproducer and the check of the mechanism on 2026-11-14 and corrected the Reach paragraph; a patched build has not been made. Louis sends it in his name. Facts below are W1's, measured on one rank, conda-forge PETSc 3.25.3, 2026-11-14. Probes: campaigns 9b95e07, `issue-sweep/internal-face-orientation/`. Issue: underworldcode/underworld3#1188.*

---

**Working title:** PetscFEIntegrateBdResidual_Basic pairs quadrature points with the face tabulation using the edge rule on triangular faces with a non-zero orientation (3-D)

**Suspected lines**, by reading; the same in 3.25.3 and main: `src/dm/dt/fe/impls/basic/febasic.c`, `PetscFEIntegrateBdResidual_Basic` and the boundary Jacobian beside it. The physical quadrature point `q` is paired with the tabulated basis at `qp = ornt < 0 ? (Nq - 1 - q) : q`. That is a reversal, which is correct for an edge, the only 2-D face. A triangle has six orientations, and positive ones are left unpermuted. The hybrid integrals in the same file use `PetscDSPermuteQuadPoint`. The measurements fit this reading (2-D clean, 3-D wrong for both signs). For positive orientations they confirm it: the wrong nodal loads of case A are reproduced at every node, to 1e-17, by the exact integral with the load's three vertex values rotated, (2, 0, 1) at orientation 1 and (1, 2, 0) at orientation 2, and by no other of the 36 choices. That is the basis tabulated at the un-rotated point. We have not built PETSc with the line changed.

**Reproducer, PETSc only** (`issue-sweep/internal-face-orientation/petsc_only/bd_residual_orientation.c`, about 150 lines, no mesh generator, one process): the unit cube cut into six tetrahedra, refined regularly, a P2 scalar field, the natural term f0 = x on the wall z = 1, residual at zero state. With b the residual, b.1 must be 1/2 and b.x must be 1/3; the default quadrature integrates both exactly.

| case | wall faces by orientation | b.1 - 1/2 | b.x - 1/3 |
|---|---|---|---|
| 3-D, refine 0 | 0: 2 | -1.1e-16 | -5.6e-17 |
| 3-D, refine 1 | 0: 6, 1: 2 | -1.7e-16 | -5.2e-3 |
| 3-D, refine 2 | 0: 18, 1: 12, 2: 2 | 0 | -2.3e-3 |
| 3-D, refine 3 | 0: 56, 1: 54, 2: 18 | 1.1e-16 | -7.3e-4 |
| 2-D, refine 2 | 0: 4 | -1.7e-16 | -5.6e-17 |

**Observed through underworld3 (one rank):**
- **A. Exterior wall, against exact integrals.** Unit cube, P2, natural condition (0,0,x) on Top, qdegree 4 (exact for the integrand):
  - refinement 0: every Top face has orientation 0, and 0 of 101 nodes differ from exact;
  - refinement 1: orientations 0/1/2 = 132/15/21, and 163 of 369 nodes differ, by up to 7.0e-5 against a largest nodal load of 3.8e-3;
  - refinement 2: 864 of 1409 nodes differ, by up to 8.8e-6 against 9.8e-4.

  Every differing node touches a face with a non-zero orientation. The total is exact to twelve digits.
- **B. Interior face integrated from its second support cell** (the two support cells swapped before the build):
  - 2-D annulus: orientation 0 -> -1, and no node changes;
  - 3-D shell: orientations -1/-2/-3, and all 534 loaded nodes change, by up to 9.4e-3 against 1.9e-2, summing to 1e-17.
- **In parallel**, an interior face whose two cells are on different ranks is integrated from the other cell on one of them. Measured once (underworld3#1150): at 8 ranks one face of 540 was held by two ranks and exactly its 6 nodes differed from the 1, 2 and 4 rank loads.

**Reach:** any boundary integrand that reads the coordinates at the quadrature point. Terms built from the solution, auxiliary fields or the face normal are evaluated at one consistent point. The error falls with h (b.x above: by 0.44, then 0.32, per refinement), which is slower than a P2 boundary term should converge. We have not run a convergence test of a solved problem through it. Only triangles are measured; quadrilateral faces of refined hexahedra are not.

**Our own exposure (not for the upstream text):** Nitsche free slip with the normal written as the radial unit vector, spherical shell, rigid rotation (residual zero by construction when velocity and normal are read at one point): unrefined 2.5e-16 of the scale; refinement 1, 1.5e-2; refinement 2, 9.2e-3. The flat-face normal gives 2.0e-2, 8.7e-3, 4.4e-3 on the same meshes, so on a refined 3-D mesh the analytic normal has an error as large as the faceting it replaces. Table in the probes' README.

**Still to do before sending:**
1. Done: the reproducer above.
2. Mechanism confirmed for positive orientations by the exact prediction. A patched build (`PetscDSPermuteQuadPoint` in place of the reversal) is not made: it needs a PETSc source build, which W1 has not started without Louis's word.
3. Done: the Nitsche probe above.
