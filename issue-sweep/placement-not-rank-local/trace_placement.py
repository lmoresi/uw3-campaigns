"""Trace of a parallel fault placement that ends in "the surgery was not rank-local".

    import trace_placement
    trace_placement.install()        # before FaultNetwork.build / place_fault_ribbon_2d

Nothing in the library is edited: four functions are wrapped in memory and the
placement runs as it would without the trace. Works on underworld3 from
80d3ebe9 (2026-11-08) to development af84cfcd (2026-11-14).

What it prints, in the order the placement does things:

1. every call of ``partition_addon``: who called it, its layers, whether it
   returned a new mesh, and its record (units moved, region owners, load);
2. every call of ``_gather_regions`` (the placement's and the split's own
   gather): who called it, its layers, the region's size and how many cells
   it moved. After a partition the count moved should be 0. When it is not,
   the vertices this gather marks and the last partition's rule does not are
   listed, with the region's cells by rank;
3. every call of ``redistribute_by_assignment`` (the one routine that moves
   cells), with its caller;
4. before every ``inherit_provenance`` check that would refuse: each refused
   cell with its rank, centroid and vertices, the rank whose host cell holds
   the centroid, and whether that host cell is the same cell (the cell moved
   between ranks) or a different one (the cell is new, or was reshaped).

The centroids are printed as (x, y) and as (radius, angle in degrees).

Tolerances and coordinate matches (a probe, not library code): "inside" is the
library's own, a barycentric coordinate above -1e-8; "the same cell" compares
the three vertex coordinates to 1e-10 of the cell's longest edge.
"""
import functools
import traceback

import numpy as np
import underworld3 as uw

_INSIDE = -1.0e-8
_last = {"marks": None, "layers": None}
_installed = []


def _say(text):
    uw.pprint(f"[trace] {text}", flush=True)


def _caller():
    """The two library frames above the wrapped function, nearest first."""
    frames = traceback.extract_stack()[-4:-2]
    return " <- ".join(f"{f.filename.rsplit('/', 1)[-1]}:{f.lineno} in {f.name}"
                       for f in reversed(frames))


def _polar(xy):
    xy = np.asarray(xy, dtype=float)
    return (f"({xy[0]:.6f}, {xy[1]:.6f}) r {np.hypot(xy[0], xy[1]):.6f} "
            f"angle {np.degrees(np.arctan2(xy[1], xy[0])):.4f}")


def _cells_by_rank(dm):
    cS, cE = dm.getHeightStratum(0)
    return uw.mpi.comm.allgather(int(cE - cS))


def refused_cells(child, host, refuse_all=False):
    """The cells of ``child`` whose centroid lies in no local cell of ``host``,
    each with where it does lie. Collective. Returns the gathered list and,
    per refused cell found on some rank, ``(index, rank, same cell)``.
    ``refuse_all`` treats every cell as refused: it is for checking this trace
    on one rank, where no cell is ever refused."""
    from underworld3.utilities.addon_partition import _cell_centroids
    from underworld3.utilities.fault_mg import locate_in_cells_exhaustive
    comm = uw.mpi.comm
    fcent, vxy_c, cv_c = _cell_centroids(child)
    _c, vxy_h, cv_h = _cell_centroids(host)
    mine = []
    if cv_c.shape[0]:
        if cv_h.shape[0] == 0:
            bad = np.arange(cv_c.shape[0])
        else:
            _cell, lam = locate_in_cells_exhaustive(fcent, vxy_h, cv_h)
            bad = (np.arange(cv_c.shape[0]) if refuse_all
                   else np.flatnonzero(lam.min(axis=1) < _INSIDE))
        mine = [(uw.mpi.rank, fcent[k][:2].copy(), vxy_c[cv_c[k]][:, :2].copy())
                for k in bad]
    everyone = [item for part in comm.allgather(mine) for item in part]

    # where each refused centroid does lie: every rank looks in its own host cells
    found = []
    if everyone and cv_h.shape[0]:
        points = np.array([c for _r, c, _v in everyone])
        if vxy_h.shape[1] > 2:
            points = np.c_[points, np.zeros((len(points), vxy_h.shape[1] - 2))]
        cell, lam = locate_in_cells_exhaustive(points, vxy_h, cv_h)
        for i in np.flatnonzero(lam.min(axis=1) >= _INSIDE):
            there = vxy_h[cv_h[cell[i]]][:, :2]
            here = everyone[i][2]
            edge = float(np.linalg.norm(here - np.roll(here, 1, axis=0), axis=1).max())
            gap = np.linalg.norm(here[:, None, :] - there[None, :, :], axis=2).min(axis=1)
            found.append((i, uw.mpi.rank, bool(gap.max() <= 1.0e-10 * edge)))
    found = [item for part in comm.allgather(found) for item in part]
    return everyone, found


