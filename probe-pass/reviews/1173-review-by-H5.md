# #1173 review by H5 (head 80aea769): READY

Checked on a build of 80aea769 (hyperion, 96-thread Linux workstation, MPICH).

1. **One rule, not two.** The callback is now a single loop over Upper, Lower and Internal, each scaled radially, `x * r / |x|`. That is the projection the generator already applied to Upper and Lower, and the projection of the radial surface registered for Internal. The `1e-16` guard dropped from Lower's denominator is safe: the generator refuses `radiusInner <= 0`, so no labelled vertex is at the origin.
2. **Every level.** `_build_refined_hierarchy` applies the callback to each refined DM. `test_every_level_keeps_each_surface_on_its_sphere` reads every DM of `dm_hierarchy` for all three labels, at refinement 1 and 2. The volume test runs on the finest DM of each fixture, so levels 1 and 2 are both covered.
3. **No inversion found.** Coarse Internal vertices come out of gmsh on the sphere, so the snap leaves them where they are; only the new vertices move outward, by the sagitta.
   - Signed volume at every level 0 to 2 on four shells: no cell turned against the majority.
   - The four shells (cellSize / radiusInternal, with radiusInner 0.5 and radiusOuter 1): 0.3 / 0.8 (the PR's), 0.15 / 0.9 (a thin outer layer), 0.25 / 0.65 and 0.2 / 0.8.
   - The smallest cell, as a fraction of the mean, falls by under 0.02 per level (e.g. 0.29, 0.25, 0.22 on the PR's shell).
   - The volume test's abs-sum comparison would catch an inverted cell at level 2: its fixture includes refinement 2.
4. `tests/test_1190_spherical_internal_refinement_snap.py`: 6 passed serially. I did not rerun the parallel file. The snap is per vertex and gives the same coordinates on every rank, and that file checks that each copy matches its owner.

Note, not this PR's: `SphericalShellInternalBoundary` refuses several reasonable parameter sets at gmsh time. At cellSize 0.4 to 0.7 with radiusInternal 0.8 it gives "Could not identify the spherical-shell volume". At radiusInternal 0.92 or 0.58 (cellSize 0.3) it gives that error or "Could not identify Lower, Internal, and Upper". The PR touches only the refinement callback, so this predates it; worth an issue.
