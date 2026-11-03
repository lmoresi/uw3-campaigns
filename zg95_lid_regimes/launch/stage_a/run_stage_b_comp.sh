#!/bin/bash
# Stage A, compositional: the subducting plate and its slab are a particle-carried material
# with a fixed temperature deficit (no diffusion) and a viscosity contrast in an isoviscous
# mantle (uw_deta 1, thermal buoyancy off); no fault, no overriding plate; weak crust on top.
#   run_stage_b_comp.sh <name> <np> <flags...>
cd ~/+Underworld/underworld3-pixi/.claude/worktrees/box-faults
export OMP_NUM_THREADS=1
D=~/+Simulations/uw3-campaigns/zg95_lid_regimes/drivers/annulus_faults.py
RA=~/+Simulations/uw3-campaigns/zg95_lid_regimes/render/render_annulus.py
# tau0/Ra 0.075 and tau1/Ra 10 as in the thermal runs, scaled to Ra 3e6
BASE="-uw_init slab -uw_over_plate 0 -uw_max_faults 0 -uw_fault_law none -uw_theta_trench 0 -uw_dip 45 -uw_age_sub 0.0025 -uw_slab_length 0.35 -uw_slab_rate 1000 -uw_slab_warm_top 0 -uw_top_hot 1 -uw_asth 1 -uw_deta 1 -uw_buoy_T 0 -uw_ra 3e6 -uw_tau0 2.25e5 -uw_tau1 3e7 -uw_comp_dT 0.5 -uw_comp_eta 100 -uw_comp_thick 0.1 -uw_crust_weak 0.001 -uw_refinement 5 -uw_steps 120 -uw_ckpt_every 10 -uw_dt_mult 20"
name=$1; shift
NP=$1; shift
T=~/+Simulations/zg95/annulus_faults/runs/$name
mkdir -p $T
nice -n 5 pixi run -e amr-dev mpirun -np $NP python $D -uw_out $T $BASE "$@" > $T/run.log 2>&1 &
RUN=$!
sleep 90
nice -n 10 pixi run -e amr-dev -q python $RA -uw_run $T -uw_panels strain -uw_zoom 0.5 -uw_watch 1 2>&1 | grep "^->"
wait $RUN
echo "RUN_DONE $name"
