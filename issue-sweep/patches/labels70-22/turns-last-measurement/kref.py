import sys, numpy as np, warnings
warnings.simplefilter("ignore")
TR = sys.argv[3]; MK = sys.argv[1]; sys.argv = ["x", sys.argv[1], sys.argv[2], "kinks"]
g = {}
exec(open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
Q = [q for t, q in g["traces"]() if t == TR][0]
uw = g["uw"]
for k in (1, 2, 4):
    m = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=g["h"] / k, regular=(MK == "box_reg"))
    try:
        m2 = m.add_fault(("F", Q))
        r = g["solve"](m2, "F")
        print(f"KREF {TR}  cells/side {12*k}: slip {r['slip_max']:.5f}", flush=True)
    except Exception as e:
        print(f"KREF {TR}  cells/side {12*k}: raised {str(e)[:90]}", flush=True)
