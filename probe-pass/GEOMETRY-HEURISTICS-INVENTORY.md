# Inventory: coordinate-keyed identity and geometric tolerances in `src/underworld3`

**2026-11-13, development 01dec8d2.** A read-only survey run by a search agent in the dev hub's
container, prompted by Louis: "Are we trying to find things by distance, relative distance or, if
in a mesh, by connectivity. I worry that this is a 101 rookie way of programming and we will end up
with a code made up of nothing but special cases."

**Status: a survey, not a review.** Counts are site-level judgements (a function with several
identical comparisons counts once). `place_surface.py` (9.5k lines) was sampled: its labels are
accurate to about +/-3. `meshing/surfaces.py`, `faults.py`, `mmpde.py`, `metrics.py`,
`spherical.py`, `segmented.py` were classified from grep hits. Nothing here was run. Line numbers
are development 01dec8d2. A desk that acts on a row confirms it first.

## Totals

| | A: identity by coordinates | B: absolute tolerance | C: relative tolerance | D: capped nearest search |
|---|---|---|---|---|
| total | 41 | 49 (+13 rounding keys) | about 65 | 15 |

| subsystem | A | B | C | D |
|---|---|---|---|---|
| point location / evaluate | 2 | 7 | 7 | 6 |
| swarm / ddt | 1 | 0 | 4 | 0 |
| movers | 1 | 2 | 1 | 1 |
| adapt | 5 | 0 | 0 | 0 |
| faults (placement, cut, split, fault MG) | 9 | 29 | 38 | 7 |
| custom multigrid | 5 | 1 | 1 | 1 |
| rotated BC | 1 | 0 | 4 | 0 |
| checkpoint | 5 | 0 | 1 | 0 |
| generators | 3 | 3 | 6 | 0 |
| other (free surface, geoid, boundary flux, level set) | 9 | 7 | 3 | 0 |

Absolute to relative is about 1:1. Most relative sites scale by the global extent or a mean
spacing, not a local cell size: scale-invariant, but not safe on strongly graded meshes.
`place_surface.py` holds about half of all B and C sites. `edge_split.py` and `adaptivity.py` are
clean.

**`_EVAL_FACE_TOL`.** The in-cell test (`discretisation_mesh.py:7062-7075`) compares squared
distances to control points placed +/-1e-3 along each face normal, an absolute offset (6928-29).
The test is `diff > -tol*sep^2`, so `_EVAL_FACE_TOL = 1e-2` (7731) is an absolute slab of about
1e-5 model units outside each face, and the default `diff >= -1e-12` (7073) one of about 2.5e-10.
The docstrings call this face-relative; the comment at 7549-7557 says the separation is absolute.

## A. Identity by coordinates where topology has the answer (the "yes" rows)

| site | function | decided by | topology would use |
|---|---|---|---|
| discretisation_mesh.py:2781-85, 3016-18 | `_build_vertex_map`, sub/parent DOF map | kd-tree, distance < 1e-10 | `subpoint_is`, already stored |
| discretisation_mesh.py:8471-74 | `_sync_across_ranks` | round(12) | a reduce over the point SF |
| nvb.py:103 | `write_tagged_state_label` | round(12) | SF / global numbering |
| nvb.py:183-88, 336-84; discretisation_mesh.py:9961 | `_exact_vertex_map`, `_nested_prolongation_local`, adapt + relax | exact coordinate bytes | the refinement transform (#425) |
| discretisation_mesh.py:3292 | `_refine_restrict` (serial) | nearest fine DOF | nested parent/child |
| line_cut.py:579-83 | `_child_vertex_of` | kd-tree, <= 1e-9 x extent | the transform's target point (not in petsc4py) |
| line_cut.py:1033 | `pull_vertex_onto` | "by position" on every rank | point SF |
| custom_mg.py:728/1074 | `_fac_patch_split(_parallel)` | `x_tol = 1e-9` | nested identity rows |
| custom_mg.py:762-68 | FAC "slit" mode | round(9) coincident coordinates | the fault_split pair map |
| custom_mg.py:1295 | `_gather_coarse_cloud` | round(9) dedup | `l2g` / SF |
| custom_mg.py:107/116 | `barycentric_prolongation` | nearest coarse DOF outside the hull | parent map if nested |
| rotated_bc.py:3604; boundary_flux.py:101/852 | `dynamic_topography_field`, `_key` | round(9) | the (point, slot) keys boundary_flux already has |
| discretisation_mesh.py:461-66, 1169 | `_match_file_points`, FMG stamp | kd-tree <= 1e-8 x max(extent, 1) | refinement numbering |
| discretisation_mesh_variables.py:1563/1643-48 | `read_timestep` | nearest rank centroid, then nearest point | `read_checkpoint` / `sectionLoad` |
| discretisation_mesh_variables.py:1762-1886 | `_read_dg1_corner_timestep` | round(12) corner keys | topology-load SF |
| free_surface.py:561, 632-33, 969-73, 1276/1301 | ring and carrier rows, seam copies | nearest, round(9), round(12) | section offsets, point SF |
| geoid.py:945 | `_rotated_topography_coefficient` | round(12) | point SF |
| level_set.py:543-59 | `_apply_boundary_neumann` | `np.unique` + isclose 1e-8 | labels plus adjacency |
| petsc_generic_snes_solvers.pyx `_setup_discretisation` (three solver classes) | early return keyed on an xxhash of the rank's own `mesh.X.coords` (added 2026-11-14 from H1's .pyx collective scan; rank-local, not reachable by a one-rank deform at np 2 because deform resets the DM) | a declared mesh-state counter, the same on every rank |
| discretisation_mesh.py `_boundary_facet_geometry` | the boundary-facet cache of the facet restore is kept while each rank's `(shape, sum of its coordinates)` is unchanged (added 2026-11-14 from the review of PR #1192, which makes the decision collective with an `allreduce`; `deform` and a direct coordinate write reset the cache, but moves inside `_coord_mutation` — the mover, a snapshot restore, the old-frame move in the semi-Lagrangian trace — rely on the sum alone; no failing case in hand) | a declared mesh-state counter, the same on every rank |

