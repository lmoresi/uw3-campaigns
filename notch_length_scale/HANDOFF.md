# Handoff: a formal shear-band length scale for the notch (2026-10-08, overnight, unsupervised)

Louis's decision (2026-10-08): the viscoplastic notch (Spiegelman) fails at refinement 3 because the band has no length
scale and keeps collapsing; give it one. Try BOTH (1) the micromorphic / gradient-plasticity penalty coupling and (2)
the simplest 2-D Cosserat continuum, on shared plumbing. Micromorphic first (smallest step, proves the plumbing).

## Rules (read first)
- Read `docs/developer/UW3_STYLE_CHARTER.md` and the repo `CLAUDE.md` before writing code.
- Branch: `feature/shear-band-length-scale` (pushed; picard-warmup-791 + development merged). Work in a worktree of it.
  Commit and PUSH to that branch only. No PR, no issues, never development/main. Attribution line in every commit:
  `Underworld development team with AI support from Claude Code`.
- Environment: `runtime` (or `dev`). NEVER an `amr*` env, NEVER build PETSc. `./uw build` after every source change;
  never `pip install -e`. Never `git stash` (WIP commits).
- Hyperion is busy with convection runs: at most 4 processes at a time, serial runs.
- Existing solvers must stay byte-identical: every new path guarded (`if self._coupled_fields:`), like the
  block-constraint multipliers. Prove it: generated C header md5 for an ordinary Stokes solve unchanged vs the branch
  base, and the Stokes test subset passes (`tests/test_1066_stokes_jacobian_layout.py`, `test_106*constrained*`,
  `test_1067_newton_cold_start.py`, `test_1010*`/`test_1011*` Stokes tests).
- Report: write `notch_length_scale/REPORT.md` here (uw3-campaigns, push to main) as you go — what works, numbers,
  what failed and why. Keep results out of git (`results/`).

## What is already measured (do not re-test)
Notch, mesh1, 5e23, softmin/sqrt/onset, delta 0.1, eta_reg = xi*eta_bg. h_min = 0.172 / 0.086 / 0.043 km at ref 1/2/3.
- Band width W ~ 31 sqrt(xi h) km: eta_reg is NOT a length scale (steady viscous problem, no elasticity).
- Ref 3, xi <= 0.01: NO route converges (line search, trust region, warm start from ref 2, 4/20-stage homotopy,
  pseudo-transient continuation, partial Newton) even with exact LU: the exact Newton step overshoots ~100x along the
  band's soft mode. Tangent is exact (Taylor slope 2).
- Exact-LU trap: set `stokes.saddle_preconditioner = 0` and factor J itself (`ksp.setOperators(J, J)`, preonly, lu,
  mumps) — see `drivers/newton_exact_linear.py`. Otherwise LU factors the Pmat's 1/eta pressure-mass block.
- Tried earlier and failed (do not rebuild): (a) smoothed edot fed to the yield law as lagged data -> Picard only;
  (b) an independent Helmholtz field ebar with eta = tau_y/(2 ebar) solved coupled -> cross term
  -tau_y edot/ebar^2 spans the whole viscosity contrast, non-symmetric, block preconditioner failed.
  (c) gradient damage on the cohesion: does not regularise (the length must enter the PLASTICITY).

## Step 1 — plumbing: extra coupled volume fields in `SNES_Stokes_SaddlePt`
File `src/underworld3/cython/petsc_generic_snes_solvers.pyx`. Follow the multiplier pattern (`self._multipliers`):
- `__init__`: `self._coupled_fields = []` (+ their F0/F1/momentum-flux contributions).
- Public `add_coupled_field(field, F0, F1=None, momentum_flux=None)` (on the saddle-point class or `SNES_Stokes`):
  residual of the field `∫ F0 ψ + F1·∇ψ = 0` (PETSc sign convention, same as Poisson F0=-f); `momentum_flux` is a
  (dim,dim) term ADDED to the Stokes F1 (Cosserat skew stress needs it; `SNES_Stokes.F1` template is
  `self.stress + self._devss_flux()` in `systems/solvers.py` — add the hook there). Set `field._solver_field_name`,
  `self.fields[name] = field`, `is_setup = False`, `_needs_function_rewire = True`.
- `_setup_discretisation`: register a PETSc FE per coupled field after the multipliers (its degree, continuity,
  num_components), `field._solver_field_id = dm.getNumFields()`.
- `_setup_pointwise_functions`: residual fns for each field; Jacobian blocks for EVERY pair touching a coupled field:
  (0,a), (a,0), (a,1), (a,a) [(1,a) is zero], through `self._jacobian_source(...)` like F0_jac (so Picard/Newton/
  continuation modes and the sqrt guard behave). Write one helper giving PETSc layout for a (row f0, row f1) and a
  column field (values c[gc], gradient grad_c[gc,dg]):
  G0[fc,gc]=d f0[fc]/d c[gc]; G1[fc*Ncg+gc, dg]=d f0[fc]/d grad_c[gc,dg]; G2[fc*Ncg+gc, df]=d f1[fc,df]/d c[gc];
  G3[fc*Ncg+gc, df*dim+dg]=d f1[fc,df]/d grad_c[gc,dg]  (matches the existing uu/up loops; use `diff_wrt_field`;
  column gradient = `field.sym.jacobian(mesh.CoordinateSystem.N)`). Register NULL for all-zero blocks.
  `prim_field_list` = [u, p] + multipliers + coupled fields (ORDER = DM field order).
