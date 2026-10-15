#!/bin/zsh
# Render new checkpoints of every box run (regimes and faults) every 3 minutes, niced, one
# process at a time; runs marked STOPPED are skipped. UW3_WORKTREE is the underworld3
# checkout whose pixi environment runs the renderer (feature/box-faults or later).
HERE=${0:A:h}
: ${UW3_WORKTREE:?set UW3_WORKTREE to the underworld3 checkout}
: ${UW3_PIXI_ENV:=amr-dev}
while true; do
  for d in ~/+Simulations/zg95/box_regimes/runs/*/ ~/+Simulations/zg95/box_faults/runs/*/; do
    [ -f $d/STOPPED ] && continue
    ( cd $UW3_WORKTREE && OMP_NUM_THREADS=1 nice -n 19 pixi run -e $UW3_PIXI_ENV python $HERE/render_box.py -uw_run $d > $d/render.log 2>&1 )
  done
  sleep 180
done
