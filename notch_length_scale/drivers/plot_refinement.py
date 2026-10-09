"""Profiles and band measures across refinement, from ../results/current_widths.json
(``measure_current.py``; no fields read, runs anywhere):

* ``refinement_profiles.png``: edot_II over the outside background on the cut
  x = -15 km (the left band), refs 1-5 overlaid, one panel per l (1 and 0.5 km);
* ``width_peak_vs_h.png``: W (integral width, background outside +-9 km) and the peak
  over the same background against h_min, for every l, refs 1-5.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
rows = json.load(open(os.path.join(RES, "current_widths.json")))
_coss = os.path.join(RES, "current_widths_cosserat.json")
coss_rows = json.load(open(_coss)) if os.path.exists(_coss) else []
REF_COLOURS = {1: "#c6dbef", 2: "#9ecae1", 3: "#4292c6", 4: "#08519c", 5: "#08306b"}
REF_WIDTH = {1: 1.0, 2: 1.2, 3: 1.5, 4: 1.8, 5: 2.0}

for model_rows, label, out in ((rows, "Micromorphic notch, beta = 0.1", "refinement_profiles.png"),
                               (coss_rows, "Cosserat notch, c = 1", "refinement_profiles_cosserat.png")):
  if not model_rows:
    continue
  fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True, sharey=True)
  for ax, l_km in zip(axes, (1.0, 0.5)):
    for r in sorted((r for r in model_rows if r["l_km"] == l_km), key=lambda r: r["ref"]):
        p = r["profile"]
        ax.plot(p["y_km"], p["over_background"], color=REF_COLOURS[r["ref"]],
                lw=REF_WIDTH[r["ref"]],
                label=f"ref {r['ref']} (h$_{{min}}$ {1e3 * r['h_min_km']:.0f} m)")
    ax.axhline(1.0, color="#999999", lw=0.8, ls=":")
    ax.set_title(f"l = {l_km:g} km,  cut x = {rows[0]['profile']['x_km']:g} km", loc="left",
                 fontsize=10)
    ax.set_xlabel("y (km)")
    ax.grid(alpha=0.25)
  axes[0].set_ylabel(r"$\dot\varepsilon_{II}$ / background (median outside $\pm$9 km)")
  axes[1].legend(frameon=False, fontsize=9)
  fig.suptitle(f"{label}, xi = 0: profile across the left band, refs 1-5", fontsize=11)
  fig.savefig(os.path.join(FIG, out), dpi=140)

L_COLOURS = {0.25: "#d95f02", 0.5: "#7570b3", 1.0: "#1b9e77", 2.0: "#666666"}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), constrained_layout=True)
for l_km, colour in L_COLOURS.items():
    sel = sorted((r for r in rows if r["l_km"] == l_km), key=lambda r: r["ref"])
    if not sel:
        continue
    h = np.array([1e3 * r["h_min_km"] for r in sel])
    for ax, key in zip(axes, ("W_km", "peak")):
        ax.plot(h, [r[key] for r in sel], "-o", color=colour, ms=5, lw=1.6,
                label=f"micromorphic, l = {l_km:g} km")
        ax.annotate(f"{sel[-1][key]:.2f}", (h[-1], sel[-1][key]), textcoords="offset points",
                    xytext=(-4, 6), ha="right", fontsize=8, color="#333333")
for l_km, colour in L_COLOURS.items():
    sel = sorted((r for r in coss_rows if r["l_km"] == l_km), key=lambda r: r["ref"])
    if not sel:
        continue
    h = np.array([1e3 * r["h_min_km"] for r in sel])
    for ax, key in zip(axes, ("W_km", "peak")):
        ax.plot(h, [r[key] for r in sel], "--s", color=colour, ms=5, lw=1.4, mfc="white",
                label=f"Cosserat c = 1, l = {l_km:g} km")
        ax.annotate(f"{sel[-1][key]:.2f}", (h[-1], sel[-1][key]), textcoords="offset points",
                    xytext=(-4, -12), ha="right", fontsize=8, color="#333333")
h_ticks = sorted({round(1e3 * r["h_min_km"]) for r in rows}, reverse=True)
for ax in axes:
    ax.set_xscale("log")
    ax.set_xticks(h_ticks, [f"{h:g}" for h in h_ticks])
    ax.minorticks_off()
    ax.invert_xaxis()
    ax.set_xlabel(r"$h_{min}$ (m), refs 1 $\rightarrow$ 5")
    ax.grid(alpha=0.25, which="both")
axes[0].set_ylabel("W (km): integral width, background outside $\\pm$9 km")
axes[1].set_ylabel("peak: (max - background) / background")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=9,
           bbox_to_anchor=(0.5, -0.13))
fig.suptitle("Band width and peak against mesh size (current estimator); micromorphic "
             "beta = 0.1 solid, Cosserat c = 1 dashed; xi = 0", fontsize=11)
fig.savefig(os.path.join(FIG, "width_peak_vs_h.png"), dpi=140, bbox_inches="tight")
print("written")
