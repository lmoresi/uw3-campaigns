#!/bin/bash
# UNFILED 66, step 2: the hang needs the files in ONE pytest process. Reproduce the audit's
# batch (six files, one mpirun, -m "tier_a or tier_b"), then bisect by leaving one file out at a
# time, and by reversing the order. Each job runs under the supervisor (stack dumps on silence).
# Run from a built development checkout:  bash bisect_batch102.sh [silence s, default 180] [np list, default "2 3"]
set -u
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
SIL=${1:-180}
NPS=${2:-"2 3"}
OUT=${OUT:-u66b_$(date +%Y%m%dT%H%M)}
mkdir -p "$OUT"
FILES=(tests/parallel/test_1097_place_sheet_partitioned_addon_parallel.py
       tests/parallel/test_1099_band_placement_partitioned_parallel.py
       tests/parallel/test_1101_custom_mg_dependent_columns_parallel.py
       tests/parallel/test_1103_custom_mg_empty_rank_parallel.py
       tests/parallel/test_1103_facet_slip_against_serial_parallel.py
       tests/parallel/test_1103_split_fault_slip_parallel.py)
run() {   # tag, files...
  local tag=$1; shift
  for np in $NPS; do
    python scripts/mpi_supervisor.py --silence "$SIL" --artifacts "$OUT/${tag}_np$np.stacks" -- \
      mpirun -n $np python -m pytest --with-mpi -v -p no:cacheprovider -m "tier_a or tier_b" "$@" \
      > "$OUT/${tag}_np$np.log" 2>&1
    echo "$tag np $np exit $? last test: $(grep -E '::test_' "$OUT/${tag}_np$np.log" | tail -1 | cut -c1-150)"
  done
}
run all "${FILES[@]}"
for i in "${!FILES[@]}"; do
  rest=("${FILES[@]:0:$i}" "${FILES[@]:$((i+1))}")
  run "without_$(basename "${FILES[$i]}" .py)" "${rest[@]}"
done
rev=(); for ((i=${#FILES[@]}-1; i>=0; i--)); do rev+=("${FILES[$i]}"); done
run reversed "${rev[@]}"
# Reading it: if "all" hangs and "without_X" passes, file X's state is needed for the hang (as
# the earlier file, or as the one that meets it). The last test before the silence names where
# the ranks stopped; the stacks name the collective. Then pair X with each later file to find
# the two that interact.
