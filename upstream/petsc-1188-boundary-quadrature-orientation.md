# Draft upstream report: PETSc, #1188 (second item for Monday, with #962)

*Status: NOT READY. It needs a petsc4py-only or C reproducer (W1) and a check of the line by a second reader. Louis sends it in his name. Facts below are W1's, measured on one rank, conda-forge PETSc 3.25.3, 2026-11-14. Probes: campaigns 9b95e07, `issue-sweep/internal-face-orientation/`. Issue: underworldcode/underworld3#1188.*

---

**Working title:** PetscFEIntegrateBdResidual_Basic pairs quadrature points with the face tabulation using the edge rule on triangular faces with a non-zero orientation (3-D)

**Suspected lines**, by reading; the same in 3.25.3 and main: `src/dm/dt/fe/impls/basic/febasic.c`, `PetscFEIntegrateBdResidual_Basic` and the boundary Jacobian beside it. The physical quadrature point `q` is paired with the tabulated basis at `qp = ornt < 0 ? (Nq - 1 - q) : q`. That is a reversal, which is correct for an edge, the only 2-D face. A triangle has six orientations, and positive ones are left unpermuted. The hybrid integrals in the same file use `PetscDSPermuteQuadPoint`. The measurements fit this reading (2-D clean, 3-D wrong for both signs), but they do not single out the line.

**Observed (one rank):**
- **A. Exterior wall, against exact integrals.** Unit cube, P2, natural condition (0,0,x) on Top, qdegree 4 (exact for the integrand):
  - refinement 0: every Top face has orientation 0, and 0 of 101 nodes differ from exact;
  - refinement 1: orientations 0/1/2 = 132/15/21, and 163 of 369 nodes differ, by up to 7.0e-5 against a largest nodal load of 3.8e-3;
  - refinement 2: 864 of 1409 nodes differ, by up to 8.8e-6 against 9.8e-4.

  Every differing node touches a face with a non-zero orientation. The total is exact to twelve digits.
- **B. Interior face integrated from its second support cell** (the two support cells swapped before the build):
  - 2-D annulus: orientation 0 -> -1, and no node changes;
  - 3-D shell: orientations -1/-2/-3, and all 534 loaded nodes change, by up to 9.4e-3 against 1.9e-2, summing to 1e-17.
- **In parallel**, this is case B for every interior face whose two cells are on different ranks (underworld3#1150's np 8 load difference).

**Reach:** any boundary integrand that reads the coordinates at the quadrature point. Terms built from the solution, auxiliary fields or the face normal are evaluated at one consistent point. The error falls with h, so refinement-convergence tests pass.

**Still to do before sending:**
1. A reproducer without underworld3.
2. Confirmation of the line, by a patched build or a second reader.
3. W1's probe of Nitsche/penalty terms with a coordinate-built normal, which decides how urgent our own workaround is.
