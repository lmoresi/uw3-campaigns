#!/bin/bash
# The near-surface split sweep: k = 0..10 cells at two dips and two cell sizes,
# on development (fbef72fa) and on the UNFILED 60 head (02f34664, its
# place_surface.py overlaid on a copy of the same install), serially, then a
# few points at np 2 and 3. One process at a time, pinned to one core.
#
# usage: bash run.sh [serial|fine|mpi|all]
# ENV must point at a script that, given dev|u60, activates the environment
# (pixi dev env of a clean development install; for u60 PYTHONPATH carries the
# overlay). See README.md.

HERE=$(cd "$(dirname "$0")" && pwd)
ENV=${ENV:?set ENV to the environment script}
UW=${UW:?set UW to an underworld3 checkout (for scripts/mpi_supervisor.py)}
WORK=${WORK:-$HERE/work}; mkdir -p "$WORK" "$HERE/logs"; cd "$WORK"
CORE=${CORE:-80}; CORES=${CORES:-80-82}

serial() {   # serial <dev|u60> <dip> <cellsize>
  local v=$1 d=$2 c=$3 log=$HERE/logs/sweep-$1-dip$2-cs$3-np1.log
  ( . "$ENV" "$v" >/dev/null 2>&1
    timeout 900 taskset -c "$CORE" python "$HERE/p_nearsurface_split.py" --dip "$d" --cellsize "$c" ) > "$log" 2>&1
  echo "EXIT $?" >> "$log"
}

fine() {     # fine <dev|u60> <dip> <cellsize> <k list>: the band's two edges at 0.1 cell
  local v=$1 d=$2 c=$3 k=$4 log=$HERE/logs/fine-$1-dip$2-cs$3-np1.log
  ( . "$ENV" "$v" >/dev/null 2>&1
    timeout 900 taskset -c "$CORE" python "$HERE/p_nearsurface_split.py" --dip "$d" --cellsize "$c" --k "$k" ) > "$log" 2>&1
  echo "EXIT $?" >> "$log"
}

mpi() {      # mpi <dev|u60> <dip> <cellsize> <np> <k list>
  local v=$1 d=$2 c=$3 n=$4 k=$5 log=$HERE/logs/mpi-$1-dip$2-cs$3-np$4.log
  ( . "$ENV" "$v" >/dev/null 2>&1
    timeout 900 taskset -c "$CORES" python "$UW/scripts/mpi_supervisor.py" --silence 180 -- \
      mpirun -n "$n" --bind-to none python "$HERE/p_nearsurface_split.py" --dip "$d" --cellsize "$c" --k "$k" ) > "$log" 2>&1
  echo "EXIT $?" >> "$log"
}

case ${1:-all} in
serial|all)
  for v in dev u60; do
    serial $v 30 0.05
    serial $v 45 0.05
    serial $v 15 0.05
    serial $v 30 0.025
  done ;;&
fine|all)
  for v in dev u60; do
    fine $v 30 0.05 1.6,1.7,1.8,1.9,2.0,3.6,3.7,3.8,3.9,4.0,4.1
  done ;;&
mpi|all)
  for n in 2 3; do
    mpi u60 30 0.05 $n 1,2.5,3.5,5,6,8
    mpi dev 30 0.05 $n 1,2.5,3.5,5,6,8
  done ;;
esac
