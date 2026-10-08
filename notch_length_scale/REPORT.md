# Report: a shear-band length scale for the notch (overnight, Hyperion, 2026-10-08)

Work for `HANDOFF.md`. Code: underworld3 branch `feature/shear-band-length-scale`.
Drivers in `drivers/`, raw results in `results/` (not in git). All runs used the `dev`
environment (conda-forge PETSc), at most 4 processes, while the convection runs held the
machine (load average ~48).

## Status

| Step | State |
|---|---|
| 1. Coupled volume fields in `SNES_Stokes_SaddlePt` | done: tests pass, ordinary Stokes byte-identical |
| 2. Micromorphic coupling on the notch | done for the first matrix: ref 3 converges with NO rate strengthening (ξ = 0) at β = 0.1, l = 1 km, in 6 exact Newton steps; W stops shrinking with h |
| 3. 2-D Cosserat | done for the first matrix: converges at ref 3 with ξ = 0 in 4-5 steps; W converged in h (3.5 km at l = 0.5, ~4.1 km at l = 1) |

## Summary (end of the overnight run)

1. **Plumbing works and is guarded.** `add_coupled_field` / `add_coupled_dirichlet_bc`
   on `SNES_Stokes_SaddlePt`, pushed to `feature/shear-band-length-scale` (`003d3b95`,
   `6f0627ce`). Ordinary Stokes C is byte-identical to the base. The handoff test subset
   passes (41), plus the new `test_1070` (projection identity, Taylor slope 2 with a
   failing negative control, Cosserat shear layer at order 3). `test_1064`'s one red is a
   stale strict xfail (XPASS) that is also red on the base. It is flagged, not changed.
