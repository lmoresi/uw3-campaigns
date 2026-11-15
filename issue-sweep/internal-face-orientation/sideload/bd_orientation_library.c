static char help[] = "Boundary residual of a position-dependent integrand on faces with a non-zero orientation.\n\n\
A P2 scalar field on the unit cube cut into six tetrahedra (or the unit square cut into two\n\
triangles), refined regularly, and the natural boundary term f0 = x on the wall where the last\n\
coordinate is 1. With b_i = int x phi_i dS the assembled residual and g the nodal values of a\n\
function the space holds exactly, b.g = int x g dS: g = 1 gives 1/2, g = x gives 1/3. The\n\
default quadrature integrates both exactly. No mesh generator is needed.\n\n\
  ./bd_residual_orientation -dim 3 -refine 0|1|2\n\
  ./bd_residual_orientation -dim 2 -refine 2\n\n";

#include <petscdmplex.h>
#include <petscsnes.h>
#include <petscds.h>
#include "uw_face_orientation.h" /* from underworld3 src/underworld3/cython, branch bugfix/boundary-quadrature-face-orientation-1188 */
static PetscInt uw_face_map_choice = 1;

static PetscInt wall_axis = 2, wall_side = 1, along = 0;
static PetscReal wall_pos = -1.0; /* an interior wall at this coordinate when set */ /* the wall and the coordinate the integrands read */

static void f0_bd_x(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar f0[])
{
  f0[0] = x[along];
}

static void g0_bd_x(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, PetscReal u_tShift, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar g0[])
{
  g0[0] = x[along];
}

static void integrand_u_x(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar f0[])
{
  f0[0] = u[0] * x[along];
}

static PetscErrorCode one(PetscInt dim, PetscReal time, const PetscReal x[], PetscInt Nc, PetscScalar *u, void *ctx)
{
  u[0] = 1.0;
  return PETSC_SUCCESS;
}

static PetscErrorCode coordinate_x(PetscInt dim, PetscReal time, const PetscReal x[], PetscInt Nc, PetscScalar *u, void *ctx)
{
  u[0] = x[along];
  return PETSC_SUCCESS;
}

