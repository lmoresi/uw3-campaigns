#!/bin/bash
# The add-on matrix row 7 (dev hub, 2026-11-01), for the kaiju dev runner: does a finer
# ladder do physical work, and does refining the base under the fault corridor give the
# slip resolution instead? H0 only. Every line is an independent job; run each from this
# directory with the underworld3 overlay built from bugfix/rotated-nullspace-from-mesh @
# 964dc3ce (the rows 4-5 build). OMP_NUM_THREADS=1 for every rank. Row 7 runs ahead of
# the remaining iterative-patch probes. Tabulate with: python collect_row7.py records
set -u
cd "$(dirname "$0")"
mkdir -p records logs
export OMP_NUM_THREADS=1

# problem A (the 022 fixture, h_b = 1/32, L/h_b = 13.19), np 1
# unrefined: h_b/S 0.99, 1.97, 4.0, 6.1, 8.0, 12.1, 16.0, 24.3 (the note's sweep is 6-24), 48.5 (the reference)
python -u row7_linear.py -uw_n_rungs 13 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n13_d0.json > logs/A7_n13_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 26 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n26_d0.json > logs/A7_n26_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 53 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n53_d0.json > logs/A7_n53_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 80 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n80_d0.json > logs/A7_n80_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 106 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n106_d0.json > logs/A7_n106_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 160 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n160_d0.json > logs/A7_n160_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 211 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n211_d0.json > logs/A7_n211_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 320 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n320_d0.json > logs/A7_n320_d0.log 2>&1
python -u row7_linear.py -uw_n_rungs 640 -uw_depth 0 -uw_rings 1 -uw_out records/A7_n640_d0.json > logs/A7_n640_d0.log 2>&1
# corridor refined k levels (h_loc = h_b/2^k), half-width 1 and 2 base cells, h_loc/S 1 and 2,
# and 1.5 at the note's 80 and 320 rungs (the same S as those unrefined arms)
python -u row7_linear.py -uw_n_rungs 26 -uw_depth 1 -uw_rings 1 -uw_out records/A7_n26_d1_r1.json > logs/A7_n26_d1_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 26 -uw_depth 1 -uw_rings 2 -uw_out records/A7_n26_d1_r2.json > logs/A7_n26_d1_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 53 -uw_depth 1 -uw_rings 1 -uw_out records/A7_n53_d1_r1.json > logs/A7_n53_d1_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 53 -uw_depth 1 -uw_rings 2 -uw_out records/A7_n53_d1_r2.json > logs/A7_n53_d1_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 53 -uw_depth 2 -uw_rings 1 -uw_out records/A7_n53_d2_r1.json > logs/A7_n53_d2_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 53 -uw_depth 2 -uw_rings 2 -uw_out records/A7_n53_d2_r2.json > logs/A7_n53_d2_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 80 -uw_depth 2 -uw_rings 1 -uw_out records/A7_n80_d2_r1.json > logs/A7_n80_d2_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 80 -uw_depth 2 -uw_rings 2 -uw_out records/A7_n80_d2_r2.json > logs/A7_n80_d2_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 106 -uw_depth 2 -uw_rings 1 -uw_out records/A7_n106_d2_r1.json > logs/A7_n106_d2_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 106 -uw_depth 2 -uw_rings 2 -uw_out records/A7_n106_d2_r2.json > logs/A7_n106_d2_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 106 -uw_depth 3 -uw_rings 1 -uw_out records/A7_n106_d3_r1.json > logs/A7_n106_d3_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 106 -uw_depth 3 -uw_rings 2 -uw_out records/A7_n106_d3_r2.json > logs/A7_n106_d3_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 160 -uw_depth 3 -uw_rings 1 -uw_out records/A7_n160_d3_r1.json > logs/A7_n160_d3_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 160 -uw_depth 3 -uw_rings 2 -uw_out records/A7_n160_d3_r2.json > logs/A7_n160_d3_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 211 -uw_depth 3 -uw_rings 1 -uw_out records/A7_n211_d3_r1.json > logs/A7_n211_d3_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 211 -uw_depth 3 -uw_rings 2 -uw_out records/A7_n211_d3_r2.json > logs/A7_n211_d3_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 211 -uw_depth 4 -uw_rings 1 -uw_out records/A7_n211_d4_r1.json > logs/A7_n211_d4_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 211 -uw_depth 4 -uw_rings 2 -uw_out records/A7_n211_d4_r2.json > logs/A7_n211_d4_r2.log 2>&1
python -u row7_linear.py -uw_n_rungs 320 -uw_depth 4 -uw_rings 1 -uw_out records/A7_n320_d4_r1.json > logs/A7_n320_d4_r1.log 2>&1
python -u row7_linear.py -uw_n_rungs 320 -uw_depth 4 -uw_rings 2 -uw_out records/A7_n320_d4_r2.json > logs/A7_n320_d4_r2.log 2>&1

