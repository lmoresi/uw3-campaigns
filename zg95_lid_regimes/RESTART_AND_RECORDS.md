# Restarts and solver records in `annulus_faults.py`

This document covers what a checkpoint holds, how a restart uses it, what each step records
about the solver, and how to plot that record. The measured numbers are in section 5.

## 1. Checkpoints and restarts

A checkpoint is written every `uw_ckpt_every` steps and at the last step. It holds these files
for step `N` (`NNNNN` is `N` padded to five digits) in `uw_out`:

| File | What it holds |
|---|---|
| `annulus.mesh.00000.h5` | the base mesh, written once and shared by every checkpoint |
| `annulus.mesh.<var>.NNNNN.h5` | base fields: `T`, `V`, `plastic_strain`, `edot_plastic`, `log10_eta`, `yield_ratio`, and the marker pictures when the swarm is on |
| `annulus.solver_mesh.NNNNN.h5` | the solver's faulted mesh, split included (`Mesh.write`). It reloads exactly through `uw.discretisation.Mesh` at any rank count (tested: written at np 16, read at np 16 and np 1, all 33650 cells and 17313 vertices, identical centroids). The renderer draws the true split mesh from it. |
| `annulus.solver_mesh.{V,P}.NNNNN.h5` | the faulted-mesh velocity and pressure as datasets `coords` and `values`: each DOF's value at its coordinate, with split copies nudged 0.1 rung onto their own side of the fault, gathered to rank 0 |
| `annulus.crust_swarm.NNNNN.h5`, `annulus.crust_swarm.<marker>.NNNNN.h5` | the particles and their markers (slab runs) |
| `state_NNNNN.json` | the state, below |
| `records.json` | every step's record, rewritten at each checkpoint |

`state_NNNNN.json` keys:
- `step`, `t`, `params`, `faults` (each with its `misses`/`idle` counters), `next_id`,
  `ridge_origin`, `ridges`, plus `theta_trench`, `dip`, `fault_depth`, `traces` for the
  single-fault readers.
- `decisions`: what steers the next fault decisions.
  - `k`: the loop counter of the next step. The detection cadence, `uw_detect_start` and the
    clearing of the refused set run on it.
  - `n_built`: the rebuild count.
  - `refused`: formation trenches the mesher refused.
  - `last_damage`: each fault's damage at the last detection.
  - `built`: the fault set the faulted mesh was built with. This lags `faults` while a fault
    has moved less than a rebuild, and `needs_rebuild` compares against it.
- `solver_checkpoint`: `{"mesh", "V", "P"}`, the faulted-mesh file names.
- `checkpoint_files`: every file a restart from this checkpoint reads (base `T`, `V`,
  `plastic_strain`, the solver mesh and its V and P, and the swarm with its markers).

A restart (`-uw_restart N`, run in the same `uw_out`) does this, in order:
1. It reads `state_N.json`. If any file listed in `checkpoint_files` is missing, it stops with
   a `FileNotFoundError` naming them, rather than starting colder or reseeding the swarm without
   saying so.
2. It reads the base fields and the swarm, then restores `decisions`.
3. It rebuilds the faulted mesh at `built`. The placement is deterministic, so this is the
   checkpointed mesh, on any rank count.
4. It gives each faulted-mesh DOF the saved V and P at the nearest saved nudged coordinate.
   - On the same mesh the match distance is 0. The first step is then exactly the warm step an
     uninterrupted run would take, with its Newton switch (`uw_warm_newton_switch`). The record
     shows `transfer: "checkpoint"`.
   - If the mesh differs, it takes the nearest values and the rebuild switch. The record shows
     `transfer: "checkpoint_nearest"`.
5. Fallbacks:
   - A checkpoint with no `solver_checkpoint` (an older driver) starts from the base velocity
     evaluated on the faulted mesh. That velocity is continuous across the faults and has no
     pressure. The record shows `transfer: "base_V"`.
   - If a warm start does not converge, `FaultedMesh.solve()` retries from rest. The record
     shows `cold_retry: true`.

Older checkpoints without `decisions` restart as close as the records allow:
- the cadence comes from the last detection step (the steps that record `damage`);
- `n_built` and the damage come from the records;
- nothing is refused;
- the mesh is built at the current faults.

`-uw_restart` takes precedence over `-uw_init slab`.

The driver truncates `records.json` to steps `<= N` on restart and rewrites it at every
checkpoint. Copy it aside before restarting a directory whose later records you want to keep.

## 2. `record["solver"]`, one per step

