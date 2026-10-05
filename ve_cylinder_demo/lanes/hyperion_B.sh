#!/usr/bin/env bash
# Hyperion 2026-10-05, lane B (24 ranks): the global-projection half of the res-80 pair, then
# FENE-P with the forward global histories: Wi 1 and 2 at res 40, Wi 0.5 at res 80
cd $(dirname "$0")/..
./run_guarded.sh 24 re100_ob_Wi05_r80 -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
./run_guarded.sh 24 re100_fene_Wi1_r40 -uw_Re 100 -uw_Wi 1.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8 -uw_debug_fene 40
./run_guarded.sh 24 re100_fene_Wi2_r40 -uw_Re 100 -uw_Wi 2.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
./run_guarded.sh 24 re100_fene_Wi05_r80 -uw_Re 100 -uw_Wi 0.5 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
