# #1168 on circles and spheres: does a given radial normal fail on the annulus and the shell?

From H6 (the curved-walls session), 2026-11-21, for the dev hub. Measurement only; no library
change. Built from the branch of #1277 (development plus a warning; numbers unchanged), a
96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH), one rank per
run, P2/P1, velocity block solved directly (MUMPS), tolerance 1e-10, pressure null space
attached, every solve converged.

## Verdict

- **As built, the annulus is safe.** `uw.meshing.Annulus` divides each wall into chords of one
  length (spread 7e-9), with and without refinement (refinement snaps the new midpoints onto
  the circle, which keeps the chords equal). The given radial normal is then consistent: the
  two solves differ by 1e-10, and both converge at rate 2.6 to 3 on every slip tried.
- **Once the wall nodes are moved along the circle, it is not.** On the same annulus with the
  nodes slid along their circles so that the chord lengths vary in step with the slip, the
  given normal `X/|X|` is **32 % to 34 % off and does not converge**, and the mean pressure grows
  like 1/h² (1e3 to 4e4). The default normal converges (rate 2.4 to 2.9). That is #1168 on a
  circle. Any run that slides wall nodes (a mesh mover with slip, adaptation, a free surface)
  and passes `normal=` is exposed; how much depends on how the grading lines up with the slip.
- **The shell, as built, shows no failure** at the two resolutions run (the given normal tracks
  the default within a few percent), but its mean pressure offset grows with refinement.
- **The ZG95 subduction drivers pass `normal=unit_r`** ("analytic", the default of every run to
  2026-11-01) on refined `Annulus` meshes, whose chords are equal: no effect as built. Moving
  their walls changes that.

## Why circles escaped, and when they do not

On a circle the given radial normal equals the chord normal at every P2 midpoint node, so the
extra constraint of #1168 (`sum_i r_i u_t,i = 0`, `r_i = W_i . t_g`) comes only from the
vertices, where `r_i = (|f1|^2 - |f2|^2) / (12 R)`: the difference of the squared lengths of the
two chords meeting there. Summed by parts, `sum r_i s_i = sum_j g_j (s_j+1 - s_j)` with
`g_j = |f_j|^2 / (12 R)`. Equal chords give r = 0 exactly. Unequal chords give a constraint that
bites only where the chord-length grading correlates with the derivative of the slip: random
jitter and a grading orthogonal to the slip leave the correlation C at 0 to 0.005, and the
velocity converges; a grading in step with the slip gives C about 0.2 at every resolution, and
it does not.

## Manufactured solutions

`manufactured_annulus.py`: the two-wall construction of `../manufactured.py` on 1/2 < r < 1,
`psi = Phi h + Phi^2 K`, exact free slip on both circles (u.n and tangential traction at most
1e-49 at 40 points per wall, 50 digits; div u = 0 exactly), slip with the angular shape of h:
`s2` (sin 2 theta), `c3` (cos 3 theta), `circ` (uniform), `s2circ` (both).
`manufactured_shell.py`: 1/2 < r < 1, `tor` (toroidal, u = q(r) grad(xy) x X) and `pol`
(poloidal, curl curl of X F(r) xy, F fixed so both walls are free slip); u.n and tangential
traction at most 1e-50 at 30 random points per wall, div u at most 1e-51.
Free slip on concentric walls leaves rigid rotations undetermined; errors are taken modulo the
least-squares rigid rotation (removed from both answers).

## Annulus, velocity error ||u - u_e|| / ||u_e|| modulo rotation

As built (`measure_annulus.py`, slide none); the two normals agree to four figures everywhere:

| slip | wall | 0.1 | 0.05 | 0.025 |
|---|---|---|---|---|
| s2 | essential (control) | 1.40e-2 | 2.30e-3 | 3.02e-4 |
| s2 | rotated, default | 1.45e-2 | 2.48e-3 | 3.82e-4 |
| s2 | rotated, X/|X| | 1.45e-2 | 2.48e-3 | 3.82e-4 |
| c3 | rotated, default and X/|X| | 1.67e-2 | 3.00e-3 | 5.20e-4 |
| circ | rotated, default and X/|X| | 1.81e-2 | 2.25e-3 | 3.31e-4 |
| s2circ | rotated, default and X/|X| | 1.71e-2 | 2.29e-3 | 3.44e-4 |

