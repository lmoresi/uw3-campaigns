#!/bin/bash
# #895 stage 1 (Louis, 2026-11-08 via the docs hub and C1; 2026-11-09: each fault on its
# own majority rank, which development's partition_addon already does). The FAC patch as
# ONE structural block (#934, development's default) against PER-RANK pieces (the
# control, no coarse space), qmd on both (#1022). Every line is an independent job; run
# each from this directory with the underworld3 overlay built from development at or
# after b8367c40 (#1022 merged). OMP_NUM_THREADS=1 for every rank.
# Tabulate with: python collect_895_stage1.py records
#
# FIRST the layout check: the 'apart' faults must sit on different ranks (record
# band_cells_per_rank, 'main' and 'second'). If at np 4, 8 or 16 they share a rank,
# stop and report: the one/per_rank comparison is then identical by construction.
set -u
cd "$(dirname "$0")"
mkdir -p records logs
export OMP_NUM_THREADS=1

# the layout check (also the first three timing jobs)
mpirun -np 4 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_apart_one_n320_np4.json > logs/S1_apart_one_n320_np4.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_apart_one_n320_np8.json > logs/S1_apart_one_n320_np8.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_apart_one_n320_np16.json > logs/S1_apart_one_n320_np16.log 2>&1

# np 1: the reference (the two arms are the same piece in serial)
python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_single_one_n320_np1.json > logs/S1_single_one_n320_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_single_one_n640_np1.json > logs/S1_single_one_n640_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_apart_one_n320_np1.json > logs/S1_apart_one_n320_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_apart_one_n640_np1.json > logs/S1_apart_one_n640_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_pair_one_n320_np1.json > logs/S1_pair_one_n320_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_pair_one_n640_np1.json > logs/S1_pair_one_n640_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_junction_one_n320_np1.json > logs/S1_junction_one_n320_np1.log 2>&1
python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_junction_one_n640_np1.json > logs/S1_junction_one_n640_np1.log 2>&1

# np 4, 8, 16: both arms (single, pair and junction are expected on one rank: the arms should agree there)
mpirun -np 4 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_apart_per_rank_n320_np4.json > logs/S1_apart_per_rank_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_apart_one_n640_np4.json > logs/S1_apart_one_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_apart_per_rank_n640_np4.json > logs/S1_apart_per_rank_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_single_one_n320_np4.json > logs/S1_single_one_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_single_per_rank_n320_np4.json > logs/S1_single_per_rank_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_single_one_n640_np4.json > logs/S1_single_one_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_single_per_rank_n640_np4.json > logs/S1_single_per_rank_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_pair_one_n320_np4.json > logs/S1_pair_one_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_pair_per_rank_n320_np4.json > logs/S1_pair_per_rank_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_pair_one_n640_np4.json > logs/S1_pair_one_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_pair_per_rank_n640_np4.json > logs/S1_pair_per_rank_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_junction_one_n320_np4.json > logs/S1_junction_one_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_junction_per_rank_n320_np4.json > logs/S1_junction_per_rank_n320_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_junction_one_n640_np4.json > logs/S1_junction_one_n640_np4.log 2>&1
mpirun -np 4 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_junction_per_rank_n640_np4.json > logs/S1_junction_per_rank_n640_np4.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_apart_per_rank_n320_np8.json > logs/S1_apart_per_rank_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_apart_one_n640_np8.json > logs/S1_apart_one_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_apart_per_rank_n640_np8.json > logs/S1_apart_per_rank_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_single_one_n320_np8.json > logs/S1_single_one_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_single_per_rank_n320_np8.json > logs/S1_single_per_rank_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_single_one_n640_np8.json > logs/S1_single_one_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_single_per_rank_n640_np8.json > logs/S1_single_per_rank_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_pair_one_n320_np8.json > logs/S1_pair_one_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_pair_per_rank_n320_np8.json > logs/S1_pair_per_rank_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_pair_one_n640_np8.json > logs/S1_pair_one_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_pair_per_rank_n640_np8.json > logs/S1_pair_per_rank_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_junction_one_n320_np8.json > logs/S1_junction_one_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_junction_per_rank_n320_np8.json > logs/S1_junction_per_rank_n320_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_junction_one_n640_np8.json > logs/S1_junction_one_n640_np8.log 2>&1
mpirun -np 8 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_junction_per_rank_n640_np8.json > logs/S1_junction_per_rank_n640_np8.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_apart_per_rank_n320_np16.json > logs/S1_apart_per_rank_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case apart -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_apart_one_n640_np16.json > logs/S1_apart_one_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case apart -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_apart_per_rank_n640_np16.json > logs/S1_apart_per_rank_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_single_one_n320_np16.json > logs/S1_single_one_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_single_per_rank_n320_np16.json > logs/S1_single_per_rank_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case single -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_single_one_n640_np16.json > logs/S1_single_one_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case single -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_single_per_rank_n640_np16.json > logs/S1_single_per_rank_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_pair_one_n320_np16.json > logs/S1_pair_one_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_pair_per_rank_n320_np16.json > logs/S1_pair_per_rank_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case pair -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_pair_one_n640_np16.json > logs/S1_pair_one_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case pair -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_pair_per_rank_n640_np16.json > logs/S1_pair_per_rank_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 320 -uw_out records/S1_junction_one_n320_np16.json > logs/S1_junction_one_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 320 -uw_out records/S1_junction_per_rank_n320_np16.json > logs/S1_junction_per_rank_n320_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case junction -uw_blocks one -uw_n_rungs 640 -uw_out records/S1_junction_one_n640_np16.json > logs/S1_junction_one_n640_np16.log 2>&1
mpirun -np 16 python -u stage1_895_blocks.py -uw_case junction -uw_blocks per_rank -uw_n_rungs 640 -uw_out records/S1_junction_per_rank_n640_np16.json > logs/S1_junction_per_rank_n640_np16.log 2>&1
