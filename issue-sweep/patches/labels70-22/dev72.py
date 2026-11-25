import sys, numpy as np, warnings
warnings.simplefilter("ignore")
import underworld3 as uw
from underworld3.utilities import line_cut as lc
lc._DEGENERATE_AREA_FRACTION = 0.0            # the guard off
ns = {}; exec(open("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_0899_cut_refuses_a_degenerate_cell.py").read().split("@pytest.fixture")[0].split("pytestmark")[1].split("\n", 1)[1], {"np": np}, ns)
TRACE = ns["TRACE"]
box = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
dm = lc.pull_vertex_onto(box.dm, TRACE, on_shared="note")
cut, info = lc.cut_along_lines(dm, [TRACE])
a = lc.cell_areas(cut); print("CUT every sample pulled: min area", a.min(), "min angle", info["min_angle"], "shared targets", lc.last_shared_targets["count"])
try:
    m2 = box.add_fault(("F", TRACE))
    print("ADD_FAULT returned a mesh; min angle", float(np.min(lc.min_angles(m2.dm))))
except Exception as e:
    print("ADD_FAULT raised:", str(e)[:150])