# problem B (the yielding-lid box, h_b = 1/32; today's S 0.004, h_b/S 7.9), np 4
# unrefined: S h_b, h_b/2, h_b/4, 0.004, h_b/16; the tip at depth 0.012 (today's 3 x 0.004) and by
# the fixture's 3S rule (the two coincide at 0.004)
mpirun -np 4 python -u row7_box.py -uw_spacing 0.03125 -uw_depth 0 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.03125_d0.json > logs/B7_s0.03125_d0.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.03125 -uw_depth 0 -uw_rings 1 -uw_tip 3S -uw_out records/B7_s0.03125_d0_tip3S.json > logs/B7_s0.03125_d0_tip3S.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.015625 -uw_depth 0 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.015625_d0.json > logs/B7_s0.015625_d0.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.015625 -uw_depth 0 -uw_rings 1 -uw_tip 3S -uw_out records/B7_s0.015625_d0_tip3S.json > logs/B7_s0.015625_d0_tip3S.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 0 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.0078125_d0.json > logs/B7_s0.0078125_d0.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 0 -uw_rings 1 -uw_tip 3S -uw_out records/B7_s0.0078125_d0_tip3S.json > logs/B7_s0.0078125_d0_tip3S.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.004 -uw_depth 0 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.004_d0.json > logs/B7_s0.004_d0.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.001953125 -uw_depth 0 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.001953125_d0.json > logs/B7_s0.001953125_d0.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.001953125 -uw_depth 0 -uw_rings 1 -uw_tip 3S -uw_out records/B7_s0.001953125_d0_tip3S.json > logs/B7_s0.001953125_d0_tip3S.log 2>&1
# corridor refined k levels, half-width 1 and 2 base cells, h_loc/S 1 and 2; today's S 0.004 at k 2 and 3
mpirun -np 4 python -u row7_box.py -uw_spacing 0.015625 -uw_depth 1 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.015625_d1_r1.json > logs/B7_s0.015625_d1_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.015625 -uw_depth 1 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.015625_d1_r2.json > logs/B7_s0.015625_d1_r2.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 1 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.0078125_d1_r1.json > logs/B7_s0.0078125_d1_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 1 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.0078125_d1_r2.json > logs/B7_s0.0078125_d1_r2.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 2 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.0078125_d2_r1.json > logs/B7_s0.0078125_d2_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.0078125 -uw_depth 2 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.0078125_d2_r2.json > logs/B7_s0.0078125_d2_r2.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.004 -uw_depth 2 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.004_d2_r1.json > logs/B7_s0.004_d2_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.004 -uw_depth 2 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.004_d2_r2.json > logs/B7_s0.004_d2_r2.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.004 -uw_depth 3 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.004_d3_r1.json > logs/B7_s0.004_d3_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.004 -uw_depth 3 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.004_d3_r2.json > logs/B7_s0.004_d3_r2.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.001953125 -uw_depth 3 -uw_rings 1 -uw_tip 0.012 -uw_out records/B7_s0.001953125_d3_r1.json > logs/B7_s0.001953125_d3_r1.log 2>&1
mpirun -np 4 python -u row7_box.py -uw_spacing 0.001953125 -uw_depth 3 -uw_rings 2 -uw_tip 0.012 -uw_out records/B7_s0.001953125_d3_r2.json > logs/B7_s0.001953125_d3_r2.log 2>&1
