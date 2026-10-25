# The compositional slab: what the three laptop runs look like

Frames and the trench-retreat curve of the stage-A/B/C runs behind the compositional-slab
recipe (`launch/stage_a/run_stage_b_comp.sh`), so the production cases can be chosen by eye.
Every run: refinement 5 (d/64), 4 ranks, 120 steps at 20x the accuracy step, checkpoints
every 10 steps. The baseline recipe is the `BASE` string of `run_stage_b_comp.sh`: an
isoviscous mantle (`-uw_deta 1`, `-uw_asth 1`), thermal buoyancy off (`-uw_buoy_T 0`), the
plate and slab a particle-carried layer 0.1 d thick with a density deficit of 0.5 and a
viscosity contrast, a weak crust one cell thick on top (`-uw_crust_weak 0.001`), no fault
(`-uw_fault_law none -uw_max_faults 0`), no overriding plate (`-uw_over_plate 0`), a 0.35 d
slab at 45 degrees, Ra 3e6 with tau0/Ra 0.075 and tau1/Ra 10.

| case | run | delta from the baseline recipe |
|---|---|---|
| B1 | `slab_B1_comp100` | none (`-uw_comp_eta 100`, the baseline itself) |
| B2 | `slab_B2_comp1000` | `-uw_comp_eta 1000` (a stiffer slab) |
| C1 | `slab_C1_over_gap015` | `-uw_over_eta 100 -uw_over_gap 0.15` (a compositional overriding plate, viscosity x100, set back 0.15 d from the trench) |

## The frames

`<case>_step<NNN>.jpg` at steps 20, 60 and 119 (early, mid, late), the left two panels of the
run's `renders_strain/zoom_<NNNNN>.png` cropped and downscaled (the plastic-strain panels are
empty in these runs: nothing in the mantle yields). Left: temperature with streamlines, the
marker outlines drawn over it (orange: the slab layer at marker 0.5; green: the crust; purple:
the overriding plate in C1). Right: log10 of the second invariant of the strain rate. The
window is the half of the annulus around the trench; the slab's initial position is the
45-degree line from the trench at the top of the window. The time of each frame is in its
title: B1 reaches t 0.0011 by step 119, B2 (a stiffer, slower slab) t 0.0038, C1 t 0.0018.

What they show: the slab hangs from the plate without a hinge pivot and the plate follows it
down, so the trench retreats toward the subducting side (roll-back). The retreat rate roughly
halves once the tip reaches the base (B1 step 70). The overriding plate in C1 halves the
rate again, is drawn along with the trench, and rides on the crust from step 40 on: that
contact is where a stage-3 fault would go.

## The trench-retreat curve

`trench_retreat.png`: the trench position against time for the three runs, from
`analysis/slab_metrics.py -uw_plate_depth 0.14` (the trench is the +theta edge of the slab
marker at the surface, in layer depths from its start; the saved series are each run's
`slab_metrics.json`). The dashed line is the stage-A target, foundering by at least half the
slab length (0.175 d). B1 passes it at t 0.0004, C1 at 0.0007, B2 at 0.0016, and all three go
on to more than the slab's own length.
