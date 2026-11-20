"""UNFILED 36: the annulus rotated datum solve fails at PC setup at np 3 with an
empty rank or a random partition (H7, review of #1261). Which partition, which
wall condition and which sub-preconditioner fail?  uw.Params: partition
default|simple|gather; wall datum|freeslip|dirichlet; velocity_pc default|lu.

Written by W1 (2026-11-21), stored here by C1 for a parallel desk. Run on #1261's
head or on development after #1261 merges: development before it fails serially
on the pure-datum case (W1, macOS), which is not UNFILED 36.

  OMP_NUM_THREADS=1 mpirun -n 3 python p_annulus_datum_pcsetup.py \
      -uw_partition {default|simple|gather} -uw_wall {datum|freeslip|dirichlet} \
      -uw_velocity_pc {default|lu}

Caveats: mesh distribution may not call setFromOptions, so check the printed cells
per rank (use the desk's own empty-rank / random partitions if 'gather' does not
empty ranks); the rotated KSP has its own prefix, so check velocity_pc in RESULT.
"""
import numpy as np
import sympy
from petsc4py import PETSc
import underworld3 as uw
from underworld3.utilities import rotated_bc

seen = []
_destroy = rotated_bc._destroy_rotated_ksp_ctx
def _read_then_destroy(ctx):
    if ctx is not None and ctx.get("ksp") is not None:
        ksp = ctx["ksp"]; pc = ksp.getPC()
        row = [f"rotated KSP {ksp.getConvergedReason()} PC {pc.getType()} failed {pc.getFailedReason()}"]
        if pc.getType() == "fieldsplit":
            for name, sub in zip(("velocity", "pressure"), pc.getFieldSplitSubKSP()):
                spc = sub.getPC()
                row.append(f"  {name}: KSP {sub.getConvergedReason()} its {sub.getIterationNumber()} "
                           f"PC {spc.getType()} failed {spc.getFailedReason()}")
                if spc.getType() == "mg":
                    coarse = spc.getMGCoarseSolve().getPC()
                    row.append(f"    coarse PC {coarse.getType()} failed {coarse.getFailedReason()}")
        seen.append(row)
    _destroy(ctx)
rotated_bc._destroy_rotated_ksp_ctx = _read_then_destroy

params = uw.Params(partition="default", wall="datum", velocity_pc="default")
partition, wall, velocity_pc = str(params.partition), str(params.wall), str(params.velocity_pc)
if partition != "default":
    PETSc.Options()["petscpartitioner_type"] = partition
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.2, qdegree=3)
c0, c1 = mesh.dm.getHeightStratum(0)
uw.pprint(f"PARTITION {partition}: cells per rank {uw.mpi.comm.gather(c1 - c0, root=0)}")
v = uw.discretisation.MeshVariable("V36", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P36", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
r, th = mesh.CoordinateSystem.xR
stokes.bodyforce = sympy.Matrix([[0, 0]])
if wall == "datum":
    stokes.add_rotated_freeslip_bc(0.1 * sympy.cos(2 * th), "Upper")
    stokes.add_rotated_freeslip_bc(0, "Lower")
elif wall == "freeslip":
    stokes.bodyforce = sympy.Matrix([[0, -sympy.cos(sympy.pi * r)]])
    stokes.add_rotated_freeslip_bc(0, "Upper"); stokes.add_rotated_freeslip_bc(0, "Lower")
else:
    stokes.bodyforce = sympy.Matrix([[0, -sympy.cos(sympy.pi * r)]])
    stokes.add_dirichlet_bc((0.0, 0.0), "Upper"); stokes.add_dirichlet_bc((0.0, 0.0), "Lower")
if velocity_pc == "lu":
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
stokes.tolerance = 1.0e-6
error = None
try:
    stokes.solve()
except Exception as e:
    error = f"{type(e).__name__}: {str(e)[:200]}"
info = getattr(stokes, "_rotated_freeslip_info", None) or {}
mine = [f"rank {uw.mpi.rank}: cells {c1 - c0}; converged {info.get('converged')} "
        f"ksp_reason {info.get('ksp_reason')} its {info.get('ksp_its')} "
        f"velocity_pc {info.get('velocity_pc')} coarse {info.get('coarse_solve')} "
        f"linear_failure {str(info.get('linear_failure'))[:160]}"]
if wall == "dirichlet":
    mine.append(f"  (no rotated wall) SNES {stokes.snes.getConvergedReason()} KSP {stokes.snes.getKSP().getConvergedReason()}")
mine += ["  " + r_ for row in seen for r_ in row]
if error:
    mine.append(f"  raised {error}")
lines = uw.mpi.comm.gather(mine, root=0)
if uw.mpi.rank == 0:
    print(f"RESULT partition={partition} wall={wall} velocity_pc={velocity_pc}")
    for block in lines:
        print("\n".join(block))
