#!/bin/bash
# kaiju_tools: the recipe v2 acceptance run (job 3830)
# Recipe v2 whole-recipe acceptance (the hub, 2026-11-03): TAf from checkpoint 40, np 16, one step, every driver
# default (chain 0, pres_rtol 1e-2, spacing = one base cell, inset 1 rung, analytic normal, retry best, wall check,
# seams gather, restart rule) plus the envelope locator, on development 25d62812, driver 6633afa + b21c264.
# kaiju-launch/scaling/scale.sh's run preparation, moved to ~/+Claude/kaiju (this session's writable root: ~/campaigns
# is read-only to it). sbatch is not called here: the managed policy needs it as a plain single command, so this
# writes the run dir and prints the argument list; the sbatch line is typed from it.
set -e
K=$HOME/+Claude/kaiju
N=16; CKPT=40; STEPS=1; SRC=TAf
LIB=$HOME/uw3/overlay-dev-25d62812; C=${LIB##*-}
DRV=$K/clones/zg95-recipe2-b21c264
S=$HOME/campaigns/zg95/runs/slab_thermal_fault_$SRC; D=$K/runs/recipe2_acceptance_dev${C}_b21c264_${SRC}_ck${CKPT}
mkdir -p "$D"
for f in "$S"/*.$(printf %05d "$CKPT").* "$S"/annulus.mesh.00000.* "$S"/annulus.solver_mesh.00000.*; do ln -sf "$(readlink -f "$f")" "$D/"; done
cp "$S/state_$(printf %05d "$CKPT").json" "$D/"
python3 -c "
import json; R=json.load(open('$S/records.json')); json.dump([r for r in R if r.get('step',0)<=$CKPT], open('$D/records.json','w'))"
BASE="-uw_init checkpoint -uw_over_plate 0 -uw_max_faults 0 -uw_fault_law none -uw_theta_trench 0 -uw_dip 45 -uw_age_sub 0.0025 -uw_slab_length 0.35 -uw_slab_rate 1000 -uw_slab_warm_top 0 -uw_top_hot 1 -uw_asth 1 -uw_deta 1 -uw_buoy_T 0 -uw_ra 3e6 -uw_tau0 2.25e5 -uw_tau1 3e7 -uw_comp_dT 0.5 -uw_comp_eta 100 -uw_comp_thick 0.1 -uw_crust_weak 0.001 -uw_refinement 5 -uw_steps $STEPS -uw_ckpt_every 10 -uw_dt_mult 20 -uw_verbose 1"
TAF="-uw_buoy_T 1 -uw_comp_dT 0 -uw_comp_eta 1 -uw_deta 4e3 -uw_ra 2.386e7 -uw_tau0 1.789e6 -uw_tau1 2.386e8 -uw_age_sub 0.0035 -uw_crust_ppc 12 -uw_crust_refill_every 5 -uw_fault_law crust -uw_fault_fit envelope -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_detect_start 0 -uw_detect_every 5 -uw_warm_newton_switch 1e-2"
ARGS="$BASE $TAF -uw_restart $CKPT"
cat > "$D/README.md" <<TXT
# Recipe v2 whole-recipe acceptance (the hub, 2026-11-03)
- Build: underworld3 development $C ($LIB), image uw3-gadi-development-20261021.sif; np $N, one node, exclusive (n1 excluded).
- Driver: $(git -C $DRV log -1 --format=%h) (6633afa + the spacing patch b21c264, not yet on the hub branch) in $DRV.
- Case: TAf as launched, $STEPS step from checkpoint $CKPT, every driver default (recipe v2) plus -uw_fault_fit envelope.
  No chain, pres_rtol, spacing, inset, wall-normal, retry, wall-check, seams or resample flags: the choices block in
  the driver's output records what each resolved to. DECISIONS.md: no decision changed by this run.
- Run directory under ~/+Claude/kaiju because this session cannot write ~/campaigns (sandbox, 2026-11-03).
- Args: $ARGS -log_view :$D/coarse_DEV_np${N}.txt
TXT
echo "$ARGS" > "$D/ARGS.txt"
echo "D=$D"
echo "ARGS=$ARGS"
