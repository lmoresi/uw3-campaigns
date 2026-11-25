#!/bin/bash
# UNFILED 66: which file of tests/parallel batch 102 hangs, at which test, and in which collective.
# Run from a development (fbef72fa or later) checkout, built, on the Linux server. One file and one
# rank count per job, each under the project's supervisor (stack dumps on silence).
#   bash run_batch102.sh [silence seconds, default 180]
set -u
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
SIL=${1:-180}
OUT=${OUT:-u66_$(date +%Y%m%dT%H%M)}
mkdir -p "$OUT"
for f in tests/parallel/test_1097_outcropping_ribbon_partitioned_parallel.py \
         tests/parallel/test_1097_place_sheet_partitioned_addon_parallel.py \
         tests/parallel/test_1099_band_placement_partitioned_parallel.py \
         tests/parallel/test_1101_custom_mg_dependent_columns_parallel.py \
         tests/parallel/test_1103_custom_mg_empty_rank_parallel.py \
         tests/parallel/test_1103_facet_slip_against_serial_parallel.py \
         tests/parallel/test_1103_split_fault_slip_parallel.py; do
  for np in 2 3; do
    tag=$(basename "$f" .py)_np$np
    python scripts/mpi_supervisor.py --silence "$SIL" --artifacts "$OUT/$tag.stacks" -- \
      mpirun -n $np python -m pytest --with-mpi -v -p no:cacheprovider "$f" \
      > "$OUT/$tag.log" 2>&1
    echo "$tag exit $? last test: $(grep -E '::test_' "$OUT/$tag.log" | tail -1 | cut -c1-140)"
  done
done
# For a job that went silent: the stacks show each rank's Python frame. The collective the ranks
# disagree on is where one rank's top frame is an MPI/PETSc collective and another's is a
# different one, or is past it.