| Field | Meaning |
|---|---|
| `kind` | `ordinary`, `rebuild_same_set` (faults moved), `rebuild_changed_set` (a fault formed or retired), `restart_first`, `init_first` |
| `start` | `warm` or `cold`, on the first attempt |
| `cold_retry` | whether `solve()` fell back to a solve from rest |
| `faults_before`, `faults_after` | fault names on the mesh before and after this step's rebuild |
| `transfer` | `driver` (a rebuild's warm start), `checkpoint`, `checkpoint_nearest`, `base_V` (restart first step), or `none` |
| `F0` | ‖F̂‖ at the start of the first attempt, after the normal-constraint projection |
| `F_rest` | the rest-state residual (library `fnorm_rest`; null before underworld3 210c7307) |
| `F_ref` | max(F0, F_rest): what the convergence test and the Picard→Newton switch measure against |
| `F_final`, `rel_final` | the final ‖F̂‖, and F_final / F_ref |
| `converged` | whether the last attempt converged |
| `nonlinear_its` | nonlinear iterations, summed over attempts |
| `picard_its`, `newton_its` | iterations before and after the switch |
| `switch_iteration` | the iteration the switch fired at (null if it never switched) |
| `F_history` | ‖F̂‖ at each iteration start (library `rnorm_history`; null before 210c7307) |
| `line_search_alpha`, `line_search_cutbacks` | the accepted step per iteration, and how many were below 1 (null before 210c7307) |
| `attempts` | the nonlinear fields above for each attempt separately |
| `ksp_its`, `vel_its`, `pres_its` | linear iterations per increment: outer, velocity block, pressure block |
| `ksp_summary` | `outer_mean/max`, `vel_mean/max`, `pres_mean/max` |
| `velocity_pc`, `velocity_pc_type`, `schur_pre` | the preconditioners used |
| `operator_reused` | the rotation and the workspace were both reused |
| `pc_fallbacks` | preconditioner fallback warnings caught during the solve |
| `wall` | seconds by phase: `build`, `transfer`, `stokes`, `to_base`, `energy_strain`, `swarm`, `detection`, `checkpoint`, `step` |
| `mesh` | on rebuild and first steps only (null otherwise): `levels_cells`, `band_cells_fraction`, `split_pairs` (null), `chain_welded` |

The top-level fields (`newton`, `vel_its`, `pres_its`, `t_stokes`, `t_step`, `n_built`,
`t_build`) are unchanged. A record is about 1.2 KB per step.

Deviation from the spec: a step's `wall.checkpoint` reaches `records.json` at the next
checkpoint write, because the file is written inside the checkpoint. The last step's value is
written at once.

## 3. `run_info.json`

There is one entry per start or restart, appended. Each entry holds:
- `started`, `host`, `nodes`, `mpi_ranks`, `ranks_per_node`, `omp_threads`, `container`;
- `uw3_path`, `uw3_commit`, `uw3_branch`: from the environment variables `UW3_COMMIT` and
  `UW3_BRANCH`, else from `<underworld3>/_build_commit.txt`;
- `driver_commit`: from `DRIVER_COMMIT`, else read from the checkout's git files, since the
  image has no git;
- `petsc`, `argv`, `params`, `restart_from`, `slurm_job`.

## 4. `analysis/solver_record.py`

    python solver_record.py -uw_runs <dir>[,<dir>...] -uw_x step|t -uw_out solver.png \
        [-uw_table solver.md] [-uw_first <step> -uw_last <step>]

It draws one column per run on a shared x axis, with these panels from top to bottom:
1. Nonlinear iterations per step: Picard (light) stacked under Newton (dark). Cold starts are
   outlined; a red x marks a cold retry.
2. Wall time per step, stacked by phase.
3. Linear iterations per increment: velocity and pressure, mean as a line, maximum as dots.
4. |F0| / F_ref on a log scale: where each solve starts relative to the rest state. A warm
   step sits near 0.03, a changed-set rebuild near 0.6.
5. Line-search cutbacks per step.
6. Each fault's trench shift from where it was first seen (wrapped; the legend gives that
   position).
7. `slip_max`.
8. `vrms`.

Vertical lines run through every panel:
- same-set rebuilds: dashed grey;
- changed-set rebuilds: solid orange, labelled `+F11` or `-F10`;
- a run's first step and restarts: dotted black.

Records written before the solver sub-record still plot. The kinds come from `n_built` (a rise
is a rebuild, a drop is a restart under older drivers) and from `run_info.json` restarts. The
panels with no data say "no solver record".

The script writes `<run>/solver_summary.csv`: medians by kind (iterations, Picard, Newton,
F0/F_ref, s/step, s per nonlinear iteration, KSP means), cold retries, and totals. With
`-uw_table` it also writes one markdown table for all the runs.

