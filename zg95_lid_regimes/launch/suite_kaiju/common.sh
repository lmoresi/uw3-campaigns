# shared by every run of the suite; source it
: "${UW3_WORKTREE:?set UW3_WORKTREE to the built underworld3 checkout}"
: "${UW3_CAMPAIGNS:?set UW3_CAMPAIGNS to the uw3-campaigns checkout}"
: "${ZG95_RUNS:?set ZG95_RUNS to the output root}"
: "${NP:?set NP to the rank count}"
export OMP_NUM_THREADS=1
DRIVER=$UW3_CAMPAIGNS/zg95_lid_regimes/drivers/annulus_faults.py
COMMON="-uw_restart 3910 -uw_rebuild_dip 5 -uw_fault_law lines -uw_fault_damage 0.5 -uw_fault_separation 6 -uw_max_faults 4
        -uw_tau0 6.075e4 -uw_weak_min 0.25 -uw_asth 0.1 -uw_asth_bottom 0.7 -uw_fault_cut_lid 1 -uw_steps 4000"
launch() {   # launch <name> <flags...>
    name=$1; shift
    out=$ZG95_RUNS/$name; mkdir -p $out
    cd $UW3_WORKTREE
    pixi run -e amr-dev mpirun -np $NP python $DRIVER -uw_out $out "$@" $COMMON >> $out/run.log 2>&1
}
