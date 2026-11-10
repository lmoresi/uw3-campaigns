# W1 territory sweep, 2026-11-10 (solvers, rotated BC, custom MG)

254 open issues; about 90 touch this territory. Grouped by shared root cause or shared code.

## Closed out by the sweep
- #683 fmg inert on semi-Lagrangian solvers: fixed by #1030, probed, labelled fixed-in-development.

## A. Custom-P / FAC hierarchy lifecycle (custom_mg.py, solvers' install path)
Root: the hierarchy and its options-database keys are not owned by the solver or tied to the mesh version.
- #1017 deform: coarse levels do not move, FAC patch declined
- #1019 gamg after FAC: leftover composite key, error 73
- #1020 reinstall leaks deferred objects at np > 1
- #898 remesh leaves dm_hierarchy and coarse wraps on the old mesh
- #885 last_builder_stats module-global
- #546 tolerance / FMG config latched into the cached KSP
One PR: drop FAC keys after set-up on every path, free garbage on reinstall, carry the deform to nested levels, resync on remesh.

## B. Timestep estimation (estimate_dt in solvers.py, advection_diffusion_eulerian.py, swarm)
- #891 units model reads dimensional coords as model units (dt 3.4x)
- #1025 SLCN diffusion limit shrinks dt as h^2
- #693 empty-rank reshape; rank-local max_magvel
- #978 (estimate_dt part) degree-2 midpoints
- H2's June mismatch lead (#688 rewrite of estimate_dt) belongs here
Separate, needs a benchmark: #1029 theta inert; #1031 setter unwrap (small, could ride with B).

## C. Rotated free-slip: corners, gauge, partition (rotated_bc.py)
- corners / partly pinned nodes: #608, #939, #941, #940 (fault_contact at a wall-pinned pair node)
- rigid-rotation gauge: #968, #969, #884
- cold start / datum: #883, #910, #348
- partition: #931 (may share #941's cause)
- #887 docs behind the code
Probably two PRs: corners+partition, gauge+datum.

## D. Silent non-convergence and reporting
- #585, #625 inner KSP caps hit silently
- #770 warm start reports CONVERGED without moving
- #778 solve_history misses the Picard stage; #806 introspection lacks the config
- #804 gradient of an unconverged forward solve
One PR: a solve that hits a cap or does not move says so, and the report records it.

## E. Fault-split MG in parallel (custom_mg, cell-located transfer)
- #873 empty-rank coarse level, #874 rank-local raises before collectives, #888 CI coverage, #880 hardening, #671 np 3 Galerkin diagonal, #956 ptest_0863-0865 at np 4
Needs hyperion for np > 1.

## F. ThinSheet
- #875 L and c_b inlined, #876 picard/time, #879 history projection + stale normals, #887 (part)

## G. Solver API traps
- #844 Stokes without pressureField discards v, #712 positional drop-ins, #742 psi_star[0] differs between families

## Not bundled (single, or not mine)
#1012 Stokes bodyforce leak (not deferred-destroy; separate from #1020), #755, #817, #821, #899, #307/#425/#429/#449 (MG prolongation quality, could be bundle H), #622/#629 (performance design).

Proposed order for W1: A (already next in queue: #1017, #1019, #1020), then B, then C.
