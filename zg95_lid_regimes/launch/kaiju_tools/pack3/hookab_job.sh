#!/bin/bash
# kaiju_tools: the #948 timing A/B: leaky against fixed hook on one node (job 4107)
# The #948 timing A/B (the Science Hub, 2026-11-06): two runs on one node, one per socket, the same driver (4f2fbaa), each with its own runner dir (launch/np52 = the fixed hook, launch/np52_leaky = the pre-#948 hook). Otherwise crust_pair_job.sh.
# 52-task allocation, two 26-task --exact steps, the first on socket 0 and the second on socket 1 (bind probe 3981),
# each with its own driver clone and --mem=90G. Each run reads its run dir's ARGS_resume.txt (a fresh line or a restart),
# so a pair runs in segments short enough for the memory leak (about 1 GB per step at np 26): 60 steps, then a restart
# from the last checkpoint, which resets the memory. Each run's resident memory and step count are logged every 60 s to
# <run dir>/mem.log; its output goes to slurm_seg.out/.err (kept per segment by the caller).
#   sbatch --export=NONE hookab_job.sh <run dir 1> <runner dir 1> <run dir 2> <runner dir 2>   (runner dirs under launch/)
#SBATCH --job-name=hookAB
#SBATCH --nodes=1
#SBATCH --ntasks=52
#SBATCH --ntasks-per-node=52
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1,n6
#SBATCH --time=12:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/hookAB_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/hookAB_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
DRV=/home/louis/+Claude/kaiju/clones/zg95-v2-4f2fbaa/zg95_lid_regimes/drivers/annulus_faults.py
R=/home/louis/+Claude/kaiju/runs
export APPTAINERENV_OMPI_MCA_btl_tcp_if_include=ib0 APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp
export APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
A=${1:?run dir 1}; DA=${2:?driver clone 1}; B=${3:?run dir 2}; DB=${4:?driver clone 2}
echo "hookAB $A ($DA) + $B ($DB) on $SLURM_NODELIST: $(date)"
( while true; do for d in "$A" "$B"; do
      echo "$(date '+%F %T') rss_GB $(ps -u louis -o rss=,args= | grep -F "$R/$d " | grep -v grep | awk '{s+=$1} END{printf "%.2f", s/1048576}') step $(grep -cE '^\[0\] step' "$R/$d/slurm_seg.out" 2>/dev/null)" >> "$R/$d/mem.log"
  done; sleep 60; done ) &
MON=$!
RUNS=""
for pair in "$A:$DA" "$B:$DB"; do
    d=${pair%%:*}; c=${pair##*:}; D=$R/$d
    RUNNER=/home/louis/+Claude/kaiju/launch/$c/run_driver.py
    ( cd "$D" && srun --export=ALL --exact --ntasks=26 --mem=90G --hint=nomultithread --cpu-bind=verbose,cores --mpi=pmix \
        apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
        bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$RUNNER" "$DRV" -uw_out "$D" $(cat "$D/ARGS_resume.txt") \
        > "$D/slurm_seg.out" 2> "$D/slurm_seg.err"
      echo "$d exit $? $(date)" ) &
    RUNS="$RUNS $!"
    sleep 5          # the first step takes socket 0 before the second asks
done
wait $RUNS
kill $MON
echo "hookAB done: $(date)"
