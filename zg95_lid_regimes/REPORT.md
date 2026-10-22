# ZG95 lid regimes: yielding-lid convection in a box, with and without a fault

Taken over from the Hyperion Server 3 annulus campaign (its note is
`scripts/sessions/fault_mg/CAMPAIGN.md` on underworld3 `feature/fault-split-multigrid`).
The regimes were established first in a flat 4 x 1 box with free-slip walls, then a
split-node fault was added through the lid. Run outputs live in
`~/+Simulations/zg95/box_regimes/runs/` and `~/+Simulations/zg95/box_faults/runs/`
(checkpoints, `records.json`, `renders/`); movies and the gallery of final states are
in `~/+Simulations/zg95/movies/`.

## Running

The drivers need the underworld3 fault-multigrid library: build `feature/box-faults`
(or a later branch carrying it) into a worktree and run from there.

```bash
export UW3_WORKTREE=/path/to/underworld3-pixi/.claude/worktrees/box-faults
cd $UW3_WORKTREE
D=~/+Simulations/uw3-campaigns/zg95_lid_regimes
# a base model (no fault), 4 ranks
OMP_NUM_THREADS=1 pixi run -e amr-dev mpirun -np 4 python $D/drivers/box_convection.py \
    -uw_out ~/+Simulations/zg95/box_regimes/runs/<name> -uw_tau1 9.1125e5 -uw_steps 8000
# a fault through a saturated state, trench moving with the overriding plate
OMP_NUM_THREADS=1 pixi run -e amr-dev mpirun -np 4 python $D/drivers/box_fault.py \
    -uw_out ~/+Simulations/zg95/box_faults/runs/<name> \
    -uw_source ~/+Simulations/zg95/box_regimes/runs/mobile_ref_H1.42 -uw_source_index 1975 \
    -uw_cold_start 1 -uw_picard 0 -uw_migrate 1 -uw_rebuild_rungs 4
# frames, montages, the gallery
pixi run -e amr-dev python $D/render/render_box.py -uw_run <run dir>
pixi run -e amr-dev python $D/render/montage_box.py -uw_run <run dir> -uw_first <step> -uw_every 5
```

All options are `uw.Params` (`-uw_<name> <value>`); each driver's docstring lists them.

- `drivers/box_model.py`: mesh, rheology, walls, per-step diagnostics shared by the drivers.
- `drivers/box_convection.py`: the base model. `drivers/box_fault.py`: the faulted model
  (lean split-ladder multigrid tail, moving trench, rebuilds).
- `render/`: frames, montages, the gallery, a niced watcher that renders new checkpoints.
- `analysis/regime_summary.py`: late-window statistics per run; `classify_regime` is a stub
  awaiting the regime thresholds.
- `probes/`: the hierarchy comparison (A / chain / lean chain), the SNES tolerance probe,
  the downwelling locator.

## Model

- eta(T) = deta^(1 - T), 1 at the base; Ra on the basal viscosity; layer depth 1.
- tau_y = tau0 + tau1 (1 - y), soft-min yield law, delta 0.2.
- Internal heating H; T = 0 at the top, 1 at the base; free-slip walls.
- SUPG transport at Courant 1 on the fastest cell; Stokes tolerance 1e-3.
- 4 x 1 box, coarsest cell 0.125 with two refinements (finest 1/32).
- The annulus numbers convert to the layer depth d = 0.45 as Ra d^3, H d^2, tau0 d^2,
  tau1 d^3: the annulus mobile case (Ra 1e7, H 7, tau 1e5 + 1e7 z) is Ra 9.11e5, H 1.42,
  tau 2.03e4 + 9.11e5 z here, deta 3e4.

## Findings

**The box lid at the annulus numbers is stagnant.** From the standard start (T_int 0.8,
four-cell seed) it settles at M 0.03, lid 0.30, T_mid 0.94. The annulus at the same
numbers was mobile with T_mid 0.70.

**Mobility against the yield-stress gradient.** From the standard start the lid is mobile
at tau1/Ra 0.25, 0.5 and 0.75 (M 0.85-0.98, lid 0.11-0.14, T_mid 0.64-0.69; 0.75 breaks
late, at t 0.07) and stagnant at 1. Strong internal heating (H 10) heats the interior
above the basal temperature and gives drips under a stagnant lid.

**The box is bistable at tau1/Ra 1.** Restarted from the saturated mobile tau1/Ra 0.5
state it stays mobile (M 0.78) for 0.34 of time, about five overturns.

**A fault flips the stagnant lid.** A frictionless split fault (45 degrees, to depth 0.35,
weak bridge to the surface) through the stagnant tau1/Ra 1 lid takes M from 0.03 to 0.85
within dt 0.003.

