"""Figure of the graded base: whole annulus and trench close-up, cells coloured by size (km)."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm

D, R_O, R_I = 2900.0, 1 / 0.45, 0.55 / 0.45
path, title, out = sys.argv[1], sys.argv[2], sys.argv[3]
m = np.load(path)
xy, tri = m["xy"], m["tri"]
P = xy[tri]
edge = np.max(np.linalg.norm(P - np.roll(P, 1, axis=1), axis=2), axis=1) * D
cen = P.mean(axis=1)
depth = (R_O - np.hypot(cen[:, 0], cen[:, 1])) * D
arc = np.abs(np.arctan2(cen[:, 0], cen[:, 1])) * R_O * D        # from the trench at the top

norm = LogNorm(8, 300)
fig = plt.figure(figsize=(14, 7.2), facecolor="white")
ax1 = fig.add_axes([0.02, 0.06, 0.46, 0.86])
ax2 = fig.add_axes([0.50, 0.30, 0.44, 0.62])
for ax in (ax1, ax2):
    pc = PolyCollection(P, array=edge, cmap="viridis_r", norm=norm, edgecolors="k", linewidths=0.08)
    ax.add_collection(pc)
    ax.set_aspect("equal")
    ax.set_facecolor("white")
    ax.set_xticks([]); ax.set_yticks([])
ax1.set_xlim(-R_O * 1.02, R_O * 1.02); ax1.set_ylim(-R_O * 1.02, R_O * 1.02)
ax1.set_title(title, fontsize=11)
w = 1300 / D
ax2.set_xlim(-w, w); ax2.set_ylim(R_O - 1000 / D, R_O + 40 / D)
ax2.set_title("trench close-up (2,600 x 1,000 km)", fontsize=10)
ax1.add_patch(plt.Rectangle((-w, R_O - 1000 / D), 2 * w, 1040 / D, fill=False, ec="red", lw=1))
cb = fig.colorbar(pc, ax=ax2, orientation="horizontal", fraction=0.06, pad=0.04)
cb.set_label("longest cell edge, km")

rows = [("trench window (|arc| < 750 km, depth < 700 km)", (arc < 750) & (depth < 700)),
        ("top 200 km outside the window", (depth < 200) & ~((arc < 750) & (depth < 700))),
        ("200-660 km outside the window", (depth >= 200) & (depth < 660) & ~((arc < 750) & (depth < 700))),
        ("lower mantle, 660 km to the core", depth >= 660)]
txt = [f"{len(tri):,} cells in all"]
for name, sel in rows:
    txt.append(f"{name}: {sel.sum():,} cells, edge median {np.median(edge[sel]):.0f} km")
fig.text(0.51, 0.06, "\n".join(txt), fontsize=9, va="bottom", family="monospace")
fig.savefig(out, dpi=130, facecolor="white")
print("\n".join(txt))
