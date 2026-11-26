import sys, os, json, warnings
import numpy as np
warnings.simplefilter("ignore")
order = sys.argv[1].split(",")
sys.argv = ["x", "box_irr", "90", "1", "0"]
src = open("row30.py").read().split("coarse = uw.meshing.UnstructuredSimplexBox")[0]
exec(src)
Q = kink()                          # trial 0 of the 90-degree seed, as in conv30
from underworld3.utilities.fault_split import _turns
coarse = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h, regular=False)
for mode in order:
    r = solve(coarse, Q, mode)
    print(f"TF {mode}: apex {r['apex']:.3e} largest {r['max']:.5f}", flush=True)