Not answerable by topology (the point is not a mesh entity, or it is pre-mesh geometry):
`swarm.py:2615` (saved particle to live particle); `place_surface.py` 315, 3873/4090, 4705,
5793/5817, 8929, 9000-10; `meshing/surfaces.py:156`; the gmsh entity matches in `spherical.py:179`,
`cartesian.py:1203`, `create_dmplex_from_medit.py:67`.

## D. Capped nearest-centroid search

| site | function | what | exact alternative |
|---|---|---|---|
| discretisation_mesh.py:7571-7609 | `_get_closest_local_cells_internal` (central: evaluate, `points_in_domain`, swarm, ddt, adaptivity) | containing cell among the 50 nearest centroids | a walk over cell adjacency |
| discretisation_mesh.py:7361-7401 | `get_closest_cells` (gradient_evaluation.py:240, adaptivity.py:767) | nearest control point, no containment test | support cells for nodes; a walk otherwise |
| fault_mg.py:135-51 | `locate_in_cells` (k=16); the serial caller at 255 has no inside check | parent coarse cell | parent map on nested levels |
| fault_mg.py:410 | `locate_in_cells_exhaustive` | 16, 128, 1024, all | uncapped but still geometric |
| custom_mg.py:3196 | `_colocate_level` | coarse cell owner = nearest owned fine centroid | parent map |
| level_set.py:179; discretisation_mesh.py:4322 | node to nearest cell centroid; nearest facet centroid | | support cells; return the facet index |
| swarm.py:3752-73, 4402; _function.pyx:743-50 | owner rank by nearest rank centroid | | none (not a mesh entity) |

## The ten sites judged most likely to give a wrong or partition-dependent answer

1. `custom_mg.py:1295` `_gather_coarse_cloud`: round(9) dedup merges the plus and minus nodes of a
   split fault (bit-identical coordinates) into one coarse column.
2. `fault_mg.py:255` `cell_located_prolongation` (serial): best of 16 nearest centroids with no
   inside check; on graded meshes all 16 can miss and the weights are silently extrapolated.
3. `fault_mg.py:308/346` (parallel): the same cap on the local search and on the answering ranks.
4. `discretisation_mesh.py:7571`: the 50-centroid cap on the central locator (issue #1123).
5. `discretisation_mesh.py:6928/7731/7073`: the absolute face slabs (1e-5, 2.5e-10): negligible on
   a mesh in metres, a large fraction of a cell on a mesh 1e-4 across.
6. `discretisation_mesh.py:7181`: boundary control points 1e-8 absolute from the face: a few ULP at
   Earth radius in metres, so the in/out sign is noise.
7. `get_closest_cells` used as a cell finder (`gradient_evaluation.py:240`, `adaptivity.py:767`).
8. `boundary_flux.py:101/852` and `rotated_bc.py:3604`: round(9) keys from two different coordinate
   computations; a miss leaves the value unwritten; above about 1e7 model units round(9) is below
   one ULP.
9. `discretisation_mesh_variables.py:1762-1886` `_read_dg1_corner_timestep`: round(12) cell keys.
10. `level_set.py:543-559`: the "inner layer" as the next distinct coordinate value (assumes a
    structured grid and an absolute scale).

## Helpers that already do the job properly

- `fault_split._point_keys(dm)` (fault_split.py:321): a global (owner rank, owner index) per point
  from the point SF. The replacement for the cross-rank rounded keys at nvb.py:103,
  discretisation_mesh.py:8471, free_surface.py:1276/1301, geoid.py:945, custom_mg.py:1295.
- `reconnect._shared_points(dm)` (reconnect.py:306): seam flags.
- `Mesh.subpoint_is`: the exact submesh to parent point map, stored and unused by the two kd-tree
  maps.
- `MeshVariable.read_checkpoint` / `load_from_h5_plex_vector`: restart through the topology SF.
- `nvb.nested_cell_parents` and the nested topological prolongations: the parent/child alternative.
- `Mesh._get_cell_radii` (partition-independent per-cell h) and `line_cut._global_extent`: scales
  for a tolerance that has to exist.
- `boundary_flux`'s own (point, slot) node keys; `_plex_topology.closure_points`.
