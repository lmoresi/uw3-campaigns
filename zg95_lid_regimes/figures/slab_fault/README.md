# The crust-following fault: the stage-3 smoke tests

Twelve steps on 4 ranks from step 60 of the compositional-slab runs B1 (slab x100) and C1
(slab x100 with the overriding plate), with the fault law `crust` added to the baseline
recipe of `launch/stage_a/run_stage_b_comp.sh`:

    -uw_init checkpoint -uw_source <B1 or C1> -uw_source_index 60
    -uw_fault_law crust -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_crust_weak 0.1
    -uw_detect_start 0 -uw_detect_every 5 -uw_steps 12 -uw_ckpt_every 5

The fault follows the weak crust: at every detection the slab marker's 0.5 contour (the
slab's top, where the crust rides) is read from the surface down to 0.15 d and replaced by
its least-squares parabola, one smooth curve from 0.02 d above the wall to the depth cap,
resampled at the rung spacing. The placement handles the surface: the cut stops three
rungs inside the wall and the top of the curve sits in the ribbon's transversely isotropic
zone. The mesh is rebuilt when the new curve lies more than four rungs (0.016 d) from the
built one. The crust is weakened less than in B1 (x0.1 instead of x0.001) so that the fault
carries the decoupling. The raw contour was tried first: its cell-scale wiggles became
kinks in the band and locked the fault (slip 440-600 in B1 against 740-850 here).

## The frames

`<case>_solver_step065.jpg`, `<case>_solver_step072.jpg`: the solver panels at the first
checkpoint after the fault formed (formed at step 61, built at 62) and at the last step.
Left: temperature on the solver mesh with the fault trace at the previous checkpoint (rust)
and this one (ink). Middle: log10 strain rate with streamlines and the trace. Right:
plastic strain (nothing yields in these runs) with the trace. Below: the nonlinear (ink,
left axis) and linear velocity (teal, right axis) iterations per step, rebuilds as rust
lines (full for a changed fault set, dashed for the same set), the fault's formation as a
triangle, cold starts as squares.

`<case>_band_step070.jpg`: the band view across the checkpoint pair over which the trace
moved most. The strain rate on a window around the fault before (step 65, its old trace
in white, the new one as a ghost) and after (step 70), and the tangential velocity jump
across the trace against depth, read from the checkpointed solver-mesh velocity. In C1 the
pair spans the same-set rebuild at step 67.

## What they show

| | B1 | C1 |
|---|---|---|
| fault formed | step 61 at -8.3 deg, dip 50, 49 points | step 61 at -6.4 deg, dip 41, 57 points |
| first build (changed set, warm start) | step 62: 1 Newton, 5 linear iterations | step 62: 1 Newton, 5 linear |
| ordinary steps | 1 Newton, 3-5 linear | 1 Newton, 3-4 linear |
| rebuild (same set, warm start) | step 72: 1 Newton, 4 linear | step 67: 1 Newton, 4 linear |
| slip on the fault | 740-850 (plate 800-970); 530 on the rebuild step | 840-930 |

Both rebuilds cost no more iterations than an ordinary step, and the first build is now a
warm start (the restart fixes merged at 4955e80). The smooth fault takes nearly all of the
plate's motion in B1; in C1 the overriding plate no longer settles the slip down as it did
on the kinked trace. Newton converged at every step of both runs.
