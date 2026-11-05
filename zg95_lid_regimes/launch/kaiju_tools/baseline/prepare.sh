#!/bin/bash
# kaiju_tools: writes a recipe v2 baseline run dir, README and ARGS (TAf-v2, Earth run 2; jobs 3849-3858, the _c reruns)
# Recipe v2 baselines (Louis, 2026-11-04, via the hub): TAf-v2 and Earth run 2, as the proposal page's launch lines
# (CDy2RR1fLhBUyPXtUMftNr): every driver default (recipe v2: chain 0, pres_rtol 1e-2, spacing one base cell, inset 1 rung,
# envelope locator, analytic normal, retry best, wall check, seams gather, restart rule), no locator flag. Driver pinned in a clean clone (9e69c6b from 2026-11-04); development 25d62812. This writes the run dir,
# its README and ARGS.txt, and prints the args; the sbatch line is typed from them (the managed policy needs it plain).
#   prepare.sh TAf_v2 | earth_run2 [suffix]     (suffix: a new run dir name, e.g. _c for the 9e69c6b reruns)
set -e
K=$HOME/+Claude/kaiju
# From 2026-11-04 (the hub): new launches use 9e69c6b (uw_rebuild_cells, the rebuild threshold as a distance) and the
# repo's watcher launch/kaiju_v2/baseline_job.sh; 64feaec (uw_rebuild_rungs counted in rungs of S) is refused.
DRV=${DRV:-$K/clones/zg95-v2-9e69c6b}; LIB=$HOME/uw3/overlay-dev-25d62812
HEAD=$(git -C "$DRV" rev-parse --short HEAD)
[ "$HEAD" = 64feaec ] && { echo "driver 64feaec is refused for new launches (rebuild threshold in rungs of S): use 9e69c6b" >&2; exit 1; }
[ "$HEAD" = 9e69c6b ] || { echo "driver clone at $HEAD, not 9e69c6b" >&2; exit 1; }
[ -z "$(git -C "$DRV" status --porcelain)" ] || { echo "driver clone not clean" >&2; exit 1; }
BASE_FOR() { echo "-uw_init slab -uw_over_plate 0 -uw_max_faults 0 -uw_fault_law none -uw_theta_trench 0 -uw_dip 45 -uw_age_sub 0.0025 -uw_slab_length 0.35 -uw_slab_rate 1000 -uw_slab_warm_top 0 -uw_top_hot 1 -uw_asth 1 -uw_deta 1 -uw_buoy_T 0 -uw_ra 3e6 -uw_tau0 2.25e5 -uw_tau1 3e7 -uw_comp_dT 0.5 -uw_comp_eta 100 -uw_comp_thick 0.1 -uw_crust_weak 0.001 -uw_refinement 5 -uw_steps $1 -uw_ckpt_every 10 -uw_dt_mult 20 -uw_verbose 1"; }
THERMAL="-uw_buoy_T 1 -uw_comp_dT 0 -uw_comp_eta 1"
TA="-uw_deta 4e3 -uw_ra 2.386e7 -uw_tau0 1.789e6 -uw_tau1 2.386e8 -uw_age_sub 0.0035"
SAMPLING="-uw_crust_ppc 12 -uw_crust_refill_every 5"
case "${1:?TAf_v2 or earth_run2}" in
TAf_v2)
    D=$K/runs/slab_thermal_fault_TAf_v2${2:-}
    FAULT="-uw_fault_law crust -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_detect_start 0 -uw_detect_every 5"
    ARGS="$(BASE_FOR 300) $THERMAL $TA $SAMPLING $FAULT -uw_warm_newton_switch 1e-2 -uw_ckpt_every 5"
    TWIN="TAf_env (~/campaigns/zg95/runs/slab_thermal_fault_TAf_env: the same case and locator on the old recipe:
  overlay-leakfix 547c2e54, driver 07667b2, chain 2, pressure rtol 1e-4 (library default), S 0.004, inset 3 rungs,
  W 0.008, checkpoints every 10; on the base at about step 101)"
    CASE="TAf-v2: TAf's recipe (TA strength, thermal buoyancy, the crust sampled at 12 particles per cell and topped up
  every 5 steps, the crust-base fault detected every 5 steps), 300 steps at most, checkpoints every 5"
    ;;