- With the trench FIXED: two overturns (the first a vertical slab to the base, v_rms peak
  649), then the slab is swept under the overriding plate, peels off the pinned fault as
  the convergence zone migrates, and detaches; after a sluggish interval the fault becomes
  a spreading centre (steady M 0.74-0.79 to t 0.405, two cells with downwellings at the
  walls).
- With the trench MOVING with the overriding plate: the slab descends along the fault
  plane, one-sided, as the trench advances from x 2.0 to 1.37; it then detaches, the fault
  turns to spreading and is carried away with the plate (to x 3.35 at t 0.28).
- With the fault REMOVED from the fixed run's final state, the lid stays mobile for dt 0.18
  (M 0.69). The fault is a trigger: it moves the bistable lid onto the mobile branch, and
  onto a longer-wavelength (two-cell) planform than the unfaulted mobile states (four cells).

## Solver

The recipe is the underworld3 capability guide `docs/developer/guides/faults-in-convection.md`
(commit c1107957 on `feature/box-faults`): a lean split-ladder tail for the multigrid (the
welded tail capped the velocity solve once the lid mobilised), the rotated loop's
warm-start rules, and the rebuild rules for a moving trench. Through an overturn the
nonlinear solve sets the cost (15-25 Newton increments per step on the moving-trench
run); a tolerance of 1e-2 or the declared regularisation eta_reg are the open choices.

## The annulus

Drivers: `drivers/annulus_model.py`, `annulus_convection.py` (no fault), `annulus_fault.py`
(one fault: fixed, window, fault-normal or strain-steered trench), `annulus_faults.py`
(faults formed and retired by damage), `strain_band.py` (the band detector). The annulus is
built in layer depths (r_o 1/0.45, r_i 0.55/0.45), so every box parameter carries over
unconverted. Outputs in `~/+Simulations/zg95/annulus_regimes/runs/` and
`~/+Simulations/zg95/annulus_faults/runs/`; the movie `movies/04_annulus_fault_strain_weakening.mp4`.

**Calibration.** At Hyperion's resolution (finest d/11) the driver reproduces Hyperion's
mobile `conv_ms98` (M 0.60, lid 0.23 d, T_mid 0.68). At tau1/Ra 1 the annulus mobilises at
d/32 too, from either seed (six cells within t 0.05, ten cells after t 0.13), where the box
stays stagnant to t 1.0 (the box at d/11 is stagnant to t 0.55, then overturns episodically).
The annulus counterpart of the box reference is tau1/Ra 1.5 with the ten-cell seed: stagnant
to t 0.59 (M 0.037, lid 0.34 d, T_mid 0.885). A two-cell box at tau1/Ra 1 is mobile (M 0.69):
long cells alone move the bistable lid onto the mobile branch.

**A moving fault through that lid** (45 degrees, 0.35 d, from t 0.295): episodic. A slab goes
down the fault and M rises to 0.51, the lid relocks (M 0.13 by t 0.33), and a second episode
follows. With **strain weakening** (yield x1.25 intact, x0.5 at gamma 0.5, transported plastic
strain) and the declared regularisation **eta_reg** (100 held M back to 0.26; 10 kept it at
0.36-0.43 at 5-14 Newton increments per step) the first episode is stronger (M 0.66) and the
second reaches M 0.81, with a ridge opening at about +100 degrees.

**The fault leaves the downwelling** under both kinematic trench laws (the overriding-plate
window, and the fault's own mean normal velocity): the slab sinks near-vertically at the
original trench while the straight fault, held at 45 degrees, drifts 15-20 degrees away.

**Strain-steered faults.** The detector finds the saturated, cold, descending plastic-strain
band and fits its ridge (the position of greatest strain at each depth, over the depth the
fault occupies). The fault relaxes onto it in trench angle, dip (which may pass vertical: the
slab steepens from 40-55 to 80-95 degrees) and depth (the local thermal boundary layer, the
T = 0.7 isotherm beside the trench, 0.08-0.15 d before the relock thickens it). The fault then
stays on the downwelling. The lid still relocks after the first slab: the relock is physical.
With faults formed where a band's damage exceeds 0.05 d^2 (and retired below 0.01), a second
fault formed at +30 degrees and took over the slip while the first stayed on its own band.
The remobilisation at +100 degrees is a spreading ridge, which the downwelling criterion
correctly leaves without a fault: mid-ocean-ridge physics is the open item.

## Next

Mid-ocean-ridge physics for the divergent boundaries; the regime map of the damage-fault
model against tau1/Ra.
