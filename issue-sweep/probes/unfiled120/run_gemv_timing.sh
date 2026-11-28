#!/bin/bash
# Row 120 (a): the default GEMV path against both options off, on the same build.
# Usage: bash run_gemv_timing.sh [np] [scale]     (defaults: np 1, scale 1)
# Pins every thread variable to 1, so the comparison is of the code path alone.
set -e
NP=${1:-1}; SCALE=${2:-1}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
launch() { if [ "$NP" -gt 1 ]; then mpirun -n "$NP" python "$@"; else python "$@"; fi; }
env -u PETSC_OPTIONS bash -c "$(declare -f launch); NP=$NP; launch gemv_timing.py -uw_out default-np$NP.json -uw_scale $SCALE"
PETSC_OPTIONS="-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0" bash -c "$(declare -f launch); NP=$NP; launch gemv_timing.py -uw_out off-np$NP.json -uw_scale $SCALE"
python gemv_timing_compare.py default-np$NP.json off-np$NP.json | tee compare-np$NP.txt
