#!/bin/bash
# kaiju_tools: #882's regression test (test_0078) at np 1, 2, 4 on f631ce42 (job 4068)
# #882's regression test (tests/parallel/test_0078_rebuild_memory_parallel.py: a faulted box mesh rebuilt 7 times, plain
# Stokes, bound 10 MB per rebuild) on development f631ce42, at np 1, 2 and 4 (the Science Hub, 2026-11-06: the kaiju
# leak, ~190 MB per rank per 5-step event, looks like #882 regressing through #937). The test does not use the rotated
# free-slip solve, the custom FMG or the split-fault pipeline, so a pass does not clear those paths. pytest-mpi is not in
# the image: each rank runs pytest and the test's own allreduce gives the worst rank.
#SBATCH --job-name=test882
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=32G
#SBATCH --hint=nomultithread
#SBATCH --exclude=n1
#SBATCH --time=01:00:00
#SBATCH --output=/home/louis/+Claude/kaiju/runs/test882_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/runs/test882_%j.err
export PATH=/usr/local/bin:/usr/bin:/bin
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/+Claude/kaiju/uw3/overlay-dev-f631ce42
SRC=/home/louis/+Claude/kaiju/uw3/src-f631ce42
export APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader,tcp APPTAINERENV_OMPI_MCA_btl_vader_single_copy_mechanism=none
export APPTAINERENV_PMIX_MCA_gds=hash APPTAINERENV_OMP_NUM_THREADS=1
cd "$SRC/tests/parallel"
for np in 1 2 4; do
    echo "=== np $np: $(date)"
    srun --export=ALL --ntasks=$np --mpi=pmix apptainer exec --bind "$LIB:/uw3-extra" "$SIF" \
        bash -c "PYTHONPATH=/uw3-extra:\${PYTHONPATH} exec python3 -m pytest -q -p no:cacheprovider test_0078_rebuild_memory_parallel.py -rA 2>&1 | grep -E 'passed|failed|MB per rebuild|skipped|Error' | sed \"s/^/[rank \$PMIX_RANK] /\""
done
echo "=== done: $(date)"
