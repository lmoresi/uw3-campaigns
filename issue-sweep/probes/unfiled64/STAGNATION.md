# UNFILED 64, option 3: the velocity sub-solve's stagnation (investigation only)

Fixture: test_1157's low-viscosity case (annulus 0.5-1, rotated free-slip on both walls,
custom FMG, tol 1e-6), cold solve. Serial, macOS (12-core Apple M4). Probes: floor1157.py and
floor_any.py (CELL, MU). The library is untouched: rtols and right-hand sides are changed from
the probe through `_set_absolute_target`, a KSP monitor and a pre-solve hook.

## Where the 3.3e-8 comes from
`fieldsplit_vel_ksp_rtol = 0.033 x tol`, with max_it 200 (rotated_bc.py, the custom-FMG branch
of the fieldsplit config, "the native path's (0.033 x tol, 200)"). At tol 1e-6 that is 3.3e-8.

## The floor, and why
On a free-slip annulus a rotation leaves the velocity block nearly singular. The PC projects
that mode out of what it is given and what it returns (`_NullModeProjectedPC`, #963). A velocity
sub-solve whose right-hand side has a component along the mode must then resolve that direction
without the preconditioner, through the block's tiny eigenvalue: a plateau and a slow creep.

Per sub-solve: iterations, the lowest relative residual reached, and the right-hand side's
component along the mode, |b.m|/|b|:

| sub-solve | its | lowest rel. residual | component along the mode |
|---|---|---|---|
| typical (16 of 18) | 4 | 1e-9 | 1e-17 to 1e-14 |
| 10th | 200 (cap) | 9.0e-6 | 6.1e-5 |
| last | 78 or 200 | plateau 1.4e-6, then creeps | 1.42e-6 |

The plateau sits at the component along the mode. A target below it (3.3e-8) can only be
reached by the creep.

## Cost, and two fixes measured
Cold solve, error against the test's direct LU solve (tol 1e-11). Three runs each where shown,
all identical:

| fixture | velocity sub-solve rule | total velocity its | capped | wall | error vs LU |
|---|---|---|---|---|---|
| cell 0.4, mu 1e-4 | default 0.033 x tol | 463 | 2 | 0.62 s | 1.59e-8 |
| | floor-aware: rtol = max(0.033 tol, 2 x component) | 68 | 0 | 0.31 s | 1.59e-8 |
| | project the mode out of the right-hand side | 71 | 0 | 0.31 s | 1.59e-8 |
| | fixed 3.3e-7 / 1e-5 (for scale) | 75 / 44 | 0 | 0.31 / 0.29 s | 1.59e-8 |
| cell 0.1, mu 1e-4 | default | 305 | 1 | 5.54 s | 1.52e-10 |
| | floor-aware | 55 | 0 | 2.52 s | 1.52e-10 |
| | project the right-hand side | 57 | 0 | 2.53 s | 1.52e-10 |
| cell 0.1, mu 1 | default | 29 | 0 | 2.18 s | 1.57e-8 |
| | floor-aware | 29 | 0 | 2.19 s | 1.57e-8 |

Either fix removes 80-85 % of the velocity iterations and halves the wall time where the mode is
excited, with the answer unchanged. Where it is not excited (mu 1), the floor rule is a no-op.

## Proposal (a register row, for Louis)
Project the projected null modes out of the velocity sub-solve's right-hand side, in the same
place the PC already projects them (#963). The mode lies in the outer solve's null space, so
the solution loses nothing, and the errors above agree. The floor-aware rtol works as well, but
it needs a factor (2) and a floor estimate. The projection needs neither, and it makes the
sub-solve consistent with its own preconditioner.

Limits: one geometry (annulus, rotated free-slip both walls), two resolutions, serial only. Not
measured: the warm re-solves, 3-D, fault and TI fixtures, and parallel. The pressure sub-solve's
own creep (the TODO(MEASURE) at the pressure rtol, fault-network layouts) is a different floor and
is not addressed here.