2. **Both continua regularise the notch, and both converge at ref 3 with ξ = 0**, where
   the handoff records that no route converged at ref 3, ξ ≤ 0.01. Every linear solve
   is exact LU, so the step count is the Newton count.
   - Micromorphic, β = H/η_bg = 0.1, l = 1 km: 5 / 6 / 6 steps at refs 1-3; W ≈ 2.5,
     2.2, 2.2 km. β = 0.01 (the handoff's value) is too weak to matter, and β = 0.05
     still needs ξ = 0.01 at ref 3. The handoff's β = 0.005 (D) was not run.
   - Cosserat, c = 1: 4-5 steps at every refinement; W converged at about 4.1 km
     (l = 1 km) and 3.5 km (l = 0.5 km), insensitive to ξ, c and the ω degree.
3. **The width is not simply proportional to l** in either model, at the two lengths
   tried. Next: l = 0.25 and 2 km, and re-measure the saved profiles with vertical
   cuts. The horizontal-cut estimator shows L/R spreads up to 0.9 km.
4. **Coarse → fine prolongation is not a speed-up**: the same solution in about 3× the
   Newton steps of a cold start from the viscous seed.
5. Not done: FMG / fieldsplit on the coupled system (only exact LU was exercised), and
   parallel runs (everything was serial).

![Band width, Newton steps and band profiles against refinement](figures/length_scale_summary.png)

Left: band width (mean of the left and right bands; the bar spans the two; converged
runs only) against mesh size, with the no-length-scale fit W = 31√(ξh). Middle: exact
Newton steps per run; × marks the plain solves that fail. Right: ε̇_II across the left
band at y = −15 km, refs 1-3. Made by `drivers/plot_length_scale.py`.

![The shear bands at ref 3](figures/shear_bands_ref3.png)

The bands alone: ref 3, ξ = 0, the strong layer above the notch, colour range clipped
so only the localised zones show (`render_strain_rate.py -uw_refs 3 -uw_view bands`).

![Strain-rate maps of the converged runs](figures/strain_rate_maps.png)

ε̇_II (log scale, shared across panels) for the ξ = 0 runs: models down, refinement
across, 64 km wide around the notch, full 30 km depth. The micromorphic bands are sharp
and keep their shape from ref 1 to ref 3; the Cosserat bands are wider and more diffuse.
At ref 1 the band edges are visibly mesh-faceted. Made by `drivers/render_strain_rate.py`
from the saved velocity fields (no re-solve).

## Step 1: plumbing

`SNES_Stokes_SaddlePt.add_coupled_field(field, F0, F1=None, momentum_flux=None)`
(`src/underworld3/cython/petsc_generic_snes_solvers.pyx`):

- residual `∫ F0 ψ + F1·∇ψ = 0` (PETSc sign convention), scalar or vector field, any
  degree and continuity; the natural condition is `F1·n = 0`;
- registered as a DM field after the multipliers (`_setup_discretisation`);
- Jacobian blocks for every pair touching a coupled field: its row against velocity,
  pressure and every coupled field, and the velocity and pressure rows against its
  column. One helper (`_coupled_jacobian_block`) gives the PETSc `[fc, gc, df, dg]`
  layout; identically zero blocks are registered as NULL, not compiled. Sources go
  through `_jacobian_source`, so Picard / Newton / continuation behave as for Stokes;
- `momentum_flux` is added to the Stokes `F1` template
  (`stress + _devss_flux() + _coupled_momentum_flux()`, zero without coupled fields);
- copy-back and the velocity complement reuse the extra-field index-set dict; a coupled
  field's index set takes every DOF per point (the pressure-keyed shortcut takes one);
- fieldsplit: split 0 = velocity + coupled fields, split 1 = pressure + multipliers
  (`_setup_block_fieldsplit_options`, now run when either list is non-empty). Only exact
  LU has been exercised; FMG on a multi-field split 0 is untested.

Guarding, proved two ways:

- **Byte-identical C.** `drivers/stokes_c_md5.py` fingerprints the generated C header of
  three ordinary solvers (isoviscous Picard, Drucker-Prager consistent Newton,
  block-constrained with two multipliers). Each bundle's C names carry a random
  five-letter prefix, which the fingerprint normalises (without that the md5 changes
  every run). Branch base `f57c2a27` and the branch agree:

  | solver | md5 (base = branch) |
  |---|---|
  | isoviscous | `655ff38ae57cbe9caa8a6d6845451539` |
  | Drucker-Prager Newton | `d5a5ba4b0355ddedc4244d631de42d1a` |
  | block-constrained | `4fc089cafa2adf72c6cedc6425b248c0` |

- **Tests**, `tests/test_1070_stokes_coupled_fields.py` (level_2, tier_b, reached by the
  `test_107*` glob in `scripts/test.sh`):
  1. one-way coupling `F0 = chi - edot_II`, `F1 = l² ∇chi` on a lid-driven Stokes flow
     equals `uw.systems.Projection` with `smoothing = l²` to 1e-8 relative;
  2. two-way coupling (`eta = 1 + chi²`): Taylor remainder slope > 1.9 on all three
     steps. Negative control: the same test with the frozen (Picard) tangent gives
     slopes 1.01 and 1.00 and fails, so it detects a wrong block;
  3. an ordinary Stokes solver has 2 DM fields and compiles only its own three residuals.

Handoff test subset on the branch: `test_1066_stokes_jacobian_layout`, `test_1061`/
`1062`/`1063` constrained, `test_1067_newton_cold_start`, `test_1010*`, `test_1011*`
and the new `test_1070`: **40 passed**. `test_1064` (constrained spherical shell; tier_c,
level_3, ~2 h on the loaded machine): 3 passed. `test_lu_subsolve_fieldsplit_constrained_
matches_default_nitsche_response` **failed**, and the run was cut off during the last
(xfail) test. For a block-constrained solver the change leaves the split options and the
generated C unchanged (md5 above), so this is probably pre-existing. It is being re-run
on the branch and on the base `f57c2a27` to settle it.
**Settled:** the failure is `XPASS(strict)`: the test is marked as a known failure and
now passes, on the branch AND on the base `f57c2a27` alike. So it predates this
work: the xfail marker is stale. Flagged with a `TODO(BUG)` at the marker; it needs
a maintainer decision.

## Step 2: micromorphic coupling on the notch

Driver `drivers/micromorphic_notch.py`: notch mesh1, 5e23, softmin/sqrt/onset, δ = 0.1,
ξ through `plastic_rate_strengthening`. χ is a P1 field with units 1/s;
`F0 = H (χ − m ė_II)`, `F1 = H l² ∇χ`. The yield stress is
`smooth_max(C_eff + sin φ p + m H (ė_II − χ), 0.02 C, 0.02 C)`. Exact Newton (MUMPS LU of
J itself), warm from the viscous seed with χ = 0. `-uw_taylor 1` adds a Taylor test of
the coupled Jacobian at the final iterate. Widths from `measure_bands` (horizontal cuts,
W_equiv). **A width from a run that did not converge is not a measurement**; such
widths are given only to show the trend.

Runs (l = 1 km throughout unless stated):

| run | ref | ξ | β = H/η_bg | result | Newton its | time | W_L / W_R (km) |
|---|---|---|---|---|---|---|---|
| A | 1 | 0.01 | 0.01 | converged | 7 | 477 s | 1.48 / 1.69 |
| A | 2 | 0.01 | 0.01 | DIVERGED_LINE_SEARCH at \|F\| = 3.89e-3 | 36 | 788 s | (0.91 / 1.06) |
| A | 3 | 0.01 | 0.01 | stalled at \|F\| = 9.2e-3 after 7 its; stopped | — | — | — |
| B | 1 | 0 | 0.01 | DIVERGED_LINE_SEARCH at \|F\| = 2.43e-2 | 35 | 429 s | (3.75 / 2.05) |
| A' | 1 | 0.01 | 0.05 | converged | 5 | 204 s | 2.07 / 2.34 |
| A' | 2 | 0.01 | 0.05 | converged | 6 | 255 s | 1.79 / 2.19 |
| A' | 3 | 0.01 | 0.05 | **converged** | 7 | 534 s | 2.20 / 1.60 |
| B' | 1 | 0 | 0.05 | converged | 7 | 114 s | 1.78 / 2.05 |
| B' | 2 | 0 | 0.05 | converged | 12 | 212 s | 1.89 / 1.43 |
| B' | 3 | 0 | 0.05 | DIVERGED_LINE_SEARCH at \|F\| = 2.18e-3 | 33 | 1861 s | (1.03 / 1.94) |
| C | 1 | 0.01 | 0.05, l = 0.5 km | converged | 6 | 223 s | 1.83 / 2.14 |
| C | 2 | 0.01 | 0.05, l = 0.5 km | converged | 8 | 416 s | 1.91 / 1.51 |
| C | 3 | 0.01 | 0.05, l = 0.5 km | converged | 10 | 686 s | 1.40 / 1.49 |
| B'' | 1 | 0 | 0.1 | converged | 5 | 180 s | 2.33 / 2.64 |
| B'' | 2 | 0 | 0.1 | converged | 6 | 263 s | 2.50 / 1.89 |
| B'' | 3 | 0 | **0.1** | **converged** | 6 | 347 s | 1.81 / 2.52 |
| C'' | 1 | 0 | 0.1, l = 0.5 km | converged | 6 | 104 s | 2.00 / 2.28 |
| C'' | 2 | 0 | 0.1, l = 0.5 km | converged | 8 | 173 s | 2.16 / 2.12 |
| C'' | 3 | 0 | 0.1, l = 0.5 km | converged | 9 | 486 s | 1.19 / 2.09 |
| E | 3, from ref 2 | 0.01 | 0.05 | converged | 20 | 1209 s | 2.20 / 1.60 |
| E | 3, from ref 2 | 0 | 0.1 | converged | 22 | 1082 s | 1.81 / 2.52 |

Controls without χ (`newton_exact_linear.py`, same law and solver):

| ref | ξ | result | its | W_L / W_R (km) |
|---|---|---|---|---|
| 1 | 0 | DIVERGED_LINE_SEARCH at \|F\| = 2.41e-2 | 23 | (3.09 / 3.93) |
| 1 | 0.01 | converged | 8 | 1.42 / 1.18 |
| 2 | 0.01 | DIVERGED_LINE_SEARCH at \|F\| = 2.34e-3 | 38 | (0.87 / 1.11) |

Reading so far:

- At β = 0.01 the coupling is too weak to matter. The shift H(ė − χ) peaks at 1.8e7 Pa
  in the strong layer at ref 1, against C = 1e8 Pa. At ξ = 0 the coupled and plain
  solves stall at the same residual (2.43e-2 vs 2.41e-2). The ref-2 widths are half the
  ref-1 ones, i.e. still tracking h.
- β = 0.05 (outside the handoff matrix; added because β = 0.01 does nothing measurable)
  is the working coupling. At ξ = 0.01 it **converges at every refinement, including
  ref 3**, in 5-7 exact Newton steps. The handoff records that no route converged at
  ref 3, ξ ≤ 0.01. The plain solve already fails at ref 2 in this configuration (the
  control above).
- The width stops tracking h. At ξ = 0.01, the mean of L and R is 2.20, 1.99, 1.90 km at
  refs 1, 2, 3: successive ratios 1.11 and 1.05, against √2 = 1.41 for the h-controlled
  W ≈ 31√(ξh) measured before (1.29, 0.91, 0.64 km). The L/R spread at ref 3 is 0.6 km,
  so the estimator is the limit on how well "constant" is established. The profiles are
  saved for re-measurement.
- The coupled tangent is exact on the notch: a Taylor test at the converged ref-2 state
  (ξ = 0.01, β = 0.05, l = 1 km) gives remainder slopes 1.26, 1.64, 2.02 over steps
  1e-2 to 1e-5. The direction is scaled to max|x|, so the first steps are outside the
  asymptotic range.
- l = 0.5 km (case C) also converges at every refinement, in 6-10 steps. Mean widths are
  1.99, 1.71, 1.45 km at refs 1-3 (ratios 1.16, 1.18), against 2.20, 1.99, 1.90 at
  l = 1 km (ratios 1.11, 1.05). The shorter length still converges in h, but not yet
  by ref 3: at l = 0.5 km the band spans fewer cells, which is the expected direction.
  W at ref 3 is still decreasing, so W(l) cannot be quoted as converged yet.
- **β = 0.1 needs no ξ at all.** At ξ = 0 it converges at refs 1, 2, 3 in 5, 6, 6
  steps. Mean widths are 2.49, 2.19, 2.16 km (ratios 1.13, 1.01). The micromorphic
  length alone regularises the notch.
- At ξ = 0, β = 0.1, l = 0.5 km also converges at every refinement (6, 8, 9 steps).
  The widths barely depend on l: mean 2.14, 2.14, 1.64 km against 2.49, 2.19, 2.16 at
  l = 1 km. Ref 3 at l = 0.5 has a large L/R asymmetry (1.19 vs 2.09). Two readings
  remain open: either W is set by β and the yield law more than by l, or the
  horizontal-cut estimator cannot resolve the difference. The saved profiles
  (`results/micromorphic/profiles_*.npz`) and fields allow re-measuring with vertical
  cuts without re-solving.
- Coarse → fine (case E): v, p and χ were prolonged from the converged ref-2 run with
  the local polyharmonic RBF (`uw.kdtree.KDTree.rbf_interpolator_local`, order 1, 6
  neighbours). Both runs reach the same solution as the cold start (widths agree to 6
  digits), but in 20 and 22 steps against 7 and 6. The prolonged band is a worse start
  than the viscous seed: the first coupled residual is 0.25, against 0.08 from the seed.
  A coarse band sits where the fine yield law is stiffest. So the cold start from the
  viscous seed is the better route; the solution is the same branch either way.
- At ξ = 0 the coupling converges at refs 1 and 2 (the plain solve fails at ref 1), but
  not at ref 3. ξ = 0.01 is therefore still needed at ref 3 at this β; the question is
  whether a stiffer coupling (larger β) removes that need.

## Step 3: 2-D Cosserat

Added `add_coupled_dirichlet_bc(conds, boundary, field)` (needed to hold ω = 0 on a
wall). Velocity and coupled-field essential BCs now share one registration helper.
Ordinary Stokes C is still byte-identical (the three md5s above, re-checked after
this change).

**Linear verification** (`test_1070`, `test_cosserat_shear_layer_converges_to_the_closed_form`):
a layer 0 < y < 1, η = η_c = 1, B = 2η l² = 0.02 (k = 10), u_x(1) = 1, ω = 0 on both
walls, the closed form imposed on the left wall and as a traction on the right. P2 ω,
P2 u:

| h | ‖ω − ω_exact‖ | ‖u_x − u_exact‖ |
|---|---|---|
| 1/8 | 1.094e-3 | 1.161e-4 |
| 1/16 | 1.504e-4 | 1.528e-5 |
| 1/32 | 1.931e-5 | 1.942e-6 |

Orders 2.86 → 2.96 (ω) and 2.93 → 2.98 (u): the skew stress, the moment balance and
their coupling are assembled correctly. ‖ω‖ = 0.465.

A trap found on the way, worth a docs fix: `add_natural_bc`'s value enters the
boundary residual as is (PETSc's f0), so for Stokes it is **minus** the traction σ·n.
The docstring just says "traction". Passing +σ·n gave a non-1D flow (u_y ~ 0.02).

Notch driver `drivers/cosserat_notch.py` (P1 ω first, η_c = c·visc_lin, the
generalised invariant replaces the model's ε̇_II). Runs below.

Notch runs (exact Newton, warm from the viscous seed, ω = 0 initially, natural
couple-stress condition on all walls):

| ref | ξ | c = η_c/visc_lin | l (km) | result | its | time | W_L / W_R (km) |
|---|---|---|---|---|---|---|---|
| 1 | 0.01 | 1 | 1 | converged | 4 | 230 s | 3.64 / 3.43 |
| 2 | 0.01 | 1 | 1 | converged | 4 | 107 s | 4.85 / 4.79 |
| 1 | 0 | 1 | 1 | converged | 4 | 231 s | 3.70 / 2.81 |
| 2 | 0 | 1 | 1 | converged | 4 | 99 s | 4.10 / 4.74 |
| 3 | 0.01 | 1 | 1 | converged | 4 | 308 s | 4.76 / 3.52 |
| 3 | 0 | 1 | 1 | **converged** | 4 | 277 s | 4.69 / 3.50 |
| 2 | 0.01 | 0.5 | 1 | converged | 4 | 186 s | 4.45 / 4.65 |
| 2 | 0.01 | 1 (P2 ω) | 1 | converged | 4 | 131 s | 4.83 / 4.78 |
| 1 | 0.01 | 0.01 | 1 | converged | 6 | 216 s | 1.67 / 1.81 |
| 2 | 0 | 1 | 0.5 | converged | 5 | 121 s | 3.39 / 3.54 |
| 3 | 0 | 1 | 0.5 | **converged** | 5 | 428 s | 3.49 / 3.43 |

- **The Cosserat coupling converges at every refinement, ξ = 0 included, in 4 exact
  Newton steps** (ref 3, ξ = 0: 277 s). At c = 1, l = 1 km the mean width is 3.26, 4.42,
  4.10 km at refs 1-3 (ξ = 0) and 3.53, 4.82, 4.14 km (ξ = 0.01). So ξ does not matter,
  ref 1 under-resolves the band, and W settles near 4 km ≈ 4 l. The band is wider than
  the micromorphic one at the same l (about 2 km): the two lengths are not the same
  parameter.
- At l = 0.5 km the width is converged in h: mean 3.46 km at ref 2 and at ref 3. Halving
  l narrows the band only from about 4.1 to 3.5 km, so W is not proportional to l. It
  looks like W ≈ W₀ + O(l), with W₀ set by the notch geometry and the yield law. Two
  points cannot separate these; l = 0.25 and 2 km would.
- P2 ω gives the same width as P1 at ref 2 (4.83 / 4.78 vs 4.85 / 4.79). c = 0.5 changes
  W by under 10% (4.45 / 4.65), so the width is set by l, not by η_c.
- c → 0 recovers the plain problem continuously: at c = 0.01 the width (1.67 / 1.81)
  moves toward the plain 1.42 / 1.18. The strong layer yields (η_eff from 7.3e21 to
  1.3e23 Pa s against η_bg = 1e23).
