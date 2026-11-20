"""#1166 judged by Louis's 2026-11-14 rule: does the mesh a mover makes from the
gradient density metric, and an answer computed on it, differ between rank counts
beyond tolerance?

    mpirun -n {1,2,4} python p_1166_answer_across_ranks.py

The mesh and field are #1166's: UnstructuredSimplexBox, cell size 0.07, the front
T = 0.5 (1 - tanh((y - 0.5 - 0.1 cos 6x) / 0.05)). One node_redistribution with
metric_density_from_gradient's front-following density at its defaults (the
projection at its default tolerance). Then, on the moved mesh, answers that do
not depend on the partition's numbering:

* the L2 error of the P1 interpolant of T against the exact front, the quantity
  the adaptation exists to reduce;
* a Poisson solve with source T (homogeneous Dirichlet): the integral of its
  solution and its L2 norm, solved to 1e-10;
* the smallest and largest cell area, and the mesh's total area.

Rank 0 prints one RES line. Compare the lines across np: a difference at or
below the solve's tolerance is "the same answer"."""
import numpy as np
import sympy

import underworld3 as uw

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=0.07, qdegree=3)
x, y = mesh.X
front = 0.5 * (1 - sympy.tanh((y - 0.5 - 0.1 * sympy.cos(6 * x)) / 0.05))
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1)
T.array[:, 0, 0] = uw.function.evaluate(front, T.coords).reshape(-1)

rho = uw.meshing.metric_density_from_gradient(mesh, T, refinement=4)
uw.meshing.node_redistribution(mesh, rho)

# the field re-read on the moved nodes, and its interpolation error
T.array[:, 0, 0] = uw.function.evaluate(front, T.coords).reshape(-1)
err = float(np.sqrt(uw.maths.Integral(mesh, (T.sym[0] - front) ** 2).evaluate()))
area = float(uw.maths.Integral(mesh, sympy.Integer(1)).evaluate())

u = uw.discretisation.MeshVariable("u", mesh, 1, degree=2)
poisson = uw.systems.Poisson(mesh, u_Field=u)
poisson.constitutive_model = uw.constitutive_models.DiffusionModel
poisson.constitutive_model.Parameters.diffusivity = 1.0
poisson.f = T.sym[0]
for wall in ("Bottom", "Top", "Left", "Right"):
    poisson.add_dirichlet_bc(0.0, wall)
poisson.tolerance = 1.0e-10
poisson.solve()
u_int = float(uw.maths.Integral(mesh, u.sym[0]).evaluate())
u_l2 = float(np.sqrt(uw.maths.Integral(mesh, u.sym[0] ** 2).evaluate()))

cS, cE = mesh.dm.getHeightStratum(0)
areas = np.array([mesh.dm.computeCellGeometryFVM(c)[0] for c in range(cS, cE)])
a_min = uw.mpi.comm.allreduce(float(areas.min()) if areas.size else np.inf, op=uw.MPI.MIN)
a_max = uw.mpi.comm.allreduce(float(areas.max()) if areas.size else 0.0, op=uw.MPI.MAX)
uw.pprint(f"RES np {uw.mpi.size}: interp L2 error {err:.10e}  poisson int {u_int:.12e}  "
          f"L2 {u_l2:.12e}  area {area:.12e}  cell area min {a_min:.6e} max {a_max:.6e}")
