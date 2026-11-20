#!/bin/bash
# One converged rerun: <mesh> <kind> <cell> <which: default|radial>
# mesh: none | graded | graded2 | graded3c (diag_graded.py) or trench (mmpde_measure.py)
set -u
mesh=$1; kind=$2; cell=$3; which=$4
PY="pixi run --manifest-path $HYPERION_WORK/wt-h6-1168/pixi.toml -e dev python"
if [ "$which" = default ]; then only=default; lu=1; else only="X/|X|"; lu=0; fi
if [ "$mesh" = trench ]; then
  timeout 5400 $PY mmpde_measure.py -uw_cell_size $cell -uw_kind $kind -uw_metric trench -uw_only "$only" -uw_lu_default $lu
else
  timeout 5400 $PY diag_graded.py -uw_cell_size $cell -uw_kind $kind -uw_slide $mesh -uw_only "$only" -uw_lu_default $lu
fi > logs/conv_${mesh}_${kind}_${cell}_${which}.log 2>&1
