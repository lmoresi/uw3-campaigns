#!/bin/bash
# kaiju_tools: Earth run isolation test job (2026-11-03)
# One arm of the Earth isolation (prepare.sh): array task 0/1/2 = arm a/b/c; its args are the arm's ARGS.txt.
#   sbatch --array=0-2 isolate_job.sh
#SBATCH --job-name=earth_iso
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=16
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=02:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/earth_iso_slurm_%A_%a.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/earth_iso_slurm_%A_%a.err
ARMS=(a b c)
D=/home/louis/+Claude/kaiju/runs/earth_iso_${ARMS[$SLURM_ARRAY_TASK_ID]}_ck20
cd "$D" || exit 1
export CONTAINER=/home/louis/uw3/images/uw3-gadi-development-20261021.sif EXTRA_PKGS=/home/louis/uw3/overlay-dev-25d62812
export SCRIPT=/home/louis/+Claude/kaiju/clones/zg95-v2-64feaec/zg95_lid_regimes/drivers/annulus_faults.py
export OMP_NUM_THREADS=1 UW3_COMMIT=25d62812 SRUN_OPTS="--hint=nomultithread --cpu-bind=cores"
# the driver's log in the run dir, as the other runs have it (the trigger and comparisons read slurm_*.out there)
exec bash /home/louis/campaigns/kaiju-launch/kaiju_uw3_job.sh -uw_out "$D" $(cat "$D/ARGS.txt") \
    > "$D/slurm_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out" 2> "$D/slurm_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.err"
