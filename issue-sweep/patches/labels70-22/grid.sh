#!/bin/bash
M=/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15
for path in surface fault; do for mk in box_irr box_reg; do for fam in lines_arcs hairpin approach; do for ds in 1.0 0.5 0.3; do for rule in old new; do
  RULE=$rule OMP_NUM_THREADS=1 pixi run --manifest-path $M -e runtime python measure_labels.py $path $mk $fam $ds 2>&1 | grep -E "^LAB|Traceback" | head -1
done; done; done; done; done
