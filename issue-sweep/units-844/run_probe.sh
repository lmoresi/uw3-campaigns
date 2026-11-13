#!/bin/bash
# usage: run_probe.sh <worktree> <tag>
cd "$1" || exit 1
export OMP_NUM_THREADS=1
OUT=~/+Simulations/issue_sweep/review_units_844/$2.log
git log --oneline -1 > $OUT
for section in plain units no_mass; do
  pixi run -e runtime python ~/+Simulations/issue_sweep/review_units_844/probe.py $section >> $OUT 2>&1
done
