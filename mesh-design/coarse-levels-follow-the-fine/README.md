# Coarse multigrid levels when the fine mesh moves

W1 (the integration session on a macOS laptop, 12-core Apple M4), 2026-11-16, on development fb75e9e0. Written at Louis's request, relayed by C1: "The coarse not following fine seems like a problem. Even worse if we have moving boundaries. Coarse and fine will have non-overlapping regions."

## What happens on development

A move (`mesh.deform`, a mover) changes the coordinates of the finest level only. `_sync_hierarchy_finest_coordinates` hands them to the finest hierarchy level. The coarse levels stay where they were built. What that does depends on how each pair's transfer is made.

- **Simplex levels (triangles, tetrahedra).** A moved level is read where it was built (#1119, `fault_mg.as_built_nodes`). The transfer after a move is the one before it, entry for entry, and the coarse operators are Galerkin products with the moved fine operator. The coarse geometry never enters the solve, so the two levels no longer overlapping costs nothing directly. What remains is whether the unmoved pair's interpolation suits a strongly moved fine mesh.
- **Quadrilateral, hexahedral and periodic levels.** The transfers are rebuilt from the moved fine coordinates against the unmoved coarse level. Fine nodes beyond the coarse boundary are outside every coarse cell. This is the case Louis describes, and it happens today.
- **Add-on and split fault levels (#1120, H5).** Only the finest level moves. The split levels are cut where their host stands, and the cut pieces' rows are located on the current geometry. At a 0.015 move across the fault, 43 coarse fault copies are left empty under every row rule. With every add-on level moved by the same displacement field, the parent and hybrid rules leave none (H5's table, in #1206).
- **A base moved before an adapt or a cut.** The child is a new mesh made on the moved coordinates, and the pair under it is rebuilt from them: 4 velocity iterations against 2 at rest (#1119).

## The measurement

`moving_wall_fmg.py`, serial, on the box of `tests/test_1176` (refined twice):
- Stokes with the custom FMG on the velocity block. Bottom, left and right walls held; body force (0, sin πx).
- Each step raises the top wall by 2.5 % of the depth times sin πx, multiplicatively, and stretches the interior with it. After 20 steps the centre stands at 1.64 times the depth.

The table gives velocity-block iterations and, in brackets, the fine velocity nodes outside the next coarser level. Outside means above the chord through that level's top-wall vertices.

| arm | step 0 | 1 | 5 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|
| triangles, development (transfers kept) | 3 (0) | 3 (31) | 3 (108) | 3 (197) | 4 (288) | 5 (357) |
| triangles, transfers rebuilt from the moved coordinates, coarse levels as built | 3 (0) | 5 (31) | 6 (108) | 9 (197) | 11 (288) | 14 (357) |
| triangles, transfers rebuilt, coarse levels moved by the same map | 3 (0) | 4 (18) | 4 (18) | 5 (18) | 5 (18) | 6 (18) |
| quadrilaterals, development (transfers rebuilt), coarse levels as built | 3 (0) | 4 (31) | 6 (92) | 8 (160) | 9 (224) | 11 (283) |
| quadrilaterals, coarse levels moved by the same map | 3 (0) | 4 (18) | 4 (18) | 4 (18) | 5 (18) | 5 (18) |

The second row switches off the as-built read, so it stands for what triangles did before #1119. Every solve converged, with one outer iteration. The per-step output of every arm is in `run_*.txt`.

What the table shows:
- **Quadrilateral levels on development degrade with the move:** 3 to 11 iterations as the wall rises. Moving their coarse levels with the fine one holds them at 4 to 5.
- **Triangles on development hold** at 3 to 5. Moving their coarse levels and rebuilding gives 4 to 6, no better.
- **The coarse levels moved by the map leave 18 fine nodes outside, at every step.** These are fine top-wall nodes between two coarse top-wall vertices, above the coarse chord by the O(h²) sag of a curved wall. They cost one or two iterations by step 20, not ten.

## Design

### 1. Refined hierarchies (every coarse vertex is a fine vertex)

Move each coarse level through the refinement's point map: give each coarse vertex the moved coordinates of the fine vertex it is.
- The map is fixed when the hierarchy is built, by the nesting already established there (`nested_prolongation_from_dms` identifies inherited vertices).
- It is exact and topological, with no search and no tolerance.
- The levels stay nested at their vertices.

What is left is the boundary sag: on a curved moving wall, a fine boundary node between two coarse boundary vertices lies off the straight coarse edge by O(h²κ). A boundary projection cannot close it. The coarse vertices already lie on the fine boundary, and a degree-1 coarse edge between them is straight; geometry is degree 1, as the Charter requires. The measurement says it does not need closing: 18 nodes outside, and 4 to 6 iterations at a 64 % rise.

Per cell type:
- **Simplex levels:** nothing to do. The kept transfers already do as well as moving the coarse levels (5 against 6 at step 20), and a moved simplex level is read where it was built either way.
- **Quadrilateral and hexahedral levels:** two choices.
  - (a) Extend the as-built read of #1119 to tensor cells, so one rule holds for every cell type: a move keeps the transfers.
  - (b) Move the coarse levels through the point map and rebuild, as measured (4 to 5).
  
  (a) has not been measured. Its measurement is the next step: the quadrilateral arm with the kept read. Take whichever holds better, and (a) if they are equal, since it needs no coordinate work.
- **Periodic levels** keep no as-built record. They need (b), or a record.

### 2. Non-nested tails (adapt children, add-on and split fault levels)

Carry the displacement to the coarse levels.
- The finest level's displacement is the difference between its current and its as-built vertex coordinates, a degree-1 field on the finest mesh.
- Each coarse level's vertices are located in the finest level's as-built geometry and take the interpolated displacement.
- Each coarse level nests in the finest level's as-built geometry, exactly for an adapt tail and through H5's host-cell record for the split levels. So the location is exact, and shared vertices get exactly the fine displacement.

**No crossing at a fault.** A coarse vertex on a fault has one copy per side on a split level. Each copy takes its displacement from fine cells on its own side, chosen by the side label, not by distance. The two sides may then separate along the fault as the fine level does, and no copy is moved by the other side's motion. H5's runs moved the levels by an analytic field before the cut. In production the finest level moves after the split, and the cut vertices are not fine vertices, so this interpolation is the mechanism.

### 3. When

Lazily, at the hierarchy build of the next solve after a committed move. That build already happens on every rank, and the solve-entry sync already sees the geometry version.
- Moving at each `_deform_mesh` would repeat the work inside a mover's sweeps and inside `ephemeral_coords`, where nothing is solved.
- The trigger is `_move_version` on the finest level, which every committed move bumps and which a snapshot restore or a trial move does not.

### 4. Cost

- **Refined hierarchies:** one copy of vertex coordinates per coarse level per committed move, plus the coordinate-field rebuild that `_sync_hierarchy_finest_coordinates` already does for the finest level. That is small beside the Galerkin products.
- **Non-nested tails:** one point location of each coarse level's vertices in the finest as-built mesh per committed move. The location's start cells are known from the nesting, so it is a walk, not a search.
- **Cached transfers.** Simplex transfers stay kept (#1119), and moving the coarse coordinates does not change them, because a moved level is read as built. Quadrilateral transfers are rebuilt after a move today, and stay rebuilt under (b). Non-nested tails are rebuilt after a move today, and are then rebuilt on a pair that overlaps.

## Next measurements

1. The quadrilateral arm with the as-built read extended to tensor cells: choice (a) against (b).
2. An adapt-child tail under the same moving wall: development, then with the displacement carried to the tail.
3. The hexahedral version of the quadrilateral arms, at one refinement.
4. np 2 and 3 for every arm that changes the coarse levels, since the locating and the moving are collective.

Underworld development team with AI support from Claude Code
