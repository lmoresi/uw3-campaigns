# kaiju_tools: optional hook (UW_LABEL_CHECK): counts the analytic-normal wall nodes added per rank
"""kaiju (2026-11-01, the np 32 wall spikes; Louis: mesh labelling or the fault insertion?): no-solve check of the
rotated route's wall-node set. Wraps rotated_bc._boundary_velocity_nodes (the per-boundary node list build_rotation
constrains) and reports every velocity point this rank OWNS that lies on that wall by radius but is missing from the
list, with whether this rank holds a labelled facet at it and which ranks do. The driver gives the walls an analytic
normal (normal=unit_r), and on that path the list is built from this rank's labelled facets only (no cross-rank
reduction, no support-1 candidates): an owned wall point whose labelled facets all sit on other ranks is dropped by
its owner and skipped by every other rank as not owned, so it gets no constraint row. With UW_LABEL_CHECK_EXIT=1 the
run stops after both walls are built (no solve). Imported by run_driver.py when UW_LABEL_CHECK is set.
"""
import os

import numpy as np
from petsc4py import PETSc

from underworld3.utilities import rotated_bc as rb

_orig = rb._boundary_velocity_nodes
_calls = [0]


def _checked(solver, boundary, normal=None):
    nodes = _orig(solver, boundary, normal=normal)
    dm = solver.dm
    comm = dm.comm.tompi4py()
    dim = solver.mesh.cdim
    lsec = dm.getLocalSection()
    gsec = dm.getGlobalSection()      # owned points have dof > 0; ghosts carry -(dof + 1)
    csec = dm.getCoordinateSection()
    cvec = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dim)
    v0, v1 = dm.getDepthStratum(0)
    pS, pE = dm.getChart()
    listed = {q for q, _ in nodes}
    sis = rb._boundary_stratum_is(dm, solver.mesh, boundary)
    fS, fE = dm.getHeightStratum(1)
    lab, lab_pt = set(), set()                 # closure of labelled FACETS (what the library uses); labelled points
    for f in ([int(z) for z in sis.getIndices()] if (sis and sis.getSize() > 0) else []):
        lab_pt.add(f)
        if fS <= f < fE:
            lab.update(int(c) for c in dm.getTransitiveClosure(f)[0])
    pts, owned = [], []
    for q in range(pS, pE):
        if lsec.getFieldDof(q, rb._VELOCITY_FIELD) <= 0:
            continue
        xy = np.asarray(rb._point_coord(dm, dim, cvec, csec, v0, v1, q), dtype=float)
        pts.append((q, xy, gsec.getDof(q) > 0))
    R = np.array([np.hypot(*p[1][:2]) for p in pts]) if pts else np.zeros(0)
    # the wall radius from this boundary's own listed points (any rank that lists one)
    mine = [float(np.hypot(*xy[:2])) for q, xy, _ in pts if q in listed]
    from mpi4py import MPI
    rw = comm.allreduce(float(np.mean(mine)) if mine else 0.0, op=MPI.SUM) / max(comm.allreduce(1 if mine else 0, op=MPI.SUM), 1)
    on_wall = [(q, xy, own) for (q, xy, own), r in zip(pts, R) if abs(r - rw) < 1e-4]
    missing = [(tuple(np.round(xy, 8)), q in lab, q in lab_pt) for q, xy, own in on_wall if own and q not in listed]
    labelled_xy = [tuple(np.round(xy, 8)) for q, xy, own in on_wall if q in lab]
    n_owned = sum(1 for _, _, own in on_wall if own)
    M = comm.gather(missing, root=0)
    L = comm.gather(labelled_xy, root=0)
    N = comm.gather(n_owned, root=0)
    if comm.rank == 0:
        allm = [(r, m) for r, part in enumerate(M) for m in part]
        print(f"LABEL_CHECK {boundary} (r {rw:.6f}, normal {'analytic' if normal is not None else 'geometric'}): "
              f"{sum(N)} owned wall points, {len(allm)} missing from the constrained list", flush=True)
        for r, (xy, lab_here, pt_here) in allm:
            holders = [k for k, part in enumerate(L) if xy in set(part)]
            print(f"LABEL_CHECK   ({xy[0]:.4f}, {xy[1]:.4f}) theta {np.degrees(np.arctan2(xy[1], xy[0])) % 360:.1f}: "
                  f"owner rank {r}, a labelled facet at it on the owner {lab_here}, the point itself labelled on the owner "
                  f"{pt_here}, ranks holding a labelled facet at it {holders}",
                  flush=True)
    _calls[0] += 1
    if os.environ.get("UW_LABEL_CHECK_EXIT") and _calls[0] >= 2:
        comm.Barrier()
        if comm.rank == 0:
            print("LABEL_CHECK: done, stopping before the solve", flush=True)
        os._exit(0)
    return nodes


rb._boundary_velocity_nodes = _checked