earth_run2)
    D=$K/runs/slab_earth_run2${2:-}
    FAULT="-uw_fault_law crust -uw_fault_top_dip_min 30 -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_detect_start 0 -uw_detect_every 1 -uw_fault_precedence 1"
    EARTH="-uw_top_hot 2 -uw_ridge_patch 0.05 -uw_over_plate 1 -uw_age_over 0.0035 -uw_over_comp_thick 0.05 -uw_cont_age 0.000625 -uw_slab_length 0.2 -uw_lm_eta 1 -uw_over_eta 1 -uw_asth 0.1 -uw_asth_top 0.12 -uw_asth_bottom 0.231 -uw_asth_ramp 0.02 -uw_over_gap 0.75 -uw_cont_extent 2.4315"
    ARGS="$(BASE_FOR 130) $THERMAL $TA -uw_ra 2.386e7 $SAMPLING $FAULT -uw_warm_newton_switch 1e-2 -uw_pres_rtol 1e-2 $EARTH -uw_over_dT -0.5 -uw_marker_rheo_depth 0.12 -uw_ckpt_every 5"
    TWIN="Earth run 1 (~/campaigns/zg95/runs/slab_earth_run1: the same line on the old recipe: overlay-leakfix 547c2e54,
  driver 07667b2, chain 2, S 0.004, inset 3 rungs, W 0.008, with -uw_fault_fit envelope then explicit; on the base at
  step 81)"
    CASE="Earth run 2: Earth run 1's line (kaiju-launch/earth/production.sh) less -uw_fault_fit envelope (now the default);
  its explicit -uw_pres_rtol 1e-2 kept (the default now has the same value); 130 steps at most, checkpoints every 5"
    ;;
*) echo "unknown case $1" >&2; exit 1 ;;
esac
[ -e "$D" ] && { echo "$D exists: not overwriting" >&2; exit 1; }
mkdir -p "$D"
cat > "$D/README.md" <<TXT
# $(basename "$D"): a recipe v2 baseline (Louis, 2026-11-04: launch, via the hub)
- $CASE.
- Recipe v2 by default: chain 0, pressure rtol 1e-2, rung spacing one base cell (0.0156; W = 2S, the ladder equant:
  Louis 2026-11-04 "make the ladder equant if given the choice"), split inset 1 rung, envelope locator, analytic wall
  normal, retry best, wall check on, seams gather, the restart rule. The driver's README choices block records each.
- Old twin for comparison: $TWIN.
- Build: underworld3 development 25d62812 ($LIB), image uw3-gadi-development-20261021.sif; np 16, one node, exclusive
  (n1 excluded); 12 h limit, one segment.
- Driver: $HEAD in $DRV; job script $DRV/zg95_lid_regimes/launch/kaiju_v2/baseline_job.sh.
- Stop rule: one checkpoint interval after the slab tip reaches the base (tip_depth.py, 0.95). Pause trigger: two
  consecutive unconverged steps, or more than two in any ten, stop the run at the next complete checkpoint. Both run
  inside the job (~/+Claude/kaiju/launch/baseline/baseline_job.sh); events in watch.log.
- DECISIONS.md: no decision changed by this run (the recipe v2 defaults as accepted, job 3830).
- Run directory under ~/+Claude/kaiju: this session cannot write ~/campaigns (sandbox, 2026-11-03).
- Args: -uw_out $D $ARGS

TXT
echo "$ARGS" > "$D/ARGS.txt"
echo "D=$D"
echo "ARGS=$ARGS"