int main(int argc, char **argv)
{
  DM          dm;
  SNES        snes;
  PetscFE     fe;
  PetscDS     ds;
  PetscWeakForm wf;
  DMLabel     top;
  Vec         X, F, G;
  PetscInt    swap = 0, fix = 0, dim, refine = 0, r, fStart, fEnd, f, bd, id = 1, counts[16], o;
  PetscScalar total, moment;
  PetscBool   simplex;
  PetscErrorCode (*funcs[1])(PetscInt, PetscReal, const PetscReal[], PetscInt, PetscScalar *, void *);

  PetscFunctionBeginUser;
  PetscCall(PetscInitialize(&argc, &argv, NULL, help));
  dim = 3;
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-dim", &dim, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-refine", &refine, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-uw_fix", &fix, NULL));
  if (fix) uw_face_map_choice = fix;
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-wall_axis", &wall_axis, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-wall_side", &wall_side, NULL));
  along = (wall_axis + 1) % dim;
  PetscCall(PetscOptionsGetReal(NULL, NULL, "-wall_pos", &wall_pos, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-swap", &swap, NULL));
  if (dim == 3) {
    /* vertex v of the cube is at (v & 1, (v >> 1) & 1, (v >> 2) & 1); each tetrahedron runs
       from vertex 0 to vertex 7 along one ordering of the three axes */
    const PetscInt  axes[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
    const PetscInt  odd[6]     = {0, 1, 1, 0, 0, 1};
    PetscInt        cells[24], c, v;
    PetscReal       coords[24];

    for (v = 0; v < 8; ++v) {
      coords[3 * v + 0] = (PetscReal)(v & 1);
      coords[3 * v + 1] = (PetscReal)((v >> 1) & 1);
      coords[3 * v + 2] = (PetscReal)((v >> 2) & 1);
    }
    for (c = 0; c < 6; ++c) {
      const PetscInt first = 1 << axes[c][0], second = first + (1 << axes[c][1]);

      cells[4 * c + 0] = 0;
      cells[4 * c + 1] = odd[c] ? first : second;
      cells[4 * c + 2] = odd[c] ? second : first;
      cells[4 * c + 3] = 7;
    }
    {
      /* an even permutation of each tetrahedron's vertices keeps its volume positive and
         changes the orientation of its faces in its cone; -shuffle k picks one per cell */
      const PetscInt even[12][4] = {{0, 1, 2, 3}, {0, 2, 3, 1}, {0, 3, 1, 2}, {1, 0, 3, 2}, {1, 2, 0, 3}, {1, 3, 2, 0},
                                    {2, 0, 1, 3}, {2, 1, 3, 0}, {2, 3, 0, 1}, {3, 0, 2, 1}, {3, 1, 0, 2}, {3, 2, 1, 0}};
      PetscInt       shuffle = 0, tmp[4];

      PetscCall(PetscOptionsGetInt(NULL, NULL, "-shuffle", &shuffle, NULL));
      for (c = 0; c < 6; ++c) {
        const PetscInt *p = even[(shuffle * (c + 5) + c * c) % 12];

        for (v = 0; v < 4; ++v) tmp[v] = cells[4 * c + p[v]];
        for (v = 0; v < 4; ++v) cells[4 * c + v] = tmp[v];
      }
    }
    PetscCall(DMPlexCreateFromCellListPetsc(PETSC_COMM_WORLD, 3, 6, 8, 4, PETSC_TRUE, cells, 3, coords, &dm));
  } else {
    const PetscInt  cells[6]  = {0, 1, 2, 1, 3, 2};
    const PetscReal coords[8] = {0, 0, 1, 0, 0, 1, 1, 1};

    PetscCall(DMPlexCreateFromCellListPetsc(PETSC_COMM_WORLD, 2, 2, 4, 3, PETSC_TRUE, cells, 2, coords, &dm));
  }
  for (r = 0; r < refine; ++r) {
    DM finer;

    PetscCall(DMRefine(dm, PETSC_COMM_WORLD, &finer));
    PetscCall(DMDestroy(&dm));
    dm = finer;
  }
  PetscCall(DMPlexCheckGeometry(dm));
  simplex = PETSC_TRUE;
  /* the wall: the faces whose centroid has the last coordinate equal to 1 */
  PetscCall(DMCreateLabel(dm, "top"));
  PetscCall(DMGetLabel(dm, "top", &top));
  PetscCall(DMPlexGetHeightStratum(dm, 1, &fStart, &fEnd));
  for (o = 0; o < 16; ++o) counts[o] = 0;
  for (f = fStart; f < fEnd; ++f) {
    PetscReal       centroid[3], normal[3], area;
    const PetscInt *support, *cone, *orientation;
    PetscInt        supportSize, coneSize, c;

    PetscCall(DMPlexGetSupportSize(dm, f, &supportSize));
    if (supportSize != (wall_pos < 0.0 ? 1 : 2)) continue;
    PetscCall(DMPlexComputeCellGeometryFVM(dm, f, &area, centroid, normal));
    if (PetscAbsReal(centroid[wall_axis] - (wall_pos < 0.0 ? (PetscReal)wall_side : wall_pos)) > 1.0e-12) continue;
    if (PetscAbsReal(PetscAbsReal(normal[wall_axis]) - 1.0) > 1.0e-12) continue; /* in the plane, not across it */
    PetscCall(DMLabelSetValue(top, f, 1));
    if (swap && supportSize == 2) {
      /* the face's support order decides which cell's frame its boundary terms use */
      const PetscInt *sup;
      PetscInt        swapped[2];

      PetscCall(DMPlexGetSupport(dm, f, &sup));
      swapped[0] = sup[1];
      swapped[1] = sup[0];
      PetscCall(DMPlexSetSupport(dm, f, swapped));
    }
    PetscCall(DMPlexGetSupport(dm, f, &support));
    PetscCall(DMPlexGetConeSize(dm, support[0], &coneSize));
    PetscCall(DMPlexGetCone(dm, support[0], &cone));
    PetscCall(DMPlexGetConeOrientation(dm, support[0], &orientation));
    for (c = 0; c < coneSize; ++c)
      if (cone[c] == f) counts[orientation[c] + 8]++;
  }
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "wall faces by orientation in their cell:"));
  for (o = 0; o < 16; ++o)
    if (counts[o]) PetscCall(PetscPrintf(PETSC_COMM_WORLD, "  %" PetscInt_FMT ": %" PetscInt_FMT, o - 8, counts[o]));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "\n"));

  PetscCall(PetscFECreateLagrange(PETSC_COMM_SELF, dim, 1, simplex, 2, 6, &fe));
  if (fix) PetscCall(UW_PetscFEPairFaceQuadratureByOrientation(fe));
  PetscCall(DMSetField(dm, 0, NULL, (PetscObject)fe));
  PetscCall(DMCreateDS(dm));
  PetscCall(DMGetDS(dm, &ds));
  PetscCall(DMAddBoundary(dm, DM_BC_NATURAL, "top", top, 1, &id, 0, 0, NULL, NULL, NULL, NULL, &bd));
  PetscCall(PetscDSGetBoundary(ds, bd, &wf, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL));
  PetscCall(PetscWeakFormSetIndexBdResidual(wf, top, 1, 0, 0, 0, f0_bd_x, 0, NULL));
  PetscCall(PetscWeakFormSetIndexBdJacobian(wf, top, 1, 0, 0, 0, 0, g0_bd_x, 0, NULL, 0, NULL, 0, NULL));

  PetscCall(SNESCreate(PETSC_COMM_WORLD, &snes));
  PetscCall(SNESSetDM(snes, dm));
  PetscCall(DMPlexSetSNESLocalFEM(dm, PETSC_FALSE, NULL));
  PetscCall(DMCreateGlobalVector(dm, &X));
  PetscCall(VecDuplicate(X, &F));
  PetscCall(VecDuplicate(X, &G));
  PetscCall(VecZeroEntries(X));
  PetscCall(SNESComputeFunction(snes, X, F));

  funcs[0] = one;
  PetscCall(DMProjectFunction(dm, 0.0, funcs, NULL, INSERT_ALL_VALUES, G));
  PetscCall(VecDot(F, G, &total));
  funcs[0] = coordinate_x;
  PetscCall(DMProjectFunction(dm, 0.0, funcs, NULL, INSERT_ALL_VALUES, G));
  PetscCall(VecDot(F, G, &moment));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "b.1 = %.14f (exact 0.5), error %.3e\n", (double)PetscRealPart(total), (double)(PetscRealPart(total) - 0.5)));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "b.x = %.14f (exact 1/3), error %.3e\n", (double)PetscRealPart(moment), (double)(PetscRealPart(moment) - 1.0 / 3.0)));
  {
    Mat         A;
    Vec         MG, G1;
    PetscScalar m11, mxx, integral[1];

    PetscCall(DMCreateMatrix(dm, &A));
    PetscCall(SNESComputeJacobian(snes, X, A, A));
    PetscCall(VecDuplicate(G, &MG));
    PetscCall(VecDuplicate(G, &G1));
    PetscCall(MatMult(A, G, MG));
    PetscCall(VecDot(G, MG, &mxx));
    funcs[0] = one;
    PetscCall(DMProjectFunction(dm, 0.0, funcs, NULL, INSERT_ALL_VALUES, G1));
    PetscCall(MatMult(A, G1, MG));
    PetscCall(VecDot(G1, MG, &m11));
    PetscCall(PetscPrintf(PETSC_COMM_WORLD, "1.M.1 = %.14f (exact 1/2), error %.3e\n", (double)PetscRealPart(m11), (double)(PetscRealPart(m11) - 0.5)));
    PetscCall(PetscPrintf(PETSC_COMM_WORLD, "x.M.x = %.14f (exact 1/4), error %.3e\n", (double)PetscRealPart(mxx), (double)(PetscRealPart(mxx) - 0.25)));
    {
      PetscBdPointFn *integrands[1] = {integrand_u_x};

      PetscCall(DMPlexComputeBdIntegral(dm, G, top, 1, &id, integrands, integral, NULL));
    }
    PetscCall(PetscPrintf(PETSC_COMM_WORLD, "int u x dS, u = x: %.14f (exact 1/3), error %.3e\n", (double)PetscRealPart(integral[0]), (double)(PetscRealPart(integral[0]) - 1.0 / 3.0)));
    PetscCall(MatDestroy(&A));
    PetscCall(VecDestroy(&MG));
    PetscCall(VecDestroy(&G1));
  }

  PetscCall(VecDestroy(&X));
  PetscCall(VecDestroy(&F));
  PetscCall(VecDestroy(&G));
  PetscCall(SNESDestroy(&snes));
  PetscCall(PetscFEDestroy(&fe));
  PetscCall(DMDestroy(&dm));
  PetscCall(PetscFinalize());
  return 0;
}
