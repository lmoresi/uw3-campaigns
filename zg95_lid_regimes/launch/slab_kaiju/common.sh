# shared by every run of the slab scan; source it
: "${UW3_WORKTREE:?set UW3_WORKTREE to the built underworld3 checkout}"
: "${UW3_CAMPAIGNS:?set UW3_CAMPAIGNS to the uw3-campaigns checkout}"
: "${ZG95_RUNS:?set ZG95_RUNS to the output root}"
: "${NP:?set NP to the rank count}"
export OMP_NUM_THREADS=1
DRIVER=$UW3_CAMPAIGNS/zg95_lid_regimes/drivers/annulus_faults.py
# the baseline: Ra 2.7e6, tau1/Ra 1.5, asthenosphere x0.1 in 0.3-0.7 d; half-space cooling from an
# age line: age 0.0025 at the trench on the subducting plate (0.1 d thick), 0.001 on the overriding
# plate (0.063 d), ridges opposite the trench, the age continued down the slab (0.35 d at 45 deg)
# at a convergence rate of 1000, the one-sided profile diffused freely since subduction so the wedge is cooled beside the slab; one fault on the rate law (advected with the overriding plate,
# corrected by the strain-rate fit from step 20), cutting the lithosphere
BASE="-uw_init slab -uw_theta_trench 0 -uw_dip 45 -uw_fault_depth 0.15 -uw_age_sub 0.0025 -uw_age_over 0.001
      -uw_slab_length 0.35 -uw_slab_rate 1000 -uw_ra 2.73375e6 -uw_tau1 4.100625e6 -uw_asth 0.1
      -uw_fault_law rate -uw_max_faults 1 -uw_fault_damage 0.5 -uw_fault_cut_lid 1 -uw_rebuild_rungs 8
      -uw_rebuild_dip 5 -uw_detect_start 20 -uw_steps 1000 -uw_ckpt_every 10"
launch() {   # launch <name> <flags that override the baseline...>
    name=$1; shift
    out=$ZG95_RUNS/slab/$name; mkdir -p $out
    cd $UW3_WORKTREE
    pixi run -e amr-dev mpirun -np $NP python $DRIVER -uw_out $out $BASE "$@" >> $out/run.log 2>&1
}
