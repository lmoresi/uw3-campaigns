"""#1150: which wall points would a rank see without a labelled wall point above them?

One rank. The mesh's cells are cut into pieces by the signs of the centroid
coordinates (2, 4, 8 pieces), standing in for a partition with no overlap. A
piece holds the closure of its cells and the label values of those points.
The solver keeps a multiplier unknown at a point when the point is in the
closure of a labelled wall point THE RANK HOLDS. We count wall points
(vertices and edges, where a degree-2 multiplier has unknowns) that a piece
holds but would not keep.

    python wall_points_by_piece.py -uw_cell_size 0.2
"""
import numpy as np
import underworld3 as uw

params = uw.Params(uw_cell_size=0.2)
mesh = uw.meshing.SphericalShellInternalBoundary(
    radiusOuter=1.0, radiusInternal=0.775, radiusInner=0.55,
    cellSize=float(params.uw_cell_size), qdegree=3)
dm = mesh.dm
cS, cE = dm.getHeightStratum(0)
depth_of = {}
for d in range(dm.getDepth() + 1):
    s, e = dm.getDepthStratum(d)
    for q in range(s, e):
        depth_of[q] = d
print(f"cells {cE - cS}  depth {dm.getDepth()}", flush=True)

closure = {c: set(int(q) for q in dm.getTransitiveClosure(c)[0]) for c in range(cS, cE)}
coords = dm.getCoordinatesLocal().array.reshape(-1, 3)
vS, _vE = dm.getDepthStratum(0)
centroid = {c: coords[[q - vS for q in closure[c] if depth_of[q] == 0]].mean(axis=0)
            for c in range(cS, cE)}

label = dm.getLabel("UW_Boundaries")
for wall in ("Upper", "Lower"):
    value = mesh.boundaries[wall].value
    stratum = set(int(q) for q in label.getStratumIS(value).getIndices())
    by_depth = np.bincount([depth_of[q] for q in stratum], minlength=4)
    named = dm.getLabel(wall).getStratumIS(value)
    named = set(int(q) for q in named.getIndices()) if named else set()
    keep_all = set()
    for q in stratum:
        keep_all.update(int(r) for r in dm.getTransitiveClosure(q)[0])
    keep_by_depth = np.bincount([depth_of[q] for q in keep_all], minlength=4)
    print(f"{wall}: labelled points by depth (vertex, edge, face, cell) {by_depth.tolist()}; "
          f"same set under the label of its own name: {named == stratum}; "
          f"closure by depth {keep_by_depth.tolist()}", flush=True)

    for axes in ((0,), (0, 1), (0, 1, 2)):
        pieces = {}
        for c in range(cS, cE):
            pieces.setdefault(tuple(bool(centroid[c][a] > 0) for a in axes), []).append(c)
        missed_v = missed_e = held = 0
        for cells in pieces.values():
            chart = set().union(*(closure[c] for c in cells))
            keep = set()
            for q in stratum & chart:
                keep.update(int(r) for r in dm.getTransitiveClosure(q)[0])
            wall_here = [q for q in keep_all & chart if depth_of[q] in (0, 1)]
            held += len(wall_here)
            missed_v += sum(1 for q in wall_here if q not in keep and depth_of[q] == 0)
            missed_e += sum(1 for q in wall_here if q not in keep and depth_of[q] == 1)
        print(f"  {len(pieces)} pieces: wall vertices and edges held (with repeats) {held}; "
              f"held without a labelled point above them: vertices {missed_v}, edges {missed_e}",
              flush=True)
