"""A rank-dependent read of a MeshVariable's array, then any collective."""
import sys
import numpy as np, underworld3 as uw
mesh = uw.meshing.UnstructuredSimplexBox(cellSize=0.25)
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
mode = sys.argv[1]
if mode == "rank0_read":
    if uw.mpi.rank == 0:
        print("rank 0 reads", float(np.abs(v.array).max()), flush=True)
elif mode == "all_read":
    print(uw.mpi.rank, "reads", float(np.abs(v.array).max()), flush=True)
uw.mpi.comm.Barrier()
s = uw.mpi.comm.allreduce(1)
print(uw.mpi.rank, "PASSED the collective", s, flush=True)
