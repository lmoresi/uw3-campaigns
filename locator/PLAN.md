# Point locator rework: plan (H4, 2026-11-13)

H4 is the adjoint and thin-sheet session. Louis gave this work to H4 through the dev hub (C1). It follows the clamp PR (#682) and #1143, and replaces #1117's interim tolerance (register row 14).

Louis's framing: "The in-cell check is exact for degree one meshes so it is the ability to select good candidates that is problematic. The face-crossing walk seems like a way to make this more efficient."

## What is there now (`discretisation_mesh.py`)
- **Candidates:** a kd-tree of control points (each centroid, and each vertex nudged 1 % towards it). The nearest one gives a first cell. A lost point then tries up to 50 nearest centroids (`_get_closest_local_cells_internal`).
- **In-cell test:** a pair of control points either side of each face (`_mark_faces_inside_and_out`), with a separation fixed at an absolute 1e-3. The point is inside when it is nearer the inner point of every pair, with a slab `tol * sep^2` (`_EVAL_FACE_TOL = 1e-2`).
- **The test needs no tolerance.** For a face, |x-o|^2 - |x-i|^2 = 4 eps n·(x-f), so the face-pair test is the half-space test, exact up to round-off for any eps. The slabs are added on top of an exact test. They are what lets a point be claimed by a neighbour that does not contain it (#1115, #1123).
- **Evaluation locates twice:** `DMPlexCoordinatesToReference` recomputes the reference coordinates the locator could have returned.

## Steps (simplex first; quads, hexes and 2-manifolds keep today's test)
1. **Benchmark the in-cell test before any change.** Compare the vectorised face-pair test with barycentric coordinates: cost per point, 2-D and 3-D, on random points and on points within 1e-6 of a vertex, on 1e5 to 1e6 points. Both are exact. Pick the faster. If they are within noise, take barycentric, which returns the reference coordinates. Result table here before step 2.
2. **Candidate selection by a face-crossing walk.**
   - Start from a cell the caller knows (a particle's previous cell, a DOF's support), or else the nearest control point's cell.
   - If the point fails, cross the face it fails worst (the most negative barycentric coordinate, or the largest half-space excess) to the neighbour through that face's support.
   - Stop when inside.
   - Leaving through a face with one cell: report whether it is the domain boundary or a partition seam (seam faces from the point SF).
   - On a non-convex domain, restart from the next nearest control points (a few) before -1.
   - No 50-candidate cap. Vectorised over points; numpy first, C only if step 1's numbers ask for it.
3. **One round-off guard, relative.** Scaled by eps times the cell size (or sep^2), named once (`_LOCATE_ROUNDOFF`), with what it bounds. `_EVAL_FACE_TOL` and #1117's 1e-13 go.
4. **Ties settled by the mesh.**
   - On a shared face, edge or vertex: the lowest cell number in the entity's star, on one rank.
   - Across ranks: the rank that owns the entity in the point SF.
   - Deterministic and independent of rank count within a rank's answer.
   - **The set of points a rank claims does not change in this PR** (swarm census, #1107 ownership). A topological seam tie-break is a separate step with its own register row.
5. **Return `(cell, reference coordinates)` up to `global_evaluate_nd`.** The evaluator, the clamp (#682's `limit`) and the integration-point path then use one answer. `DMInterpolationSetUp_UW` takes the hint as now.
6. **#960 item 3:** `global_evaluate` agrees on failure (an Allreduce of a flag) before each collective phase, so a rank-local raise cannot strand the others.

## Evidence for the PR (register row 14, replacing #1117)
- test_0511: exact to 1e-12 near faces, edges and vertices.
- #1123's sheared 3-D repro (errors up to 0.17 today).
- #1133's case.
- H1's near-vertex timing and H2's mover timing, against development.
- Swarm and ownership tests bit-identical at np 2 to 4.
- Before/after cost of `global_evaluate` and swarm migration at 1e5 and 1e6 points.

## Reviews and notes
- H3 reviews (it wrote #1117). W1 checks ownership and swarm. H1 runs parallel.
- If the walk changes what UWTN 2026-009 ("Finding particles in a distributed unstructured mesh") describes, the body says so; updating the note is Louis's.

## Open questions for C1 or Louis
- (a) Should a swarm's migration pass each particle's previous cell as the walk's start? That is the largest win, but it touches swarm code: in this PR, or a follow-up?
- (b) Should 2-manifold cells get barycentric in their tangent plane now, or later with quads and hexes?
