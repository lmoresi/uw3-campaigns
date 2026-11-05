#!/bin/bash
# kaiju_tools: resume one crust arm alone on a node with node-memory logging (jobs 4032-4059)
# Resume one crust-test arm from its last complete checkpoint after an out-of-memory kill (2026-11-05: jobs 3993 and 3997
# gave each 26-rank step --mem=60G; Earth hit it after 22-28 steps, TAf passive after 51). Here the arm runs alone on a
# node with all its memory, still np 26 (the same decomposition as its control), and the node's memory use is logged
# every minute to mem.log in the run dir (the growth per step is a question for the hub). The run dir's ARGS_resume.txt
# holds the restart line. Otherwise as crust_job.sh.
#   sbatch --export=NONE crust_resume_job.sh <run dir name>
#SBATCH --job-name=crust_r
#SBATCH --nodes=1
#SBATCH --ntasks=26
#SBATCH --ntasks-per-node=26
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=12:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/crust_r_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/crust_r_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
RUNNER=/home/louis/+Claude/kaiju/launch/np52/run_driver.py
DRV=/home/louis/+Claude/kaiju/clones/zg95-v2-4f2fbaa/zg95_lid_regimes/drivers/annulus_faults.py
export APPTAINERENV_OMPI_MCA_btl_tcp_if_include=ib0 APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp
export APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
D=/home/louis/+Claude/kaiju/runs/${1:?run dir name}
echo "crust_r $1 on $SLURM_NODELIST: $(date)"
( while true; do echo "$(date '+%F %T') used_GB $(free -g | awk '/^Mem:/{print $3}') rss_GB $(ps -u louis -o rss= | awk '{s+=$1} END{printf "%.1f", s/1048576}') step $(grep -cE '^\[0\] step' "$D/slurm_resume.out" 2>/dev/null)" >> "$D/mem.log"; sleep 60; done ) &
MON=$!
cd "$D" && srun --export=ALL --ntasks=26 --hint=nomultithread --cpu-bind=verbose,cores --mpi=pmix \
    apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
    bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$RUNNER" "$DRV" -uw_out "$D" $(cat "$D/ARGS_resume.txt") \
    > "$D/slurm_resume.out" 2> "$D/slurm_resume.err"
echo "$1 exit $? $(date)"
kill $MON
echo "crust_r done: $(date)"
