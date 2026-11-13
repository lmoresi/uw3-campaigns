#!/bin/bash
# Build PR #1134's head in the review worktree, then run item 1 twice. Serial.
set -u
W=/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/review-1127
D=~/+Simulations/issue_sweep/review_1134
cd "$W" || exit 1
export OMP_NUM_THREADS=1
git rev-parse --short HEAD > "$D/head.txt"
./uw build > "$D/build.log" 2>&1; echo "build exit $?" >> "$D/build.log"
pixi run -e runtime python -c "import underworld3 as uw; print(uw.__file__)" >> "$D/head.txt" 2>&1
for name in head no_one_cell_condition; do
  pixi run -e runtime python "$D/item1.py" "$name" > "$D/item1_$name.log" 2>&1
done
pixi run -e runtime pytest tests/test_0753_nested_mg_prolongation.py -q -p no:cacheprovider -k "not 3d-every-pass" -W ignore --durations=5 > "$D/test_0753_rest.log" 2>&1
pixi run -e runtime pytest tests/test_0449*.py -q -p no:cacheprovider -W ignore --durations=5 > "$D/test_0449.log" 2>&1
echo done
