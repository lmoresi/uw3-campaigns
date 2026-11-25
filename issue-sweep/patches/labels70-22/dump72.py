import os, sys, numpy as np
os.environ["THIN"] = "0"; os.environ["SHARP_DEG"] = "90"
sys.argv = ["x", "box_reg", "0.5", "kinks"]
src = open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0]
src = src.replace('MODE = os.environ.get("MODE", "dev")', 'MODE = "new_light_sharp"')
exec(src)
import corners_plugin as cp
from underworld3.utilities import line_cut as lc
for tag, Q in traces():
    if tag in ("kink90_9",):
        T = cp.with_sharp(np.asarray(Q), mesh.dm, cp.thinned(Q, mesh.dm))
        np.set_printoptions(precision=17)
        print("TRACE", repr(Q.tolist())); print("TARGETS", repr(T.tolist()))
        dm = lc.pull_vertex_onto(mesh.dm, T, on_shared="note")
        try:
            lc.cut_along_lines(dm, [Q]); print("CUT ok")
        except Exception as e:
            print("CUT raised", str(e)[:300])
