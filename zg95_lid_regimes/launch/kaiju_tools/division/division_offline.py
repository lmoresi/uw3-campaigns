# kaiju_tools: offline fault division of stored checkpoints (the division study)
"""Offline placement check for the fault-division design (the hub, 2026-11-04; Louis on decision 1b: "the along-fault
resolution is set by the discretisation of the fault, the fault width is set by the local mesh size ... the ladder is
built from the fault points"). For every stored crust-law fault (the "points" polyline in each checkpoint's
state_*.json), place the finest-level ladder (chain 0) as the driver does, through its four attempts
(margin_rings/clearance/width), in four arms:
    v2  the recipe today: re-sampled uniformly at S = uw_cell / 2**uw_refinement, W = 2S, cut 1 S inside the wall
    D0  divided at the measured local cell size h(s) along the trace, W = 2 h_f
    D1  the design: divided at h(s), W = h_f (one cell), cut 1 h(wall) inside the wall
    D2  divided at h(s)/2, W = h_f (the library's ~2 elements across the width, aspect ~1)
h(x) is the mesh's own local cell size, the mean length of the edges meeting the vertices nearest x (the quantity
uw_cell sets: gmsh's target edge length); h_f is its arc-length-weighted mean along the in-domain spine. Records per
placement: built (attempt) or refused (reasons), rungs and rung length (mean/min/max), W, h along the trace, the cut's
top depth, and element quality (smallest angle; cells under 20 deg) in the band, in the fill round it and overall.
No solve. Serial.
    python3 division_offline.py <out.jsonl> <state.json> [...]
"""
import json
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

import underworld3 as uw
from underworld3.utilities.line_cut import _coords, _edge_vertices, _vertex_h
from underworld3.utilities.place_surface import place_fault_ribbon_2d

ATTEMPTS = [(1, 0.7, 1.0), (1, 0.7, 1.25), (2, 0.7, 1.0), (1, 0.7, 1.5)]   # the driver's (rings, clearance, widen)
ARMS = ["v2", "D0", "D1", "D2"]
out = sys.argv[1] if __name__ == "__main__" else None
meshes = {}


def base_mesh(cell, refinement, ratio=0.55):
    key = (cell, refinement, ratio)
    if key not in meshes:
        r_o = 1.0 / (1.0 - ratio)
        base = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=ratio / (1.0 - ratio), cellSize=cell,
                                  refinement=refinement, qdegree=3)
        X = _coords(base.dm)
        hv = _vertex_h(X, _edge_vertices(base.dm))
        meshes[key] = (base, r_o, cKDTree(X), hv)
    return meshes[key]


def local_h(tree, hv, pts, k=6):
    """The mesh's local cell size at each point: the mean of the vertex h of the k nearest vertices."""
    _, idx = tree.query(np.asarray(pts, dtype=float), k=k)
    return hv[idx].mean(axis=1)


def divide(poly, h_of, factor=1.0, block=1, n_fine=4000):
    """``poly`` divided by arc length so each segment is about factor x the local cell size there: points uniform in
    u(s) = int ds / (factor h(s)), with a multiple of ``block`` segments (chain levels subsample by 2^k)."""
    poly = np.asarray(poly, dtype=float)
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    sf = np.linspace(0.0, s[-1], n_fine)
    xf = np.c_[np.interp(sf, s, poly[:, 0]), np.interp(sf, s, poly[:, 1])]
    hf = factor * h_of(xf)
    u = np.r_[0.0, np.cumsum(0.5 * (1.0 / hf[1:] + 1.0 / hf[:-1]) * np.diff(sf))]
    n = block * max(1, int(round(u[-1] / block)))
    t = np.interp(np.linspace(0.0, u[-1], n + 1), u, sf)
    return np.c_[np.interp(t, s, poly[:, 0]), np.interp(t, s, poly[:, 1])]


def uniform(poly, spacing):
    poly = np.asarray(poly, dtype=float)
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    t = np.linspace(0.0, s[-1], max(1, int(round(s[-1] / spacing))) + 1)
    return np.c_[np.interp(t, s, poly[:, 0]), np.interp(t, s, poly[:, 1])]


def arc_mean(poly, values):
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    mid = 0.5 * (values[1:] + values[:-1])
    return float((seg * mid).sum() / seg.sum())


