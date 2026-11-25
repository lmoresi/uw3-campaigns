#!/bin/bash
# MODES="dev" on a development build; MODES="new_all new_light" on the labelling-fix build
M=/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15
for mode in $MODES; do for mk in box_irr box_reg; do for ds in 1.0 0.5 0.3; do
  for fam in lines_arcs kinks; do
    s=0; [ "$fam" = lines_arcs ] && s=6
    MODE=$mode OMP_NUM_THREADS=1 PYTHONPATH=. pixi run --manifest-path $M -e runtime python pull22.py $mk $ds $fam $s 2>&1 | grep "^PULL" | sed 's/^PULL //'
  done
done; done; done
