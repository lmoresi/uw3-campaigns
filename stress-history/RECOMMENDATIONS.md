# Viscoelastic stress history: where it stands and what to do

H7 (the stress-history desk, a Claude session on a 96-thread Linux workstation), 2026-11-16.
Code read at `development` fafbecb8. No code or defaults were changed. Sources are named at each claim,
and anything without a measurement behind it is marked **unmeasured**. "Doc" means
`docs/developer/subsystems/stress-transport.md` on development, and "guide" means
`docs/developer/guides/transport-schemes.md` (status: draft, "rulings to be confirmed").

## Summary for Louis

1. **The default stress history on development does not carry the stored stress.** The nodal
   semi-Lagrangian history (`stress_transport="semi_lagrangian"`, the Stokes default) refreshes its
   commit snapshot *before* the trace-back (`ddt.py:3990`, with the trace at 4044). So the stored
   stress is rebuilt every step from the field that has not moved. A session found this on
   2026-10-18. The fix has been on a pushed branch since then, but it is not on development.
   **Confirmed by H7 on 2026-11-16 (serial, fafbecb8)** with the port branch's rotation test
   (`test_1102`, a stored stress turned 0.5 rad by eight steps of rigid rotation, 1/16 simplex box).
   The table gives the relative error against the rotated stress and against where it was made:

   | `stress_transport` | vs rotated | vs unmoved |
   |---|---|---|
   | `semi_lagrangian` **(default)** | 1.538 | **0.000** |
   | `none` | 1.538 | 0.000 |
   | `integration_point` | 0.291 | 1.550 |
   | `forward` | 0.234 | 1.559 |
   | `eulerian` | 0.086 | 1.553 |
   | `lagrangian` | 0.036 | 1.548 |

   The default behaves exactly like `"none"`: it does not transport the stress at all. The probe
   script and its output are in `stress-history/probe/`.
2. **Every measurement of the nodal history from before 2026-10-18 was taken on that defect.** That
   includes #735's "50% too much stress at the wall". The ruling built on it (the guide's
   2026-09-11 "a flux history lives on the integration points") is right in direction, but its
   evidence has to be re-measured.
