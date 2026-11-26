# UNFILED 80: a surface mesh in 3-D can fail to build

Branch `bugfix/surface-mesh-cell-sizes-by-cell`, base development fbef72fa, one commit
(d8d843d2), as `git format-patch`. Not pushed.

## The defect
`Mesh._get_cell_radii` takes each cell's volume from `DMPlexComputeGeometryFVM`, which also
orients every face. On a 2-D mesh in 3-D, PETSc takes an edge's normal as (-dy, dx, 0), in the
xy plane, and turns it towards the cell by the sign of its dot product with the vector from the
face centroid to the cell centroid.

Cut a sphere along the equator, with the cut inserting its own point on a meridian edge. The
new slit edge runs from (0.9916, 0.1293, 0) to (0.9972, 0, 0). Each of its cells has its third
vertex at (0.9972, 0, ±0.0747), directly above or below the inserted point. The cell-to-face
vector then runs along the edge in xy, so the dot product is 2.4e-18 (the true in-surface normal
gives 3.1e-5). PETSc raises "Direction for face 2096 could not be fixed" (error 77), and the
Mesh cannot be built.

It is reachable on development through `pull_vertex_onto` plus `cut_along_lines` (test_0901).
The row 29 draft hit it through `add_fault` (test_1092, test_0559).

## The fix
When the coordinate dimension exceeds the mesh dimension, `petsc_fvm_get_local_cell_sizes`
measures each cell with `DMPlexComputeCellGeometryFVM`, in a C loop. This is the call the full
routine makes for each cell, without the face orientation. Full-dimensional meshes are unchanged.

## Checks
- test_0901 (tier B): every radius of the equator cut equals sqrt(triangle area) at rtol 1e-12.
  It fails on development (error 77) and passes with the fix.
- Same numbers (`radii_dump.py`, on development's build and the fix's): radii AND centroids are
  bit-identical on all 12 manifold meshes. These are SphericalManifold at h = 0.5, 0.4, 0.3, 0.25,
  0.2, 0.15, 0.12, 0.1, 0.05, at 0.1 with one refinement (12,608 cells), and two faulted spheres
  from test_1079's helper. Nitsche gamma and the custom-MG level selection see no change.
- Cost: the loop's lines are pure C in the Cython annotation (scores 0 and 2, the 2 being
  memoryview bounds). The time is linear: 0.26 us per cell, 3.28 ms on 12,608 cells, against
  6.69 ms for the full routine, which also builds the face geometry.
- The 19 test files that build a manifold mesh: 158 passed.

Not run in parallel here. Each cell is measured locally, as before, so the rank count cannot
change a value.
