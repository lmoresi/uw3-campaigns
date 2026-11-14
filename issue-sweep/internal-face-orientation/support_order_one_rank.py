"""One rank: does the load on an interior surface depend on which of a face's two
cells PETSc lists first?

PETSc integrates a boundary term on a face from the face's first support cell.
On one rank that is the cell the face was created from, where the face has
orientation 0. A rank that holds only the other cell sees the face with a
non-zero orientation. This probe reproduces that on one rank by swapping the
support order of every `Internal` face in memory (`-uw_swap_support 1`) before
anything is assembled, and writes the same file as `internal_load_by_face.py`
(`internal_load_swap<0|1>.npz`). It also prints the orientation of each
`Internal` face in its first and second support cell.

    python support_order_one_rank.py -uw_swap_support 0 -uw_cell_size 0.3
    python support_order_one_rank.py -uw_swap_support 1 -uw_cell_size 0.3
    python compare_internal_load.py internal_load_swap0.npz internal_load_swap1.npz
"""
from collections import Counter

import numpy as np
import sympy

import underworld3 as uw

params = uw.Params(uw_cell_size=0.3, uw_multiplier_degree=2, uw_swap_support=0)
SWAP = int(params.uw_swap_support)
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

# before anything is assembled: the orientation census and the swap, on the mesh's DM
# (the solver's DM is built from it)
base = mesh.dm
bf_start, bf_end = base.getHeightStratum(1)
istratum = base.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Internal.value)
ifaces = [int(p) for p in istratum.getIndices() if bf_start <= p < bf_end]
census = Counter()
for face in ifaces:
    support = base.getSupport(face)
    orientation = []
    for cell in support:
        cone = list(base.getCone(cell))
        orientation.append(int(base.getConeOrientation(cell)[cone.index(face)]))
    census[tuple(orientation)] += 1
    if SWAP:
        base.setSupport(face, np.array(support[::-1], dtype=support.dtype))
print(f"Internal faces: {len(ifaces)}; (orientation in first cell, in second cell): count "
      f"{dict(sorted(census.items()))}; support order swapped: {bool(SWAP)}", flush=True)
after = Counter()
for face in ifaces:
    cell = base.getSupport(face)[0]
    cone = list(base.getCone(cell))
    after[int(base.getConeOrientation(cell)[cone.index(face)])] += 1
print(f"orientation in the first support cell as PETSc will now see it: {dict(sorted(after.items()))}", flush=True)

stokes._build()

dm = stokes.dm
check = Counter()
df_start, df_end = dm.getHeightStratum(1)
for p in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Internal.value).getIndices():
    if df_start <= p < df_end:
        cell = dm.getSupport(p)[0]
        cone = list(dm.getCone(cell))
        check[int(dm.getConeOrientation(cell)[cone.index(p)])] += 1
print(f"the same on the solver's DM: {dict(sorted(check.items()))}", flush=True)
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
    np.savez(f"internal_load_swap{SWAP}.npz",
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
