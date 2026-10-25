# The crust-following fault: the stage-3 smoke tests

Twelve steps on 4 ranks from step 60 of the compositional-slab runs B1 (slab x100) and C1
(slab x100 with the overriding plate), with the fault law `crust` added to the baseline
recipe of `launch/stage_a/run_stage_b_comp.sh`:

    -uw_init checkpoint -uw_source <B1 or C1> -uw_source_index 60
    -uw_fault_law crust -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_crust_weak 0.1
    -uw_detect_start 0 -uw_detect_every 5 -uw_steps 12 -uw_ckpt_every 5

The fault follows the weak crust: its trace is the slab marker's 0.5 contour (the slab's
top, where the crust rides) from the trench down to 0.15 d, read every detection and
resampled at the rung spacing; the mesh is rebuilt when the trace moves more than four
rungs (0.016 d) from the built one. The crust is weakened less than in B1 (x0.1 instead
of x0.001) so that the fault carries the decoupling.

## The frames

`<case>_solver_step065.jpg`, `<case>_solver_step072.jpg`: the solver panels at the first
checkpoint after the fault formed (formed at step 61, built at 62) and at the warm,
same-set rebuild (step 72). Left: temperature on the base mesh with the fault trace at the
previous checkpoint (rust) and this one (ink). Middle: log10 strain rate with streamlines
and the trace. Right: plastic strain (nothing yields in these runs) with the trace. Below:
the nonlinear (ink, left axis) and linear velocity (teal, right axis) iterations per step,
rebuilds as rust lines, the fault's formation as a triangle.

`<case>_band_step072.jpg`: the band view of the rebuild. The strain rate on a window
around the fault before (step 70, its old trace in white, the new one as a ghost) and
after (step 72), and the tangential velocity jump across the trace against depth, sampled
two cells to either side on the base mesh (the split mesh is not checkpointed in these runs).

## What they show

| | B1 | C1 |
|---|---|---|
| fault formed | step 61 at -8.3 deg, 53 points | step 61 at -6.4 deg, 53 points |
| first build (changed set, cold start) | step 62: 1 Newton, 6 linear iterations | step 62: 1 Newton, 5 linear |
| ordinary steps | 1 Newton, 3-4 linear | 1 Newton, 4-5 linear |
| rebuild (same set, warm start) | step 72: 1 Newton, 4 linear | step 72: 1 Newton, 5 linear |
| slip on the fault | 440-600 (plate 800-970) | 290 falling to 180 |

The warm rebuild costs no more iterations than an ordinary step. In C1 the slip falls as the
overriding plate settles onto the contact. Newton converged at every step of both runs.
