"""#1150: do the ranks that share a wall point agree on its multiplier unknown?

The case is the one of the issue: a 3-D shell with an internal surface, an l = 2
load on it, and multiplier free slip (degree 2) on `Upper` and `Lower`. The
solver is built and never solved. Nothing here is timed.

For each wall this prints, at the rank count it is run with:

  A  the wall's points: those carrying the `UW_Boundaries` value on some rank,
     the closure of those on each rank, and the union of the closures over all
     ranks (by global point number). A rank's "held without a labelled point"
     are the points of the union it holds outside its own closure.
  B  PETSc's label completion (`DMPlexLabelComplete` on a scratch label holding
     the local stratum) against the union of A: the points on which they differ.
  C  the multiplier's unknowns in the solver's local section: how many a rank
     keeps, the global count (kept unknowns at owned points), the wall points a
     rank holds and pins, and the shared wall points on which the ranks that hold
     them disagree (kept by some, pinned by others).
  D  every field together: the shared points where a rank's count of free
     unknowns differs from the owner's, read from the global section.
  E  the assembled residual, with no solve: for two states set from the
     coordinates (every field zero, which leaves the load; and a smooth
     velocity, pressure and multiplier) each rank's own integrals are
     contracted with fixed functions of the coordinates and summed over the
     ranks. Assembly is that sum, so each number is a property of the mesh and
     the equations: it must agree across rank counts to round-off (1e-12
     relative). A face of `Internal` integrated on two ranks, or a rank's
     integral that differs, shows here. The rows a rank pins are not removed
     from these sums; C and D are the check on those.

The global counts in A and C are the same mesh at every rank count, so they
must not change with it. Run at 1, 2, 4 and 8 ranks:

    mpirun -np N python multiplier_unknowns_by_rank.py -uw_cell_size 0.2
"""
from collections import Counter

import numpy as np
import sympy
from petsc4py import PETSc

import underworld3 as uw

params = uw.Params(uw_cell_size=0.2, uw_multiplier_degree=2)
CELL_SIZE = float(params.uw_cell_size)
DEGREE = int(params.uw_multiplier_degree)
WALLS = ("Upper", "Lower")
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
depth_of = np.empty(p_end - p_start, dtype=int)
for depth in range(dm.getDepth() + 1):
    lo, hi = dm.getDepthStratum(depth)
    depth_of[lo - p_start:hi - p_start] = depth
NAMES = ("vertices", "edges", "faces", "cells")

# global point numbers: non-negative at the points this rank owns
numbering = dm.createPointNumbering()
raw = numbering.getIndices().copy()
owned = raw >= 0
global_id = np.where(owned, raw, -(raw + 1))


def by_depth(points):
    counts = Counter(int(depth_of[p - p_start]) for p in points)
    return ", ".join(f"{counts.get(d, 0)} {NAMES[d]}" for d in range(3))


def everywhere(local_value):
    """One value per rank, in rank order, on every rank."""
    return comm.allgather(local_value)


def report(title, per_rank):
    uw.pprint(0, f"  {title}")
    for rank, text in enumerate(per_rank):
        uw.pprint(0, f"    rank {rank}: {text}")


n_cells = comm.allreduce(int(np.count_nonzero(owned[slice(*[c - p_start for c in dm.getHeightStratum(0)])])),
                         op=uw.MPI.SUM)
uw.pprint(0, f"ranks {uw.mpi.size} | cell size {CELL_SIZE} | cells {n_cells} | multiplier degree {DEGREE} "
             f"| overlap {dm.getDistributionOverlap() if hasattr(dm, 'getDistributionOverlap') else 'n/a'}")

section = dm.getLocalSection()
global_section = dm.getGlobalSection()
label = dm.getLabel("UW_Boundaries")

