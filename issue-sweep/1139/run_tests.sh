#!/bin/bash
# usage: run_tests.sh <list-file> <tag>   (serial pytest over the listed files, level_3 deselected)
cd /Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/kept-transfer || exit 1
export OMP_NUM_THREADS=1 PYVISTA_OFF_SCREEN=true MPLBACKEND=Agg
P=~/+Simulations/issue_sweep/review_1139
date > $P/after.tests_$2.log
pixi run -e runtime pytest $(cat $P/$1 | tr '\n' ' ') -m "not level_3" -p no:cacheprovider -q --tb=short --durations=15 >> $P/after.tests_$2.log 2>&1
echo "EXIT $?" >> $P/after.tests_$2.log
date >> $P/after.tests_$2.log
