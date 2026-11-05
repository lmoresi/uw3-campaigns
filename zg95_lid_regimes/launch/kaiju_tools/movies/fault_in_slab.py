# kaiju_tools: kaiju's early copy of analysis/fault_in_slab.py (superseded by the repo's)
"""Where the fault sits (Louis, 2026-11-04: "the old recipe locates the fault always within the slab somewhere but the new
recipe frequently has the fault in the hot mantle"): at each checkpoint, the temperature along the fault's stored
polyline (state_N.json "points", the spine the ladder is built on), sampled every 0.002 along it from the wall down,
nearest P2 node of the checkpointed T. Per checkpoint: the fraction of the fault's length in cold slab (T < 0.5), in
the warm margin (0.5-0.7) and in hot mantle (T > 0.7), the deepest cold point and the depth where it first leaves
the slab for good. Prints a table per run.
    python3 fault_in_slab.py <run dir> [...]
"""
import glob
import json
import os
import re
import sys

import h5py
import numpy as np
from scipy.spatial import cKDTree

for run in sys.argv[1:]:
    print(f"== {os.path.basename(run.rstrip('/'))}")
    print("  ckpt  t        fault len  cold<0.5  warm  hot>0.7  T mean  leaves slab at depth  dip   theta")
    for sp in sorted(glob.glob(os.path.join(run, "state_*.json"))):
        n = int(re.search(r"state_(\d+)\.json", sp).group(1))
        tf = os.path.join(run, f"annulus.mesh.T.{n:05d}.h5")
        if not os.path.exists(tf):
            continue
        s = json.load(open(sp))
        faults = [f for f in s.get("faults", []) if "points" in f]
        traces = s.get("traces") or []                    # the faults BUILT into this checkpoint's mesh (cut traces)
        if not faults:
            continue
        with h5py.File(tf, "r") as h:
            xy = h["fields/coordinates"][:]
            T = h["fields/T"][:].ravel()
        r_o = np.hypot(xy[:, 0], xy[:, 1]).max()
        tree = cKDTree(xy)
        for f, kind in [(f, "detected") for f in faults] + [({"points": tr}, "built") for tr in traces]:
            p = np.asarray(f["points"], dtype=float)
            seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
            s_ = np.r_[0.0, np.cumsum(seg)]
            t = np.arange(0.0, s_[-1], 0.002)
            q = np.c_[np.interp(t, s_, p[:, 0]), np.interp(t, s_, p[:, 1])]
            depth = r_o - np.hypot(q[:, 0], q[:, 1])
            q = q[depth > 0.005]                                   # below the surface layer
            depth = depth[depth > 0.005]
            Tq = T[tree.query(q)[1]]
            L = len(Tq) * 0.002
            cold, hot = (Tq < 0.5).mean(), (Tq > 0.7).mean()
            leave = depth[np.flatnonzero(Tq < 0.5).max() + 1] if (Tq < 0.5).any() and (Tq < 0.5).nonzero()[0].max() + 1 < len(Tq) else None
            gap = ""
            if kind == "built" and faults:
                d = cKDTree(np.asarray(faults[0]["points"], dtype=float)).query(p)[0]
                gap = f"  gap to detected: max {d.max():.4f} mean {d.mean():.4f}"
            print(f"  {n:4d}  {kind:8s} {s['t']:.5f}  {L:6.3f}     {cold:5.2f}   {1 - cold - hot:5.2f}  {hot:5.2f}   {Tq.mean():.3f}   "
                  f"{('%.3f' % leave) if leave is not None else '  -  '}                {f.get('dip', float('nan')):5.1f} "
                  f"{np.degrees(f.get('theta', np.nan)):6.2f}{gap}")
