#!/bin/zsh
cd $(dirname "$0")/..
while pgrep -f "lane5.sh" > /dev/null; do sleep 60; done
./run_guarded.sh 4 re100_fene_Wi2_r20 -uw_Re 100 -uw_Wi 2.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_t_end 8
