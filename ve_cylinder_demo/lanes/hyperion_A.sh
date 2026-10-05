#!/usr/bin/env bash
# Hyperion 2026-10-05, lane A (24 ranks): the Eulerian half of the res-80 pair, the cell-fit
# third member, Newtonian at res 80, then FENE-P Wi 1 at res 80 (HYPERION.md priorities 1-3)
cd $(dirname "$0")/..
./run_guarded.sh 24 re100_grid_Wi05_r80 -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport eulerian -uw_stress_transport eulerian -uw_devss 1.0 -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
./run_guarded.sh 24 re100_ob_Wi05_cell_r80 -uw_Re 100 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
./run_guarded.sh 24 re100_newt_r80 -uw_Re 100 -uw_Wi 0 -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
./run_guarded.sh 24 re100_fene_Wi1_r80 -uw_Re 100 -uw_Wi 1.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 80 -uw_circle_ratio 1 -uw_t_end 8 -uw_snapshot_every 100