- `_setup_solver`: `PetscDSSetResidual(ds, fid, f0, f1)`, `PetscDSSetJacobian` AND `...Preconditioner` for each block.
- `_ensure_local_field_index_sets`: add coupled fields to the extra-field IS dict (`_multiplier_is`, keyed by name;
  copy-out and the velocity complement then work). Its `get_local_field_is` keys continuity on the PRESSURE — for a
  coupled field take all `dof` entries per point.
- Fieldsplit: `pc_fieldsplit_type schur` needs 2 splits. Generalise `_setup_block_fieldsplit_options`: split 0 =
  velocity + coupled field ids, split 1 = pressure + multipliers; run it when either list is non-empty. For the
  experiments use exact LU (no fieldsplit) first; FMG on the 2-field split 0 is a later question.
- Tests (new file, tier/level marks, reachable from `scripts/test.sh`): (i) one-way: field with F0 = chi - e(u),
  F1 = l^2 grad chi on a solved Stokes flow equals a separate `uw.systems.Projection` with smoothing l^2; (ii) Taylor
  test (slope 2) of the full coupled Jacobian on a small mesh with two-way coupling; (iii) ordinary Stokes C-source
  md5 unchanged.

## Step 2 — micromorphic (gradient plasticity) on the notch
Field chi (P1 continuous scalar). Moduli: H (a viscosity, Pa s) and A = H l^2. Potential adds (H/2)(e-chi)^2 + (A/2)|grad chi|^2, e = edot_II(u).
- chi equation: F0 = H (chi - m e), F1 = A grad chi  =>  chi - l^2 lap chi = m e  (m = strong-layer mask `S["mat"].sym[0]`,
  so the 100x rate jump at the weak inclusion does not drive chi).
- Yield stress shifted by s = H (e - chi) (= -A lap chi): rebuild in the driver
  `sigma_y = uw.maths.smooth_max(S["C_eff"] + sin(phi) p + m*H*(e - chi), smin, smin)`, smin = 0.02*C (positive floor:
  the shift lowers the flank yield stress by up to H chi), `yield_full = m*sigma_y + (1-m)*S["yield_none"]`,
  `cm.Parameters.yield_stress = yield_full`; xi via `cm.Parameters.plastic_rate_strengthening` as in the drivers.
  e = `stokes.Unknowns.Einv2` (or `cm._strainrate_inv_II`).
- Why it should work: cross blocks are -H n (n = edot/2e), scaled by H not eta; eliminating chi adds stiffness 0 for
  modes longer than l and ~H for modes shorter than l — exactly the collapsing soft mode.
- Scales (non-dim, eta_bg = 1): tau_y ~ 0.6, band rate ~ 30 at W = 1 km => H ~ tau_y/e_band ~ 0.02. Use
  H = beta*eta_bg, beta in {0.005, 0.01}; l in {0.5, 1.0} km (non-dim l = l_km/30) = 3-23 cells across refs 1-3.
- Solve: Newton (`consistent_jacobian=True`), exact LU as in `newton_exact_linear.py`, cold from the viscous seed
  (chi = 0 initially is fine). Measure per run: converged?, Newton its, seconds, W_L/W_R (`measure_bands`, W_equiv_km),
  chi range, min yield stress.
- Matrix, in priority order: (A) l = 1 km, beta 0.01, xi 0.01, refs 1,2,3 — the key question: does W stop depending
  on h, and does ref 3 converge at xi = 0.01 (where nothing did)? (B) same at xi = 0 (C) l = 0.5 km (D) beta 0.005.
  (E) coarse->fine: prolong v, p, chi from ref 2 (`rbf_interpolate(order=1, nnn=6)`) and compare with cold at ref 3.

## Step 3 — 2-D Cosserat
Field omega (micro-rotation rate, scalar; try P1 then P2). W = 1/2 (du_y/dx - du_x/dy) (continuum spin), E = [[0,-1],[1,0]].
- Momentum flux gains the skew stress  2 eta_c (W - omega) E  (pass as `momentum_flux`).
- omega equation: F0 = 4 eta_c (omega - W), F1 = m = 2 eta_eff l^2 grad omega  =>  -div(m) + 4 eta_c (omega - W) = 0.
  The coupled Jacobian is symmetric for the linear law (check it).
- Plasticity: generalised invariant e_gen^2 = edot_II^2 + (1/2) l^2 |grad omega|^2; eta_eff = tau_y/(2 e_gen) (+eta_reg),
  soft-min with eta_bg, applied to BOTH the deviatoric stress and the couple stress (prototype: set
  `cm._strainrate_inv_II.sym` to e_gen before the first solve). eta_c stays unyielded: eta_c = c * visc_lin, c in {0.5, 1}.
- Verify the LINEAR law first: shear layer 0<y<h, u_x(0)=0, u_x(h)=U, omega=0 on both walls, uniform eta, eta_c,
  B = 2 eta l^2: sigma_xy = T const, (eta+eta_c) u' + 2 eta_c omega = T, omega'' - k^2 omega = k^2 T/(2 eta),
  k^2 = 4 eta_c eta / (B (eta+eta_c)), omega = -T/(2 eta) [1 - cosh(k(y-h/2))/cosh(kh/2)]; check convergence in h.
- Then the notch matrix as in step 2 (l = 1 km first).

## If blocked
Write what blocked you and the evidence into REPORT.md, push, and stop rather than guess. Message the laptop session
when done (it may be asleep; the report on GitHub is the deliverable).