Wall nodes slid along the circles (`slide.py`):

| mesh, slip | wall | 0.1 | 0.05 | 0.025 | mean pressure offset |
|---|---|---|---|---|---|
| graded2 (theta + 0.1 sin 2 theta), s2 | essential | 1.38e-2 | 2.29e-3 | 2.98e-4 | |
| | rotated, default | 1.44e-2 | 2.61e-3 | 5.31e-4 | |
| | **rotated, X/|X|** | **0.318** | **0.339** | **0.342** | -2.2e3, -9.4e3, -3.7e4 |
| graded3c (theta + 0.1 cos 3 theta), c3 | essential | 1.53e-2 | 2.57e-3 | 3.49e-4 | |
| | rotated, default | 1.71e-2 | 3.20e-3 | 5.85e-4 | |
| | **rotated, X/|X|** | **0.307** | **0.329** | **0.332** | -1.1e3, -4.7e3, -1.9e4 |
| jitter (wall vertices +-1/4 chord), s2 | rotated, default | 1.59e-2 | 3.16e-3 | 8.99e-4 | |
| | rotated, X/|X| | 1.46e-2 | 2.54e-3 | 4.12e-4 | -9.8, -9.0, +19 |
| jitter, c3 | rotated, default | 1.84e-2 | 3.85e-3 | 1.13e-3 | |
| | rotated, X/|X| | 1.71e-2 | 3.37e-3 | 5.62e-4 | +8.9, -40, +0.27 |
| graded (theta + 0.1 sin 3 theta), s2 | rotated, default and X/|X| | 1.49e-2 | 2.6e-3 | 4.2e-4 | |
| graded, c3 | rotated, default | 4.22e-2 | 2.04e-2 | 1.03e-2 | -27 at 0.025 |
| | rotated, X/|X| | 1.74e-2 | 3.20e-3 | 5.82e-4 | |

The last row is not explained: on that mesh the default normal converges at first order only;
it is noted, not diagnosed.

Inconsistency (`inconsistency_annulus.py`): sum |r| and the correlation C of r with the exact slip.

| mesh | sum |r| at 0.1 / 0.05 / 0.025 | C (slip it is aligned with) |
|---|---|---|
| as built | 1.7e-10 / 1.2e-10 / 6.1e-11 | 0.00 to 0.005 |
| graded2 | 7.5e-3 / 1.9e-3 / 5.0e-4 | +0.18 (s2), at every resolution |
| graded3c | 1.7e-2 / 4.4e-3 / 1.1e-3 | +0.21 (c3), at every resolution |
| jitter | 5.7e-2 / 3.0e-2 / 1.6e-2 | 0.000 to 0.006 |

## ZG95 driver meshes (`chords_refined.py`)

`Annulus(radiusOuter=1/0.45, radiusInner=0.55/0.45, cellSize=0.5, refinement=n)`: wall chord
lengths spread 7e-9 relative at n = 0, 2 and 4 (448 and 256 chords at n = 4). Equal chords:
the given radial normal is consistent as built.

## Shell (`measure_shell.py`), velocity error modulo rotation

| slip | wall | 0.3 (1023 cells) | 0.2 (2285 cells) | mean pressure offset |
|---|---|---|---|---|
| pol | essential | 8.62e-2 | 2.98e-2 | |
| pol | rotated, default | 1.03e-1 | 4.81e-2 | |
| pol | rotated, X/|X| | 1.01e-1 | 4.79e-2 | +0.056, +0.84 |
| tor | essential | 3.08e-3 | 1.51e-3 | |
| tor | rotated, default | 1.42e-2 | 7.05e-3 | |
| tor | rotated, X/|X| | 1.50e-2 | 6.77e-3 | +0.086, -0.049 |

Cost: 83 to 560 s per run (three solves) at these sizes. Two resolutions only, and coarse: they
show no O(1) failure, not a converged rate. A shell with its wall nodes moved was not run.

## Not run

More than one rank; a shell with moved wall nodes; an annulus moved by the actual movers
(the slides here are prescribed); the free-surface module's walls.

## Files

`manufactured_annulus.py`, `manufactured_shell.py`, `measure_annulus.py`, `measure_shell.py`,
`inconsistency_annulus.py`, `slide.py`, `chords_refined.py`; logs in `logs/`.

Underworld development team with AI support from Claude Code
