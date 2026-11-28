"""Smallest (vertex to non-adjacent ring edge) / local edge over every 2-D fill of a placement."""
import sys, runpy, numpy as np
import underworld3.utilities.place_surface as ps
real = ps._gmsh_fill_2d
seen = []
def pinch(X):
    n = len(X); L = np.linalg.norm(np.roll(X, -1, 0) - X, axis=1)
    A = X; B = np.roll(X, -1, 0); E = B - A
    best = np.inf
    for i in range(n):
        u = np.clip(((X[i] - A) * E).sum(1) / (E * E).sum(1), 0, 1)
        d = np.linalg.norm(X[i] - A - u[:, None] * E, axis=1)
        d[[i, (i - 1) % n]] = np.inf
        loc = np.minimum(L, min(L[i], L[(i - 1) % n]))
        best = min(best, float((d / loc).min()))
    return best
def wrapped(Xall, ring, chain, holes=(), size_of=None):
    seen.append(pinch(np.asarray(Xall)[list(ring)]))
    return real(Xall, ring, chain, holes=holes, size_of=size_of)
ps._gmsh_fill_2d = wrapped
import os
if sys.argv[1] == "off":
    os.environ["UW_EXP_RAIL_CELLS"] = "0"
sys.argv = ["residual.py"] + sys.argv[2:]
try:
    runpy.run_path("residual_norail.py" if os.environ.get("UW_EXP_RAIL_CELLS") == "0" else "residual.py", run_name="__main__")
finally:
    print("PINCH", sys.argv[1:], "fills", len(seen), "smallest", f"{min(seen):.3e}" if seen else "-")
