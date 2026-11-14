"""#1150: where does the velocity load differ between 1 rank and 8?

H1's residual moments (H1-RESULTS-np2-8.md) show the velocity load, and only the
load, differs at 8 ranks by 2e-5 relative. The load is the l = 2 traction on the
`Internal` surface, whose faces are interior: each has a cell on either side,
and a partition can put the two cells on different ranks.

The mesh is NOT refined (`SphericalShellInternalBoundary` with no refinement),
as in the issue. The solver is built and never solved.

This prints, and writes to `internal_load_np<N>.npz` in the working directory:

  F  the faces of `Internal`: for each (by global point number) the ranks that
     hold it, the number of its support cells each of them holds, and which
     rank owns it. A face held by more than one rank is one whose two cells are
     on different ranks. The counts: faces, faces held by 1, 2, more ranks,
     and the distribution of the summed support size (2 for every face when
     the distribution has no overlap).
  G  the velocity residual with every field zero, which is the load: each
     rank's own rows at its own nodes, with the node's coordinates. Rows are
     kept per rank and not summed here.

`compare_internal_load.py` then matches two such files node by node.

    mpirun -np N python internal_load_by_face.py -uw_cell_size 0.2
"""
from collections import Counter

import numpy as np
import sympy

import underworld3 as uw

params = uw.Params(uw_cell_size=0.2, uw_multiplier_degree=2)
CELL_SIZE = float(params.uw_cell_size)
DEGREE = int(params.uw_multiplier_degree)
comm = uw.mpi.comm

mesh = uw.meshing.SphericalShellInternalBoundary(
    radiusOuter=1.0, radiusInternal=0.775, radiusInner=0.55,
    cellSize=CELL_SIZE, qdegree=2, degree=1)
velocity = uw.discretisation.MeshVariable("U1150", mesh, mesh.dim, degree=2, vtype=uw.VarType.VECTOR)
pressure = uw.discretisation.MeshVariable("P1150", mesh, 1, degree=1, continuous=True)

stokes = uw.systems.Stokes_Constrained(mesh, velocityField=velocity, pressureField=pressure)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = sympy.Matrix([0.0, 0.0, 0.0])
theta = mesh.CoordinateSystem.xR[1]
unit_r = mesh.CoordinateSystem.unit_e_0
stokes.add_natural_bc(sympy.assoc_legendre(2, 0, sympy.cos(theta)) * unit_r, mesh.boundaries.Internal.name)
stokes.add_constraint_bc(0.0, "Upper", normal=unit_r, augmentation_base=1.0e4, degree=DEGREE)
stokes.add_constraint_bc(0.0, "Lower", normal=-unit_r, augmentation_base=1.0e4, degree=DEGREE)
stokes.petsc_use_nullspace = True
stokes.tolerance = 1.0e-7
stokes.petsc_options["snes_type"] = "ksponly"
stokes._build()

dm = stokes.dm
p_start, p_end = dm.getChart()
raw = dm.createPointNumbering().getIndices().copy()
owned = raw >= 0
global_id = np.where(owned, raw, -(raw + 1))
f_start, f_end = dm.getHeightStratum(1)
v_start, v_end = dm.getDepthStratum(0)
c_start, c_end = dm.getHeightStratum(0)
n_cells = comm.allreduce(int(np.count_nonzero(owned[c_start - p_start:c_end - p_start])), op=uw.MPI.SUM)
uw.pprint(0, f"ranks {uw.mpi.size} | cell size {CELL_SIZE} | cells {n_cells} | no refinement "
             f"| overlap {dm.getDistributionOverlap() if hasattr(dm, 'getDistributionOverlap') else 'n/a'}")

# F. the faces of Internal
coord_section = dm.getCoordinateSection()
coord_array = dm.getCoordinatesLocal().array
value = mesh.boundaries.Internal.value
stratum = dm.getLabel("UW_Boundaries").getStratumIS(value)
points = stratum.getIndices() if stratum and stratum.getSize() > 0 else np.empty(0, dtype=int)
faces = [int(p) for p in points if f_start <= p < f_end]

mine = []
for face in faces:
    vertices = [int(q) for q in dm.getTransitiveClosure(face)[0] if v_start <= q < v_end]
    xyz = np.array([coord_array[coord_section.getOffset(v):coord_section.getOffset(v) + 3]
                    for v in vertices])
    mine.append((int(global_id[face - p_start]), uw.mpi.rank, int(dm.getSupportSize(face)),
                 bool(owned[face - p_start]), xyz))

held = {}
for per_rank in comm.allgather(mine):
    for gid, rank, support, is_owner, xyz in per_rank:
        entry = held.setdefault(gid, {"ranks": [], "support": [], "owner": -1, "xyz": xyz})
        entry["ranks"].append(rank)
        entry["support"].append(support)
        if is_owner:
            entry["owner"] = rank
            entry["xyz"] = xyz

by_ranks = Counter(len(e["ranks"]) for e in held.values())
by_support = Counter(sum(e["support"]) for e in held.values())
unowned = sum(1 for e in held.values() if e["owner"] < 0)
uw.pprint(0, f"F. Internal (label value {value}): {len(held)} faces")
uw.pprint(0, f"   held by this many ranks: {dict(sorted(by_ranks.items()))}")
uw.pprint(0, f"   support cells summed over the ranks holding a face: {dict(sorted(by_support.items()))}")
uw.pprint(0, f"   faces no rank owns: {unowned}")
uw.pprint(0, f"   faces of the label per rank: {comm.allgather(len(faces))}")

# G. the load, row by row, per rank
for var in stokes.fields.values():
    var.array[...] = 0.0
rows = stokes.compute_volume_residual_fields()
coords = np.asarray(stokes.fields["velocity"].coords)
values = np.asarray(rows["velocity"]).reshape(coords.shape[0], -1)
gathered = comm.gather((coords, values, np.full(coords.shape[0], uw.mpi.rank)), root=0)

if uw.mpi.rank == 0:
    node_xyz = np.concatenate([g[0] for g in gathered])
    node_load = np.concatenate([g[1] for g in gathered])
    node_rank = np.concatenate([g[2] for g in gathered])
    order = sorted(held)
    np.savez(f"internal_load_np{uw.mpi.size}.npz",
             face_id=np.array(order),
             face_xyz=np.array([held[g]["xyz"] for g in order]),
             face_ranks=np.array([len(held[g]["ranks"]) for g in order]),
             face_support=np.array([sum(held[g]["support"]) for g in order]),
             face_owner=np.array([held[g]["owner"] for g in order]),
             node_xyz=node_xyz, node_load=node_load, node_rank=node_rank)
    radius = np.linalg.norm(node_xyz, axis=1)
    size = np.abs(node_load).max(axis=1)
    loaded = size > 1.0e-12 * size.max()      # above round-off of the largest row
    print(f"G. velocity rows over all ranks: {len(node_xyz)}; with a load above round-off: {int(loaded.sum())}; "
          f"radius of the loaded nodes: {radius[loaded].min():.6f} to {radius[loaded].max():.6f}; "
          f"sum of the load: {node_load.sum(axis=0)}", flush=True)
    print(f"wrote internal_load_np{uw.mpi.size}.npz", flush=True)
