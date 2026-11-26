import sys, numpy as np, warnings
warnings.simplefilter("ignore")
sys.argv = ["x", "box_irr", "0.3", "kinks"]
g = {}
exec(open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
Q = [q for t, q in g["traces"]() if t == "kink90_9"][0]
uw = g["uw"]
for k in (1, 2, 4):
    m = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=g["h"] / k, regular=False)
    try:
        m2 = m.add_fault(("F", Q))
        r = g["solve"](m2, "F")
        print(f"K9REF cells/side {12*k}: slip {r['slip_max']:.5f}", flush=True)
    except Exception as e:
        print(f"K9REF cells/side {12*k}: raised {str(e)[:90]}", flush=True)
