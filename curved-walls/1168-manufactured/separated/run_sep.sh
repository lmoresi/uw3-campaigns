#!/bin/bash
# One run of measure_sep.py: <mesh> <kind> <cell> <method>
set -u
PY="pixi run --manifest-path $HYPERION_WORK/wt-h6-1168-sep/pixi.toml -e dev python"
timeout 5400 $PY measure_sep.py -uw_mesh $1 -uw_kind $2 -uw_cell_size $3 -uw_method $4 > logs/sep_$1_$2_$3_$4.log 2>&1
