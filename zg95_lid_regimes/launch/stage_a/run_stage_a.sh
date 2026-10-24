#!/bin/bash
# Stage A: a half-annulus plate with its slab, a thin boundary layer elsewhere, NO fault and
# NO overriding plate; the baseline for how the slab founders. Two runs at a time, 4 ranks each.
#   run_stage_a.sh <name> <flags...>      (one run; the stage's launcher queues pairs)
cd ~/+Underworld/underworld3-pixi/.claude/worktrees/box-faults
export OMP_NUM_THREADS=1
D=~/+Simulations/uw3-campaigns/zg95_lid_regimes/drivers/annulus_faults.py
RA=~/+Simulations/uw3-campaigns/zg95_lid_regimes/render/render_annulus.py
BASE="-uw_init slab -uw_over_plate 0 -uw_max_faults 0 -uw_fault_law none -uw_theta_trench 0 -uw_dip 45 -uw_age_sub 0.0025 -uw_slab_length 0.35 -uw_slab_rate 1000 -uw_ra 2.73375e6 -uw_tau1 4.100625e6 -uw_asth 0.1 -uw_slab_warm_top 0 -uw_steps 60 -uw_ckpt_every 5 -uw_dt_mult 20"
name=$1; shift
T=~/+Simulations/zg95/annulus_faults/runs/$name
mkdir -p $T
nice -n 5 pixi run -e amr-dev mpirun -np 4 python $D -uw_out $T $BASE "$@" > $T/run.log 2>&1 &
RUN=$!
sleep 90
nice -n 10 pixi run -e amr-dev -q python $RA -uw_run $T -uw_panels strain -uw_zoom 0.5 -uw_watch 1 2>&1 | grep "^->"
wait $RUN
echo "RUN_DONE $name"
