#!/bin/bash
# kaiju_tools: the CPU-binding probe: where --exact srun steps land (job 3981)
# Where do packed 16-rank srun steps land (cores/sockets)? pack3 v1's control ran alone at 295 s/step on n4 against
# 223 on n7 in the np16 test (same answers): if a --exact 16-task step in a 48-task allocation is packed onto one
# socket, it gets half the memory bandwidth. Prints each rank's allowed CPUs; runs for seconds, no model.
#SBATCH --job-name=bindprobe
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --ntasks-per-node=48
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=00:05:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/bind_probe_%j.out
echo "node $SLURM_NODELIST"; lscpu | grep -E 'NUMA node[0-9] CPU|Socket'
show='echo "rank $SLURM_PROCID cpus $(grep Cpus_allowed_list /proc/self/status | cut -f2)"'
echo "== one step, 16 tasks, as pack3 (--exact --cpu-bind=cores)"
srun --export=ALL --exact --ntasks=16 --mem=100M --hint=nomultithread --cpu-bind=cores bash -c "$show" | sort -n -k2
echo "== three concurrent steps"
for a in A B C; do srun --export=ALL --exact --ntasks=16 --mem=100M --hint=nomultithread --cpu-bind=cores bash -c "$show" | sed "s/^/$a /" | sort -n -k3 & done; wait
echo "== one step, 16 tasks, --distribution=block:cyclic"
srun --export=ALL --exact --ntasks=16 --mem=100M --hint=nomultithread --cpu-bind=cores --distribution=block:cyclic bash -c "$show" | sort -n -k2
