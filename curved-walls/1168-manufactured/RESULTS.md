# #1168: which free-slip treatment is right on an ellipse

From H6 (the curved-walls session), 2026-11-20. Measurement and diagnosis only; no library change.
Development 4ab522a4, a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R,
MPICH), one rank, P2/P1, velocity block solved directly (MUMPS), tolerance 1e-10, every solve
converged (SNES reason 2 or 4) unless the table says otherwise.

## Verdict

- **The default normal is right**: rotated free slip with `normal=None` converges to the exact
  free-slip solution at rate 2 in every case, which is the limit a straight-sided (degree-1) wall
  allows.
- **A given curved normal (`normal=` the ellipse's own) is wrong by design on a faceted wall of an
  enclosed domain**: it adds one exact constraint on the wall slip that the true flow does not
  satisfy, and the answer does not converge. It is 63 %, 66 % and 67 % off at cell sizes 0.1,
  0.05 and 0.025 on a manufactured solution whose slip has the symmetry of #1168's flow. On a
  manufactured solution whose slip is orthogonal to that constraint (a one-signed circulation),
  it is as good as the default. That is why it looked right in earlier checks.
- **Nitsche fails the same case, with either normal** (47–68 %, not converging, mean pressure
  growing like 1/h²): the same signature, not diagnosed here.

## The manufactured solutions (`manufactured.py`)

Elliptical annulus of the issue: outer ellipse x²/1.5² + y² = 1, inner circle of radius 0.5;
viscosity 1, `-div(2 eps(u)) + grad p = f`, `div u = 0`, `p = x y`.

- `u = (psi_y, -psi_x)`, so `div u = 0` exactly.
- **"outer"**: `psi = phi h + phi^2 k`, `phi = x²/A² + y² - 1`, `h = 1 + x/4`. Since psi = 0 on the
  ellipse, `u.n = 0` there. The `phi² k` term leaves the wall velocity unchanged and adds
  `-2 k |grad phi|²` to the tangential traction (found symbolically). k cancels the traction
  of `phi h`. The inner circle takes the exact velocity as essential data.
- **"both"**, free slip on both walls (#1168's setting): `Phi = phi_o phi_i`,
  `psi = Phi h + Phi² K`. K is blended so that it takes each wall's required value on that
  wall: `K = [phi_i T_o/(2|grad phi_o|⁴) - phi_o T_i/(2|grad phi_i|⁴)] / (phi_i³ - phi_o³)`,
  whose denominator is positive and of order one in the fluid. Slip is a one-signed
  circulation (h = 1 + x/4).
- **"both-xy"**: the same with `h = 2 x y`, so the slip is odd in x and odd in y. That is the
  symmetry of #1168's flow (radial load cos 4θ).
- Checks (`python manufactured.py`):
  - "outer" exactly: div u = 0, and u.n and the tangential traction both simplify to 0 on
    x = 1.5 cos s, y = sin s.
  - "both" and "both-xy": div u = 0 exactly; u.n and the tangential traction are at most 3e-49
    on both walls at 40 points each, evaluated to 50 digits.
  - Slip speed on the ellipse: 0.83–2.2 ("outer"), 1.46–3.67 ("both"), 0–3.6 ("both-xy").
- A first "both" construction divided by `|grad Phi|⁴ + Phi²`. It was exact too, but had sharp
  features where grad Phi nearly vanishes, and the control was 9 % off at cell 0.1. It was
  replaced; no number from it is used.

## Velocity error ||u - u_e|| / ||u_e|| (`measure.py`)

**Inner wall essential, outer free slip ("outer").**

| outer wall | 0.1 | 0.05 | 0.025 | rates |
|---|---|---|---|---|
| essential (control) | 1.82e-3 | 2.26e-4 | 3.05e-5 | 3.0, 2.9 |
| rotated, default normal | 1.87e-3 | 2.52e-4 | 4.11e-5 | 2.9, 2.6 |
| rotated, `normal=` exact | 1.82e-3 | 2.31e-4 | 3.28e-5 | 3.0, 2.8 |
| Nitsche, default normal, γ 12.5 | 2.39e-3 | 4.48e-4 | 1.01e-4 | 2.4, 2.1 |
| Nitsche, `normal=` exact, γ 1000 | 1.82e-3 | 2.31e-4 | 3.28e-5 | 3.0, 2.8 |
| penalty, exact normal, 1e6 | 1.82e-3 | 2.31e-4 | 3.26e-5 | 3.0, 2.8 |

**Both walls free slip, circulation slip ("both").**

| both walls | 0.1 | 0.05 | 0.025 | rates |
|---|---|---|---|---|
| essential (control) | 3.13e-3 | 4.23e-4 | 5.58e-5 | 2.9, 2.9 |
| rotated, default normal | 2.07e-2 | 5.11e-3 | 1.28e-3 | 2.0, 2.0 |
| rotated, `normal=` exact | 2.03e-2 | 5.02e-3 | 1.25e-3 | 2.0, 2.0 |
| Nitsche, default normal, γ 12.5 | 2.20e-2 | 5.42e-3 | 1.35e-3 | 2.0, 2.0 |
| Nitsche, `normal=` exact, γ 1000 | 2.03e-2 | 5.02e-3 | 1.25e-3 | 2.0, 2.0 |
| penalty, exact normal, 1e6 | 2.03e-2 | 5.02e-3 | 1.25e-3 | 2.0, 2.0 |

**Both walls free slip, odd-odd slip ("both-xy"): #1168 reproduced on a known answer.**

| both walls | 0.1 | 0.05 | 0.025 | rates | mean pressure offset |
|---|---|---|---|---|---|
| essential (control) | 3.12e-3 | 4.34e-4 | 5.64e-5 | 2.8, 2.9 | see note |
| rotated, default normal | 5.70e-3 | 1.25e-3 | 2.97e-4 | 2.2, 2.1 | ~1e-4 |
| **rotated, `normal=` exact** | **0.626** | **0.655** | **0.671** | none | −2.6e4, −1.1e5, −4.5e5 |
| Nitsche, default normal, γ 12.5 | 0.507 | 0.581 | 0.628 | none | +7.0e3, +3.2e4, +1.4e5 |
| Nitsche, default normal, γ 1000 | 0.677 | 0.679 | 0.682 | none | +9.4e3, +3.8e4, +1.5e5 |
| Nitsche, `normal=` exact, γ 12.5 | 0.470 | 0.560 | 0.617 | none | −1.9e4, −9.3e4, −4.1e5 |
| Nitsche, `normal=` exact, γ 1000 | 0.598 | 0.636 | 0.660 | none | −2.5e4, −1.1e5, −4.4e5 |
| penalty, exact normal, 1e4 | 5.67e-3 | 1.06e-3 | 4.87e-4 | 2.4, 1.1 | −5.5, −1.4, −0.35 |
| penalty, exact normal, 1e6 | 1.78e-2 | 2.03e-3 | 3.51e-4 | 3.1, 2.5 | −544, −139, −35 |

- The control of this variant stopped on SNES reason −6 (line search) with a drifting mean
  pressure (3e9 to 6e9). An all-essential domain is singular in the constant pressure, and the
  null space is off by default, as in #1168's script. Its velocity converges regardless.
  Rerun with the null space attached (`-uw_pressure_nullspace 1`, `logs/control_ns_*.log`): it
  converges (reason 4, 4, 2), with the same velocity errors (3.12e-3, 4.34e-4, 5.64e-5) and a mean
  pressure offset below 1e-4.
- Pressure errors and the other columns are in `logs/`.
- A pressure-balanced load (body force + 100 grad(r⁴ cos 4θ), `-uw_lambda 100`, `logs/both_l100_0.1.log`)
  changes nothing on the circulation solution: the given normal is still 2.05e-2. It is the slip
  pattern that matters, not the size of the pressure.

## #1168's own fixture (`which_wall.py`, cell 0.1)

Same mesh, the issue's load and solver; each wall takes its default or its given normal.

| outer | inner | rms velocity | mean pressure | from default/default |
|---|---|---|---|---|
| default | default | 1.4437e-2 | +6.4e-6 | 0 |
| given | default | 9.5942e-3 | +178.7 | 43.7 % |
| default | given | 1.4437e-2 | +6.4e-6 | 1.4e-10 |
| given | given | 9.5942e-3 | +178.7 | 43.7 % |

The ellipse's given normal carries the whole effect; the circle's changes nothing.

## Diagnosis (`inconsistency.py`)

At each P2 velocity node on the wall the assembler's boundary term weights the facet normals by
the basis integrals: W_i = Σ_f (∫_f φ_i ds) n_f, which is |f|/6 n_f at a vertex and 2|f|/3 n_f at
a midpoint. The default normal is W_i/|W_i|, the consistent normal (Engelman, Sani and Gresho,
1982; the measure weighting of #560). With it, a uniform pressure exerts no force on the free
(tangential) row of any rotated node.

With a given normal n_g, the free direction t_g is not perpendicular to W_i. A uniform pressure c
then exerts c r_i on node i, with r_i = W_i·t_g. Because the constant is in the P1 pressure space,
its continuity row is an exact equation of the discrete system. With every wall
normal-constrained it reads

    Σ_i r_i u_t,i = 0      (u_t,i the slip at node i)

The mean pressure is its multiplier. The constraint is homogeneous: r shrinks with the mesh, but
the condition only depends on r's direction. So it removes from the slip whatever correlates
with r, at every resolution.

| | cell 0.1 | cell 0.05 |
|---|---|---|
| largest angle, default vs given normal, at a vertex | 0.112° | 0.028° |
| same at a midpoint (the ellipse's normal there is the chord's) | 4e-13° | 8e-13° |
| Σ\|r\| | 2.28e-3 | 5.75e-4 |
| correlation of r with #1168's slip (default-normal solve) | −0.616 | −0.615 |
| correlation of r with the "both" exact slip | 0.0000 | 0.0000 |
| correlation of r with the "both-xy" exact slip | +0.632 | +0.631 |

What the measurements show:

- r is antisymmetric under both reflections of the ellipse, largest near θ = ±15° and ±165°.
- Σ|r| falls like h², and the mean pressure grows like 1/|r|: ×4.2 per halving in #1168 (179,
  then 750) and here (−2.6e4, −1.1e5, −4.5e5).
- The correlation does not change with the mesh.
- A slip pattern with no projection on r (a circulation, by symmetry) is untouched, so the
  given normal converges there.
- A pattern with a projection of 0.6 loses it: 44 % in #1168, 63–67 % here.
- The penalty with the exact normal is a soft version of the same constraint. At 1e4 it
  converges; at 1e6 it is visibly polluted at coarse cells and recovers as h falls.
- The essential-inner-wall runs ("outer") carry the same constraint, with the inner data flux
  on the right-hand side. Their slip is a circulation, so they show nothing.
- Normalisation, sign and evaluation points were checked concretely:
  - The ellipse normal passed is unit length.
  - Outward on the ellipse, pointing out of the fluid on the circle.
  - Evaluated at the node coordinates: vertices on the ellipse, midpoints on the chords, where
    it equals the chord normal to 1e-12°.
  - Nothing in `normal=`'s evaluation is wrong; the inconsistency is in using it at all on a
    faceted wall.

## What needs deciding

This is a ruling, not a quiet fix:

- `normal=` with a non-constant normal is the documented way to make rigid rotation an exact
  null mode on annuli and shells (#963), and many tests use `X/|X|`.
- A constant normal on a planar wall equals the facet normal, so it is unaffected.
- On a faceted circle or sphere with unequal facets, r ≠ 0 too. Whether it matters depends on
  how the slip correlates with the facet pattern; that was not measured here.

Options:

1. Refuse a non-constant `normal=` on a domain with no open boundary. Straight, but it breaks
   the shell rotation-gauge use.
2. Impose the constraint along the consistent normal always, and keep a given normal only for
   what needs the true geometry: the rotation null modes and the direction of a datum. That
   changes `build_rotation`'s inputs and the tests built on exact rotations (`test_1131`,
   `test_1018`, `test_1142`, `test_1064`).
3. Keep it and warn whenever a non-constant normal is given on a domain whose every boundary is
   normal-constrained. Say in `rotated-freeslip.md` that it adds the constraint above.

Separately, Nitsche fails "both-xy" with either normal and the same 1/h² mean pressure.
Probably the same constant-pressure coupling through its wall terms; not diagnosed here.

## Not run

More than one rank; 3-D; a sphere or a circle with unequal facets; meshes finer than 0.025;
a domain with an open boundary (where the constraint would not exist).
