#!/bin/bash
# Build each mutant of the two-call routine, run the bitwise test, restore.
W=UW3_WORKTREE
D=~/+Simulations/issue_sweep/probe_962/two_call
H=src/underworld3/cython/petsc_compat.h
T=tests/test_0786_stokes_jacobian_and_preconditioner_one_call_each.py
export OMP_NUM_THREADS=1
cd $W || exit 1
git diff --quiet || { echo "tree not clean"; exit 1; }
for m in first_call_on_the_whole_system second_call_keeps_the_jacobian_kernels jacobian_tables_not_restored preconditioner_tables_not_restored boundary_tables_left_alone not_registered; do
  python3 $D/mutate.py $W/$H $m || { echo "MUTATE FAILED $m"; git checkout -- $H; continue; }
  ./uw build > $D/build_mutant_$m.log 2>&1; echo "--- $m build exit $?"
  pixi run -e runtime pytest $T -q -p no:cacheprovider 2>&1 | tail -6
  git checkout -- $H
done
git diff --quiet && echo "tree clean"
./uw build > $D/build_restored.log 2>&1; echo "--- restored build exit $?"
pixi run -e runtime pytest $T -q -p no:cacheprovider 2>&1 | tail -2
