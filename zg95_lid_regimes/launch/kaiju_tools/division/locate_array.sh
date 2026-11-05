#!/bin/bash
# kaiju_tools: Slurm array for the locator worst-case scan (the division study)
# Where the slivers are (locate_worst.py): the worst placements of each arm of the division check, one arm per task.
#   sbatch --array=0-3 locate_array.sh
#SBATCH --job-name=division_locate
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/runs/division_offline/locate_%A_%a.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/division_offline/locate_%A_%a.err
set -e
D=/home/louis/+Claude/kaiju/runs/division_offline
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/uw3/overlay-dev-25d62812
SCRIPT=/home/louis/+Claude/kaiju/launch/division/locate_worst.py
ARMS=(v2 D0 D1 D2)
ARM=${ARMS[$SLURM_ARRAY_TASK_ID]}
export APPTAINERENV_OMP_NUM_THREADS=1
echo "arm $ARM, node $(hostname -s), $(date)"
apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
    bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$SCRIPT" "$D/locate_$ARM.jsonl" "$D/cases_$ARM.json"
echo "done $(date)"
