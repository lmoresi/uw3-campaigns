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

## Round 2 (2026-11-21, the hub's follow-up): converged reruns and the circumcircle normal

### Which earlier entries were not converged

The "reason" column in the tables above (and in `../circles/`) is a stale SNES reason: the
rotated path does not run the SNES. The rotated solve's own record (`_rotated_freeslip_info`:
converged, final residual, KSP reason) is now printed for every solve. Five earlier cell-0.025
entries had a velocity sub-solve fall back to GAMG and stop unconverged, all with the default
normal: graded sin 2θ, graded cos 3θ, graded2 sin 2θ, graded3c cos 3θ (`../circles/` and the
diagnosis above), and the MMPDE trench sin 2θ.

### Converged reruns (`run_converged.sh`; `logs/conv_*`)

Default normal: direct MUMPS LU on the rotated system (`solver._rotated_use_lu`; one pressure
pin instead of the null space; with the default normal the summed continuity row is already
implied by the wall constraint, so dropping one row changes nothing). `X/|X|`: the iterative
route unchanged (the LU route's pin would drop the very row that carries #1168's extra
constraint, and hide it). Every solve below reports converged True with a final residual of
1e-11 to 1e-13 against an initial 3 to 6, except the as-built default LU at s2 0.05 / 0.025 and
c3 0.05, which stop at 7.5e-10, 3.0e-9 and 4.6e-8 (relative 1e-10 to 1e-8) and give the
`X/|X|` error to four figures.

Velocity error ||u - u_e|| / ||u_e|| modulo rotation (rate between 0.05 and 0.025), mean
pressure offset in brackets where it is large:

| mesh, slip | default | `X/|X|` = circumcircle |
|---|---|---|
| as built, sin 2θ | 2.48e-3, 3.82e-4 (2.70) | 2.48e-3, 3.82e-4 (2.70) |
| as built, cos 3θ | 3.00e-3, 5.20e-4 (2.53) | 3.00e-3, 5.20e-4 (2.53) |
| graded, sin 2θ | 2.58e-3, 4.19e-4 (2.62) | 2.60e-3, 4.26e-4 (2.61) |
| graded, cos 3θ | **8.82e-2, 4.39e-2 (1.01)** | 3.20e-3, 5.82e-4 (2.46) |
| MMPDE trench, sin 2θ | 2.65e-3, 3.99e-4 (2.73) | **1.43e-2, 7.20e-3 (0.99)** (p -3.6e3, -1.4e4) |
| MMPDE trench, cos 3θ | 3.32e-3, 5.51e-4 (2.59) | **5.49e-2, 2.75e-2 (1.00)** (p +1.3e4, +5.0e4) |
| graded2, sin 2θ, 0.025 only | 3.93e-4 | (0.342, `../circles/`) |
| graded3c, cos 3θ, 0.025 only | 5.85e-4 | (0.332, `../circles/`) |

What moved: of the five unconverged entries, four are unchanged with a converged solver
(graded sin 2θ 4.19e-4, graded3c 5.85e-4, trench sin 2θ 3.99e-4) or unchanged in kind; graded2
sin 2θ moves from 5.31e-4 to 3.93e-4. The graded cos 3θ default stays first order with a
converged LU solve, at about twice the iterative route's values (8.8e-2 and 4.4e-2 against
2.0e-2 and 1.0e-2): the answer depends on how the near-null rotation is gauged, which is the
diagnosis of (b), now with converged solves.

### H6-fix-1, the circumcircle normal (`circumcircle.py`; `logs/circumcircle.log`)

At each wall vertex, the unit normal of the circle through it and its two wall neighbours
(found from the wall facets, not by angle). At each P2 edge midpoint, the normalised mean of
the edge's two vertex normals ("mean"), or the normal at the midpoint of the circle through
the edge's two vertices and the nearer other neighbour ("cc3").

On every mesh measured (as built, graded, MMPDE trench; 0.05 and 0.025) every wall vertex lies
on its circle (to 2.2e-16 of R), so the circumcircle of three wall vertices is the wall circle
itself. Measured at every wall node: the angle between the circumcircle normal and `X/|X|` is
at most 8.5e-7° at vertices and 1.2e-6° at midpoints, under either midpoint rule: that is
arccos's resolution near 1, i.e. identical to round-off. A rigid rotation's normal component
`|n . (-y, x)| / R` is at most 1.3e-13: the rotation is an exact null mode, as the hub asked.
And #1168's weights `sum |r_i|` (r_i = W_i . t) are identical for the two normals, e.g. graded
0.05 outer wall 1.4858e-3 both, MMPDE trench 0.025 outer wall 8.9944e-5 both: the extra
constraint does not vanish.

So on a circular wall whose vertices lie on the circle (every mesh here, and any mesh a
slip-restoring mover leaves) H6-fix-1 is `X/|X|`, node for node: the "`X/|X|` = circumcircle"
column above is both, and the circumcircle normal does **not** converge at second order
everywhere: it is first order after the MMPDE move, exactly as `X/|X|`. The two differ only
on a wall whose vertices are off the circle (a non-circular wall, or a released one).

Why no single normal does both: the rotation is an exact null mode only if n is radial at
every wall node (n . (-y, x) = 0 there); #1168's extra constraint vanishes only if n is
parallel to the measure-weighted facet normal W_i at every node (r_i = W_i . t = 0). On unequal
chords W_i is not radial at the vertices (its angle is 0.25° at graded 0.05), so one normal
cannot satisfy both. A fix has to separate the two roles: constrain along W_i (no extra
constraint), and treat the rotation by gauging the constrained operator's actual near-null
mode rather than the declared rotation with its normal rows zeroed (not measured).

### `normal=` does not accept a field

A P2 vector MeshVariable passed as `normal=V.sym` fails inside the lambdify step with
`SyntaxError: invalid syntax. Perhaps you forgot a comma?` (`<lambdifygenerated-1>`), before
any solve: a field normal is not supported, and the error says nothing about why. (The #1277
gap list assumed such a normal is accepted but not seen as varying.) Measuring the
circumcircle normal through `normal=` therefore needs an expression; on these meshes it is
`X/|X|` to round-off, so the `X/|X|` solves are its solves.

Not run (round 2): np 2; a mesh whose wall vertices are off the circle, where the circumcircle
normal would differ from `X/|X|`; the separated fix.
