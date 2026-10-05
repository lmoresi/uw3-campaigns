# Handoff to the Hyperion session (2026-10-05)

You are taking over the viscoelastic cylinder runs that need more cores than the laptop has. Read this file, then the
wiki's [Confined cylinder benchmark](https://github.com/underworldcode/underworld3/wiki/Confined-cylinder-benchmark) and
[Cylinder campaign 2026](https://github.com/underworldcode/underworld3/wiki/Cylinder-campaign-2026) pages, then the
roadmap items whose titles start "VE:" (`gh project item-list 10 --owner underworldcode --limit 300 --format json`).
The planning protocol is `docs/developer/guides/planning-on-github.md` in underworld3 (branch `docs/github-planning`,
PR #816, until it merges).

## 1. Set up (once)

```bash
gh auth login -h github.com -s project,read:project        # needs repo access to lmoresi/uw3-campaigns (private)
git clone https://github.com/underworldcode/underworld3.git ~/+Underworld/underworld3-pixi
cd ~/+Underworld/underworld3-pixi
git switch feature/forward-from-nodes                      # PR #800: forward histories, global projection, FENE-P log(f c) record (020b02f1 or later)
./uw setup                                                  # follow it; the runs use the pixi environment amr-dev (custom PETSc with AMR)
./uw build
pixi run -e amr-dev python -m pytest tests/test_1068_fene_p.py -q      # 8 pass; ~40 min, the shear-box tests are slow
git clone https://github.com/lmoresi/uw3-campaigns.git ~/+Simulations/uw3-campaigns
export UW3_WORKTREE=~/+Underworld/underworld3-pixi         # the checkout whose amr-dev environment runs the jobs
```

The driver also needs `pygmsh` (meshes are built on first use and cached in `ve_cylinder_demo/runs/`).

## 2. Run (from `~/+Simulations/uw3-campaigns/ve_cylinder_demo`)

`./run_guarded.sh <ranks> <label> <options>` runs one job under a guard (stops on blow-up, a 15-minute hang, or three
nonlinear failures) and logs one line to `runs/night_queue.log`. Resolution: res 20 = 2 wake cells per diameter
(`-uw_resolution 20 -uw_circle_ratio 0.25`, the defaults), res 40 = 4 (`-uw_resolution 40 -uw_circle_ratio 0.5`),
res 80 = 8 (`-uw_resolution 80 -uw_circle_ratio 1`). Ranks: res 40 ran at 4 ranks, about 7 s per step, 960 steps to
t 8; res 80 has four times the cells and twice the steps, so give it 16 to 32 ranks. Ask Louis how many cores Claude may
use on Hyperion before launching more than one job (the laptop budget was 8; it does not apply here, but a budget does).

In priority order:

1. **The res-80 pair at Re 100, Wi 0.5** (roadmap: "VE: Re 100 Wi 0.5 regime shift"). Decides whether the steady
   wake of the global projection or the shedding of the Eulerian stress is right.
   ```bash
   ./run_guarded.sh 24 re100_grid_Wi05_r80 -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport eulerian -uw_stress_transport eulerian -uw_devss 1.0 -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
   ./run_guarded.sh 24 re100_ob_Wi05_r80 -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
   ```
   Add the cell-fit stress at res 80 (drop `-uw_reconstruction global`) if cores allow: it is the third member.
2. **FENE-P at res 40 and 80** (roadmap: "VE: Wi 2 cases ... rerun at res 40"). `-uw_relaxation fene_p -uw_L2 100`
   with the forward global histories, Wi 1 and 2 at res 40, then Wi 0.5 and 1 at res 80. Wi 2 at res 20 was unresolved
   (stopped at t 7.1). Add `-uw_debug_fene 40` to the first one: it prints the spring factor and the record's trace every
   tenth step and every step from 40 to 65, which is how the last FENE-P failure was diagnosed.
3. **Newtonian at res 80** (`-uw_Wi 0`, or the Newtonian label the driver uses) to put the DFG validation at the same
   resolution as the pair.

## 3. Read the results

```bash
pixi run --manifest-path $UW3_WORKTREE/pixi.toml -e amr-dev python forces_summary.py 6 8 re100_grid_Wi05_r80 re100_ob_Wi05_r80
pixi run --manifest-path $UW3_WORKTREE/pixi.toml -e amr-dev python night_report.py > runs/REPORT.md
./render_movie.sh <label>                                   # frames and a movie of a run
```

Look at the frames and check the run has saturated before tabulating (lift amplitude steady over the window).

## 4. Report back

- Numbers and figures go on the wiki: the **Confined cylinder benchmark** status table and the **Cylinder campaign 2026**
  page (clone `underworld3.wiki.git`; figures under `images/`; math as `` $`...`$ `` and `math` blocks; a History line).
  Follow the page structure described on the wiki's How we plan page.
- Annotate the roadmap items you advance (a draft's body edit takes the `DI_` content id and the title again).
- Commit any script changes and the figure-generating scripts to this repository. Do not commit `runs/`.
- Large outputs (checkpoints, movies) stay on Hyperion or go to Dropbox; say where on the campaign page.
