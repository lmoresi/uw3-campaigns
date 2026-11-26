A surface mesh in 3-D (coordinate dimension above the mesh dimension) could fail to build. PETSc's
`DMPlexComputeGeometryFVM`, which `Mesh._get_cell_radii` calls for cell volumes, also orients
every face. It takes an edge's normal in the xy plane. On a sphere cut along its equator, that
normal was perpendicular to the cell-to-face vector (dot 2.4e-18), and PETSc raised error 77.

On such meshes the cell sizes now come from `DMPlexComputeCellGeometryFVM`, one cell at a time in
a C loop. This is the same per-cell call, without the face pass.

Tolerances and matches:
- test_0901 compares each radius with sqrt(triangle area) at rtol 1e-12 (no coordinate matching).
- Radii and centroids are bit-identical to development's on 12 manifold meshes (324 to 12,608
  cells, two of them faulted).
- 0.26 us per cell, against 0.53 for the full routine.

The manifold tests (19 files): 158 passed. Parallel runs are for the reviewer.

Underworld development team with AI support from Claude Code
