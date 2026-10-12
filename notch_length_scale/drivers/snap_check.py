"""Geometric check of the notch's arc-snapping refinement callback (no solve).

Builds the notch mesh hierarchy twice, with and without ``nm.notch_arc_snap``, and at
every FMG level reports:

  (a) the max distance from every Inner-labelled vertex to the analytic interface (the
      straight parts plus the four fillet arcs), overall and for the arc vertices;
  (b) the max vertex displacement the callback makes on that level (the callback is
      wrapped, so this also shows which levels it runs on);
  (c) the min cell area / volume and the min mean-ratio quality;
  (d) per arc, the area between the Inner polyline and the analytic arc (the chord
      deficit; in 3-D on the z = 0 face), summed over the four arcs, and the Weak area /
      volume against the analytic filleted value;
  (e) label coverage: every local vertex shared by a Weak and a Strong cell must carry
      the Inner label (ghosts included: the local DM), and every Inner vertex must lie
      on the interface (counted by (a)).

Also (level 0) the number of segments gmsh gave each arc.

Usage: [mpirun -n 4] python snap_check.py -uw_mesh <gmsh file> -uw_ref <levels>
Writes ../results/snap_check/<mesh>_ref<k>_np<n>.json and prints a table.
"""
import json
import os
import sys

import numpy as np
import underworld3 as uw
from mpi4py import MPI

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import notch_model as nm   # noqa: E402

params = uw.Params(
    uw_mesh=uw.Param("", description="gmsh file of the notch (2-D or 3-D)"),
    uw_ref=uw.Param(3, description="refinement levels"),
)
H_KM = 30.0
A, B, RC = 1.0 / 12.0, 0.75, nm.RC
comm = uw.mpi.comm

# The interface: straight segments (non-dimensional x, y) and the four arcs.
SEGMENTS = [((-2.0, -B), (-(A + RC), -B)), ((-A, -(B - RC)), (-A, -(2 / 3 + RC))),
            ((-(A - RC), -2 / 3), ((A - RC), -2 / 3)), ((A, -(2 / 3 + RC)), (A, -(B - RC))),
            (((A + RC), -B), (2.0, -B))]


def seg_dist(p, a, b):
    a, b = np.asarray(a), np.asarray(b)
    d = b - a
    t = np.clip(((p - a) @ d) / (d @ d), 0.0, 1.0)
    return np.linalg.norm(p - (a + t[:, None] * d), axis=1)


def arc_dist(p, cx, cy, sx, sy):
    """Distance to the quarter circle of radius RC about (cx, cy) in quadrant (sx, sy)."""
    dx, dy = p[:, 0] - cx, p[:, 1] - cy
    r = np.hypot(dx, dy)
    inside = (sx * dx >= 0) & (sy * dy >= 0)
    ends = np.array([[cx + sx * RC, cy], [cx, cy + sy * RC]])
    d_end = np.min(np.linalg.norm(p[:, None, :] - ends[None], axis=2), axis=1)
    return np.where(inside, np.abs(r - RC), d_end)


def interface_dist(p):
    d = np.min([seg_dist(p, a, b) for a, b in SEGMENTS], axis=0)
    for arc in nm.ARCS:
        d = np.minimum(d, arc_dist(p, *arc))
    return d


def on_arc(p):
    """Points strictly inside an arc's quadrant and near it (the callback's own test)."""
    m = np.zeros(len(p), bool)
    for cx, cy, sx, sy in nm.ARCS:
        dx, dy = p[:, 0] - cx, p[:, 1] - cy
        m |= (np.sign(dx) == sx) & (np.sign(dy) == sy) & (np.hypot(dx, dy) < 2 * RC)
    return m


def label_points(dm, name, depth):
    lab = dm.getLabel(name)
    if lab is None:
        return np.array([], int)
    s, e = dm.getDepthStratum(depth)
    out = []
    for v in lab.getValueIS().getIndices():
        pts = lab.getStratumIS(v)
        if pts is not None:
            out.append(pts.getIndices())
    pts = np.unique(np.concatenate(out)) if out else np.array([], int)
    return pts[(pts >= s) & (pts < e)]


def cell_vertices(dm):
    """(n_cells, dim + 1) vertex indices (offset to the coordinate array)."""
    cs, ce = dm.getHeightStratum(0)
    vs, ve = dm.getDepthStratum(0)
    out = []
    for c in range(cs, ce):
        cl = dm.getTransitiveClosure(c)[0]
        out.append([q - vs for q in cl if vs <= q < ve])
    return np.array(out, int)


