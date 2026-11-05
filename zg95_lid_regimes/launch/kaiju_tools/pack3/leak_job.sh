#!/bin/bash
# kaiju_tools: driver 23f509d against 4f2fbaa on f631ce42, per-run rss (job 4043)
# The memory-growth test (the hub, 2026-11-05): two np 26 TAf-v2 runs on one node, one per socket, library f631ce42,
# driver 23f509d (socket 0) against 4f2fbaa (socket 1). Each run's resident memory (the sum over processes whose
# command line names its run dir) and its step count are logged every 30 s to <run dir>/mem.log. Otherwise sock2_job.sh.
#SBATCH --job-name=leak
#SBATCH --nodes=1
#SBATCH --ntasks=52
#SBATCH --ntasks-per-node=52
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=04:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/leak_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/leak_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
RUNNER=/home/louis/+Claude/kaiju/launch/np52/run_driver.py
export APPTAINERENV_OMPI_MCA_btl_tcp_if_include=ib0 APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp
export APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
echo "leak on $SLURM_NODELIST: $(date)"
( while true; do for drv in 23f509d 4f2fbaa; do D=/home/louis/+Claude/kaiju/runs/leak_TAf_$drv
      echo "$(date '+%F %T') rss_GB $(ps -u louis -o rss=,args= | grep -F "$D " | grep -v grep | awk '{s+=$1} END{printf "%.2f", s/1048576}') step $(grep -cE '^\[0\] step' "$D/slurm_sock2.out" 2>/dev/null)" >> "$D/mem.log"
  done; sleep 30; done ) &
MON=$!
for drv in 23f509d 4f2fbaa; do
    D=/home/louis/+Claude/kaiju/runs/leak_TAf_$drv
    DRV=/home/louis/+Claude/kaiju/clones/zg95-v2-$drv/zg95_lid_regimes/drivers/annulus_faults.py
    ( cd "$D" && srun --export=ALL --exact --ntasks=26 --mem=80G --hint=nomultithread --cpu-bind=verbose,cores --mpi=pmix \
        apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
        bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$RUNNER" "$DRV" -uw_out "$D" $(cat "$D/ARGS.txt") \
        -log_view ":$D/log_view.txt" > "$D/slurm_sock2.out" 2> "$D/slurm_sock2.err"
      echo "$drv exit $? $(date)" ) &
    RUNS="$RUNS $!"
    sleep 5
done
wait $RUNS
kill $MON
echo "leak done: $(date)"
