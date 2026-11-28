# gmsh calls that spin on degenerate input (C1, 2026-11-28; diagnosis only)

Reproducer: the 116 experiment (local branch measure/116-outcrop-floor, rail projection on), dip 15 k 0.15
and dip 10 k 0.85. The captured fill inputs are fill_call_*.pkl; replay_fill.py replays one alone.

## Where it spins (correction)
faulthandler after 90 s: gmsh.model.mesh.generate in **_gmsh_fill_2d**, called from
_place_thin_volume_2d's fill loop. It is the cavity ring fill, not the ladder cap, as I had guessed.
118's guard was in this build. These rings have no holes, so the band test had nothing to check.

## The degenerate input: a ring vertex lying on a non-adjacent ring edge
ring_geometry.py on both captured rings:
- the ring touches itself: a vertex lies on a non-adjacent ring edge, 1e-15 of the local edge;
- the corner beside it is 0.2 deg;
- 113's crossing counter gives 0, correctly: a touch is not a proper crossing.
The rail projection put a rail point exactly onto a wall edge that is also in the ring.

perturb_pinch.py moves that vertex off the edge by a relative distance, on either side:

| move | crossings counted | gmsh |
|---|---|---|
| 0 (as built) | 0 | spins (>20 s) |
| 1e-12 .. 1e-2, inside | 0 | meshes in <0.1 s |
| 1e-12, outside | 1 (refused by 113 before gmsh) | spins |
| 1e-4, outside | 2 (refused by 113) | spins |

So only the exact touch reaches gmsh and spins.

pinch_margin.py, the same measure over every fill in passing placements (dips 20/45/60/30, rail on
and off): smallest 1.8e-2. Hanging rings: about 1e-15. The two are separated by thirteen orders of magnitude.

## gmsh bounds tried (replay, 30 s limit, both rings): none turns the spin into an error
Mesh.Algorithm 1 / 5 / 8 / default 6, Mesh.MaxRetries=1, General.AbortOnError=2, Mesh.MeshSizeMin=0:
all time out. gmsh offers no time or iteration limit. A Python signal handler cannot interrupt the
C call. The only hard bound is a child process with a timeout: a bare `import gmsh` + initialize
costs about 0.7 s per call on the laptop, paid by every fill.

## The calls (place_surface.py on the 118 stack; the meshing/ constructors are separate)
| line | call | function | in a try | failure agreed by |
|---|---|---|---|---|
| 791 | _gmsh_fill_2d | _place_one (serial) | no | none (serial) |
| 1088 | _gmsh_fill_2d | _place_one_parallel | yes | allgather 1116 |
| 2261 | _gmsh_fill_2d | _resample_planar_sheet | no | none |
| 3518 | _gmsh_fill_3d | place_sheet | yes | allgather 3567 |
| 5251 | _gmsh_fill_2d | _outcrop_collar_3d | yes | (local) |
| 7281 | _gmsh_fill_2d | _remove_embedded_2d | yes | allgather 7301 |
| 7527 | _gmsh_fill_plain_3d | remove_embedded | yes | allgather 7539 |
| 7692/7700 | _occ_(ladder_)assembly_2d (the cap is inside it) | _thin_volume_assembly_2d, rank 0 | yes | allgather 7712 |
| 8341 | _gmsh_fill_2d | _place_thin_volume_2d | yes; 113 + 118 guards | allgather 8399 |
| 8870 | _occ_assembly_3d | place_thin_volume, rank 0 | yes | allgather 8894 |
| 9103 | _gmsh_fill_annulus_3d | place_thin_volume | yes | allgather 9127 |

Every parallel call raises into a gathered failure, so a raise is safe everywhere. A spin hangs the
other ranks in that allgather. Only 8341 has guards against the inputs known to spin: 113's
crossings and 118's band. Nothing guards the touch.

## Proposed minimum
1. A touch guard beside 113's counter, inside the same try at 8341 (and in _place_one_parallel's and
   _remove_embedded_2d's fill tries, which build rings the same way): refuse when a ring vertex lies
   within 1e-9 of the local edge length of a non-adjacent ring edge. It is cheap, vectorised, n
   by n per ring. The measured gap is 1e-15 against 1.8e-2 or more. It raises into the existing gather, so all ranks refuse together.
2. No gmsh option bounds the call. A child-process bound would be the only general guarantee,
   at about 0.7 s per fill. I would not take it as the default; at most an opt-in for long
   campaigns. Louis/C1.
3. Not reachable on development: the touch needs the experiment's rail projection. So this is a guard
   for when 116 resumes, plus a cheap closing of the class: any input that makes a vertex land on an
   edge, such as a snap.
