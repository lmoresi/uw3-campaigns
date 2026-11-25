#!/bin/bash
# UNFILED 64: repeat rep1157.py N times under each condition
M=/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15
N=${N:-10}
run() { for i in $(seq $N); do env OMP_NUM_THREADS=1 "$@" pixi run --manifest-path $M -e runtime python rep1157.py "$COND" 2>&1 | grep ^REP; done; }
COND=base run
COND=hashseed0 run PYTHONHASHSEED=0
COND=blas1 run OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MKL_NUM_THREADS=1
