#!/bin/bash
# Truncate each corrected example after its last corrected BC call and run it. Serial.
cd /Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/kept-transfer || exit 1
export OMP_NUM_THREADS=1 PYVISTA_OFF_SCREEN=true MPLBACKEND=Agg
P=~/+Simulations/issue_sweep/review_1139
: > $P/examples_run/summary.txt
for f in \
 docs/examples/WIP/developer_tools/Timing_NonLinear_ShearBand.py \
 docs/examples/convection/advanced/Ex_Convection_Cartesian-Swarm.py \
 docs/examples/convection/intermediate/Ex_Convection_2_SLCN_Cartesian-TdepVisc.py \
 docs/examples/convection/intermediate/Ex_Convection_4_SLCN_Cartesian-NL.py \
 docs/examples/convection/intermediate/Ex_Convection_5_SLCN_Cartesian-Yield.py \
 docs/examples/convection/intermediate/Ex_Convection_Cartesian_ThermoChem.py \
 docs/examples/fluid_mechanics/basic/falling_sphere.py \
 docs/examples/fluid_mechanics/intermediate/Ex_Stokes_Disk_CylCoords_DEPRECATED_NATIVE.py \
 docs/examples/utilities/advanced/Ex_Tensor_Variables_etc.py ; do
  b=$(basename $f .py)
  n=$(grep -nE '^\s*(stokes|stokes_xy)\.add_(dirichlet|essential)_bc\(\(None, 0(\.0)?\), ' $f | tail -1 | cut -d: -f1)
  head -n $n $f > $P/examples_run/$b.trunc.py
  echo 'print("REACHED_END_OF_BC_CALLS", [ (str(b.fn.T), list(map(int,b.components)), b.boundary) for b in (stokes_xy if "stokes_xy" in dir() else stokes).essential_bcs ])' >> $P/examples_run/$b.trunc.py
  ( cd $P/examples_run && perl -e 'alarm 240; exec @ARGV' pixi run --manifest-path /Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/kept-transfer/pixi.toml -e runtime python $b.trunc.py > $b.log 2>&1 ; echo "$b lines=$n exit=$?" >> summary.txt )
done
echo DONE >> $P/examples_run/summary.txt
