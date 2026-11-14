# Review of underworld3 PR #1192 (facet restore, #1176): one-process checks

`serial_checks.py` runs on one process against a build of PR #1192 at fec6d95a
(it imports `_facets_that_can_hold_the_nearest_point`, which the PR adds).
Run on macOS, 12-core Apple M4, conda-forge PETSc 3.25.3, 2026-11-14.

    OMP_NUM_THREADS=1 python -u serial_checks.py

It prints three things for five meshes (a scaled annulus, two stretched 2-D
boxes, a stretched 3-D box, a scaled spherical shell):

1. The restore against the previous code (nearest point over every facet, then
   the same side test), and the kd-tree's 16 nearest against a full sort.
   Measured: 0 points restored differently on every mesh.
2. The restore with the gathered facets in five random orders, standing in for
   other rank counts. Measured: at most 53 of 5200 points differ, by at most
   5.6e-17 (points whose nearest boundary point is a vertex shared by two facets).
3. The graded corner. 2-D box, cell 0.05, deformed by y -> y^3: at the top right
   corner the right wall's facet is 0.143 long and the top wall's 0.050. 49
   points at x = 1.02 beside that facet. Measured: 10 are returned unmoved
   (left outside), those within 0.029 of the corner. Same on development: the
   side test takes its normal from the facet whose centroid is nearest the
   restored point, not from the facet the search found.

Item 3 is the case for the follow-up change that carries the facet index out of
the search. The review record is on the PR.

Underworld development team with AI support from Claude Code
