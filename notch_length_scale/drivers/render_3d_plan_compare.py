"""Plan views of several 3-D notch-block runs side by side: one row per run, one column
per depth, from the .npz files render_3d_plan_view.py writes. Each column has its own
colour range (the band contrast grows with depth), shared down the column so the runs
compare directly.

Usage:
  python render_3d_plan_compare.py <out name> <run npz> [<run npz> ...]
       (each npz may carry a label after '=': path.npz=10 km block, ref 3)
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

_here = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(_here, "..", "figures")
out_name = sys.argv[1]
runs = []
for arg in sys.argv[2:]:
    path, _, label = arg.partition("=")
    runs.append((np.load(path), label or os.path.basename(path)))

ys = runs[0][0]["ys"]
yield_field = str(runs[0][0]["field"]) == "yield"
ncol, nrow = len(ys), len(runs)
clims = []
for k in range(ncol):
    allv = np.concatenate([d[f"f{k}"] for d, _ in runs])
    clims.append((0.0, 1.0) if yield_field else
                 (float(np.percentile(allv, 2)), float(np.percentile(allv, 99.5))))

Lz = float(runs[0][0]["Lz"])
fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 1.95 * nrow + 1.3),
                         sharex=True, sharey=True, squeeze=False)
for i, (d, label) in enumerate(runs):
    Ln = float(d["Ln"])
    for k in range(ncol):
        ax = axes[i, k]
        P, T, F = d[f"pts{k}"], d[f"tri{k}"], d[f"f{k}"]
        im = ax.tripcolor(P[:, 0], P[:, 1], T, facecolors=F, cmap="inferno",
                          vmin=clims[k][0], vmax=clims[k][1], shading="flat")
        ax.plot([-2.5, -2.5, 2.5, 2.5], [0, Ln, Ln, 0], color="white", lw=0.8, ls="--")
        ax.set_aspect("equal")
        ax.set_xlim(-32, 32)
        ax.set_ylim(0, Lz)
        if i == 0:
            ax.set_title(f"y = {ys[k]:g} km", fontsize=10)
        if k == 0:
            ax.set_ylabel(f"{label}\nz along strike (km)", fontsize=9)
        if i == nrow - 1:
            ax.set_xlabel("x (km)")
        if i == nrow - 1:
            cb = fig.colorbar(im, ax=axes[:, k], orientation="horizontal", fraction=0.04,
                              pad=0.08, aspect=25)
            cb.ax.tick_params(labelsize=8)
fig.suptitle((r"$\eta_{eff}/\eta_{lin}$" if yield_field else
              r"$\dot\varepsilon_{II}/(V/H)$")
             + " on horizontal slices of the strong layer; dashed: the notch block",
             fontsize=11)
os.makedirs(FIG, exist_ok=True)
out = os.path.join(FIG, out_name + ".png")
fig.savefig(out, dpi=120, bbox_inches="tight")
print(out)
