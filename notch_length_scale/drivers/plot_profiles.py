"""Strain-rate profiles across a shear band, against resolution and against l.

Reads the vertical-cut profiles (``vprofiles_<run>.npz``) and the widths and peaks in
``sweep_widths.json``, both written by measure_sweep.py. The profile is the vertical
cut through the right limb at x = 15 km, centred on its peak; edot_II is shown over
the cut's own median background (the profiles' unit then cancels).

  (a) one l (1 km), refs 1-4: does the band converge as h halves?
  (b) one resolution (ref 3), l = 0.25..2 km: how does l set the band?
  (c) the peak of edot_II over the far-field background on the vertical cuts, against
      h, per l: with a length scale it stays put as h -> 0; with none it would grow
      like 1/h. (A ratio, so the profiles' unit cancels.)
  (d) band width W (vertical cuts) against h, per l.

Writes ../results/band_profiles.png.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_here, "..", "results")
M = os.path.join(RES, "micromorphic")
STATION = 0.5                  # x / H of the cut: 15 km, right limb
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dc"
L_COLOURS = {0.25: "#2a78d6", 0.5: "#eb6834", 1.0: "#1baf7a", 2.0: "#eda100"}
REF_ALPHA = {1: 0.3, 2: 0.55, 3: 0.8, 4: 1.0}


def profile(name):
    """(y relative to the peak in km, edot_II over the cut's median background) on the
    cut at STATION, or None. The ratio cancels the profiles' unit."""
    path = os.path.join(M, f"vprofiles_{name}.npz")
    if not os.path.exists(path):
        return None
    p = np.load(path)
    k = int(np.argmin(np.abs(p["stations"] - STATION)))
    f = p["edot_II"][k]
    y_km = p["y"] * float(p["H_km"])
    return y_km - y_km[np.argmax(f)], f / np.median(f)


def run_name(ref, beta, l_km, tag=""):
    return f"micro_ref{ref}_xi0_beta{beta:g}_l{l_km:g}" + (f"_{tag}" if tag else "")


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


rows = json.load(open(os.path.join(RES, "sweep_widths.json")))
fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))
(ax_a, ax_b), (ax_c, ax_d) = axes

for ref in (1, 2, 3, 4):
    for tag in ("", "production_tight"):
        got = profile(run_name(ref, 0.1, 1.0, tag))
        if got is not None:
            ax_a.plot(*got, color=L_COLOURS[1.0], alpha=REF_ALPHA[ref], linewidth=2,
                      label=f"ref {ref}")
            break
ax_a.set_title("(a) l = 1 km, β = 0.1: refinement", loc="left", color=INK)
ax_a.legend(frameon=False, fontsize=9)

for l_km, colour in L_COLOURS.items():
    got = profile(run_name(3, 0.1, l_km))
    if got is not None:
        ax_b.plot(*got, color=colour, linewidth=2, label=f"l = {l_km:g} km")
ax_b.set_title("(b) ref 3, β = 0.1: band length l", loc="left", color=INK)
ax_b.legend(frameon=False, fontsize=9)

for ax in (ax_a, ax_b):
    ax.set_xlim(-8, 8)
    ax.set_xlabel("distance along the vertical cut from the peak (km), x = 15 km",
                  color=INK)
    ax.set_ylabel("ε̇_II / background on the same cut", color=INK)
    style(ax)


def mean_side(values):
    v = [x for x in values.values() if x is not None]
    return (np.mean(v), min(v), max(v)) if v else None


def relative_peaks(name):
    """Peak over the far-field background on each vertical cut, as {side: (mean, min,
    max)} over that side's stations. Dimensionless, so the profiles' unit cancels."""
    p = np.load(os.path.join(M, f"vprofiles_{name}.npz"))
    out = {}
    for side, sel in (("L", p["stations"] < 0), ("R", p["stations"] > 0)):
        f = p["edot_II"][sel]
        base = np.median(f, axis=1)
        out[side] = float(np.mean((f.max(axis=1) - base) / base))
    return out


for l_km, colour in L_COLOURS.items():
    sel = sorted((r for r in rows if r["beta"] == 0.1 and r["l_km"] == l_km and r["tag"] == ""),
                 key=lambda r: r["ref"])
    for r in sel:
        r["relative_peak"] = relative_peaks(r["run"][7:-4])
    for ax, key in ((ax_c, "relative_peak"), (ax_d, "W_vertical_km")):
        pts = [(r["h_min_km"],) + mean_side(r[key]) for r in sel if mean_side(r[key])]
        if not pts:
            continue
        pts = np.array(pts)
        ax.errorbar(pts[:, 0], pts[:, 1], yerr=[pts[:, 1] - pts[:, 2], pts[:, 3] - pts[:, 1]],
                    color=colour, marker="o", markersize=7, linewidth=2, capsize=3,
                    markeredgecolor="white", label=f"l = {l_km:g} km")
for ax, title, ylabel in (
        (ax_c, "(c) peak strain rate against h (β = 0.1)", "(peak − background) / background"),
        (ax_d, "(d) band width against h (β = 0.1, vertical cuts)", "W (km)")):
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("mesh size h (min cell radius, km)", color=INK)
    ax.set_ylabel(ylabel, color=INK)
    ax.set_title(title, loc="left", color=INK)
    ax.legend(frameon=False, fontsize=9)
    style(ax)

fig.tight_layout()
out = os.path.join(RES, "band_profiles.png")
fig.savefig(out, dpi=140)
print(out)
