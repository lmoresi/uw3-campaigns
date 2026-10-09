"""The beta-xi map at ref 3 (tag ``map``): Newton steps, integral band width W, relative
peak and the largest yield shift H chi / C against beta and xi, one row per l. Reads the
runs' json records only (no fields), so it runs anywhere. Writes
../figures/beta_xi_map.png and ../results/beta_xi_map.json."""
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
ETA_BG, C = 1.0e23, 1.0e8          # Pa s, Pa (coupled_notch, the notch's cohesion)
NAME = re.compile(r"micro_ref3_xi([\d.]+)_beta([\d.]+)_l([\d.]+)_map\.json$")

rows = []
for path in glob.glob(os.path.join(RES, "micromorphic", "micro_ref3_*_map.json")):
    match = NAME.search(path)
    xi, beta, l_km = map(float, match.groups())
    r = json.load(open(path))
    peaks = [v for v in r["relative_peak"].values() if v is not None]
    rows.append(dict(l_km=l_km, beta=beta, xi=xi, converged=r["converged"], reason=r["reason"],
                     nl_its=r["nl_its"], W_km=r["W_integral_km"]["median"],
                     peak=float(np.mean(peaks)), shift_over_C=beta * ETA_BG * r["chi_max"] / C,
                     floor_bound_over_floor=r["floor_bound_over_floor"]))
json.dump(sorted(rows, key=lambda d: (d["l_km"], d["beta"], d["xi"])),
          open(os.path.join(RES, "beta_xi_map.json"), "w"), indent=1)

betas = sorted({d["beta"] for d in rows})
xis = sorted({d["xi"] for d in rows})
ls = sorted({d["l_km"] for d in rows}, reverse=True)
panels = [("nl_its", "Newton steps", "Greys", "{:.0f}"),
          ("W_km", "band width W (km)", "Blues", "{:.2f}"),
          ("peak", "peak / background", "Oranges", "{:.2f}"),
          ("shift_over_C", r"max $H\chi$ / C", "Purples", "{:.2f}")]
fig, axes = plt.subplots(len(ls), len(panels), figsize=(4.2 * len(panels), 3.6 * len(ls)),
                         constrained_layout=True)
for i, l_km in enumerate(ls):
    for j, (key, title, cmap, fmt) in enumerate(panels):
        ax = axes[i, j]
        grid = np.full((len(betas), len(xis)), np.nan)
        for d in rows:
            if d["l_km"] == l_km and d["converged"]:   # a diverged iterate is no data
                grid[betas.index(d["beta"]), xis.index(d["xi"])] = d[key]
        vals = [d[key] for d in rows if d["converged"]]
        ax.imshow(grid, cmap=cmap, origin="lower", aspect="auto",
                  vmin=min(vals), vmax=max(vals) * 1.15)
        for d in rows:
            if d["l_km"] != l_km:
                continue
            a, b = betas.index(d["beta"]), xis.index(d["xi"])
            text = fmt.format(d[key]) if d["converged"] else "diverged"
            ax.text(b, a, text, ha="center", va="center", fontsize=9,
                    color="#222222" if d["converged"] else "#b00000",
                    fontweight="normal" if d["converged"] else "bold")
        ax.set_xticks(range(len(xis)), [f"{x:g}" for x in xis])
        ax.set_yticks(range(len(betas)), [f"{b:g}" for b in betas])
        ax.set_xlabel(r"$\xi$  (rate strengthening / $\eta_{bg}$)")
        ax.set_ylabel(r"$\beta = H/\eta_{bg}$")
        ax.set_title(f"{title},  l = {l_km:g} km", fontsize=10)
fig.suptitle("Micromorphic notch, ref 3: which (beta, xi) converge, and what each buys", fontsize=12)
out = os.path.join(_here, "..", "figures", "beta_xi_map.png")
fig.savefig(out, dpi=130)
print(out)
