"""Whether the fault sits in the slab (Louis, 2026-11-04: "the old recipe locates the fault always within the slab
somewhere but the new recipe frequently has the fault in the hot mantle").

At each checkpoint, the temperature along two polylines, sampled every 0.002 of arc below 0.005 deep, nearest P2 node
of the checkpointed T (annulus.mesh.T.N.h5):
  - the DETECTED fault: state_N.json "faults"[k]["points"], what the locator found;
  - the BUILT fault: state_N.json "traces"[k], the cut actually in that checkpoint's mesh.
Per polyline: the fraction of its length in cold slab (T < 0.5), in the warm margin (0.5-0.7) and in hot mantle
(T > 0.7), and the mean T; for the built cut also its gap to the detected polyline (largest and mean distance of its
points to the detected one). The built cut lags the detected fault by up to the rebuild threshold (uw_rebuild_cells
base cells; uw_rebuild_rungs x S before 2026-11-04), so a growing hot fraction of the BUILT cut means the threshold
is too loose for how fast the slab moves. Run in the container (h5py):
    python3 fault_in_slab.py <run dir> [...]               a table, every checkpoint
    python3 fault_in_slab.py <run dir> --ckpt N --json     one JSON line for checkpoint N (the in-job watcher)
"""
import argparse
import glob
import json
import os
import re

import h5py
import numpy as np
from scipy.spatial import cKDTree


def sample(points, tree, T, r_o, step=0.002, top=0.005):
    p = np.asarray(points, dtype=float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    t = np.arange(0.0, s[-1], step)
    q = np.c_[np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])]
    q = q[r_o - np.hypot(q[:, 0], q[:, 1]) > top]                  # below the surface layer
    Tq = T[tree.query(q)[1]]
    return {"length": round(len(Tq) * step, 4), "cold": round(float((Tq < 0.5).mean()), 3),
            "hot": round(float((Tq > 0.7).mean()), 3), "T_mean": round(float(Tq.mean()), 3)}


def checkpoint(run, n):
    sp = os.path.join(run, f"state_{n:05d}.json")
    tf = os.path.join(run, f"annulus.mesh.T.{n:05d}.h5")
    if not (os.path.exists(sp) and os.path.exists(tf)):
        return None
    s = json.load(open(sp))
    detected = [f["points"] for f in s.get("faults", []) if "points" in f]
    built = s.get("traces") or []
    with h5py.File(tf, "r") as h:
        xy = h["fields/coordinates"][:]
        T = h["fields/T"][:].ravel()
    r_o = float(np.hypot(xy[:, 0], xy[:, 1]).max())
    tree = cKDTree(xy)
    out = {"ckpt": n, "t": s["t"], "detected": [sample(p, tree, T, r_o) for p in detected], "built": []}
    for b in built:
        rec = sample(b, tree, T, r_o)
        if detected:                        # gap to the nearest detected polyline
            d = min((cKDTree(np.asarray(p, dtype=float)).query(np.asarray(b, dtype=float))[0] for p in detected),
                    key=lambda x: x.max())
            rec.update({"gap_max": round(float(d.max()), 4), "gap_mean": round(float(d.mean()), 4)})
        out["built"].append(rec)
    out["built_hot_max"] = max((b["hot"] for b in out["built"]), default=0.0)
    out["gap_max"] = max((b.get("gap_max", 0.0) for b in out["built"]), default=0.0)
    return out


ap = argparse.ArgumentParser()
ap.add_argument("runs", nargs="+")
ap.add_argument("--ckpt", type=int, default=None)
ap.add_argument("--json", action="store_true")
a = ap.parse_args()
for run in a.runs:
    ns = ([a.ckpt] if a.ckpt is not None else
          sorted(int(re.search(r"state_(\d+)\.json", f).group(1)) for f in glob.glob(os.path.join(run, "state_*.json"))))
    if not a.json:
        print(f"== {os.path.basename(run.rstrip('/'))}")
        print("  ckpt  t         detected: cold  hot   T     built: cold  hot   T     gap max  mean")
    for n in ns:
        c = checkpoint(run, n)
        if c is None:
            continue
        if a.json:
            print(json.dumps(c))
            continue
        for k, d in enumerate(c["detected"]):
            b = c["built"][k] if k < len(c["built"]) else None
            print(f"  {n:4d}  {c['t']:.6f}       {d['cold']:5.2f} {d['hot']:5.2f} {d['T_mean']:.3f}" +
                  (f"        {b['cold']:5.2f} {b['hot']:5.2f} {b['T_mean']:.3f}   {b.get('gap_max', float('nan')):.4f}"
                   f"  {b.get('gap_mean', float('nan')):.4f}" if b else "        (no built cut)"))
