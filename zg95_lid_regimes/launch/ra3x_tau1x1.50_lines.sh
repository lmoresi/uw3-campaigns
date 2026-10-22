# Ra x3 from the line-law run's checkpoint 3250 (mobile-ish lid, faults and damage carried over); tau1/Ra kept at 1.5
cd ~/+Underworld/underworld3-pixi/.claude/worktrees/box-faults
export OMP_NUM_THREADS=1
nohup nice -n 5 pixi run -e amr-dev mpirun -np 7 python /Users/lmoresi/+Simulations/uw3-campaigns/zg95_lid_regimes/drivers/annulus_faults.py -uw_out /Users/lmoresi/+Simulations/zg95/annulus_faults/runs/ra3x_tau1x1.50_lines -uw_restart 3320 -uw_rebuild_dip 5 -uw_ra 2.73375e6 -uw_tau1 4.100625e6 -uw_fault_law lines -uw_fault_damage 0.5 -uw_fault_separation 6 -uw_max_faults 4 -uw_steps 3000 >> /Users/lmoresi/+Simulations/zg95/annulus_faults/runs/ra3x_tau1x1.50_lines/run.log 2>&1 &
