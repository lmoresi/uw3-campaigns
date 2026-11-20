# #1168: a real MMPDE move with wall slip, and the default normal on a graded circle

From H6 (the curved-walls session), 2026-11-21, for the dev hub, before the lead's ruling on
`normal=`. Measurement only; no library change. Development plus the #1277 warning (numbers
unchanged), a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH),
one rank per run, P2/P1, tolerance 1e-10, pressure null space attached. Manufactured solutions
from `../circles/manufactured_annulus.py` (exact free slip on both circles; errors modulo the
least-squares rigid rotation, as in `../circles/`).

## (a) After a real MMPDE move with slip on both walls

`mmpde_measure.py`: `uw.meshing.node_redistribution(mesh, density, slip_surfaces=True,
skip_threshold=None, method_kwargs=dict(accel="none", n_outer=20))`, the call the annulus MMPDE
runs make, on `Annulus(radiusInner=0.5, radiusOuter=1)`. Metric "trench": a band near the outer
wall localised in angle, `1 + 24 exp(-((r-0.95)/0.06)^2 - (dtheta/0.25)^2)`, the kind of
concentration a subduction run asks for; "band": `1 + 24 exp(-((r-0.9)/0.06)^2)`. After the move
every wall vertex is on its circle to 2.2e-16 of the radius (the slip restore works); the outer
wall's chords vary by max/min 1.29 (0.1), 1.23 (0.05), 1.12 (0.025) under "trench", 1.05 under
"band".

Velocity error ||u - u_e|| / ||u_e||, and the mean pressure offset with `normal=X/|X|`:

| metric, slip | essential (control) | rotated, default | rotated, `X/|X|` | `X/|X|` mean p offset |
|---|---|---|---|---|
| trench, sin 2θ, 0.1 | 1.45e-2 | 1.49e-2 | 3.22e-2 | -9.5e2 |
| trench, sin 2θ, 0.05 | 2.47e-3 | 2.65e-3 | 1.43e-2 | -3.6e3 |
| trench, sin 2θ, 0.025 | 3.22e-4 | 3.99e-4 | 7.20e-3 | -1.4e4 |
| trench, cos 3θ, 0.1 | 1.76e-2 | 1.88e-2 | 1.04e-1 | +3.0e3 |
| trench, cos 3θ, 0.05 | 2.89e-3 | 3.32e-3 | 5.49e-2 | +1.3e4 |
| band, sin 2θ, 0.1 | 3.15e-2 | 3.17e-2 | 3.59e-2 | -2.2e3 |

**Verdict (a):** after a real MMPDE move with wall slip, `normal=X/|X|` converges at about first
order (rates 1.2, 1.0 for sin 2θ; 0.9 for cos 3θ) while the default normal converges at 2.5 to
2.7; at cell 0.025 the given normal's error is 18 times the default's, and its mean pressure
grows like 1/h^2. It does not stall at 33 % as on the hand-graded mesh of `../circles/`, because
the mover's chord grading weakens as the mesh is refined (max/min 1.29 to 1.12) and correlates
only weakly with these slips (C 0.007 to 0.09), but it is wrong at first order. A radial band
metric barely changes the chords and barely matters. The phase-3 MMPDE runs with wall slip and
`normal=unit_r` are in this regime. Serial only; the np 2 spot check was not run.

## (b) Why the default normal converged at first order on the graded circle

Case of `../circles/`: every node moved by theta -> theta + 0.1 sin 3θ, slip cos 3θ; default
4.22e-2, 2.04e-2, 1.03e-2; `X/|X|` 1.74e-2, 3.20e-3, 5.82e-4.

1. **Not the direction of the default normal.** Its largest angle from the true radial normal at
   a wall vertex is 0.97°, 0.25°, 0.064° (`../circles/logs/inconsistency_annulus_graded_*`):
   second order. (At P2 midpoints it is exact.) The hypothesis that the facet-weighted vertex
   normal is first-order wrong on a smooth grading is refuted: (|f1| - |f2|) is O(h^2) there.
2. **Not the forcing's net torque by itself.** On the graded mesh the discrete forcing has a net
   torque (T = 9.8e-2, 2.5e-2, 6.3e-3 in rotation units, O(h^2)); taking it out of the body force
   (`diag_graded.py -uw_detorque 1`) leaves the error unchanged (4.23e-2, 2.04e-2).
3. **The rotation mode.** On a circle a rigid rotation is a null mode of the continuous problem.
   With `X/|X|` it satisfies u.n = 0 at every wall node exactly, so it is an exact discrete null
   mode and the #906 gauge removes it exactly. With the default normal on unequal chords it
   violates u.n = 0 at the vertices by ω R sin(angle), O(h^2): the constrained operator then has
   a near-null rotation-like mode instead of a null one. Both answers carry a rotation of about
   -0.04 (against 1e-4 in the exact solution), set by the gauge.
   - With the mesh's declared rotation (#906, development's default) the gauge projects out the
     declared mode with its constrained rows zeroed: compatible with u.n = 0 but not rigid and not
     null. The answer is first order (above).
   - With no declared rotation (`-uw_declare_rotation 0`), nothing gauges it and the near-null
     mode is driven freely: rotation amplitude 66 (0.1), 131 (0.05); error 18 %, 8.9 %; at 0.025
     the preconditioner set-up fails.
   So the first-order error comes from the default normal making the rigid rotation inexact on
   unequal chords, not from the normal's direction error as such, and the declared gauge only
   limits it.

**Verdict (b):** a defect of the default normal on graded closed circular walls, in combination
with the rotation null mode: option 2 (always the default normal) is not free there. A default
that keeps the rigid rotation exact on a circle would remove it, e.g. the vertex normal taken from
the circle through the vertex and its two wall neighbours (exactly radial on a circle, second
order on a general curve), or the facet-weighted normal for the constraint with the rotation
gauge built from the projected mode's rigid part. Neither was measured. Note also that on the
graded mesh at cell 0.025 the rotated velocity sub-solve did not converge (GAMG fallback, 200
iterations, |r| 0.30); the 0.025 default-normal entry rests on that solve.

## Files

`mmpde_measure.py`, `diag_graded.py` (options `-uw_detorque`, `-uw_declare_rotation`),
`manufactured_annulus.py` and `slide.py` (copies from `../circles/`), `logs/`.

Not run: np 2; the driver itself (`annulus_faults.py`) with its fault ladder and ZG95 geometry;
the shell after a move; the second-order default normals above.
