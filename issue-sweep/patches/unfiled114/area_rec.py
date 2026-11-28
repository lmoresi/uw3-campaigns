"""Record |mesh area - CAD area| / CAD area for every ladder assembly, then run a probe."""
import atexit, sys, runpy, json
import numpy as np
import underworld3.utilities.place_surface as ps

REC = []
real = ps._occ_ladder_assembly_2d


def wrapped(*a, **k):
    pts, tris, cad = real(*a, **k)
    P = pts[tris]
    twice = ((P[:, 1, 0] - P[:, 0, 0]) * (P[:, 2, 1] - P[:, 0, 1])
             - (P[:, 1, 1] - P[:, 0, 1]) * (P[:, 2, 0] - P[:, 0, 0]))
    area = float(np.abs(twice).sum() / 2)
    REC.append((abs(area - cad) / cad, cad, len(tris)))
    return pts, tris, cad


ps._occ_ladder_assembly_2d = wrapped
out = sys.argv[1]
atexit.register(lambda: json.dump(REC, open(out, "w")))
sys.argv = sys.argv[2:]
runpy.run_path(sys.argv[0], run_name="__main__")