def measures(X, cells):
    """Cell size (area / volume) and mean-ratio quality, both per cell."""
    P = X[cells]
    dim = P.shape[2]
    E = P[:, 1:] - P[:, :1]
    if dim == 2:
        size = 0.5 * np.abs(E[:, 0, 0] * E[:, 1, 1] - E[:, 0, 1] * E[:, 1, 0])
        pairs = [(0, 1), (1, 2), (0, 2)]
        l2 = sum(np.sum((P[:, i] - P[:, j]) ** 2, axis=1) for i, j in pairs)
        q = 4 * np.sqrt(3) * size / l2
    else:
        size = np.abs(np.linalg.det(E)) / 6
        pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        l2 = sum(np.sum((P[:, i] - P[:, j]) ** 2, axis=1) for i, j in pairs)
        q = 12 * (3 * size) ** (2 / 3) / l2
    return size, q


def arc_deficit(Xin):
    """Per arc: (sector area) - (area of the polygon centre + Inner vertices on that arc,
    ordered by angle, with the analytic end points): the chord deficit, >= 0 for any
    polyline whose vertices lie on or inside the arc. Uses the x, y of Xin."""
    out = []
    for cx, cy, sx, sy in nm.ARCS:
        dx, dy = Xin[:, 0] - cx, Xin[:, 1] - cy
        m = (np.sign(dx) == sx) & (np.sign(dy) == sy) & (np.hypot(dx, dy) < 2 * RC)
        th = np.arctan2(dy[m], dx[m])
        ends = [(sx * RC, 0.0), (0.0, sy * RC)]
        pts = np.vstack([np.column_stack([dx[m], dy[m]]), ends])
        th = np.concatenate([th, [np.arctan2(0.0, sx * RC), np.arctan2(sy * RC, 0.0)]])
        # order by angle within the quadrant (unwrap around the branch cut)
        th = np.where(th < np.arctan2(sy * RC, sx * RC) - np.pi, th + 2 * np.pi, th)
        pts = pts[np.argsort(th)]
        poly = np.vstack([[0.0, 0.0], pts])
        x, y = poly[:, 0], poly[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        out.append(np.pi * RC ** 2 / 4 - area)
    return out


def inner_edges(dm, dim):
    """Local Inner edges as (n, 2) vertex indices (offset to the coordinate array):
    the labelled edges in 2-D, the edges of labelled faces in 3-D."""
    vs, _ = dm.getDepthStratum(0)
    es, ee = dm.getDepthStratum(1)
    pts = label_points(dm, "Inner", 1) if dim == 2 else np.unique(np.concatenate(
        [dm.getCone(f) for f in label_points(dm, "Inner", 2)] or [np.array([], int)]))
    pts = pts[(pts >= es) & (pts < ee)]
    return np.array([dm.getCone(e) for e in pts], int).reshape(-1, 2) - vs


def arc_deficit_edges(segs):
    """Per arc: quarter-disc area minus the fan (centre + each Inner edge inside the arc's
    closed quadrant): the chord deficit, 0 for a polyline on the arc in the limit."""
    out = []
    tol = 1.0e-12
    for cx, cy, sx, sy in nm.ARCS:
        d = segs - np.array([cx, cy])[None, None, :]
        inq = np.all((sx * d[..., 0] >= -tol) & (sy * d[..., 1] >= -tol)
                     & (np.hypot(d[..., 0], d[..., 1]) < 1.5 * RC), axis=1)
        e = d[inq]
        fan = 0.5 * np.abs(e[:, 0, 0] * e[:, 1, 1] - e[:, 0, 1] * e[:, 1, 0]).sum()
        out.append(np.pi * RC ** 2 / 4 - fan)
    return out


def coordinate_mismatch(dm):
    """Max difference between a rank's local coordinates and the owner's value: a
    shared vertex moved on one rank and not another."""
    cdm = dm.getCoordinateDM()
    loc = dm.getCoordinatesLocal()
    g = cdm.createGlobalVec()
    cdm.localToGlobal(loc, g)                 # INSERT: the owner's value
    back = cdm.createLocalVec()
    cdm.globalToLocal(g, back)
    diff = float(np.max(np.abs(back.array - loc.array))) if loc.getLocalSize() else 0.0
    g.destroy(); back.destroy()
    return comm.allreduce(diff, op=MPI.MAX)


def gather_unique(X):
    """All ranks' points on rank 0 (deduplicated by rounded coordinates)."""
    allx = comm.gather(X, root=0)
    if uw.mpi.rank != 0:
        return None
    Y = np.vstack([a for a in allx if len(a)]) if any(len(a) for a in allx) else np.zeros((0, 3))
    _, keep = np.unique(np.round(Y, 12), axis=0, return_index=True)
    return Y[keep]


def check(snap):
    moves = {}

    def wrapped(dm):
        X0 = dm.getCoordinatesLocal().array.copy()
        nm.notch_arc_snap(dm)
        X1 = dm.getCoordinatesLocal().array
        moves.setdefault(id(dm), []).append(float(np.max(np.abs(X1 - X0))) if len(X0) else 0.0)

    plex = uw.discretisation._from_gmsh(str(params.uw_mesh), useMultipleTags=True,
                                        useRegions=True)
    cv = plex[1].getCoordinates()
    cv.scale(1.0 / H_KM)
    plex[1].setCoordinates(cv)
    dim = plex[1].getDimension()
    mesh = uw.discretisation.Mesh(
        plex[1], boundaries=nm.boundaries if dim == 2 else nm.boundaries3d,
        useMultipleTags=True, useRegions=True,
        coordinate_system_type=uw.coordinates.CoordinateSystemType.CARTESIAN,
        qdegree=3, refinement=int(params.uw_ref),
        refinement_callback=wrapped if snap else None)

    rows = []
    for level, dm in enumerate(mesh.dm_hierarchy):
        X = dm.getCoordinatesLocal().array.reshape(-1, dm.getCoordinateDim())
        vs, _ = dm.getDepthStratum(0)
        # the callback's own extraction: vertices in the closure of Inner edges / faces
        # (refined midpoints inherit the label on the edge, not on the vertex)
        inner = uw.cython.petsc_discretisation.petsc_dm_find_labeled_points_local(dm, "Inner")
        inner = np.unique(np.asarray(inner, int)) if dm.getLabel("Inner") else np.array([], int)
        inner0 = label_points(dm, "Inner", 0) - vs
        Xin = X[inner]
        d = interface_dist(Xin[:, :2]) if len(Xin) else np.zeros(0)
        arcm = on_arc(Xin[:, :2]) if len(Xin) else np.zeros(0, bool)
        cells = cell_vertices(dm)
        size, q = measures(X, cells)
        P = X[cells]
        E = P[:, 1:] - P[:, :1]
        signed = (E[:, 0, 0] * E[:, 1, 1] - E[:, 0, 1] * E[:, 1, 0]) if dim == 2 else np.linalg.det(E)
        cs, _ = dm.getHeightStratum(0)
        weak = label_points(dm, "Weak", dim) - cs
        # (e) interface vertices by cell adjacency must all carry Inner
        is_weak = np.zeros(len(cells), bool)
        is_weak[weak] = True
        touch_w = np.zeros(len(X), bool)
        touch_s = np.zeros(len(X), bool)
        np.logical_or.at(touch_w, cells[is_weak].ravel(), True)
        np.logical_or.at(touch_s, cells[~is_weak].ravel(), True)
        both = np.flatnonzero(touch_w & touch_s)
        missing = int(np.setdiff1d(both, inner).size)
        # (d) chord deficit on the arcs, from the Inner vertices on z = 0 (3-D) / all (2-D)
        face = Xin if dim == 2 else Xin[np.abs(Xin[:, 2]) < 1.0e-9]
        allface = gather_unique(np.ascontiguousarray(face))
        ed = inner_edges(dm, dim)
        segs = X[ed][:, :, :2]
        if dim == 3:
            segs = segs[np.all(np.abs(X[ed][:, :, 2]) < 1.0e-9, axis=1)]
        allsegs = comm.gather(segs.reshape(-1, 4), root=0)
        row = dict(
            level=level,
            cells=int(comm.allreduce(int(dm.getHeightStratum(0)[1] - cs))),
            inner_vertices_local_max=int(comm.allreduce(len(inner), op=MPI.MAX)),
            dist_max=float(comm.allreduce(float(d.max()) if len(d) else 0.0, op=MPI.MAX)),
            dist_max_arc=float(comm.allreduce(float(d[arcm].max()) if arcm.any() else 0.0,
                                              op=MPI.MAX)),
            min_size=float(comm.allreduce(float(size.min()), op=MPI.MIN)),
            min_quality=float(comm.allreduce(float(q.min()), op=MPI.MIN)),
            weak_measure=float(comm.allreduce(float(size[is_weak].sum()))),
            interface_missing_inner=int(comm.allreduce(missing)),
            inner_vertex_labels=int(comm.allreduce(int(inner0.size))),
            inner_closure_vertices=int(comm.allreduce(int(inner.size))),
        )
        row["_signed"] = np.sign(signed)
        row["coord_mismatch"] = coordinate_mismatch(dm)
        if uw.mpi.rank == 0:
            S4 = np.vstack(allsegs)
            # dedupe edges shared between ranks (either orientation)
            a, b = np.round(S4[:, :2], 12), np.round(S4[:, 2:], 12)
            key = np.where((a[:, :1] < b[:, :1]) | ((a[:, :1] == b[:, :1]) & (a[:, 1:] < b[:, 1:])),
                           np.hstack([a, b]), np.hstack([b, a]))
            _, keep = np.unique(key, axis=0, return_index=True)
            deficit = arc_deficit_edges(S4[keep].reshape(-1, 2, 2))
            row["arc_deficit_sum"] = float(np.sum(deficit))
            row["arc_deficit"] = [float(v) for v in deficit]
            if level == 0:
                row["arc_vertices_interior"] = [
                    int(np.sum((np.sign(allface[:, 0] - cx) == sx)
                               & (np.sign(allface[:, 1] - cy) == sy)
                               & (np.hypot(allface[:, 0] - cx, allface[:, 1] - cy) < 2 * RC)))
                    for cx, cy, sx, sy in nm.ARCS]
        rows.append(row)
    # (b) displacement per level: the callback ran on these DMs (in call order)
    ids = [id(dm) for dm in mesh.dm_hierarchy]
    for level, key in enumerate(ids):
        local = max(moves.get(key, [0.0])) if key in moves else -1.0
        rows[level]["callback_calls"] = int(comm.allreduce(len(moves.get(key, [])),
                                                           op=MPI.MAX))
        rows[level]["callback_max_move"] = float(comm.allreduce(local, op=MPI.MAX))
    return rows


results = {"snapped": check(True), "unsnapped": check(False)}
# inverted cells: same refinement of the same base, same partition, so the same local
# cell order; a cell whose orientation differs between the two has been turned inside out
for rs, ru in zip(results["snapped"], results["unsnapped"]):
    flips = int(np.sum(rs.pop("_signed") != ru.pop("_signed")))
    rs["inverted_by_snap"] = int(comm.allreduce(flips))
# analytic Weak measure: the filleted notch's fillets cancel in area (two convex, two
# concave, the same radius), so Weak = slab + rectangle in 2-D, times Lz in 3-D
with uw.selective_ranks(0) as rank0:
    if rank0:
        name = os.path.splitext(os.path.basename(str(params.uw_mesh)))[0]
        out_dir = os.path.join(_here, "..", "results", "snap_check")
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, f"{name}_ref{int(params.uw_ref)}_np{uw.mpi.size}.json")
        json.dump(results, open(out, "w"), indent=1)
        print(f"{name}  np {uw.mpi.size}   (analytic Weak area 2-D: {1 + 1 / 72:.9f} x Lz in 3-D)")
        print("variant   lvl  cells     max d(all)  max d(arc)  calls max move   min size    "
              "min q   Weak measure    arc deficit  missing Inner  inverted  rank mismatch")
        for k, rows in results.items():
            for r in rows:
                print(f"{k:9s} {r['level']:3d} {r['cells']:8d}  {r['dist_max']:.3e}  "
                      f"{r['dist_max_arc']:.3e}  {r['callback_calls']:3d}  "
                      f"{r['callback_max_move']:.3e}  {r['min_size']:.3e}  {r['min_quality']:.4f}  "
                      f"{r['weak_measure']:.9f}  {r.get('arc_deficit_sum', float('nan')):.3e}  "
                      f"{r['interface_missing_inner']:6d}  {r.get('inverted_by_snap', ''):>4}  "
                      f"{r['coord_mismatch']:.2e}")
        print("arc vertices (interior, level 0):", results["unsnapped"][0].get("arc_vertices_interior"))
        print(out)
