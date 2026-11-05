#!/bin/bash
# kaiju_tools: warm-switch arms, two run dirs given, one per socket (jobs 3985, 3987)
# Warm-switch arms (the hub for Louis, 2026-11-05): the two run dirs given as arguments, np 26 each, one per socket. Otherwise sock2_job.sh.
# in a 52-task allocation take cores in order, so the first 26-task step gets socket 0 (0-25) and the second socket 1
# (26-51). Each step's binding is printed (--cpu-bind=verbose) into its err file to confirm. Otherwise as pack3_job_v2.sh.
#SBATCH --job-name=wsw
#SBATCH --nodes=1
#SBATCH --ntasks=52
#SBATCH --ntasks-per-node=52
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=03:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/wsw_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/wsw_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
RUNNER=/home/louis/+Claude/kaiju/launch/np52/run_driver.py
DRV=/home/louis/+Claude/kaiju/clones/zg95-v2-23f509d/zg95_lid_regimes/drivers/annulus_faults.py
export APPTAINERENV_OMPI_MCA_btl_tcp_if_include=ib0 APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp
export APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
echo "wsw on $SLURM_NODELIST: $(date)"
for arm in "$@"; do
    D=/home/louis/+Claude/kaiju/runs/${arm}
    ( cd "$D" && srun --export=ALL --exact --ntasks=26 --mem=60G --hint=nomultithread --cpu-bind=verbose,cores --mpi=pmix \
        apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
        bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$RUNNER" "$DRV" -uw_out "$D" $(cat "$D/ARGS.txt") \
        -log_view ":$D/log_view.txt" > "$D/slurm_sock2.out" 2> "$D/slurm_sock2.err"
      echo "$arm exit $? $(date)" ) &
    sleep 5          # A takes cores 0-25 before B asks
done
wait
echo "wsw done: $(date)"