def report_refused(child, host, caller):
    everyone, found = refused_cells(child, host)
    _say(f"provenance check from {caller}: {len(everyone)} cell(s) in no local host cell; "
         f"cells by rank, host {_cells_by_rank(host.dm)}, result {_cells_by_rank(child.dm)}")
    for i, (rank, centroid, vertices) in enumerate(everyone):
        homes = [(r, same) for j, r, same in found if j == i]
        where = ("in no host cell on any rank (new or reshaped past the host's edge)" if not homes else
                 "; ".join(f"in a host cell of rank {r}, "
                           f"{'the same cell (it changed rank)' if same else 'a different cell (new or reshaped)'}"
                           for r, same in homes))
        _say(f"  refused cell {i}: on rank {rank}, centroid {_polar(centroid)}; {where}")
        for v in vertices:
            _say(f"      vertex {_polar(v)}")
    return everyone, found


def _wrap_partition(original):
    @functools.wraps(original)
    def partition_addon(mesh, region_marks, layers=1, *args, **kwargs):
        caller = _caller()
        before = _cells_by_rank(mesh.dm)
        out = original(mesh, region_marks, layers, *args, **kwargs)
        _last["marks"], _last["layers"] = region_marks, layers
        record = getattr(out, "_addon_partition", None) or {}
        _say(f"partition_addon from {caller}: layers {layers}, "
             f"{'a new mesh' if out is not mesh else 'the same mesh (nothing moved)'}; "
             f"cells by rank {before} -> {_cells_by_rank(out.dm)}")
        for key in ("regions", "owners", "region_weight", "units_moved", "sweeps",
                    "load_before", "load_after"):
            if key in record:
                _say(f"    {key}: {record[key]}")
        return out
    return partition_addon


def compare_with_partition(dm, vertex_region_chart, layers):
    """A gather's marks and region against the last partition's rule on the
    same DM. Collective."""
    from underworld3.utilities import place_surface
    comm = uw.mpi.comm
    ids = np.asarray(vertex_region_chart, dtype=np.int32)
    cell_region, _c, _regions = place_surface._region_cells(dm, ids, layers=layers)
    _say(f"    this gather's region cells by rank: "
         f"{comm.allgather(int(np.count_nonzero(cell_region)))}")
    if _last["marks"] is None:
        return
    vS, vE = dm.getDepthStratum(0)
    pStart, _pEnd = dm.getChart()
    X = place_surface._coords(dm)[: vE - vS]
    rule = np.asarray(_last["marks"](dm), dtype=np.int32)
    extra = np.flatnonzero((ids[vS - pStart: vE - pStart] != 0)
                           & (rule[vS - pStart: vE - pStart] == 0))
    listed = comm.allgather([(uw.mpi.rank, X[k][:2].copy()) for k in extra[:20]])
    _say(f"    vertices this gather marks and the last partition's rule "
         f"(layers {_last['layers']}) does not, by rank: "
         f"{comm.allgather(int(extra.size))} (a shared vertex is counted on each rank "
         f"that holds it; the first 20 per rank follow)")
    for part in listed:
        for rank, xy in part:
            _say(f"      rank {rank}: {_polar(xy)}")
    partition_cells, _c2, _r2 = place_surface._region_cells(dm, rule, layers=_last["layers"])
    outside = (np.asarray(cell_region) != 0) & (np.asarray(partition_cells) == 0)
    _say(f"    cells of this gather's region outside the partition's region, by rank: "
         f"{comm.allgather(int(np.count_nonzero(outside)))}")


def _wrap_gather(original):
    @functools.wraps(original)
    def _gather_regions(dm, vertex_region_chart, verbose=False, layers=1):
        caller = _caller()
        result = original(dm, vertex_region_chart, verbose=verbose, layers=layers)
        _new, n_region, n_moved, owner, _canon = result
        _say(f"_gather_regions from {caller}: layers {layers}, region of {n_region} cells, "
             f"{n_moved} moved, owner {owner}")
        if n_moved and uw.mpi.size > 1:
            compare_with_partition(dm, vertex_region_chart, layers)
        return result
    return _gather_regions


def _wrap_redistribute(original):
    @functools.wraps(original)
    def redistribute_by_assignment(dm, *args, **kwargs):
        _say(f"redistribute_by_assignment from {_caller()}: cells by rank {_cells_by_rank(dm)}")
        return original(dm, *args, **kwargs)
    return redistribute_by_assignment


def _wrap_inherit(original):
    @functools.wraps(original)
    def inherit_provenance(child, host):
        caller = _caller()
        recorded = (getattr(host, "_addon_parent", None) is not None
                    and getattr(host, "_addon_below", None) is not None)
        _say(f"inherit_provenance from {caller}: the host "
             f"{'carries a partition record (the check runs)' if recorded else 'carries no record (no check)'}")
        if recorded:
            report_refused(child, host, caller)
        return original(child, host)
    return inherit_provenance


def install():
    """Wrap the four functions. Call once, on every rank, before the placement."""
    if _installed:
        return
    from underworld3.utilities import addon_partition, fault_split, place_surface
    for module, name, wrap in ((addon_partition, "partition_addon", _wrap_partition),
                               (addon_partition, "inherit_provenance", _wrap_inherit),
                               (place_surface, "_gather_regions", _wrap_gather),
                               (fault_split, "redistribute_by_assignment", _wrap_redistribute)):
        original = getattr(module, name)
        setattr(module, name, wrap(original))
        _installed.append((module, name, original))
    _say(f"installed at {uw.mpi.size} rank(s)")


def remove():
    while _installed:
        module, name, original = _installed.pop()
        setattr(module, name, original)
