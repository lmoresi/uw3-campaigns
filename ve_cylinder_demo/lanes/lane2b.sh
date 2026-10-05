#!/bin/zsh
cd $(dirname "$0")/..
while pgrep -f "lane2.sh" > /dev/null; do sleep 60; done
./run_guarded.sh 1 par_check_cell_np1 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_t_end 0.2 -uw_log_every 4
./run_guarded.sh 4 par_check_cell_np4 -uw_Wi 0.5 -uw_velocity_transport forward_nodes -uw_stress_transport forward_nodes -uw_t_end 0.2 -uw_log_every 4
python3 - <<'PY' >> runs/night_queue.log
import numpy as np
a = np.genfromtxt("runs/par_check_cell_np1/forces.csv", delimiter=",", names=True); b = np.genfromtxt("runs/par_check_cell_np4/forces.csv", delimiter=",", names=True)
n = min(len(a), len(b)); print(f"PARALLEL CHECK cell fit (reference), {n} steps: max |cd np4 - np1| {np.abs(a['cd'][:n]-b['cd'][:n]).max():.2e}, max |cl| diff {np.abs(a['cl'][:n]-b['cl'][:n]).max():.2e}")
PY