for constraint in stokes._block_constraint_bcs:
    wall = constraint.boundary
    value = mesh.boundaries[wall].value
    field = constraint.lam._solver_field_id
    uw.pprint(0, f"--- {wall} (label value {value}, multiplier is solver field {field})")

    # A. the wall's points
    stratum = label.getStratumIS(value)
    labelled = set(stratum.getIndices().tolist()) if stratum and stratum.getSize() > 0 else set()
    closure = set()
    for point in labelled:
        closure.update(dm.getTransitiveClosure(point)[0].tolist())
    union_ids = set().union(*everywhere({int(global_id[p - p_start]) for p in closure}))
    wall_points = {p for p in range(p_start, p_end) if int(global_id[p - p_start]) in union_ids}
    held_without = wall_points - closure

    owned_wall = [p for p in wall_points if owned[p - p_start]]
    totals = Counter()
    for counts in everywhere(Counter(int(depth_of[p - p_start]) for p in owned_wall)):
        totals.update(counts)
    owned_labelled = Counter()
    for counts in everywhere(Counter(int(depth_of[p - p_start]) for p in labelled if owned[p - p_start])):
        owned_labelled.update(counts)
    uw.pprint(0, "  A. wall points, counted once: labelled "
                 + ", ".join(f"{owned_labelled.get(d, 0)} {NAMES[d]}" for d in range(3))
                 + " | union of the closures "
                 + ", ".join(f"{totals.get(d, 0)} {NAMES[d]}" for d in range(3)))
    report("A. on each rank: labelled | closure of the labelled | held without a labelled point above",
           everywhere(f"{by_depth(labelled)} | {by_depth(closure)} | {by_depth(held_without)}"))

    # B. PETSc's completion of a scratch label against the union
    scratch = PETSc.DMLabel().create("probe_1150_wall", comm=PETSc.COMM_SELF)
    for point in labelled:
        scratch.setValue(point, 1)
    try:
        dm.labelComplete(scratch)
        done = scratch.getStratumIS(1)
        completed = set(done.getIndices().tolist()) if done and done.getSize() > 0 else set()
        note = (f"completed {by_depth(completed)} | in the union only {by_depth(wall_points - completed)} "
                f"| in the completion only {by_depth(completed - wall_points)}")
    except Exception as err:  # noqa: BLE001 - a probe reports whatever stops it
        note = f"raised {type(err).__name__}: {str(err)[:160]}"
    scratch.destroy()
    report("B. label completion against the union", everywhere(note))

    # C. the multiplier's unknowns
    def free(point):
        return section.getFieldDof(point, field) - section.getFieldConstraintDof(point, field)

    kept = {p for p in range(p_start, p_end) if free(p) > 0}
    carries = {p for p in wall_points if section.getFieldDof(p, field) > 0}
    pinned_on_wall = carries - kept
    kept_off_wall = kept - wall_points
    n_global = comm.allreduce(sum(free(p) for p in kept if owned[p - p_start]), op=uw.MPI.SUM)
    n_wall_global = comm.allreduce(
        sum(section.getFieldDof(p, field) for p in carries if owned[p - p_start]), op=uw.MPI.SUM)
    uw.pprint(0, f"  C. multiplier unknowns in the global system: {n_global} "
                 f"| unknowns the wall's points carry: {n_wall_global}")
    report("C. on each rank: kept | wall points pinned (owned / not owned) | kept off the wall",
           everywhere(f"{by_depth(kept)} | "
                      f"{by_depth([p for p in pinned_on_wall if owned[p - p_start]])} / "
                      f"{by_depth([p for p in pinned_on_wall if not owned[p - p_start]])} | "
                      f"{by_depth(kept_off_wall)}"))

    # the ranks that hold a wall point, and those that keep its unknown
    views = everywhere({int(global_id[p - p_start]): (p in kept, bool(owned[p - p_start]), int(depth_of[p - p_start]))
                        for p in carries})
    holders, keepers, owner_keeps, depth_by_id = Counter(), Counter(), {}, {}
    for view in views:
        for gid, (is_kept, is_owner, depth) in view.items():
            holders[gid] += 1
            keepers[gid] += int(is_kept)
            depth_by_id[gid] = depth
            if is_owner:
                owner_keeps[gid] = is_kept
    split = [gid for gid in holders if 0 < keepers[gid] < holders[gid]]
    none = [gid for gid in holders if keepers[gid] == 0]

    def ids_by_depth(ids):
        counts = Counter(depth_by_id[g] for g in ids)
        return ", ".join(f"{counts.get(d, 0)} {NAMES[d]}" for d in range(3))

    uw.pprint(0, f"  C. shared wall points whose ranks disagree: {ids_by_depth(split)} "
                 f"(owner keeps: {sum(1 for g in split if owner_keeps.get(g))}, "
                 f"owner pins: {sum(1 for g in split if not owner_keeps.get(g))}) "
                 f"| wall points no rank keeps: {ids_by_depth(none)}")

# D. every field: a shared point's free unknowns here against the owner's
mismatch = []
for point in range(p_start, p_end):
    if owned[point - p_start]:
        continue
    here = section.getDof(point) - section.getConstraintDof(point)
    at_owner = -(global_section.getDof(point) + 1)
    if here != at_owner:
        mismatch.append(point)
uw.pprint(0, "--- all fields")
report("D. shared points whose free unknowns differ from the owner's", everywhere(by_depth(mismatch)))


# E. moments of the residual, summed over the ranks' own integrals
def weights(coords):
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    return np.stack([np.cos(1.3 * x + 0.7 * y - 0.4 * z + 0.3),
                     np.sin(0.9 * x - 1.1 * y + 1.7 * z),
                     np.cos(2.1 * z - 0.6 * x) * np.sin(1.5 * y + 0.2)], axis=1)


def residual_moments(state):
    try:
        rows = stokes.compute_volume_residual_fields()
    except Exception as err:  # noqa: BLE001 - a probe reports whatever stops it
        problems = everywhere(f"{type(err).__name__}: {str(err)[:160]}")
        uw.pprint(0, f"  E. {state}: the residual stopped: {problems}")
        return
    for name, var in stokes.fields.items():
        if name not in rows:
            continue
        coords = np.asarray(var.coords)
        values = np.asarray(rows[name])
        if coords.shape[0] == 0 or values.size % coords.shape[0]:
            sizes = everywhere((values.size, coords.shape[0]))
            uw.pprint(0, f"  E. {state} | {name}: entries and nodes do not match on some rank: {sizes}")
            continue
        values = values.reshape(coords.shape[0], -1)
        w = weights(coords)
        local = [float((values * w[:, [k]]).sum()) for k in range(3)]
        if values.shape[1] == 3:
            local.append(float((values * w).sum()))
        total = [comm.allreduce(m, op=uw.MPI.SUM) for m in local]
        uw.pprint(0, f"  E. {state} | {name}: " + "  ".join(f"{m:+.12e}" for m in total))


uw.pprint(0, "--- residual moments (three weights; a fourth for a vector field)")
for var in stokes.fields.values():
    var.array[...] = 0.0
residual_moments("every field zero")

for name, var in stokes.fields.items():
    x, y, z = (np.asarray(var.coords)[:, k] for k in range(3))
    if name == "velocity":
        var.array[:, 0, 0] = np.sin(1.1 * y + 0.6 * x + 0.2)
        var.array[:, 0, 1] = np.cos(0.8 * z - 0.9 * y - 0.1)
        var.array[:, 0, 2] = np.sin(0.7 * x + 0.4 * z + 0.5)
    elif name == "pressure":
        var.array[:, 0, 0] = np.cos(x + 2.0 * y - z)
    else:
        var.array[:, 0, 0] = np.sin(2.0 * x - y + z)
residual_moments("smooth state")
