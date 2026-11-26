# Slab workbench: what 24-27 Nov 2026 established

Louis, 27 Nov: "We should try to lock in any gains in understanding." Each rule has the runs it rests on (kaiju `runs/wb_*`).
Rules marked *ruled* are Louis's decisions; the rest are findings.

## The model

1. **No weakening by depth alone** (*ruled* 24-25 Nov). A viscosity channel applied by depth weakens the cold slab as much
   as the mantle (every run to 24 Nov). The workbench and annulus_faults refuse `-uw_asth < 1` without a temperature switch
   (edf87b1, dbf7f10). Effect: with the depth-only channel the slab tip ran to near the CMB as a thin stream within 130 Myr
   (Rold); with the slab's strength kept it hung ~200 Myr in the stiff mantle (Rsw).
2. **The mantle's viscosity is set from published numbers, not from a channel** (*ruled* 24-25 Nov). The base file
   (`runs/wb_ladder/ARGS_earth.txt`) is now: upper mantle 1e21 Pa s, lower mantle x30 below 670 km, cap 1e24, yield floor
   1.26e21, no channel. The old 2e22 mantle gave a third of Earth's heat flow and plates that thicken without limit
   (heatflow_lith.py: ~32 mW/m2, 1175 C at 130-250 km and deepening).
3. **The initial slab is the plate bent down** (*ruled* 25 Nov): `-uw_slab_wedge_age_myr -1` puts the upper halo at the
   slab's own age (it was a fixed 167 Myr from 25 Oct, thicker than an 80 Myr plate).
4. **Every model has a fault** (*ruled* 25 Nov). A run whose first fit forms none stops (430b0ed).

## The fault

5. **The fit follows a marker line, and that line must lie below the split's top** (where the frictionless part begins,
   about one rung below the surface). A line above it is dragged across the trench in the welded layer and the march loses it
   at the hinge: R6c/R17c (7 km line) froze the fault on 85-95 % of steps; R17d (17.4 km line, 17 km rung) failed from step 5
   under an 80 Myr overriding plate; S3n/S4f (17.4 km line under the weak strip) held for 60-100 Myr, and R6d (6 km rung)
   held its first 7 fits before it was cancelled. Rsw (the recipe line) failed 47 of 329 fits, once 28 in a row (steps 14-41,
   while the slab hung): a run stopped by the guard is resumed with a higher limit and inspected, not discarded. Louis, 27 Nov:
   the marker is easier to fit than a smooth field.
6. **No jump limit at start-up.** The one-rung limit made the fault cut across the steepening slab for ~10 Myr (S2f: the
   free fit up to ~140 km away, the fault moved 12-33 % per fit). Without it (S3n) the fault follows the slab; S3f (limit after
   15 Myr) and S3n were identical to 60 Myr.
7. **A failing fit stops the run** (907369c, `-uw_fit_fail_stop 10`). Before reading any run, count good fits against
   "the fault keeps its place".
8. **A flat shallow fault is a symptom, not a fault.** When the line runs off along the overriding plate's top the fault's
   top follows it (Un, Un24, S2f: up to 1800-2700 km off the slab while the fault at 150-300 km stays on it; slip 3-4 cm/yr
   against 0.4-1.7 convergence). `fault_on_slab.py` flags the top's drift from its start (> +100 km).
9. **Where the slab decouples is read kinematically, not thermally.** The peak along-dip shear across the slab top sits
   at the fault (+-12 km at 100-300 km, S3n_ns); the half-T edge reads 60-100 km off because cold overriding lithosphere is
   dragged down on top (`kin_check.py`, `check_4974.py`). Caveat: the split's own velocity jump biases the peak toward the
   fault, so compare the fault's slip rate at depth with the slab-to-wedge velocity difference over +-50 km as well; a
   ratio well below 1 means the fault is there but not doing the work (S3n_ns step 58 at 200-300 km).

## The set-up

10. **The old overriding side is not a plate.** It is a 26 km (5 Myr) strip for 2175 km from the trench, then a 167 Myr
    continent (`-uw_over_gap_km`, `-uw_cont_age_myr`). The strip lies almost wholly above the split's top, so it is welded to
    the slab; it yields over 150-350 km (plastic strain rate ~1e-14 /s at 150-250 km from the fault's top) and takes about
    half the convergence (S3n, S4f).
11. **Without a fault the slab sinks two-sided** (S0, S1, S1o: vertical, trench fixed, both plates drawn in). With a fault
    that stays on the slab at depth it is one-sided at the same rate (S3n; S2f before its top ran off, vs S1o): the slab's sinking sets the rate, the fault the
    geometry.
12. **In the upper mantle the slab is at its yield stress** (~1e23 Pa s straining at 1e-15 to 1e-14.5 /s, S4f): the yield
    law sets its strength there. Below 670 km it is rigid (the x30 multiplies after the cap; Louis, 25 Nov: leave it).

## Cost and memory

13. **The faulted runs' cost is the first solve after a rebuild** (residual ~0.1 against ~0.02-0.05, 6-14 Newton, most
    line-search cutbacks). Meshing is ~13 s. Moving the warm start with the fault (`-uw_warm_shift`) did not help (S3n_ws/ns).
14. **Memory grows ~5-8 MB/rank/step with or without a fault.** `launch/prep/workbench_seg.sh` runs in segments of <= 150
    steps (exact restarts) and ends the chain on exit 3.

## Checks to run on every new run

`fault_on_slab.py` (top drift), `kin_check.py` (decoupling at the fault), `plate_budget.py` (convergence, fault share, slab
tip), the fit counts, and the record's `fault_check` (fit, top, slip ratio; the thermal slab check over-reads where cold
lithosphere is dragged down).
