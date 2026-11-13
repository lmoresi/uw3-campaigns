"""Review of PR #1130: a 2-D mesh wound clockwise throughout (x -> -x), cut at
the PR head. In two dimensions there is no vote; what does the cut say?"""
import numpy as np
import underworld3 as uw
from underworld3.utilities import line_cut as HEAD

params = uw.Params(uw_cell_size=uw.Param(1.0 / 12.0, description="cell size of the box"))
box = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                        cellSize=float(params.uw_cell_size), regular=False)
clock = box.dm.clone()
X = HEAD._coords(box.dm).copy()
X[:, 0] *= -1.0
HEAD._set_coordinates(clock, np.arange(len(X)), X)
print("cells", len(HEAD.cell_areas(clock)), "| negative area", int((HEAD.cell_areas(clock) < 0).sum()),
      "| vote", HEAD._global_flip(X[HEAD._cell_vertices(clock)]))
for frac in (0.0, 0.1):
    try:
        HEAD.cut_along_lines(clock, [np.array([[-0.31, -0.1], [-0.62, 1.1]])], snap_frac=frac)
        print("snap_frac", frac, "cut")
    except Exception as err:
        print("snap_frac", frac, type(err).__name__, str(err)[:120])
