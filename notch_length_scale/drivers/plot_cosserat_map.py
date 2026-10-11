"""The Cosserat width map at ref 3 (tag ``cmap``, exact LU, xi = 0, omega P1): W and
the peak (current estimator: integral width, background outside +-9 km) and the
Newton steps against l and c = eta_c / visc_lin, with the micromorphic widths at
ref 3 (beta 0.1, l = 0.25, 0.5, 1 km) marked as contours on the W panel. Reads the
runs' json records only. Writes ../figures/cosserat_width_map.png and
../results/cosserat_width_map.json."""
import glob
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_here, "..", "results")
NAME = re.compile(r"cosserat_ref3_xi0_c([\d.]+)_l([\d.]+)_P1(?:_np4)?_cmap\.json$")
rows = []
for path in glob.glob(os.path.join(RES, "cosserat", "cosserat_ref3_*_cmap.json")):
    m = NAME.search(path)
    if not m:
        continue
    c, l_km = map(float, m.groups())
    r = json.load(open(path))
    rows.append(dict(l_km=l_km, c=c, converged=r["converged"], reason=r["reason"],
                     nl_its=r["nl_its"], W_km=r.get("W_outside9_km"),
                     peak=r.get("peak_outside9"), seconds=r["seconds"]))
rows.sort(key=lambda d: (d["l_km"], d["c"]))
json.dump(rows, open(os.path.join(RES, "cosserat_width_map.json"), "w"), indent=1)

micro = {r["l_km"]: r["W_km"] for r in json.load(open(os.path.join(RES, "current_widths.json")))
         if r["ref"] == 3}
ls = sorted({d["l_km"] for d in rows})
cs = sorted({d["c"] for d in rows})
panels = [("W_km", "band width W (km)", "Blues", "{:.2f}"),
          ("peak", "peak / background", "Oranges", "{:.2f}"),
          ("nl_its", "Newton steps (exact LU)", "Greys", "{:.0f}")]
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)
for ax, (key, title, cmap, fmt) in zip(axes, panels):
    grid = np.full((len(ls), len(cs)), np.nan)
    for d in rows:
        if d["converged"] and d[key] is not None:
            grid[ls.index(d["l_km"]), cs.index(d["c"])] = d[key]
    ax.imshow(grid, cmap=cmap, origin="lower", aspect="auto",
              vmin=np.nanmin(grid), vmax=np.nanmax(grid) * 1.15)
    for d in rows:
        i, j = ls.index(d["l_km"]), cs.index(d["c"])
        ok = d["converged"] and d[key] is not None
        ax.text(j, i, fmt.format(d[key]) if ok else "diverged", ha="center", va="center",
                fontsize=9, color="#222222" if ok else "#b00000",
                fontweight="normal" if ok else "bold")
    if key == "W_km":
        # the micromorphic targets as contours of the (log c, l) grid
        cs_ = ax.contour(np.arange(len(cs)), np.arange(len(ls)), grid,
                         levels=sorted(micro[l] for l in (0.25, 0.5, 1.0) if l in micro),
                         colors="#d95f02", linewidths=1.4)
        ax.clabel(cs_, fmt=lambda v: f"micro {v:.2f}", fontsize=8)
    ax.set_xticks(range(len(cs)), [f"{c:g}" for c in cs])
    ax.set_yticks(range(len(ls)), [f"{l:g}" for l in ls])
    ax.set_xlabel(r"$c = \eta_c / \eta_{lin}$")
    ax.set_ylabel("Cosserat l (km)")
    ax.set_title(title, fontsize=10)
fig.suptitle("Cosserat notch at ref 3 (exact LU, xi = 0, omega P1): width map; orange "
             "contours = micromorphic W at beta 0.1, l = 0.25 / 0.5 / 1 km", fontsize=11)
fig.savefig(os.path.join(_here, "..", "figures", "cosserat_width_map.png"), dpi=130)
print("written", len(rows), "runs")
