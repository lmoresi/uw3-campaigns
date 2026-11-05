#!/bin/bash
# kaiju_tools: Slurm array for the offline fault-division study (fault division page UANqhA82AfRoh7fjgrPwYG)
# The fault-division offline placement check (division_offline.py), one run family per array task, serial.
#   sbatch --array=0-5 division_array.sh
#SBATCH --job-name=division_offline
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/runs/division_offline/slurm_%A_%a.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/division_offline/slurm_%A_%a.err
set -e
RUNS=/home/louis/campaigns/zg95/runs
OUT=/home/louis/+Claude/kaiju/runs/division_offline
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/uw3/overlay-dev-25d62812
SCRIPT=/home/louis/+Claude/kaiju/launch/division/division_offline.py
FAMILIES=(slab_earth_run1 slab_thermal_fault_TA_age25f slab_thermal_fault_TAf_env slab_thermal_fault_TAf
          slab_thermal_fault_TAti_smooth slab_thermal_fault_TBf)
FAM=${FAMILIES[$SLURM_ARRAY_TASK_ID]}
# the same checkpoints the inset test used (every stored crust-law fault: 80 in all)
STATES=$(python3 -c "
import json
seen = []
for l in open('$RUNS/inset_offline/${FAM#slab_}.jsonl'):
    s = json.loads(l)['state']
    if s not in seen:
        seen.append(s)
print(' '.join(seen))")
export APPTAINERENV_OMP_NUM_THREADS=1
echo "family $FAM: $(echo $STATES | wc -w) checkpoints, node $(hostname -s), $(date)"
apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
    bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 \"\$0\" \"\$@\"" "$SCRIPT" "$OUT/$FAM.jsonl" $STATES
echo "done $(date)"
