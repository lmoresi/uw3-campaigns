"""Figure for REPORT.md: band width, Newton cost and band profiles against refinement.

Reads the json records and saved profiles in ../results (micromorphic_notch.py,
cosserat_notch.py, newton_exact_linear.py). Widths are the mean of the left and right
bands (W_equiv, horizontal cuts); the bar spans the two. Only converged runs carry a
width. Writes ../results/length_scale_summary.png.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_here, "..", "results")
H_MIN_KM = {1: 0.172, 2: 0.086, 3: 0.043}
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dc"
SERIES = [
    # label, colour (fixed categorical order), record path pattern, profile pattern
    ("micromorphic β=0.1, l=1 km, ξ=0", "#2a78d6",
     "micromorphic/micro_ref{r}_xi0_beta0.1_l1.json",
     "micromorphic/profiles_micro_ref{r}_xi0_beta0.1_l1.npz"),
    ("micromorphic β=0.1, l=0.5 km, ξ=0", "#eb6834",
     "micromorphic/micro_ref{r}_xi0_beta0.1_l0.5.json", None),
    ("micromorphic β=0.05, l=1 km, ξ=0.01", "#1baf7a",
     "micromorphic/micro_ref{r}_xi0.01_beta0.05_l1.json", None),
    ("Cosserat c=1, l=1 km, ξ=0", "#eda100",
     "cosserat/cosserat_ref{r}_xi0_c1_l1_P1.json",
     "cosserat/profiles_cosserat_ref{r}_xi0_c1_l1_P1.npz"),
    ("Cosserat c=1, l=0.5 km, ξ=0", "#e87ba4",
     "cosserat/cosserat_ref{r}_xi0_c1_l0.5_P1.json", None),
]


def load(pattern, ref):
    path = os.path.join(RES, pattern.format(r=ref))
    return json.load(open(path)) if os.path.exists(path) else None


def width(record):
    w = [record["W_equiv_km"].get(side) for side in ("L", "R")]
    w = [v for v in w if v is not None]
    return np.mean(w), min(w), max(w)


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


fig, (ax_w, ax_n, ax_p) = plt.subplots(1, 3, figsize=(16, 6.4),
                                       gridspec_kw=dict(width_ratios=[1.2, 1, 1.2]))

# ---- band width against h ----------------------------------------------------------
h = np.array([H_MIN_KM[r] for r in (1, 2, 3)])
h_fine = np.geomspace(0.035, 0.2, 50)
ax_w.plot(h_fine, 31 * np.sqrt(0.01 * h_fine), color=MUTED, linestyle="--", linewidth=1.5,
          label="no length scale: W = 31√(ξh), ξ=0.01")
for label, colour, rec, _ in SERIES:
    pts = []
    for r in (1, 2, 3):
        d = load(rec, r)
        if d is not None and d["converged"]:
            pts.append((H_MIN_KM[r],) + width(d))
    if not pts:
        continue
    pts = np.array(pts)
    ax_w.errorbar(pts[:, 0], pts[:, 1], yerr=[pts[:, 1] - pts[:, 2], pts[:, 3] - pts[:, 1]],
                  color=colour, marker="o", markersize=8, linewidth=2, capsize=3,
                  markeredgecolor="white", markeredgewidth=1.5, label=label)
plain = load("control/plain_xi0.01_ref1.json", 1)
if plain is not None:
    w = [v for v in plain["bands"].values() if v is not None]
    ax_w.plot([H_MIN_KM[1]], [np.mean(w)], marker="s", markersize=9, color=MUTED,
              linestyle="none", label="plain Newton, ξ=0.01 (converged at ref 1 only)")
ax_w.set_xscale("log")
ax_w.set_xticks(h, [f"ref {r}\n{H_MIN_KM[r]} km" for r in (1, 2, 3)])
ax_w.minorticks_off()
ax_w.invert_xaxis()
ax_w.set_ylim(0, 5.5)
ax_w.set_xlabel("mesh size h (min cell radius)", color=INK)
ax_w.set_ylabel("band width W (km)", color=INK)
ax_w.set_title("Band width stops tracking h", color=INK, loc="left", fontsize=12)
style(ax_w)
ax_w.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22),
            ncol=2)

# ---- Newton steps -------------------------------------------------------------------
offsets = np.linspace(-0.24, 0.24, len(SERIES))
for (label, colour, rec, _), dx in zip(SERIES, offsets):
    for r in (1, 2, 3):
        d = load(rec, r)
        if d is None:
            continue
        if d["converged"]:
            ax_n.bar(r + dx, d["nl_its"], width=0.11, color=colour)
        else:
            ax_n.plot(r + dx, d["nl_its"], marker="x", markersize=9, color=colour,
                      markeredgewidth=2)
for r, name in ((1, "plain_xi0_ref1"), (2, "plain_xi0.01_ref2")):
    d = load(f"control/{name}.json", r)
    if d is not None:
        ax_n.plot(r + 0.36, d["its"], marker="x", markersize=10, color=MUTED, markeredgewidth=2)
        ax_n.annotate(f"plain ξ={d['xi']:g}:\nline search fails",
                      (r + 0.36, d["its"]), xytext=(9, 0), textcoords="offset points",
                      fontsize=8, color=MUTED, va="center")
ax_n.set_xticks([1, 2, 3], ["ref 1", "ref 2", "ref 3"])
ax_n.set_ylabel("exact Newton steps (bars = converged, × = failed)", color=INK)
ax_n.set_title("Every coupled run converges, ref 3 included", color=INK, loc="left",
               fontsize=12)
ax_n.text(0.0, -0.16, "bar colours as in the left panel", transform=ax_n.transAxes,
          fontsize=8, color=MUTED)
ax_n.set_xlim(0.5, 3.9)
style(ax_n)

# ---- profiles across the left band ---------------------------------------------------
level = 2          # y = -0.5 of the cut levels [-0.7, -0.6, -0.5, -0.4]
ref_shade = {1: 0.35, 2: 0.65, 3: 1.0}
for label, colour, _, prof in SERIES:
    if prof is None:
        continue
    for r in (1, 2, 3):
        path = os.path.join(RES, prof.format(r=r))
        if not os.path.exists(path):
            continue
        p = np.load(path)
        x_km = p["x"] * float(p["H_km"])
        f = p["edot_II"][level]
        left = x_km < 0
        ax_p.plot(x_km[left], f[left] / np.median(f), color=colour, alpha=ref_shade[r],
                  linewidth=2, label=f"{label.split(',')[0]}, ref {r}")
ax_p.set_xlim(-30, -2)
ax_p.set_xlabel("x (km), cut at y = −15 km", color=INK)
ax_p.set_ylabel("ε̇_II / median along the cut", color=INK)
ax_p.set_title("Band profile converges in h (l = 1 km, ξ = 0)", color=INK,
               loc="left", fontsize=12)
style(ax_p)
ax_p.legend(fontsize=8, frameon=False, loc="upper left")

fig.tight_layout()
out = os.path.join(RES, "length_scale_summary.png")
fig.savefig(out, dpi=150)
print(out)
