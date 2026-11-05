#!/bin/bash
# kaiju_tools: job wrapper for bending_fit.py (jobs 4088, 4089, 4093)
# The offline bending-line fault fit (Louis, 2026-11-06), bending_fit.py on stored checkpoints of six runs; reads only.
#SBATCH --job-name=bendfit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/movies/bendfit_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/movies/bendfit_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
apptainer exec /home/louis/uw3/images/uw3-gadi-development-20261021.sif bash -c \
    "MPLBACKEND=Agg OMP_NUM_THREADS=4 BEND_Q=${BEND_Q:-0.10} BEND_TAG=${BEND_TAG:-v2} python3 /home/louis/+Claude/kaiju/launch/movies/bending_fit.py"
