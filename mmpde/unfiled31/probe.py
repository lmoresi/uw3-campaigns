"""UNFILED 31: node_redistribution's partition dependence with an analytic density.

The mesh and density are those of the #1166 measurement (UnstructuredSimplexBox,
cell 0.07; density from the analytic front's gradient, no projection). After one
node_redistribution, every vertex's moved position is gathered on rank 0 keyed by
its ORIGINAL position (identical on every rank count, since the gmsh mesh is the
same) and saved, with the interpolation error of the front on the moved mesh.

    mpirun -n N python probe.py -uw_tag NAME [-uw_tol 1e-3 -uw_stol 3e-4 -uw_n_outer 150]
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(
    uw_tag="run",
    uw_tol=1.0e-3,
    uw_stol=3.0e-4,
    uw_n_outer=150,
    uw_outer_tol=1.0e-7,
)

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=0.07, qdegree=3)
x, y = mesh.X
front = 0.5 * (1 - sympy.tanh((y - 0.5 - 0.1 * sympy.cos(6 * x)) / 0.05))
rho = 1 + 15 * (sympy.diff(front, y) ** 2 + sympy.diff(front, x) ** 2) / 100.0

dm = mesh.dm
vS, vE = dm.getDepthStratum(0)
before = np.asarray(mesh.X.coords).copy()

stol = float(params.uw_stol)
uw.meshing.node_redistribution(
    mesh, rho, verbose=True,
    method_kwargs=dict(tol=float(params.uw_tol), stol=(stol if stol > 0 else None),
                       n_outer=int(params.uw_n_outer), outer_tol=float(params.uw_outer_tol)))
after = np.asarray(mesh.X.coords).copy()

T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1)
T.array[:, 0, 0] = uw.function.evaluate(front, T.coords).reshape(-1)
err = float(np.sqrt(uw.maths.Integral(mesh, (T.sym[0] - front) ** 2).evaluate()))

pairs = np.hstack([before, after])
allp = np.vstack(uw.mpi.comm.allgather(pairs))
if uw.mpi.rank == 0:
    order = np.lexsort((allp[:, 1], allp[:, 0]))
    allp = allp[order]
    keep = np.ones(len(allp), bool)
    keep[1:] = np.any(allp[1:, :2] != allp[:-1, :2], axis=1)
    np.save(f"out/{params.uw_tag}.npy", allp[keep])
uw.pprint(f"RES {params.uw_tag} np {uw.mpi.size}: interp L2 error {err:.10e} "
          f"vertices {int(keep.sum()) if uw.mpi.rank == 0 else 0}")
