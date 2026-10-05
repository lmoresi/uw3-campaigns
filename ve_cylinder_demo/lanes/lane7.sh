#!/bin/zsh
cd $(dirname "$0")/..
./run_guarded.sh 4 re100_ob_Wi1_r40 -uw_Re 100 -uw_Wi 1.0 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
./run_guarded.sh 4 re100_ob_Wi2_r40 -uw_Re 100 -uw_Wi 2.0 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
