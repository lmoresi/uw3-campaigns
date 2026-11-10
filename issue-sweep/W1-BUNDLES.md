# W1 territory sweep, 2026-11-10 (solvers, rotated BC, custom MG)

254 open issues; about 90 touch this territory. Grouped by shared root cause or shared code.

## Closed out by the sweep
- #683 fmg inert on semi-Lagrangian solvers: fixed by #1030, probed, labelled fixed-in-development.

## A. Custom-P / FAC hierarchy lifecycle (custom_mg.py, solvers' install path)
Root: state an install leaves behind (options-database keys, deferred objects, a patch built on old geometry) outlives a change to the solver or mesh.
- #1019 gamg after FAC: leftover composite key, error 73
- #1020 reinstall leaks deferred objects at np > 1
- #1017 deform kills the FAC patch (ruled 2026-11-08); this PR does the kill and its record; the rebuild is the fault-move cycle
Branch bugfix/custom-mg-hierarchy-lifecycle (W1). Moved out: #898 (remesh() is mmg-only; Louis 2026-11-10: "let the mmg stuff atrophy"), #546 (rotated cache) to C, #885 (builder stats, fault-split review) to E.

## B. Timestep estimation (estimate_dt in solvers.py, advection_diffusion_eulerian.py, swarm)
- #891 units model reads dimensional coords as model units (dt 3.4x)
- #1025 SLCN diffusion limit shrinks dt as h^2
- #693 empty-rank reshape; rank-local max_magvel (H1 verifying on development: out of B if fixed)
- #978 (estimate_dt part) degree-2 midpoints
- H2's June mismatch lead (#688 rewrite of estimate_dt) belongs here
Separate, needs a benchmark: #1029 theta inert; #1031 setter unwrap (small, could ride with B).

## C. Rotated free-slip: corners, gauge, partition (rotated_bc.py)
- corners / partly pinned nodes: #608, #939, #941, #940 (fault_contact at a wall-pinned pair node)
- rigid-rotation gauge: #968, #969, #884
- cold start / datum: #883, #910, #348
- partition: #931 (may share #941's cause)
- #546 rotated workspace cache latches tolerance / FMG config
- #887 docs behind the code
Probably two PRs: corners+partition, gauge+datum.

## D. Silent non-convergence and reporting
- #585, #625, #755 sub-solve iteration caps. Changing a cap is a solver default: register row and evidence to Louis before any merge
- #770 warm start reports CONVERGED without moving (H1 verifying; author withdrew the evidence)
- #778 solve_history misses the Picard stage; #806 introspection lacks the config (H1 verifying)
- #804 gradient of an unconverged forward solve
One PR: a solve that hits a cap or does not move says so, and the report records it.

## E. Fault-split MG in parallel (custom_mg, cell-located transfer)
- #873 empty-rank coarse level, #874 rank-local raises before collectives, #888 CI coverage, #880 hardening, #671 np 3 Galerkin diagonal, #956 ptest_0863-0865 at np 4, #885 builder stats module-global / outside_hull cross-partition trigger
Needs hyperion for np > 1.

## F. ThinSheet
- #875 L and c_b inlined, #876 picard/time, #879 history projection + stale normals, #887 (part)

## G. Solver API traps
- #844 Stokes without pressureField discards v, #712 positional drop-ins, #742 psi_star[0] differs between families

## Not bundled (single, or not mine)
#1012 Stokes bodyforce leak (not deferred-destroy; separate from #1020), #817, #821, #899, #307/#425/#429/#449 (MG prolongation quality, could be bundle H), #622/#629 (performance design).

Agreed with C1 (2026-11-10): A, then B, then C, one PR per bundle, each reviewed by H1 in whole-code context. B and D wait for H1's verification table (#693, #770, #806). Hub triage: TRIAGE-2026-11-10.md, clusters C1, C2, C5.
