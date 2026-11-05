#!/bin/bash
# kaiju_tools: the same with per-step --mem (job 3975)
# v2 (each step its own --mem=55G: in v1 the first step took the whole allocation and the others waited). Three 16-rank TAf-v2 runs packed on one node (Louis, 2026-11-04: "let's try all these options"): control and two warm
# Newton switch arms, as three concurrent srun steps in one 48-rank exclusive allocation, so all three share the node.
# Each arm's args are its run dir's ARGS.txt. The MPI settings are kaiju_uw3_job.sh's (every one load-bearing).
#SBATCH --job-name=pack3v2
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=06:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/pack3v2_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/pack3v2_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin      # submitted with --export=NONE
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
RUNNER=/home/louis/+Claude/kaiju/launch/np52/run_driver.py
DRV=/home/louis/+Claude/kaiju/clones/zg95-v2-23f509d/zg95_lid_regimes/drivers/annulus_faults.py
export APPTAINERENV_OMPI_MCA_btl_tcp_if_include=ib0 APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp
export APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
echo "pack3 on $SLURM_NODELIST: $(date)"
for arm in control wns3e-2 wns1e-1; do
    D=/home/louis/+Claude/kaiju/runs/pack3v2_${arm}_TAf_v2_ck20
    ( cd "$D" && srun --export=ALL --exact --ntasks=16 --mem=55G --hint=nomultithread --cpu-bind=cores --mpi=pmix \
        apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
        bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$RUNNER" "$DRV" -uw_out "$D" $(cat "$D/ARGS.txt") \
        -log_view ":$D/log_view.txt" > "$D/slurm_pack3.out" 2> "$D/slurm_pack3.err"
      echo "$arm exit $? $(date)" ) &
done
wait
echo "pack3 done: $(date)"
