"""place_sheet's wall refusals: a flat sheet at height z near the top wall of a unit box.

    python p_sheet_wall.py z [z ...]"""
import sys
import numpy as np
import underworld3 as uw
from underworld3.utilities.place_surface import place_sheet

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0),
                                         cellSize=0.11, regular=False, qdegree=2)
n, half = 5, 0.2
s = np.linspace(-half, half, n)
for z in map(float, sys.argv[1:]):
    pts = np.array([(0.5 + a, 0.5 + b, z) for a in s for b in s])
    tris = []
    for i in range(n - 1):
        for j in range(n - 1):
            a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j, (i + 1) * n + j + 1
            tris += [(a, b, d), (a, d, c)]
    try:
        place_sheet(mesh.dm, pts, np.array(tris, dtype=np.int64), label="Fault")
        print("RES z", z, "placed")
    except Exception as err:
        print("RES z", z, type(err).__name__, err)
