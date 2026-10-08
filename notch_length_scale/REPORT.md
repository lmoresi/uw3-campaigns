# Report: a shear-band length scale for the notch (overnight, Hyperion, 2026-10-08)

Work for `HANDOFF.md`. Code: underworld3 branch `feature/shear-band-length-scale`.
Drivers in `drivers/`, raw results in `results/` (not in git). All runs used the `dev`
environment (conda-forge PETSc), at most 4 processes, while the convection runs held the
machine (load average ~48).

## Status

| Step | State |
|---|---|
| 1. Coupled volume fields in `SNES_Stokes_SaddlePt` | done: tests pass, ordinary Stokes byte-identical |
| 2. Micromorphic coupling on the notch | in progress: at β = 0.05, l = 1 km, ref 3 converges at ξ = 0.01 and W stops shrinking with h |
| 3. 2-D Cosserat | not started |

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

Controls without χ (`newton_exact_linear.py`, same law and solver):

| ref | ξ | result | its | W_L / W_R (km) |
|---|---|---|---|---|
| 1 | 0 | DIVERGED_LINE_SEARCH at \|F\| = 2.41e-2 | 23 | (3.09 / 3.93) |
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
- At ξ = 0 the coupling converges at refs 1 and 2 (the plain solve fails at ref 1), but
  not at ref 3. ξ = 0.01 is therefore still needed at ref 3 at this β; the question is
  whether a stiffer coupling (larger β) removes that need.
