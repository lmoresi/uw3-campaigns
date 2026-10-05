#!/bin/zsh
cd $(dirname "$0")/..
# the global projection in parallel against serial: 24 steps, forces compared
./run_guarded.sh 1 par_check_np1 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_t_end 0.2 -uw_log_every 4
./run_guarded.sh 4 par_check_np4 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_t_end 0.2 -uw_log_every 4
python3 - <<'PY' >> runs/night_queue.log
import numpy as np
a = np.genfromtxt("runs/par_check_np1/forces.csv", delimiter=",", names=True); b = np.genfromtxt("runs/par_check_np4/forces.csv", delimiter=",", names=True)
n = min(len(a), len(b)); print(f"PARALLEL CHECK global projection, {n} steps: max |cd np4 - np1| {np.abs(a['cd'][:n]-b['cd'][:n]).max():.2e}, max |cl| diff {np.abs(a['cl'][:n]-b['cl'][:n]).max():.2e} (cd ~ {a['cd'][n-1]:.3f})")
PY
./run_guarded.sh 4 re100_fene_Wi1_r40 -uw_Re 100 -uw_Wi 1.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
./run_guarded.sh 4 re200_fwd_global2_r40 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_velocity_reconstruction global -uw_bubble_penalty 0.1 -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 5
./run_guarded.sh 4 re100_fene_Wi4_r40 -uw_Re 100 -uw_Wi 4.0 -uw_relaxation fene_p -uw_L2 100 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_reconstruction global -uw_resolution 40 -uw_circle_ratio 0.5 -uw_t_end 8
