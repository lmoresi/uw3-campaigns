#!/bin/bash
# usage: run_note_and_zhong.sh <worktree> <tag>
set -u
D=~/+Simulations/issue_sweep/p_blocks_1072
cd "$1" || exit 1
export OMP_NUM_THREADS=1
for part in sweep contrast gamma; do
  pixi run -e runtime python $D/probe_note_solcx.py -uw_part $part 2>&1 | grep -E "^\||^part=|Error|error" >> $D/note_solcx_$2.log
done
for gamma in 10.0 12.5; do
  PYTHONPATH="$1/tests" pixi run -e runtime python $D/probe_zhong_gamma.py -uw_gamma $gamma 2>&1 | grep -E "^gamma|Error|error" >> $D/zhong_gamma_$2.log
done
echo done