## 5. Measured (kaiju, np 16, 0.5/4 mesh, Ra x3 lines setup, overlay warmonly)

These runs started from the laptop's 3580 state. Each test ran 3580→3600 uninterrupted, then
restarted from its own 3590 checkpoint for 10 steps.

| First step after the restart | Newton its | Stokes s | Agreement with uninterrupted, steps 3591-3600 |
|---|---|---|---|
| original driver (cold start, mesh rebuilt at the current faults) | 36 | 783 | slip_max 6-8% off from the first step, events differ at 3596, n_built reset |
| decision state + V_b warm start (19004eb-4485bea) | 17 | 387 | events and n_built identical, faults 2e-6, vrms ≤ 4e-4 |
| faulted-mesh checkpoint (item 3) | 4 (uninterrupted: 4) | 103 | step 3591 exact (vrms 3e-15); events and n_built identical; vrms ≤ 4.1e-4 by 3600 |

- From the 3580 laptop checkpoint (old format), the first step took 33 its / 687 s with the
  original driver and 17 / 430 s with the V_b warm start.
- The kaiju A/B (878b9c2 vs b0147e1, from 3590) measured 34.5 → 18 its and 736 → 460 s.
- Item 3 matches the checkpointed mesh exactly (distance 0) when restarting at np 8 from the
  np-16 checkpoint as well (first step 4 its, vrms 1.7e-8).
- On overlay-warmdiag (99259d35) a checkpoint restart's first step took 3 Newton iterations at
  F0/F_ref 0.026, with every line-search step at 1.

The remaining drift (≤ 4e-4 in vrms over 10 steps) is within the solver tolerance (uw_tol
1e-3) and leaves the fault events identical. It starts at the second step after the restart:
- The fields entering step 3592 agree with the uninterrupted run to 1e-11 (T 5e-13,
  plastic strain 8e-11, fault geometry 5e-9), and the initial guess is identical.
- Yet the starting residual differs by 6e-4.
- Checkpointing the plastic-strain-rate projection and the advection solvers' `.state` changed
  nothing.

So the difference is state the Stokes solver object keeps between solves, which a restart
builds fresh. It is a library question; hyperion is probing it.

The fault decisions jump on small differences in the state. Two uninterrupted runs that
differed only by a warm or cold first solve (vrms 1e-6) took different `keep_apart`
shortenings at the next detection. Compare events only between runs with the same driver and
library.

### Known limitation: a segment restart that lands on a rebuild (kaiju, 2026-10-27)

A segment restart reproduces the uninterrupted run only to the solver tolerance, and slip_max
shows it most strongly when the first step after the restart is a rebuild. Measured: two
restarts of `slab_fault_B1_crust1_fault` from its checkpoint 150, np 16, driver 0fb51f9, for
30 steps:
- One on overlay-leakfix (underworld3 547c2e54) and one on overlay-warmdiag (99259d35). They
  agreed with each other to 6e-10 in slip and 5e-12 in vrms, so the path is deterministic.
- Both took the path one would want. The checkpoint's own mesh (f0) was rebuilt, and V, P
  restored onto it at match distance 0.00e+00 ("same mesh"). Step 151's rebuild (to F0 at
  -18.40 deg / dip 78.9) then took the driver's ordinary rebuild path, warm-started from
  f0's solution.
- Yet against the uninterrupted run's step 151 (also a rebuild, from the same fault set):
  - slip_max was 8.83 against 17.99;
  - vrms was 158.987 against 158.907 (5e-4 relative);
  - both solves took 1 Picard iteration at F0/F_ref 1.0.
- The difference shrinks over the next steps: slip 19.5/21.5 at 152, 24.77/24.75 at 155,
  30.59/30.55 at 160. It is still up to about 20% at 162, while vrms stays within 0.5%.
- Rebuild steps, events and Newton iterations are unchanged; KSP means differ by one iteration
  at 10 of 30 steps.
- The rungs-8 run's segment restart at 151 showed the same effect: slip 29.0 against 23.9 on
  the same step.

So this is the restart drift described in section 5. The new solver starts from state a
restart cannot reproduce, which gives about 5e-4 in vrms. A rebuild step converges in a single
Picard iteration to uw_tol 1e-3, and slip_max, the largest velocity jump across the fault, is
far more sensitive to that drift than vrms. Compare runs across a segment restart in vrms,
events and trench history, not in slip_max at single steps near the restart. Reproducing the
uninterrupted run's slip exactly needs that solver state at the checkpoint. It is the same
library question as in section 5, now with hyperion.
