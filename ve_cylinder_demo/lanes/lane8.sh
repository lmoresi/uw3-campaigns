#!/bin/zsh
cd $(dirname "$0")/..
./run_guarded.sh 4 re200_fwd_global2_r40 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_velocity_reconstruction global -uw_bubble_penalty 0.1 -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 5
./run_guarded.sh 4 re100_fene_Wi4_r20 -uw_Re 100 -uw_Wi 4.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_t_end 8
