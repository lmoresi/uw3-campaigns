# uw3-campaigns

Driver scripts, guards and post-processing for Underworld3 simulation campaigns, kept here so the same campaign runs on any machine. Results (checkpoints, movies, forces) stay out of the repository; each campaign writes to its own `runs/` directory, which is ignored. Plans and findings live on GitHub: the [Underworld roadmap](https://github.com/orgs/underworldcode/projects/10), the repository [Discussions](https://github.com/underworldcode/underworld3/discussions) and [wiki](https://github.com/underworldcode/underworld3/wiki).

## Running on a new machine

```bash
git clone https://github.com/lmoresi/uw3-campaigns.git ~/+Simulations/uw3-campaigns
export UW3_WORKTREE=/path/to/underworld3-pixi       # the checkout whose pixi environment runs the jobs
export UW3_PIXI_ENV=runtime                          # pixi environment (default runtime: standard PETSc + pyvista)
cd ~/+Simulations/uw3-campaigns/ve_cylinder_demo
./run_guarded.sh 4 my_run -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
```

`run_guarded.sh <ranks> <label> <options...>` runs one job under a guard that stops it on a blow-up, a hung solve (no force write for 15 minutes) or three nonlinear-solver failures and appends one line to `runs/night_queue.log`. All options are `uw.Params` options of the driver (`-uw_<name> <value>`); the driver's docstring lists them.

## Campaigns

- `ve_cylinder_demo/` — the confined cylinder (DFG 2D-2 geometry) for viscoelastic flow: Oldroyd-B and FENE-P, every stress history and reconstruction, Re 100 and 200. `ve_cylinder.py` is the driver; `render_demo.py` / `render_movie.sh` render frames and movies; `forces_summary.py t0 t1 runs...` gives cd, lift amplitude and St over a window; `night_report.py` tabulates every run; `lanes/` are the overnight queue scripts of 2026-10-04/05; `reports/` keeps the reports those produced.

- `zg95_lid_regimes/` — yielding-lid convection in a 4 x 1 box (Moresi & Solomatov rheology with internal heating) with and without a split-node fault through the lid: the base regimes, the bistable lid at tau1/Ra 1, a fixed and a moving-trench fault, and the fault removed again. `drivers/` (base and faulted models, needing underworld3 `feature/box-faults`), `render/`, `analysis/`, `probes/`; `REPORT.md` has the findings and how to run.

## Tools

- `tools/` — the scripts that moved the planning hub to GitHub (parse the planning file, load Project items, the viscoelastic items). One-off, kept for the record.
