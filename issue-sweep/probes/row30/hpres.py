import sys, os, warnings
import numpy as np
warnings.simplefilter("ignore")
g = {}
sys.argv = ["x", "box_reg", "0.3", "kinks"]
exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
Q = [q for t, q in g["traces"]() if t == "kink150_3"][0]
uw = g["uw"]
for k in (1, 2, 4, 8):
    m = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=g["h"] / k, regular=True)
    try:
        m.add_fault(("F", Q)); print(f"HR {12*k}: added", flush=True)
    except Exception as e:
        print(f"HR {12*k}: refused: {str(e)[:110]}", flush=True)
