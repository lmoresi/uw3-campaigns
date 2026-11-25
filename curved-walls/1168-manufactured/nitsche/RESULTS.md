# UNFILED 24: why Nitsche free slip does not converge on the elliptical annulus

Diagnosis only; no library change. Development fbef72fa plus local branches that do not touch Stokes
or Nitsche (build in `wt-h6-unfiled58`). Serial, P2/P1, viscosity 1, velocity block by MUMPS,
tolerance 1e-10, on a 96-thread Linux workstation (Intel Xeon Gold 6240R, MPICH). Scripts: `diag.py` (ellipse),
`annulus_nitsche.py` (annulus), `gamma_sign.py`. Logs in `logs/`.

## Diagnosis

`add_nitsche_bc` on Stokes adds `-(n.d)(u.d - g) q` to the continuity row (the #1145 term), with
`d = n` for free slip. Tested with a constant pressure, the continuity row becomes
`int div u - sum_walls int u.n_used`. P2 velocity on straight facets satisfies the divergence theorem
exactly, so this is `sum_walls int u.(n_facet - n_used)`. On a domain whose whole boundary has its flux
fixed, that is an equation on the wall slip, with the mean pressure as its multiplier: #1168's
extra constraint, here through Nitsche's pressure coupling.

- **The default normal** (`mesh.boundary_normal`: P1 vertex-averaged facet normals, linear along
  each facet) and **the exact normal** both differ from the facet normal at the quadrature points.
  - Both fail on the ellipse, with the mean pressure growing like 1/h², and on the annulus once
    the wall nodes have slid.
  - On the as-built annulus (equal chords) the constraint does not bind, and both converge.
- **Opening one boundary removes the constraint.**
  - Nitsche with the default normal on the ellipse and a traction (natural) condition on the
    circle converges at rate 2.1.
  - The same Nitsche on the ellipse with the circle given its exact velocity (still closed) fails.
- **The facet normal** (`normal=mesh.Gamma`) removes the constraint (mean pressure ~1e-4). But it
  imposes `u.n_chord = 0`, which the exact solution violates by O(h) on a curved wall.
  - It converges at first order only, closed or open.
  - It gets worse as gamma grows, since a larger penalty enforces the wrong condition harder:
    8.3e-3 at gamma 10 and 69 % at gamma 1e5, at cell 0.05.
- **Gamma does not rescue the default normal:** 53 to 73 % at every gamma from 1 to 1e5.

So, as for the rotated condition in #1168, no single normal serves both roles.
- The pressure coupling (the continuity-row term, and `p n.v` in the momentum rows) is
  consistent with the discrete divergence only with the facet normal.
- The penalty and consistency terms need a smooth normal.

The fix that suggests is to use the facet normal in the two pressure terms and the default normal
elsewhere. **It is not tested here**: it needs a library change, and this note proposes it only as
the hypothesis to test next.

## Ellipse (manufactured both-xy: exact free slip on both walls, slip odd in x and y)

Velocity L2 error, relative; outer wall / inner wall treatments.

| outer | inner | 0.1 | 0.05 | 0.025 | rates | mean p offset at 0.025 |
|---|---|---|---|---|---|---|
| exact | exact (control) | 3.12e-3 | 4.34e-4 | 5.64e-5 | 2.8, 2.9 | 7e-5 |
| rotated, default | rotated, default | 5.70e-3 | 1.25e-3 | 2.97e-4 | 2.2, 2.1 | 7e-5 |
| Nitsche, default | Nitsche, default | 0.507 | 0.581 | 0.628 | none | +1.4e5 |
| Nitsche, exact normal | Nitsche, exact normal | 0.470 | 0.560 | 0.617 | none | −4.1e5 |
| Nitsche, default | exact | 0.498 | 0.563 | 0.605 | none | +1.5e5 |
| exact | Nitsche, default | 3.12e-3 | 4.35e-4 | 5.68e-5 | 2.8, 2.9 | 7e-5 |
| Nitsche, default | open (traction) | 7.07e-3 | 1.63e-3 | 3.97e-4 | 2.1, 2.0 | 4e-4 |
| Nitsche, facet normal | Nitsche, facet normal | 2.29e-2 | 1.05e-2 | 4.97e-3 | 1.1, 1.1 | 6e-5 |
| Nitsche, facet normal | open (traction) | 2.87e-2 | 1.31e-2 | 6.22e-3 | 1.1, 1.1 | 2e-2 |
| exact | open (traction), control | 3.12e-3 | 4.34e-4 | 5.64e-5 | 2.8, 2.9 | 5e-6 |

Gamma 12.5 (the default) throughout. Every solve converged (SNES reason 2 or 4; KSP reason 3 is the preconditioner-only velocity block). The traction condition takes
`-sigma.n` in `add_natural_bc` (the control with it on the circle matches the all-exact control; with
`+sigma.n` it was 5.5e-2 at 0.1).

**Gamma sweep, cell 0.05** (`logs/gamma_sweep_0.05.log`):

| gamma | 1 | 10 | 100 | 1e3 | 1e4 | 1e5 |
|---|---|---|---|---|---|---|
| Nitsche default, both walls | 0.731 | 0.530 | 0.670 | 0.679 | 0.682 | 0.686 |
| Nitsche facet normal, both walls | 1.70e-2 | 8.35e-3 | 7.57e-2 | 0.362 | 0.628 | 0.691 |
| Nitsche default, circle open | 1.84e-3 | 1.63e-3 | 1.64e-3 | 1.64e-3 | 1.64e-3 | 1.64e-3 |

## Annulus (radii 0.5, 1; slip sin 2 theta; inner circle exact, outer circle under test)

Nitsche on both circles leaves the rigid rotation undetermined (it has no gauge): those solves
diverged (rotation ~3e9), so the inner circle takes the exact velocity, keeping the domain closed.
Errors modulo rigid rotation.

| mesh | outer circle | 0.1 | 0.05 | 0.025 | rates |
|---|---|---|---|---|---|
| as built | rotated, default | 1.44e-2 | 2.45e-3 | 3.68e-4 | 2.6, 2.7 |
| as built | Nitsche, default | 1.44e-2 | 2.44e-3 | 3.68e-4 | 2.6, 2.7 |
| as built | Nitsche, X/\|X\| | 1.44e-2 | 2.44e-3 | 3.68e-4 | 2.6, 2.7 |
| as built | Nitsche, facet normal | 2.00e-2 | 7.56e-3 | 3.59e-3 | 1.4, 1.1 |
| slid (graded2) | rotated, default | 1.42e-2 | 2.47e-3 | 3.77e-4 | 2.5, 2.7 |
| slid (graded2) | Nitsche, default | 0.378 | 0.479 | 0.558 | none (mean p to +1.0e5) |
| slid (graded2) | Nitsche, X/\|X\| | 0.474 | 0.554 | 0.606 | none (mean p to −2.2e5) |
| slid (graded2) | Nitsche, facet normal | 2.03e-2 | 7.86e-3 | 3.74e-3 | 1.4, 1.1 |

Caveat: on the slid mesh the facet-normal solves at 0.1 and 0.05, and the control at 0.1, stopped on
SNES reason −5 (iteration cap); their velocity errors are recorded but rest on unconverged outer
iterations. All other annulus entries converged.

## Not run

More than one rank; 3-D; the hybrid (facet normal in the pressure terms only), which needs a library
change; theta other than 1.

Underworld development team with AI support from Claude Code
