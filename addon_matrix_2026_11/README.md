# Add-on matrix, rows 3-5 (2-D)

The dev hub's question is in DEV-HUB.md, under "Can the add-on replace split coarse levels everywhere?". These are rows 3-5 in 2-D. H0 is the welded base, then the split S level with the FAC LU patch, which is the production tail ruled on 2026-11-01. H1 is the lean chain of split ladders. Both fixtures are the UWTN 2026-022 tail sweep's.

## Files

| file | row | what it runs |
|---|---|---|
| `row3_cover_gate.py` | 3 | problem A (unit box, simple shear, one straight fault, h_b = 1/32) at a given spine count. It records the FAC cover gate's verdict on the finest level. |
| `uniform_level_gate.py` | 3 | the same box, no fault: the gate on a uniformly refined level |
| `row4_interface_laws.py` | 4 | problem B (the yielding-lid box at the faults-in-convection guide's hard state) with a viscous, Coulomb or rate-and-state law on the split fault |
| `row5_networks.py` | 5 | problem A's box with a stop-short junction, two close parallel faults, or a TI band beside the split fault |
| `kaiju_commands.sh` | 4, 5 | the np 4 arms, one independent job per line |
| `data/box_state_02000/` | 4 | the input row 4 reads: checkpoint 2000 of the fixed-trench fault run `stagnant_tau1x1.00_fault_x2.0_dip45` (state JSON, mesh and T). It is force-added, because the repository ignores `*.h5`. |

`row4_interface_laws.py` imports `box_model` from `../zg95_lid_regimes/drivers`.

## Laws in row 4

Neither the sweep driver nor the guide uses a law other than frictionless, so the parameters come from the box's own scales. V_free = 323.4 is the frictionless peak slip at S = 0.004. tau_y(0.175) = 1.797e5 is the lid's yield stress at mid-fault depth.

- **Viscous:** eta_f = tau_y(0.175) / V_free = 555.7.
- **Coulomb:** mu = 0.3, sigma_n from the reaction, V0 = 1e-4 V_free.
- **Rate-and-state:** f0 = 0.3, a = 0.020, b = 0.010 (test_0846's set), V0 = 1e-2 V_free, Dc = 1e-3, sigma_n from the reaction.

The rotated loop's cap is raised to 200 by wrapping `rotated_bc.solve_rotated_freeslip`, because `snes_max_it` cannot reach it (underworld3 #920). At the default cap of 50, Coulomb and rate-and-state stop in the Picard phase at rel 2e-2.

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