def quality(mesh, band, spine, W):
    """Smallest angle (deg) and the count under 20 deg in the band, in the fill (non-band cells within 2W + 2 cells of
    the spine) and everywhere."""
    dm = mesh.dm
    X = _coords(dm)
    vS, vE = dm.getDepthStratum(0)
    cS, cE = dm.getHeightStratum(0)
    tri = np.array([[p - vS for p in dm.getTransitiveClosure(c)[0] if vS <= p < vE] for c in range(cS, cE)])
    P = X[tri]
    ang = []
    for i in range(3):
        a, b, c = P[:, i], P[:, (i + 1) % 3], P[:, (i + 2) % 3]
        u, v = b - a, c - a
        ang.append(np.degrees(np.arccos(np.clip((u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1)),
                                                -1, 1))))
    amin = np.min(ang, axis=0)
    cen = P.mean(axis=1)
    sp = np.asarray(spine, dtype=float)
    d = cKDTree(np.vstack([sp[i] + np.outer(np.linspace(0, 1, 9)[:-1], sp[i + 1] - sp[i]) for i in range(len(sp) - 1)])
                ).query(cen)[0]
    band = np.asarray(band, dtype=bool)
    hloc = np.median(np.linalg.norm(P[:, 0] - P[:, 1], axis=1))
    fill = (~band) & (d < 2.0 * W + 2.0 * hloc)
    r = {}
    for name, m in (("band", band), ("fill", fill), ("all", np.ones_like(band))):
        r[name] = {"cells": int(m.sum()), "min_angle": round(float(amin[m].min()), 2) if m.any() else None,
                   "under20": int((amin[m] < 20.0).sum())}
    return r


def main():
    for sf in sys.argv[2:]:
        st = json.load(open(sf))
        p = st.get("params", {})
        cell, ref = float(p.get("uw_cell", 0.5)), int(p.get("uw_refinement", 4))
        base, r_o, tree, hv = base_mesh(cell, ref)
        h_nom = cell / 2 ** ref

        def h_of(x):
            return local_h(tree, hv, x)

        for f in st.get("faults", []):
            if "points" not in f:
                continue
            stored = np.asarray(f["points"], dtype=float)
            for arm in ARMS:
                if arm == "v2":
                    spine = uniform(stored, h_nom)
                    W, inset_len = 2.0 * h_nom, h_nom
                else:
                    spine = divide(stored, h_of, 0.5 if arm == "D2" else 1.0)
                    inside = np.hypot(spine[:, 0], spine[:, 1]) <= r_o
                    h_sp = h_of(spine)
                    h_f = arc_mean(spine[inside], h_sp[inside])
                    W = 2.0 * h_f if arm == "D0" else h_f
                    k = int(np.argmax(inside))
                    inset_len = float(h_of(spine[k:k + 1])[0])         # one local cell at the wall
                trace = spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - inset_len]
                seg = np.linalg.norm(np.diff(spine, axis=0), axis=1)
                h_tr = h_of(spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o])
                rec = {"state": sf, "fault": f.get("name"), "arm": arm, "h_nominal": h_nom,
                       "h_trace": [round(float(h_tr.min()), 5), round(float(h_tr.mean()), 5), round(float(h_tr.max()), 5)],
                       "W": round(W, 5), "rungs": int(len(spine)), "trace_points": int(len(trace)),
                       "rung_len": [round(float(seg.min()), 5), round(float(seg.mean()), 5), round(float(seg.max()), 5)],
                       "cut_top_depth": round(float(r_o - np.hypot(*trace[0])), 5) if len(trace) else None,
                       "inset": round(inset_len, 5)}
                t0 = time.perf_counter()
                for n, (rings, clearance, widen) in enumerate(ATTEMPTS):
                    try:
                        mesh, info = place_fault_ribbon_2d(base, [(f.get("name", "F0"), trace)], W * widen,
                                                           spines=[(f.get("name", "F0"), spine)], margin_rings=rings,
                                                           clearance=clearance, split=True, mesher="ladder", seams="gather")
                        rec.update({"built": True, "attempt": n, "seconds": round(time.perf_counter() - t0, 1),
                                    "cells": int(info.get("n_cells", 0) or 0),
                                    "quality": quality(mesh, info["band"], spine, W * widen)})
                        break
                    except Exception as err:
                        rec.setdefault("errors", []).append(f"{type(err).__name__}: {str(err)[:160]}")
                else:
                    rec.update({"built": False, "seconds": round(time.perf_counter() - t0, 1)})
                with open(out, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                q = rec.get("quality", {})
                print(sf.split("/")[-2], sf.split("/")[-1], arm, "built" if rec.get("built") else "REFUSED",
                      rec.get("attempt"), rec["seconds"], "W", rec["W"], "rungs", rec["rungs"],
                      "band min angle", (q.get("band") or {}).get("min_angle"),
                      "fill", (q.get("fill") or {}).get("min_angle"), flush=True)


if __name__ == "__main__":
    main()
