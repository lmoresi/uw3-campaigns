# UNFILED 63 and option 2: the serial orphan repair, on or off

Question: on the serial custom-FMG route (`_reduced_transfer`, which calls the barycentric
builder with the default `repair_orphans=True`), does the repair help? Install drops unreached
columns anyway (`drop_orphans`, `restrict_unreached`), as the parallel route (#890) already does
with the repair off. The alternative, option 2, is the repair off on this route too.

Measured on development's custom_mg (fbef72fa), macOS (12-core Apple M4), serial, Stokes P2/P1,
rotated free-slip on both walls, the pressure null space, tolerance 1e-8. The counts are the
solver's own: outer, and the last velocity and pressure inner counts (`_rotated_freeslip_info`).
The orphan and empty-column counts are for the top coarse level's transfer, the only one with
orphans in any of these runs.

| fixture | orphans | empty columns after the repair | its, repair (outer / vel / pres) | its, no repair | rel. diff of v |
|---|---|---|---|---|---|
| K1 #893 hierarchy, refinement 4, chain 2 (`run_k1.py`) | 10 and 38 (two levels) | not logged | 1 / 4 / 9 | 1 / 4 / 9 | 2.4e-9 |
| graded finest, 0.006 to 0.06, under a uniform tail (cells 600 / 2400 / 9600) | 3,245 | 8,631 | 1 / 13 / 9 | 1 / 3 / 9 | 3.2e-10 |
| graded finest, 0.01 to 0.04 | 185 | 338 | 1 / 3 / 9 | 1 / 3 / 9 | 1.5e-12 |
| unnested uniform finest, 0.02 | 0 | 0 | 1 / 3 / 9 | 1 / 3 / 9 | 0 |
| unnested uniform finest, 0.012 | 0 | 0 | 1 / 4 / 8 | 1 / 4 / 8 | 0 |

The graded runs set `UW_CUSTOM_MG_DISABLE_NESTED_NATIVE=1`, but no pair there is a native
refine pair (the finest is a separate gmsh mesh), so the barycentric route is the one in use
either way.

What it shows:
- The repair never helped. With no orphans the two runs are bit-identical. With few orphans,
  the iterations are the same.
- The repair leaves more empty columns than it found (UNFILED 63): 185 became 338, and 3,245
  became 8,631. Each repaired orphan takes over a fine row, and that row's old columns can lose
  their only fine image.
- At 3,245 orphans it costs velocity iterations: 13 against 3.
- The answers agree to the solver tolerance in every case.

Limits: serial only, 2-D annuli, one coarse tail (cell 0.1, refinement 2), and one forcing. No
MMPDE-moved ladder levels were measured; the graded independent finest level stands in for
"the finest is coarser than a coarse level in places".

Proposal (C1 and Louis decide): pass `repair_orphans=False` on the serial custom-FMG route, to
match the parallel route and the install's drop rule. That settles UNFILED 63 on this route,
and the repair's cost with it. The public default (`barycentric_prolongation(...,
repair_orphans=True)` called on its own, #424) and legacy `set_custom_mg` (no drop at install)
are a separate question: a standalone caller has no install-time drop, so turning the repair off
there leaves zero columns.
