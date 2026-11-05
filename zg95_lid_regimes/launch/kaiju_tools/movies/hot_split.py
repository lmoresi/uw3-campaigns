# kaiju_tools: splits a built cut's hot fraction into top and deep parts (2026-11-04 diagnosis)
"""Hot (T > 0.7) fraction of the detected fault and of the built cut, top (depth <= 0.09) and deep (> 0.09) apart,
at given checkpoints. python3 hot_split.py <run dir> <ckpt> [...]"""
import json, sys
import h5py, numpy as np
from scipy.spatial import cKDTree
run = sys.argv[1]
for n in map(int, sys.argv[2:]):
    s = json.load(open(f"{run}/state_{n:05d}.json"))
    with h5py.File(f"{run}/annulus.mesh.T.{n:05d}.h5", "r") as h:
        xy = h["fields/coordinates"][:]; T = h["fields/T"][:].ravel()
    r_o = np.hypot(xy[:, 0], xy[:, 1]).max(); tree = cKDTree(xy)
    for kind, p in [("detected", f["points"]) for f in s["faults"] if "points" in f] + [("built", b) for b in s.get("traces") or []]:
        p = np.asarray(p); seg = np.linalg.norm(np.diff(p, axis=0), axis=1); sa = np.r_[0, np.cumsum(seg)]
        t = np.arange(0, sa[-1], 0.002); q = np.c_[np.interp(t, sa, p[:, 0]), np.interp(t, sa, p[:, 1])]
        d = r_o - np.hypot(q[:, 0], q[:, 1]); keep = d > 0.005; d, q = d[keep], q[keep]; Tq = T[tree.query(q)[1]]
        top, deep = d <= 0.09, d > 0.09
        print(f"{run.split('/')[-1]} ckpt {n} {kind:8s}: top hot {(Tq[top] > 0.7).mean():.3f} (T {Tq[top].mean():.2f}), "
              f"deep hot {(Tq[deep] > 0.7).mean():.3f} (T {Tq[deep].mean():.2f}, n {deep.sum()})")