3. **There was a move toward SUPG for the stress, but it was a preference, not a decision.** You
   said on 2026-10-06, in the cylinder campaign session: "SUPG is the recommendation for VE models,
   in my view. Lagrangian and semi-Lagrangian are noisy." On 2026-10-18 you ruled more generally:
   "Choose best of the time integration strategies by default … default should be the most
   versatile strategy … Consider devss on by default. SUPG needs devss for most settings too." A
   defaults study was started on a #800 build to settle it. It stopped for three reasons:
   - it found the defect in item 1, after which every nodal comparison was void;
   - hyperion's system disk failed the same day, and the study's data, about 70 of 530 runs, was
     lost;
   - #800, which the defaults change was to follow, went idle on 2026-10-12.

   Nothing on GitHub records a decision to move the stress default to SUPG. SUPG is the default
   for scalar transport and Navier–Stokes momentum (#688, #689), and that part was acted on.
4. **No scheme is yet clean enough to be the single default.**
   - The grid (SUPG) history diverges on Waters and King at every step (#749, open).
   - The integration-point history rings below Courant 1 unless store smoothing is on (#737), and
     it does not follow a moving mesh.
   - The particle history NaNs on the cylinder (#738) and differs from serial at np ≥ 4 (#797).
   - Every trace-back scheme can read across a fault (#871).

   The recommendations below therefore stage the change: fix, then re-measure, then switch.

## 1. The schemes on development

Selected with `solver.stress_transport` before the constitutive model is assigned
(`solvers.py:579`). The default is `"semi_lagrangian"` (`solvers.py:612`).

| `stress_transport` | class (`ddt.py`) | storage, carried by | solvers that can use it | stabilisation it needs |
|---|---|---|---|---|
| `semi_lagrangian` **(default)** | `SemiLagrangian` (2792) | continuous P1 at nodes, RK2 trace-back from nodes nudged 0.1% toward the cell centroid (3706) | Stokes VE, NavierStokes (composed), NavierStokesSLCN (always nodal, order 2) | none in use: its `smoothing` is forced to 0 at the commit (1225) |
| `integration_point` | `IntegrationPointSemiLagrangian` (4945) | P1 snapshot, sampled by tracing back every quadrature point | Stokes VE, NavierStokes | Courant ≈ 1, or `store_smoothing` 0.07 below it (doc); default 0 |
| `forward` | `ForwardSemiLagrangian` (5560) | per-cell discontinuous-P1 fit of forward arrivals | Stokes VE, NavierStokes; order 1; no manifold; **refuses a moving mesh** (5945) | `flux_smoothing = 0.023 h²` (doc); the global reconstruction that fixes #811 is only on #800 |
| `lagrangian` | `Lagrangian` (4163) | solver-owned swarm, cells proxy | Stokes VE, NavierStokes; BDF order 1 | none (an inflow value, #783, fix on unmerged #785) |
| `eulerian` | `EulerianSUPG(transport_on_update=True)` (2098) | continuous P1, implicit SUPG transport solve per level per step | Stokes VE, NavierStokes, **ThinSheet default** (`thin_sheet.py:305`) | SUPG (on, `supg_weight=1`); DEVSS (doc: "use it with the grid history"); **DEVSS is off by default** |
| `none` | `EulerianSUPG(transport_on_update=False)` | continuous P1, never transported | Stokes VE, ThinSheet | none: valid only while displacement per step ≪ h |
| (forward from nodes) | only on PR #800 | | | |

Other facts that bear on the recommendations:
- **DEVSS** (`devss_viscosity`, `solvers.py:1977`) is lagged on a time-stepping VE run: the lag
  loop "exits after its check solve" (`solvers.py:2254`), so $\bar{\mathbf D}$ is a step behind.
  The 2026-10-18 study measured this lag on Waters and King at Courant 0.4, RMS centre error with
  DEVSS off → on (session plan of 2026-10-18; the data is lost):

  | integrator | DEVSS off | DEVSS on |
  |---|---|---|
  | BDF-1 | 0.0098 | 0.045 |
  | ETD-1 | 0.011 | 0.045 |
  | ETD-2 | 0.004 | 0.043 |

  That is about four times worse with DEVSS on.
- **Integration-point history on a moving mesh:** the docstring says ALE and old-frame trace-back
  are "not here (yet)" (4974). It does not raise, so on a deforming or free-surface mesh it runs
  without the mesh-velocity correction. **Unmeasured.**
- **Log-conformation and the deformation step** (PR #795, merged) are accepted by every flavour
  (doc). They are 2-D, first order and upper-convected only, and `NavierStokesSLCN` refuses them.
  **Known failure on development fafbecb8:** with the log-conformation history, decoding the stress
  after a solve (`Stokes.tau`) raises. The error is a shape mismatch, (15,) into (45,), in the
  `Tensor_Projection` into the SYM_TENSOR decode variable. W1 (the integration session) found it on
  a StructuredQuadBox 4x2, VEP order 1, ETD, upper-convected, after one solve, and is fixing it in a
  small PR. Until then, read the carried stress through `constitutive_model.stress_star`. Whether
  this depends on the flavour is **unmeasured**.

### What is measured

Waters and King (Maxwell start-up of Poiseuille flow) has $u\cdot\nabla\sigma \equiv 0$, so it
tests the store-and-commit cycle, not the trace (doc).

| scheme | Waters and King | DFG cylinder (Wi 1, #735 setup) | cylinder, Re 100, Wi 0.5 (Oct. campaign) | Maxwell box / rotation | parallel | known failures |
|---|---|---|---|---|---|---|
| nodal (default) | 1/32, Δt 0.01: settles 0.5054 vs 0.5055 (#749 comment). **On the defect**: converges as the step falls. The port of the fix converges worse: 2.42e-3 → 1.97e-3 vs 7.8e-4 → 3.9e-4 (#1009) | ~30% above grid/IP in near-wall $\|\tau_{II}\|$ at every h (.0099 vs .0075 at 1/40, #735 comment 09-14). **On the defect** | blew up with both momentum transports (peak 1.9 → 24). **On the defect** | rotation: 1.538, bit-identical to `none` (H7 probe, development); 0.285 with the fix (review at adb20e9d) | np1 vs npN 1.6e-3 on the unclamped scalar SLCN path (#1153 review; not the stress); equal to 1e-7 on #800 only | the defect; wall excess (#735, to re-measure); fault crossing (#871); TI-fault cell-scale mode at Courant 0.8 (2026-10-18, on the defect) |
| integration point | rings, then diverges as Δt falls without smoothing (#737: 0.50493 / 0.49038 / 0.37367 / diverged at Δt .04/.02/.01/.005); c = 0.07 holds it at 0.5% on the peak | agrees with grid to 0.2% on the stress norm, converging 3–4× per refinement (#735) | res 40, Courant 1: drag −0.79 vs SUPG res 80; Courant 2 with SL momentum +0.03, hangs at Courant 4 (campaign transcript, 10-05/08) | rotation 0.291 (H7 probe; same in review at adb20e9d); Maxwell box 0.851356 / 0.863858 at order 1 / 2 vs exact 0.864665, the same as every flavour (a29a5b1f) | 1e-6 of serial at np 3–6 on #800 (test_1066); **unmeasured on development** | low-Courant mode (#737, mitigated); admissible to Wi 0.6 on the cylinder with `max_elastic_timestep` (#768, doc) |
| grid (SUPG) | **diverges at every Δt**: t 1.41 / 2.34 / 2.56 / 3.20 for Δt .01–.08 (#749) | agrees with IP (#735) | converges, order 1.98 in drag over res 20/40/80 (4.593, 4.227, 4.134); res 80 St 0.277 | rotation 0.086 (H7 probe) | "same answer on any partition" (`solvers.py:597`); **no number found** | #749; without DEVSS, 80,000 inner solves at Wi 0.4 on the cylinder (doc); Re 200 lift falls with resolution (overnight report 2026-10-05, `ve_cylinder_demo/reports/`) |
| forward (IP launch) | diverges at t 2.4 unsmoothed; with c = 0.023: 0.9543 at t 1, 0.5185 at t 6.5 (doc on #800) | **unmeasured** | per-cell fit "tau_II = 4 where nothing above 0.8 arrived", fails at t 5.2 (#811); global fit on #800: runs to t 8, 5% excursion | half-turn Gaussian 2.00e-2 (#800); rotation 0.234 (H7 probe) | np 2 test_1062 | #811 (fixed only on #800) |
| forward from nodes (#800 only) | **unmeasured** | **unmeasured** | res 80: drag 4.208 vs SUPG 4.194; lift amp 0.270 vs 0.306; drag fluctuation 0.060 vs 0.006 | Gaussian 1.78e-2 vs backward nodes 2.52e-2 (#800) | equal to serial to 1e-6 (#800) | 10× drag noise |
| particles | **unmeasured** | NaN at the first solve (#738) | res 40 drag +0.01, noisy; three SNES failures at t 2.4 | Gaussian 2.04e-2 (#800); rotation 0.036, the best (H7 probe) | differs from serial at np ≥ 4 by 1.2e-5 (#797) | #738, #797, #783 |
| none | n/a | n/a | n/a | n/a | n/a | wrong once material moves a cell |

On a ThinSheet fault, the nodal history gave a period-2 slip-rate oscillation and patchy stress,
"both gone with the grid (Eulerian SUPG) history" (#871). A traced-back history read "a quarter of
the slip rate on the second step" (doc).

## 2. Decided before, not acted on

| when, where | what was decided | acted on? | what stopped it |
|---|---|---|---|
| 2026-09-08, #688/#689 | SUPG is the default manager for scalar AdvDiffusion and NavierStokes momentum | **yes** | — |
| 2026-09-11, guide "Stress histories" (#735) | "a flux history lives on the integration points (or on the grid, with DEVSS opted in)" | **no**: Stokes VE still defaults to nodal; the guide stays draft | the open ruling "whether a nodal history should ever be offered for a flux quantity"; then the defect voided its evidence |
| 2026-09-13, #737 | run the IP history at Courant ≈ 1; refine h and Δt together; the grid history is the reference for a Δt sweep | as documentation only | — |
| doc, "The recommended configuration" | IP history, `max_elastic_timestep(safety=0.3)`, `store_smoothing` 0.07, DEVSS off | **no**: `store_smoothing` defaults to 0 and the transport to nodal | never proposed as a default change |
| 2026-10-06, cylinder campaign session (Louis) | "SUPG is the recommendation for VE models, in my view" | **no** | #749 open; the study below |
| 2026-10-18, session plan (Louis) | best integrator and "most versatile" SL by default; consider DEVSS on by default; "SUPG needs devss for most settings" | **no**: the study was started on a #800 build, "Defaults change lands after #800" | the defect (study halted: "No defaults change until you've seen that comparison"); disk failure lost the data; #800 idle since 2026-10-12 |
| 2026-10-18 to 10-23 | snapshot-order fix, `bugfix/backward-nodes-snapshot-order` (adb20e9d), with an adversarial review | pushed, **no PR**; 1106 behind development | — |
| 2026-11-06 to 11-08 | port to development, `bugfix/stress-snapshot-order-735` (913694e8) | **on hold** (Louis, 2026-11-08) | #1009: the port's nodal history is biased on Waters and King |

**The October "unpushed commit"** on `bugfix/backward-nodes-snapshot-order` is no longer only
local. On 2026-11-16 the local branch and origin are both at adb20e9d. The worktree has no diff, and
the 2026-10-20 rescue copy holds only mesh caches. Nothing needs pushing.

## Update, 2026-11-20: what the code work measured

Louis ruled on 2026-11-19 (DEV-HUB): "Fixes, land them. OK to change defaults, this is not widely used yet." H7 then measured A1 before opening it, and **A1 no longer stands as written**.

**PRs:**
- **B1 is PR #1231.** The nodal history now carries its stress. On the rotation test it scores 0.285 against the rotated stress; development scores 1.538 and is identical to `"none"`. #1009's Waters and King bias is the trace's own error: with the trace velocity forced to $(u,0)$ the fixed history reproduces development, and the carried nodal history does not converge there at fixed Courant number. `test_1054` had relied on the defect and now pins `"none"`.
- **A2 is PR #1232**, stacked on #1231: the fault guard. The docs PR is #1233, stacked on #1232.

**A1 measurements** (serial, development + #1231 + A1):

| case | grid | nodal (fixed) | IP + 0.07 | IP, no smoothing |
|---|---|---|---|---|
| DFG cylinder, Re 100, Wi 0.5, β 0.5, res 20: drag at t 2 (grid reference 4.593 at res 20, 4.134 at res 80) | 4.505 | 4.985 | 3.046 | 3.370 |
| Waters and King, 1/16, Δt 0.0125: error at t 2 | diverges (#749) | 2.3e-3 | 1.2e-2 | 6.6e-4 at t 2; rings by t 6.5 |
| Maxwell box, order 1 / 2 | 1.54e-2 / 9.3e-4 | the same | the same | — |

**Row (b), grid + DEVSS on Waters and King** (development's lagged DEVSS, same settings):

| $\eta_a$ | 1/16, Δt 0.0125 | 1/32, Δt 0.00625 |
|---|---|---|
| $\eta/4$ | diverges at t 2.25 | diverges at t 1.625 |
| $\eta$ | diverges at t 3.25 | t 2: 0.75601 (error 3.5e-2), $\max\lvert v_y\rvert \approx 1$ and growing |

DEVSS does not rescue the grid history on Waters and King; #749 stands.

**What this changes in the recommendations:**
- The smoothed integration-point history is a quarter to a third low on the cylinder's drag. Even unsmoothed it is a quarter low, as the October campaign also saw at res 40.
- The subsystem doc's statement that smoothing "costs nothing" when the solvent fraction is large does not hold here.
- The smoothing's cost on Waters and King is about 2% at 1/16, falling as $h^2$. The "0.5%" in A1 below is the 1/32 figure.

The default is back with Louis. The options are:
- (a) keep the fixed nodal history;
- (b) the grid history, closest on the cylinder but with #749 open;
- (c) integration point, as ruled.

## 3. Recommendations

### A. Default and documentation changes (no new code)

| # | recommendation | reason and evidence | closes |
|---|---|---|---|
| A1 | **(Superseded by the 2026-11-20 update above.) Stokes VE: change the default to `integration_point`, with `store_smoothing` defaulting to 0.07.** Keep the nodal history selectable. | It is the only flavour with an acceptable result on all three benchmarks: Waters and King with smoothing (#737), the cylinder to Wi 0.6 (#768, doc), and the Maxwell box (a29a5b1f). The doc already recommends exactly this. Smoothing costs 0.5% on the peak and nothing when the solvent fraction is large (doc). The current default does not transport. | the 2026-09-11 guide ruling; #737 in practice |
| A2 | **When the mesh has split-node faults** (`mesh._fault_point_pairs` non-empty), **default to `eulerian`, or to `none` when the step moves ≪ h; refuse the trace-back flavours** with a message citing #871. | Standing rule (DEV-HUB, 2026-11-15). ThinSheet already does this, and the grid history removed the oscillation (#871). The check is one test at history creation: `_create_stress_history_ddt`, `cython/petsc_generic_snes_solvers.pyx:5730`. This is a guard, not a fix. | #871's exposure on Stokes VE (the full fix is B3) |
| A3 | **NavierStokes (composed): keep SUPG momentum. Give its stress history the A1 default for now. Move it to `eulerian` + DEVSS once B2 lands.** | Your SUPG preference is best supported on the cylinder: second-order drag convergence, and agreement with IP to 0.2% (#735). It is not ready while #749 is open and DEVSS is lagged. | — |
| A4 | **ThinSheet: keep `eulerian`.** | Fault-safe, measured (#871, `thin-sheet.md:126`). | — |
| A5 | **NavierStokesSLCN: leave as is, and document it as the legacy all-nodal path.** It inherits the defect until B1 lands. | It has its own two nodal histories (`solvers.py:5547`). #742 (one-step-stale `psi_star[0]`) is fixed only on #800. | — |
| A6 | **Docs:** promote the guide out of draft with the rulings above. Fix the inconsistencies the code read found: | Readers get contradictory advice today. | — |
| | - the guide's adjoint claim contradicts `SemiLagrangian._adjoint_support`; | | |
| | - `vep-transverse-isotropy-faults.md:30` says the history is particles; | | |
| | - the SLCN docstring's `clamp` description; | | |
| | - the guide's table omits forward and `lagrangian`; | | |
| | - the "nodal converges as the step falls" line, until it is re-measured. | | |
| A7 | **Mark every pre-2026-10-18 nodal number** in the doc, the guide and #735 as measured on the defect. | Otherwise the next reader repeats the error. | — |

### B. Changes that need code

| # | recommendation | reason and evidence | closes |
|---|---|---|---|
| B1 | **Land the snapshot-order fix first, as a minimal PR.** It moves `_refresh_source_snapshot()` to after the carry. Settle #1009 with it rather than block on it. | The default history does not transport today (item 1). #1009's bias appears on Waters and King, where $u\cdot\nabla\sigma\equiv 0$. One hypothesis: the non-transporting history was *exact* there by accident, and the port exposes the nodal trace's real interpolation error. #1009 measured max $\|v_y\|$ rising from 2.6e-4 to 1.2e-3. **Unmeasured**: open question Q2. | #1009, then #735 (after Q1) |
| B2 | **Make DEVSS iterate within the VE step instead of lagging it,** then re-test the grid history on Waters and King with DEVSS on. | The lag costs about 4× on Waters and King (table above). #749 has not been run with DEVSS; the doc says the grid history needs it. | #749, if Q4 confirms |
| B3 | **The no-crossing rule in code.** Clip each RK2 segment at fault facets in `CharacteristicTrace.departure_points` (`ddt.py:2714`; it clamps only to the domain with `return_coords_to_bounds`). Make the foot evaluation side-aware in `SemiLagrangian._sample_history_at_departure` (3844) and `IntegrationPointSemiLagrangian._fill_slots` (5429), down through `global_evaluate` (`functions_unit_system.py:1376`) to DMLocatePoints. For the forward fit, assign arrivals by side in `ForwardSemiLagrangian._fit_arrivals` (5828). | Louis, 2026-11-15, on #871. A point within about h/2 of the slit evaluates on either side (#871). With B3, A2's refusal becomes a choice again. | #871 |
| B4 | **Split #800 and close it.** Port, as separate PRs: | It is 1206 commits behind, `dirty`, and keeps the defective snapshot order (DEV-HUB). Its update placement conflicts and "needs the author" (comment 2026-10-06). The #682 clamp fix has already landed separately (#1153). | #742, #811; partly #797 |
| | (a) the serial-equality fixes: projections at CG/Jacobi 1e-12, and removing the centroid nudge, which "gave a velocity to a node on a no-slip wall" and is the other candidate for #735. W1 measured it on #1237's empty-rank triangle, serially: the SLCN history record moves a static field by 7.5e-5 per record (no flow, Dirichlet $x + y$). Planned as a small PR after #1231 lands: remove the nudge, or nudge only a node that sits on a facet, with a test that a static field stays put to round-off; | | |
| | (b) the global reconstruction for `forward` (#811); | | |
| | (c) the SUPG memory term in the residual; | | |
| | (d) the SLCN stress-history mixin (#742); | | |
| | (e) FENE-P. | | |
| | Park forward-from-nodes and the trace/launch renaming. Forward from nodes gains about 30% on a Gaussian (1.78e-2 vs 2.52e-2) but shows 10× the drag noise on the cylinder. The renaming is API churn best done after the default settles. | | |
| B5 | **Integration-point history on a moving mesh:** add the ALE correction, or raise as `forward` does. | Otherwise A1's default runs silently without a mesh-velocity term on free-surface and MMPDE meshes (`ddt.py:4974`). | — |
| B6 | **Particles stay opt-in** until #738 and #797 are fixed. | Not a default candidate. | — |

**Order:** B1 → re-measure (Q1–Q3) → A1, A2, A6, A7 → B2 and Q4 → A3 → B3, then lift A2. B4 and B5
run alongside.

## 4. Open questions for the student (each one a measurement)

| # | question | measurement | decides |
|---|---|---|---|
| Q1 | With the snapshot fix (and with the nudge removed), does the nodal history still carry ~30% excess near a no-slip wall? | the #735 cylinder at h 1/20, 1/30, 1/40: near-wall $\|\tau_{II}\|_{L^2}$ and shell ratios, nodal vs IP vs grid | whether #735 stands, and whether nodal may be offered for a flux |
| Q2 | Is #1009's Waters and King bias the nodal trace's true error, which the defect had hidden? | Waters and King at 1/16, 1/32, 1/64, fixed Courant: error with the fix, with the trace velocity forced to $(u,0)$, and with the nudge removed | whether B1 is safe as is |
| Q3 | Rotation and translation of a stored stress, every flavour, on development + B1, across Courant numbers (H7 did one case: Courant up to about 1, development only) | the probe in `probe/` at Courant 0.4, 1 and 4, h 1/16 and 1/32, with B1 applied | the transport-accuracy column of A1 |
| Q4 | Does the grid history survive Waters and King with DEVSS iterated (B2)? With it lagged? | #749's Δt sweep, DEVSS off / lagged / iterated, $\eta_a \in \{\eta/4, \eta\}$ | A3: SUPG as the NavierStokes stress default |
| Q5 | Is the default partition-independent on development? | the test_1066 matrix (six histories, np 1/3/4/6) on development + B1 | whether B4(a) is needed before A1 |
| Q6 | How wrong is the integration-point history on a moving mesh without ALE? | a Maxwell box with a moving top wall: compare the ALE nodal history, `eulerian`, and IP | B5 |
| Q7 | Which store smoothing suits a geodynamic VEP model (no solvent, Courant ≪ 1, yielding)? | a VEP shear band and the TI horizontal fault, `store_smoothing` 0, 0.023, 0.07, 0.23, at Courant 0.1 and 0.4 | A1's coefficient for geodynamics |
| Q8 | What does the no-crossing clip cost and buy? | #871's thin-sheet fault and a Stokes box fault: slip-rate oscillation amplitude, before and after B3 | B3, and lifting A2 |
| Q9 | Does the P2 nodal history have any use (your question of 2026-10-06)? | Waters and King and the cylinder, nodal order 1 vs 2, after B1 | whether order 2 SL stays offered |

## Sources not on GitHub

- **Session transcripts, kept on the workstation in Louis's Claude mirror:**
  - the cylinder campaign of 2026-10-05 to 10-15, which holds Louis's SUPG remark of 2026-10-06;
  - the 2026-10-13 to 10-18 session, which holds the defaults study and the defect discovery;
  - the 2026-10-20 to 10-30 session, which holds the verification and the review.
- **The September sessions:**
  - "SUPG advection scheme hardening" left no transcript. Its work is in commits 451efe3f, 01261ddc,
    a29a5b1f, b5bfc29d, 71bb82d7 and eba681fe.
  - "Forward-IP limiter neighbour-range" is in commits bf4e663e and a62aa9d3, and in the journal
    entry `entries/2026-10-05-dead-end-a-barth-jespersen-limiter-on-the-cell-fit.md`. The
    neighbour-range limiter was never built.
- **The 2026-10-18 plan** (`ve-plastic-gap-closure.md`) records both of Louis's default rulings.
- **Gaps:** the defaults-study data, about 70 runs, and the September laptop scripts cited by #735
  and #749 are not on the workstation.
