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

static void f0_bd_x(PetscInt dim, PetscInt Nf, PetscInt NfAux, const PetscInt uOff[], const PetscInt uOff_x[], const PetscScalar u[], const PetscScalar u_t[], const PetscScalar u_x[], const PetscInt aOff[], const PetscInt aOff_x[], const PetscScalar a[], const PetscScalar a_t[], const PetscScalar a_x[], PetscReal t, const PetscReal x[], const PetscReal n[], PetscInt numConstants, const PetscScalar constants[], PetscScalar f0[])
{
  f0[0] = x[0];
}

static PetscErrorCode one(PetscInt dim, PetscReal time, const PetscReal x[], PetscInt Nc, PetscScalar *u, void *ctx)
{
  u[0] = 1.0;
  return PETSC_SUCCESS;
}

static PetscErrorCode coordinate_x(PetscInt dim, PetscReal time, const PetscReal x[], PetscInt Nc, PetscScalar *u, void *ctx)
{
  u[0] = x[0];
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
  PetscInt    dim, refine = 0, r, fStart, fEnd, f, bd, id = 1, counts[16], o;
  PetscScalar total, moment;
  PetscBool   simplex;
  PetscErrorCode (*funcs[1])(PetscInt, PetscReal, const PetscReal[], PetscInt, PetscScalar *, void *);

  PetscFunctionBeginUser;
  PetscCall(PetscInitialize(&argc, &argv, NULL, help));
  dim = 3;
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-dim", &dim, NULL));
  PetscCall(PetscOptionsGetInt(NULL, NULL, "-refine", &refine, NULL));
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
    PetscReal       centroid[3], area;
    const PetscInt *support, *cone, *orientation;
    PetscInt        supportSize, coneSize, c;

    PetscCall(DMPlexGetSupportSize(dm, f, &supportSize));
    if (supportSize != 1) continue;
    PetscCall(DMPlexComputeCellGeometryFVM(dm, f, &area, centroid, NULL));
    if (centroid[dim - 1] < 1.0 - 1.0e-12) continue;
    PetscCall(DMLabelSetValue(top, f, 1));
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

  PetscCall(PetscFECreateLagrange(PETSC_COMM_SELF, dim, 1, simplex, 2, PETSC_DETERMINE, &fe));
  PetscCall(DMSetField(dm, 0, NULL, (PetscObject)fe));
  PetscCall(DMCreateDS(dm));
  PetscCall(DMGetDS(dm, &ds));
  PetscCall(DMAddBoundary(dm, DM_BC_NATURAL, "top", top, 1, &id, 0, 0, NULL, NULL, NULL, NULL, &bd));
  PetscCall(PetscDSGetBoundary(ds, bd, &wf, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL));
  PetscCall(PetscWeakFormSetIndexBdResidual(wf, top, 1, 0, 0, 0, f0_bd_x, 0, NULL));

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

  PetscCall(VecDestroy(&X));
  PetscCall(VecDestroy(&F));
  PetscCall(VecDestroy(&G));
  PetscCall(SNESDestroy(&snes));
  PetscCall(PetscFEDestroy(&fe));
  PetscCall(DMDestroy(&dm));
  PetscCall(PetscFinalize());
  return 0;
}
