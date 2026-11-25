"""pytest plugin, UNFILED 22 proposal: when add_fault pulls a trace's control points onto
vertices, pull only the two tips and the interior points where the trace turns by more than
CORNER_DEG (default 45). Direct calls of pull_vertex_onto are untouched."""
import os, sys
import numpy as np
from underworld3.utilities import line_cut as lc
DEG = float(os.environ.get("CORNER_DEG", "45"))
_orig = lc.pull_vertex_onto
def corners(P, deg=DEG):
    P = np.asarray(P, dtype=float)
    if P.ndim == 1 or len(P) <= 2:
        return P
    keep = [0]
    for i in range(1, len(P) - 1):
        a, b = P[i] - P[i - 1], P[i + 1] - P[i]
        c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        if np.degrees(np.arccos(np.clip(c, -1, 1))) > deg:
            keep.append(i)
    keep.append(len(P) - 1)
    return P[keep]
SPACING = float(os.environ.get("THIN", "0"))     # 0: corners only; else keep points >= SPACING x median edge apart
def median_edge(dm):
    vS, vE = dm.getDepthStratum(0); eS, eE = dm.getDepthStratum(1)
    cdim = dm.getCoordinateDim()
    X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, cdim)
    E = np.array([dm.getCone(e) for e in range(eS, min(eE, eS + 4000))]) - vS
    return float(np.median(np.linalg.norm(X[E[:, 0]] - X[E[:, 1]], axis=1)))
def thinned(P, dm):
    P = np.asarray(P, dtype=float)
    if P.ndim == 1 or len(P) <= 2 or SPACING <= 0:
        return corners(P)
    h = SPACING * median_edge(dm)
    corner_set = {tuple(q) for q in corners(P)}
    keep = [0]
    for i in range(1, len(P) - 1):
        if tuple(P[i]) in corner_set or np.linalg.norm(P[i] - P[keep[-1]]) >= h:
            keep.append(i)
    if len(keep) > 1 and np.linalg.norm(P[-1] - P[keep[-1]]) < 0.5 * h and tuple(P[keep[-1]]) not in corner_set:
        keep.pop()
    keep.append(len(P) - 1)
    return P[keep]
def pull(dm, targets, *a, **kw):
    if sys._getframe(1).f_code.co_filename.endswith("fault_split.py"):
        targets = thinned(targets, dm)
    return _orig(dm, targets, *a, **kw)
lc.pull_vertex_onto = pull
