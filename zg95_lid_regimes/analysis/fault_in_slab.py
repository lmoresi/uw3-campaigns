"""Whether the fault sits in the slab (Louis, 2026-11-04: "the old recipe locates the fault always within the slab
somewhere but the new recipe frequently has the fault in the hot mantle").

At each checkpoint, the temperature along two polylines, sampled every 0.002 of arc below 0.005 deep, nearest P2 node
of the checkpointed T (annulus.mesh.T.N.h5):
  - the DETECTED fault: state_N.json "faults"[k]["points"], what the locator found;
  - the BUILT fault: state_N.json "traces"[k], the cut actually in that checkpoint's mesh.
Per polyline: the fraction of its length in cold slab (T < 0.5), in the warm margin (0.5-0.7) and in hot mantle
(T > 0.7), and the mean T, over the whole line and split at TOP_DEPTH (default 0.09) into the top (depth <= TOP_DEPTH)
and the deep end; for the built cut also its gap to the detected polyline (largest and mean distance of its points to
the detected one), in model units and in base cells (h_b = uw_cell / 2**uw_refinement from the state's params).

The built cut lags the detected fault by up to the rebuild threshold (uw_rebuild_cells base cells) plus the drift
between detections, so the gap is the drift test. The top of the cut must sit in cold lid; the deep end runs along the
warm margin of the slab top near the depth cap, where a five-step lag across the steep gradient puts part of the built
cut in hot mantle (TAf-v2 checkpoint 50: 47 % of the deep end, the detected fault 0 %; TAf_env on the old recipe 37 %),
so the deep end is watched, not paused on (the hub, 2026-11-04). Run in the container (h5py):
    python3 fault_in_slab.py <run dir> [...] [--top 0.09]               a table, every checkpoint
    python3 fault_in_slab.py <run dir> --ckpt N --json [--top 0.09]     one JSON line for checkpoint N (the watcher)
"""
import argparse
import glob
import json
import os
import re

import h5py
import numpy as np
from scipy.spatial import cKDTree


def frac(Tq):
    if len(Tq) == 0:
        return {"cold": None, "hot": None, "T_mean": None, "samples": 0}
    return {"cold": round(float((Tq < 0.5).mean()), 3), "hot": round(float((Tq > 0.7).mean()), 3),
            "T_mean": round(float(Tq.mean()), 3), "samples": int(len(Tq))}


def sample(points, tree, T, r_o, top_depth, step=0.002, top=0.005):
    p = np.asarray(points, dtype=float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    t = np.arange(0.0, s[-1], step)
    q = np.c_[np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])]
    d = r_o - np.hypot(q[:, 0], q[:, 1])
    q, d = q[d > top], d[d > top]                                  # below the surface layer
    Tq = T[tree.query(q)[1]]
    out = frac(Tq)
    out["length"] = round(len(Tq) * step, 4)
    out["top"] = frac(Tq[d <= top_depth])
    out["deep"] = frac(Tq[d > top_depth])
    return out


def checkpoint(run, n, top_depth):
    sp = os.path.join(run, f"state_{n:05d}.json")
    tf = os.path.join(run, f"annulus.mesh.T.{n:05d}.h5")
    if not (os.path.exists(sp) and os.path.exists(tf)):
        return None
    s = json.load(open(sp))
    prm = s.get("params") or {}
    h_b = float(prm.get("uw_cell", 0.5)) / 2 ** int(prm.get("uw_refinement", 4))
    detected = [f["points"] for f in s.get("faults", []) if "points" in f]
    built = s.get("traces") or []
    with h5py.File(tf, "r") as h:
        xy = h["fields/coordinates"][:]
        T = h["fields/T"][:].ravel()
    r_o = float(np.hypot(xy[:, 0], xy[:, 1]).max())
    tree = cKDTree(xy)
    out = {"ckpt": n, "t": s["t"], "h_b": h_b, "top_depth": top_depth,
           "detected": [sample(p, tree, T, r_o, top_depth) for p in detected], "built": []}
    for b in built:
        rec = sample(b, tree, T, r_o, top_depth)
        if detected:                        # gap to the nearest detected polyline
            d = min((cKDTree(np.asarray(p, dtype=float)).query(np.asarray(b, dtype=float))[0] for p in detected),
                    key=lambda x: x.max())
            rec.update({"gap_max": round(float(d.max()), 4), "gap_mean": round(float(d.mean()), 4),
                        "gap_cells": round(float(d.max()) / h_b, 2)})
        out["built"].append(rec)

    def worst(recs, part, key):
        vals = [r[part][key] if part else r[key] for r in recs]
        vals = [v for v in vals if v is not None]
        return max(vals, default=0.0)
    out["built_hot_max"] = worst(out["built"], None, "hot")
    out["built_hot_top_max"] = worst(out["built"], "top", "hot")
    out["built_hot_deep_max"] = worst(out["built"], "deep", "hot")
    out["detected_hot_top_max"] = worst(out["detected"], "top", "hot")
    out["detected_hot_deep_max"] = worst(out["detected"], "deep", "hot")
    out["gap_max"] = max((b.get("gap_max", 0.0) for b in out["built"]), default=0.0)
    out["gap_cells_max"] = max((b.get("gap_cells", 0.0) for b in out["built"]), default=0.0)
    return out


ap = argparse.ArgumentParser()
ap.add_argument("runs", nargs="+")
ap.add_argument("--ckpt", type=int, default=None)
ap.add_argument("--json", action="store_true")
ap.add_argument("--top", type=float, default=0.09, help="depth splitting the top of the fault from its deep end")
a = ap.parse_args()
for run in a.runs:
    ns = ([a.ckpt] if a.ckpt is not None else
          sorted(int(re.search(r"state_(\d+)\.json", f).group(1)) for f in glob.glob(os.path.join(run, "state_*.json"))))
    if not a.json:
        print(f"== {os.path.basename(run.rstrip('/'))} (top: depth <= {a.top})")
        print("  ckpt  t         detected hot: top  deep   built hot: top  deep  all   gap max (cells)  mean")
    for n in ns:
        c = checkpoint(run, n, a.top)
        if c is None:
            continue
        if a.json:
            print(json.dumps(c))
            continue
        if not c["built"]:
            print(f"  {n:4d}  {c['t']:.6f}  {c['detected_hot_top_max']:5.3f} {c['detected_hot_deep_max']:5.3f}"
                  "   (no built cut)")
            continue
        b = c["built"][0]
        print(f"  {n:4d}  {c['t']:.6f}       {c['detected_hot_top_max']:5.3f} {c['detected_hot_deep_max']:5.3f}"
              f"            {c['built_hot_top_max']:5.3f} {c['built_hot_deep_max']:5.3f} {c['built_hot_max']:5.3f}"
              f"   {b.get('gap_max', float('nan')):.4f} ({b.get('gap_cells', float('nan')):.2f})"
              f"  {b.get('gap_mean', float('nan')):.4f}")
