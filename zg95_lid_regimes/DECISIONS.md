# Decisions ledger: the zg95 fault and rollback drivers

These drivers (`drivers/annulus_faults.py`, `annulus_fault.py`, `box_fault.py`, `annulus_model.py`)
are campaign code in `uw3-campaigns`, not part of underworld3. Every choice they make that the
library does not make for them is a campaign decision and is recorded here, dated, with the
evidence and who ruled. The hub's day-to-day record is `HUB.md` at the repository root; the
pages linked there hold the figures. A run's own `README.md` carries a "Choices" block
(every knob below, its value, set or default) and `run_info.json` the resolved parameters,
since 094e4f3. Louis, 2026-11-01: "every exposed knob is a recorded choice"; 2026-11-02:
these decisions must be findable by other Claudes and by people, not only by the hub.

Newest first within each section. "Ruled" means Louis decided; "measured" means the value
rests on a kaiju measurement cited; "taken" means a default inherited without a decision.

## Solver

| knob | value | status | evidence / ruling |
|---|---|---|---|
| `uw_pres_rtol` (Schur pressure KSP rtol) | 1e-2 (was the library's 0.1 x tol = 1e-4) | ruled 2026-11-01 ("feel free to try the lax pressure tolerance") | kaiju A/B 2026-10-28: -28 to -57 % Stokes time, answer to 7e-6; budget 2026-11-01 (TAf 40, np 16, development 25d62812): 2.3x faster, vrms to 6 figures, slip within 0.05; at 1e-4 every Newton increment ran 41-47 pressure iterations, each an inner velocity solve. Every campaign result before Earth run 1 and TAti ran at 1e-4. |
| `uw_tol` (outer) | 1e-3 | taken (never set in any run) | sets the library's pressure and inner velocity rtols when `uw_pres_rtol` is 0; the inner velocity rtol (0.033 x tol) has no knob on the rotated route. |
| Newton switches (`uw_newton_switch`, `uw_warm_newton_switch`, `uw_rebuild_newton_switch`) | 1e-2 (TI runs: 3e-2) | taken for the split runs; measured for TI | the library clamps the switch to max(switch, tolerance), so a switch below `uw_tol` means pure Picard (this cost a day on TAti, 2026-10-31). TI at 3e-2 converges where 1e-2 and 1e-3 stalled. The warm switch is measured against the rest-state residual, so warm steps run 5-6 Picard iterations before Newton (budget page; a lever not yet taken). |
| `uw_retry_keep` | best | fixed 2026-11-01 (bug) | a failed warm start's cold retry was kept even when worse; 15 of TAti's first 20 failures kept a worse answer. |
| `consistent_jacobian` | "continuation" | hard-coded, taken | never compared with the alternatives in production. |
| `uw_chain` (split ladders on coarse MG levels) | **0** (default from 2026-11-02, driver commit b440b88, with the build move to development 25d62812); 2 before | ruled 2026-10-31 (#892): the production tail is the welded base + split finest level + FAC LU patch; Louis 2026-11-02: go on the build move, so the default changes with it | measured 2026-11-01 at np 16 on development (TAf 40; TAf 20 and TBf 70, 10 steps): same answer; a wash on speed at the production band ratio 3.9 (within +-10 %); chain 0 20-35 % faster at fault depth 0.45; chain 0 avoids coarse-level ladder refusals and welding (the demo OOM). The default moves to 0 when the campaign's builds move to development: on the leak-fix overlay (no #912) chain 0 is ~1.5x slower. |
| TI band (`-uw_fault_realisation ti`) | L1 strength (f_b 3.3e-3, eta_reg 0.033, floor 0.033), w = 2S, whole-band mask, smooth law | measured 2026-10-30 | the split is frictionless, so the band is pushed toward that limit: deepest level that converges. TI costs ~2.7x the split per step; a third of TAti's steps did not converge (the rotated loop's line-search exit ends converging Picard phases: library finding with the dev hub). |

## Fault placement and geometry

| knob | value | status | evidence / ruling |
|---|---|---|---|
| `uw_fault_fit` (crust-base locator) | envelope (default parabola until the switch) | ruled by the go on the Earth plan, 2026-10-29 | 40/40 stored checkpoints fit, monotone, 0.0055 trace change under 10 % particle dropout; the parabola fit 29/40 and moved 0.75. TAf (parabola) overstated slip ~50 % and plate speed ~10 % against TAf_env (envelope); large-scale evolution the same. Flexure tested, parameters unconstrained from the hinge alone. |
| `uw_fault_top_dip_min` | 30 deg | taken (default kept) | bound 13 of 81 detections in Earth run 1 (data down to 28), never in the demo. |
| `uw_split_inset` (cut stops this many rungs inside the wall) | 3 rungs (0.012 at S 0.004); 1 rung proposed | taken; with Louis 2026-11-02 | Louis: the inset is one element because surface DOFs cannot be rotated, not a physical depth; asks for 1 rung if possible. Tested 2026-11-02 (kaiju, page T37Y3MMpYyfgQZbCmuk5YQ): no evidence ever stood behind 3 (a bare 3.0 S in the first box driver, 15 Oct); placement of 80 stored faults is 80/80 at 1, 2 and 3 rungs on the finest level and at 2S, and 1 rung refuses 2 of 80 at 4S (so safe with chain 0, not always with chain 2); the answer differs: at 1 rung slip is +11-16 % in the top 0.02 and +6-9 % at 0.04-0.08 (slip_max 6546 vs 5878, vrms 1380 vs 1359), i.e. 3 rungs locks more of the top. A physics choice worth ~10 % in slip, not a numerical margin. |
| `uw_fault_seams` / mesher | gather / ladder | taken in every run until 2026-11-01 | every fault lives on one rank (addon_partition on development; the placement itself on 99259d35), so its FAC patch solve is serial. conform (#670) needs the network mesher, which cannot place a wall-reaching fault (serial repro with the dev hub): unusable here. Louis: "disappointing to discover it is not used and has been forgotten". |
| `uw_wall_normal` | analytic (unit_r) today; geometric recommended | with Louis 2026-11-02 | the analytic path leaves a wall node unconstrained when its owning rank holds none of its labelled facets (np 24/32/40/52; np 16 clean by partition); the geometric path (the library default) is clean at np 32 with the same answer. Library defect with the dev hub. |
| `uw_wall_check` | 1 | added 2026-11-01 | records max |v.n| per wall every solve; the defect above showed only as a smaller dt before. |
| placement attempts | margin_rings 1/1/2/1, clearance 0.7, width x1/x1.25/x1/x1.5 | hard-coded, taken | the library's defaults are margin_rings 2, clearance 0.3; never compared. |
| restart at a different rung spacing (`uw_resample_restored`) | auto: re-sample restored crust-law polylines when this run's S differs from the checkpoint's, else leave them (bit-identical restarts) | fixed 2026-11-02 (the restart rule) | a restart rebuilt the fault from the stored polyline at the old S and kept those rungs until the next re-fit: the first ladder-spacing arms at S = h_b kept 0.004 rungs for all 10 steps (79 pairs against 19 when re-sampled). `force`/`never` remain for tests. |
| `uw_rebuild_rungs` | 4 | measured 2026-10-26 (rungs 8 vs 4: 29 vs 47 rebuilds, -10 % wall, trench and slip unchanged) | with the envelope the per-step trace change is 0.19-0.76 of the threshold, so production rebuilds every 2-4 steps. |
| `uw_weld_ok` | 0 (a refused chain level refuses the build) | fixed 2026-10-29 | the silent weld put a band along the surface and OOM'd (186 GB). |
| restart and the rung spacing | a restored crust-law polyline is sampled at the WRITING run's S until a detection re-fits it | found 2026-11-02 (kaiju); fix in test | a restart that changes `uw_spacing` therefore changes only the band width and the inset until the first re-fit, which confounded the first ladder-spacing arms. Rule (hub, 2026-11-02): the driver re-samples a restored polyline at the run's S automatically when the checkpoint's S differs, and leaves it alone otherwise so existing restarts stay bit-identical; the knob is an override for tests. |

## Model

| knob | value | status | evidence / ruling |
|---|---|---|---|
| crust marker | one cell thick, x0.001 on viscosity and yield, `uw_crust_ppc` 12 | ruled 2026-10-27 (Louis: keep the thin crustal layer; its base is the fault's target, Sandiford & Moresi) | x0.001 is "very, very weak" (Louis); a crust-strength sweep is on the list. |
| `uw_fault_precedence` | 1 in TAti and the Earth runs, 0 in TAf/TBf | ruled 2026-10-29 (fault rheology always wins; no double weakening) | the mask is the whole band. |
| Earth setup | continent x1 (deforms), buoyant -0.5, lid age 0.000625, gate depth 0.12, Ra 2.386e7, over_gap 0.75, cont_extent 2.4315, ridge fixed | ruled 2026-10-29/30 ("the continent is fine to deform ... unless they are cratons") | run 1 complete at the base, 81 steps. |
| `uw_dt_mult` | 20 | set campaign-wide in slab_case.sh (driver default 3) | taken once, never revisited. |
| units | dimensionless; `-uw_scaled` check only | ruled 2026-10-29 ("file as a bug, fall back to dimensionless for the demo") | underworld3 #891. |

## Builds

| decision | value | status | evidence / ruling |
|---|---|---|---|
| library build for new runs | current development (head of the day, recorded per run) | ruled 2026-11-02 (Louis: "go ahead with the build move") | the leak fix, the fault-split work (A/B/C), #912 (FAC LU on the rotated route) and #914 are on development; the pinned leak-fix overlay 547c2e54 served every result from 2026-10-27 to 2026-11-01 and stays for restarts of those runs. Acceptance PASSED 2026-11-02 (kaiju job 3154, driver with uw_chain 0 and pressure rtol 1e-2 on the fresh development overlay): step 41 vrms 1358.9188, slip 5877.77, mobility 1.2870, Newton 6, walls clean to 1e-12, equal to the 25d62812 chain-0 reference to the printed figures. Results from here are on a different library than the thermal and Earth sets (which were also at pressure rtol 1e-4): a documented discontinuity. |

## Machine

| setting | value | status | evidence |
|---|---|---|---|
| kaiju ranks | np 16 | taken (coarse-solve null-mode limit; later the only partition clean of the wall-node defect) | every production result is at np 16; walls verified clean to 1e-12 at the latest checkpoints. |
| packing | three 16-rank jobs per node for independent runs (--mem=60G, no --exclusive, core binding); timing studies exclusive | measured 2026-11-01 | 2.1x node throughput; socket pinning has no effect. |

## Open

- The inset's unit and default (1 rung if possible: Louis 2026-11-02; test pending).
- The wall normal default (geometric recommended).
- Levers measured but not taken: a warm Newton switch measured against the warm iterate's own residual; an inexact inner velocity solve; the crust-strength sweep.
