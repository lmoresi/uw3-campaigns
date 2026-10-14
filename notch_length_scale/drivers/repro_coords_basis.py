"""Repro: _get_coords_for_basis on a small 3-D notch mesh at high rank count, per rank."""
import sys
import os
import numpy as np
import underworld3 as uw
from mpi4py import MPI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notch_model as nm

msh = sys.argv[1]
mesh = nm.load_notch_mesh(msh, 0)
cS, cE = mesh.dm.getHeightStratum(0)
vS, vE = mesh.dm.getDepthStratum(0)
out = []
for deg in (1, 2):
    try:
        c = mesh._get_coords_for_basis(deg, True)
        out.append(f"deg{deg} ok {c.shape[0]}")
    except Exception as e:
        out.append(f"deg{deg} FAIL {type(e).__name__} {str(e)[:60]}")
rows = MPI.COMM_WORLD.gather((uw.mpi.rank, cE - cS, vE - vS, out), root=0)
if uw.mpi.rank == 0:
    for r in rows:
        print(r)
