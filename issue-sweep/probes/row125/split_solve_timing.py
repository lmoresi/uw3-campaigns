"""Row 125: what the fault-region partition costs a Stokes solve.

partition_addon gives each fault region to one rank (the owner) and balances
only the cells outside the regions; the cut and the split move nothing after it,
and nothing rebalances before the solve. On the adapt k 3, h 0.1 fixture the
region is more than half the finest cells, so at np 8 the owner holds about
4x the mean.

Three arms on the same adapted mesh (unit box, cellSize h, refinement 1, an
add-on of k levels toward the trace), the same Stokes solve (simple shear on the walls, a buoyant blob):
  plain   the adapted mesh as adapt partitions it; no fault
  region  the same mesh after partition_addon for the trace (the partition
          add_fault would make); no fault. Same cells as plain, so the
          difference is the partition alone
  fault   add_fault on the trace (partition, cut, split), frictionless fault
Each arm solves twice; the second solve (zero initial guess) is the timed one,
so JIT and setup are out of it. RES lines on rank 0:

    mpirun -n 8 python split_solve_timing.py -uw_arm plain -uw_k 3 -uw_cellsize 0.1
"""
import time

import numpy as np
import sympy

import underworld3 as uw

params = uw.Params(
    uw_arm=uw.Param("plain", description="plain | region | fault"),
    uw_k=uw.Param(3, description="add-on levels toward the trace"),
    uw_cellsize=uw.Param(0.1, description="base cell size"),
)
comm = uw.mpi.comm
ARM, K, H = str(params.uw_arm), int(params.uw_k), float(params.uw_cellsize)
TIP_A, TIP_B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
TRACE = np.vstack([TIP_A, TIP_B])

base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=H, refinement=1, qdegree=2)
pts = np.column_stack([np.linspace(TIP_A[0], TIP_B[0], 9),
                       np.linspace(TIP_A[1], TIP_B[1], 9), np.zeros(9)])
guide = uw.meshing.Surface("guide", base, pts)
guide.discretize()
mesh = base.adapt(guide.refinement_metric_function(
    h_near=H / 2 / 2**K, h_far=H / 2, width=0.08, profile="linear"), max_levels=K)

if ARM == "region":
    from underworld3.utilities.addon_partition import mark_polylines, partition_addon
    mesh = partition_addon(mesh, mark_polylines([TRACE]), layers=1)
elif ARM == "fault":
    mesh = mesh.add_fault([("Flt", TRACE)])

cS, cE = mesh.dm.getHeightStratum(0)
cells = comm.allgather(cE - cS)

x, y = mesh.X
stokes = uw.systems.Stokes(mesh)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.tolerance = 1.0e-6
stokes.petsc_use_pressure_nullspace = True
# a buoyant blob below the trace, so the solve has work to do (simple shear on
# the walls alone is met exactly by the boundary values)
stokes.bodyforce = sympy.Matrix(
    [0, sympy.exp(-((x - 0.5) ** 2 + (y - 0.3) ** 2) / 0.02)])
for side in ("Top", "Bottom", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), side)
if ARM == "fault":
    stokes.add_fault_bc(0, "Flt")

times, its = [], []
for attempt in range(2):
    # start each solve from zero: the second would otherwise begin converged
    stokes.u.array[...] = 0.0
    stokes.p.array[...] = 0.0
    comm.Barrier()
    t0 = time.perf_counter()
    stokes.solve(zero_init_guess=True)
    comm.Barrier()
    times.append(time.perf_counter() - t0)
    # the solve report, not stokes.snes: a solve with a fault (rotated
    # constraints) runs its own Krylov solve and never touches the SNES
    rep = stokes.solve_report
    its.append((rep.nl_its, rep.ksp_its, rep.reason_str,
                ",".join(f"{r.name}={r.its}" for r in rep.sub.values())))

uw.pprint(f"RES arm={ARM} k={K} h={H} np={comm.size} cells={cells} "
          f"max/mean={max(cells) / np.mean(cells):.2f} "
          f"first_s={times[0]:.3f} timed_s={times[1]:.3f} "
          f"snes_its={its[1][0]} ksp_its={its[1][1]} reason={its[1][2]} "
          f"sub=[{its[1][3]}] first_its={its[0][:2]}")
