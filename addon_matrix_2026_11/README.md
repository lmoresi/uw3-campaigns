# Add-on matrix, rows 3-5 and 7 (2-D)

The dev hub's question is in DEV-HUB.md, under "Can the add-on replace split coarse levels everywhere?". These are rows 3-5 in 2-D. H0 is the welded base, then the split S level with the FAC LU patch, which is the production tail ruled on 2026-11-01. H1 is the lean chain of split ladders. Both fixtures are the UWTN 2026-022 tail sweep's.

## Files

| file | row | what it runs |
|---|---|---|
| `row3_cover_gate.py` | 3 | problem A (unit box, simple shear, one straight fault, h_b = 1/32) at a given spine count. It records the FAC cover gate's verdict on the finest level. |
| `uniform_level_gate.py` | 3 | the same box, no fault: the gate on a uniformly refined level |
| `row4_interface_laws.py` | 4 | problem B (the yielding-lid box at the faults-in-convection guide's hard state) with a viscous, Coulomb or rate-and-state law on the split fault |
| `row5_networks.py` | 5 | problem A's box with a stop-short junction, two close parallel faults, or a TI band beside the split fault |
| `kaiju_commands.sh` | 4, 5 | the np 4 arms, one independent job per line |
| `row7_linear.py`, `row7_box.py` | 7 | problems A and B, H0 only, the ladder at a given S |
| `row7_common.py` | 7 | the slip profile in fixed coordinates, the FAC block timer |
| `collect_row7.py` | 7 | the row 7 tables against the references |
| `kaiju_commands_row7.sh` | 7 | 9 jobs at np 1 (problem A) and 26 at np 4 (problem B) |
| `data/box_state_02000/` | 4 | the input row 4 reads: checkpoint 2000 of the fixed-trench fault run `stagnant_tau1x1.00_fault_x2.0_dip45` (state JSON, mesh and T). It is force-added, because the repository ignores `*.h5`. |

`row4_interface_laws.py` and `row7_box.py` import `box_model` from `../zg95_lid_regimes/drivers`.

## Laws in row 4

Neither the sweep driver nor the guide uses a law other than frictionless, so the parameters come from the box's own scales. V_free = 323.4 is the frictionless peak slip at S = 0.004. tau_y(0.175) = 1.797e5 is the lid's yield stress at mid-fault depth.

- **Viscous:** eta_f = tau_y(0.175) / V_free = 555.7.
- **Coulomb:** mu = 0.3, sigma_n from the reaction, V0 = 1e-4 V_free.
- **Rate-and-state:** f0 = 0.3, a = 0.020, b = 0.010 (test_0846's set), V0 = 1e-2 V_free, Dc = 1e-3, sigma_n from the reaction.

The rotated loop's cap is raised to 200 by wrapping `rotated_bc.solve_rotated_freeslip`, because `snes_max_it` cannot reach it (underworld3 #920). At the default cap of 50, Coulomb and rate-and-state stop in the Picard phase at rel 2e-2.

## Row 7: does a finer ladder do physical work?

Louis, 2026-11-01: "For split nodes, the ladder is to improve how we cut the mesh and this works best when the ladder and the base mesh have similar resolution." Row 7 asks whether a finer ladder changes the answer. H0 only, the ladder placed in the base as it is.

Both fixtures have h_b = 1/32. The production annulus runs at h_b/S 3.9 (S 0.004 on h_b 0.0156).

| fixture | today's S | h_b/S | the row 7 S values |
|---|---|---|---|
| A (the 022 fixture, L = 0.4123) | the note's sweep, 80-320 rungs | 6-24 | 13, 26, 53, 80, 106, 160, 211, 320 and 640 rungs: h_b/S 1-48 |
| B (the box, `tail_sweep_box.py`) | 0.004 | 7.9 | h_b, h_b/2, h_b/4, 0.004, h_b/16: h_b/S 1-16 |

**Dropped arms.** The first version of the job list also refined the base under the fault corridor (`-uw_depth`, `-uw_rings`, nested NVB `mesh.adapt`). Louis did not propose that (2026-11-02):
- the cut represents the discontinuity, so it should need little refinement;
- the ladder is there to compute stresses and slip rates accurately;
- near-fault stress lobes are a separate question.

So those 32 arms were dropped. The drivers keep the option at its default of 0.

**The box's tip and bridge move with S in the fixture.** The fixture splits the fault from three rung spacings below the surface, and the weak bridge is the band cells above that tip. At S = h_b, the tip would sit at depth 0.10 rather than 0.012.
- `row7_box.py` holds the tip physical by default: `-uw_tip 0.012` puts the split's upper end at the first spine point at least 0.012 deep, at any S.
- `-uw_tip 3S` keeps the fixture's rule, and the unrefined arms run both ways.
- `-uw_tip 1el` (or `2el`) is the inset Louis gave (2026-11-02, relayed by the hub): "One element ... if it works. I am not sure about units. 1 is normalised by the element size." The tip is the first spine point at least k rung spacings S down dip from where the fault meets the surface. The rung spacing is the band cell's length along the fault.
- The bridge stays the band cells above the tip, so it is 2S wide. A weak zone cannot be narrower than the band it lives in.

**The tip as placed** (`-uw_mesh_only 1`, serial, 2026-11-02). Every arm's record carries the same measures under `tip`. The spine starts at y = 1.02 and is sampled at S, so it does not meet the surface at a rung. An inset of k elements therefore lands between k and k + 1 rungs down dip.

| S | h_b/S | 1el: tip depth, inset in S (down dip / depth) | 2el | 0.012 | 3S |
|---|---|---|---|---|---|
| 0.03270 | 0.96 | 0.0263, 1.14 / 0.80 | 0.0494, 2.14 / 1.51 | = 1el | 0.1188, 5.14 / 3.63 |
| 0.01635 | 1.91 | 0.0147, 1.27 / 0.90 | 0.0263, 2.27 / 1.61 | = 1el | 0.0494, 4.27 / 3.02 |
| 0.00770 | 4.06 | 0.0072, 1.32 / 0.94 | 0.0127, 2.32 / 1.64 | = 2el | 0.0235, 4.32 / 3.06 |
| 0.00396 | 7.88 | 0.0052, 1.86 / 1.32 | 0.0080, 2.86 / 2.03 | 0.0136, 4.86 / 3.44 | = 0.012 |
| 0.00195 | 16.0 | 0.0021, 1.51 / 1.07 | 0.0035, 2.51 / 1.78 | 0.0131, 9.51 / 6.73 | 0.0062, 4.51 / 3.19 |

- No pair point lies on the surface in any arm, so the rotated assembly's wall-and-pair refusal cannot fire.
- The top pair's frame normal (the measure-weighted normal of its Plus facets) matches the fault's normal to 12 digits in every arm.
- At one element the tip's shortest edge is 0.54-0.68 S: that is the band cell clipped by the surface.
- Whether one element works in the solve (convergence, and the slip on the pairs next to the tip) is what the `1el` arms on kaiju answer. `pairs_near_tip` records the four pairs nearest the surface.

**On kaiju, one element works at every S:**
- Newton 35-42, the same as the deeper tips;
- the frame is exact, and the leak is at rounding;
- the peak slip is within 1% of the 0.012 tip at the same S.

**Geometry held (dev hub, 2026-11-02).** The box converges more slowly in S than problem A. The bridge (2S of band cells) and the tip (a spine point) both move with S. The hold-geometry arms fix both:
- `-uw_tip_exact 1` samples the spine at S from the tip, so the tip lies at the asked depth.
- `-uw_bridge_width w` makes the bridge a smooth zone of physical width w, sampled at the quadrature points: a super-Gaussian across the fault, and a tanh of width w/4 at the tip.

The tip is held at 0.026, which is at least one element at every S (1.1 at h_b). At 0.012 it would be 0.52 elements at S = h_b; that placed cleanly in a serial check, but it falls below Louis's one element. There are two widths:
- 0.008, the reference arms' 2S;
- 0.0654 (2 h_b), which every S resolves.

Each family is compared with its own finest S. If both converge in S as problem A does, the box's slow convergence is the geometry riding on S, not the ladder.

**What each record holds:**
- the slip profile in fixed physical coordinates (problem A: from the fault's end at (0.30, 0.45); B: down dip from the surface);
- problem A: the velocity on a line across the fault's midpoint;
- problem B: the surface velocity and the vertical velocity at depth 0.05;
- the Newton and velocity iterations, the set-up and solve times;
- the FAC patch's rows, its blocks' rows, and their LU set-up, refactorisation and solve time (`row7_common.FacBlockTimer`);
- the peak resident memory per rank.

`collect_row7.py records` compares every arm against the finest arm. For problem B, the velocity iterations come from the log, summed over every application. The cover gate is forced open (`UW_FAC_COVER=1.01`, #918) in every row 7 arm. Row 7 runs on the same build as rows 4-5.

## Build

Use underworld3 `bugfix/rotated-nullspace-from-mesh` at 964dc3ce: development 25d62812 plus #906. #906 changes only rotated free slip with declared rotation modes, and these boxes declare none. Set `OMP_NUM_THREADS=1`.

## What to report

For every job:
- the record JSON in `records/`;
- the exit status;
- for a nonzero exit or a timeout, the log tail.

The job `ti ... zone both` is wrapped in `timeout 900`: at np 4 on the laptop it ran 3600 s without finishing, where np 1 takes about 15 s. If it times out again, take a stack of each rank before the kill, with `py-spy dump --pid` or `gdb -p <pid> -batch -ex "thread apply all bt"`.

## Results so far

From the laptop, at np 1 and 2. Velocity iterations are summed over the second solve's applications.

- **Row 3 (the gate):**
  - The gate declines a patch whose subdomain is above 75 %, without logging it. At h_b/S = 48 that means 909 iterations against 66 with the gate open; at 97, 1487 against 66. H1 takes 302 and 725.
  - A uniformly refined level has a 100 % subdomain and no background outside it. Filed as underworld3 #918.
- **Row 5, np 1:**
  - pair: H0 761 (gate declined), 68 with the gate open, H1 231;
  - TI band: H0 609 declined, 66 open; `fac_zone` = TI band 820; TI + structural 94; H1 230;
  - junction (8 S gap): H0 78, and H1 cannot place its 4S ladder; at a 24 S gap, H0 77 and H1 230.
- **Row 4, np 4 at cap 50:** viscous H0 125 against H1 388 velocity iterations, both converged in 29 Newton iterations to slip 77.359.
