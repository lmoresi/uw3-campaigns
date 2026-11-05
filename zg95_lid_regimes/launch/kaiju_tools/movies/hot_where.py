# kaiju_tools: where along the built cut the hot mantle lies (2026-11-04 diagnosis)
"""Where along the built cut the hot (T > 0.7) samples are: depth below the outer wall of each hot sample, per run and
checkpoint. python3 hot_where.py <run dir> <ckpt> [...]"""
import json, sys
import h5py, numpy as np
from scipy.spatial import cKDTree
run = sys.argv[1]
for n in map(int, sys.argv[2:]):
    s = json.load(open(f"{run}/state_{n:05d}.json"))
    with h5py.File(f"{run}/annulus.mesh.T.{n:05d}.h5", "r") as h:
        xy = h["fields/coordinates"][:]; T = h["fields/T"][:].ravel()
    r_o = np.hypot(xy[:, 0], xy[:, 1]).max(); tree = cKDTree(xy)
    for b in s.get("traces") or []:
        p = np.asarray(b); seg = np.linalg.norm(np.diff(p, axis=0), axis=1); sa = np.r_[0, np.cumsum(seg)]
        t = np.arange(0, sa[-1], 0.002); q = np.c_[np.interp(t, sa, p[:, 0]), np.interp(t, sa, p[:, 1])]
        d = r_o - np.hypot(q[:, 0], q[:, 1]); Tq = T[tree.query(q)[1]]
        hot = d[Tq > 0.7]
        print(f"{run.split('/')[-1]} ckpt {n}: cut depth 0-{d.max():.3f}; hot samples {len(hot)} of {len(d)} at depths "
              f"{(f'{hot.min():.3f}-{hot.max():.3f}' if len(hot) else '-')}; T along the cut in depth bins 0.03: "
              + " ".join(f"{Tq[(d>=a)&(d<a+0.03)].mean():.2f}" if ((d>=a)&(d<a+0.03)).any() else "-" for a in np.arange(0, 0.16, 0.03)))
