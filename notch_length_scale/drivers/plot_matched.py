"""Figures for the matched-width comparison: (1) edot_II profiles at x = -15 km,
micromorphic against Cosserat at the same W, one panel per pair
(../results/matched_profiles_ref<r>.json from profile_pairs.py); (2) the Newton
residual histories of pair P2 (micromorphic l = 0.5 km against Cosserat l = 0.236 km,
c = 1) at refs 3 and 4 (../results/eff_table.json from eff_table.py). Writes
../figures/matched_profiles.png and ../figures/matched_residuals.png."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
ref = int(sys.argv[1]) if len(sys.argv) > 1 else 3

rows = json.load(open(os.path.join(RES, f"matched_profiles_ref{ref}.json")))
STYLE = {"micromorphic": dict(color="#1b9e77", lw=2.2),
         "cosserat": [dict(color="#7570b3", lw=1.6, ls="--"), dict(color="#d95f02", lw=1.6, ls=":")]}
fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), constrained_layout=True, sharey=False)
for ax, pair in zip(axes, ("P1", "P2", "P3")):
    k = 0
    for r in (r for r in rows if r["pair"] == pair):
        style = STYLE["micromorphic"] if r["model"] == "micromorphic" else STYLE["cosserat"][k]
        if r["model"] == "cosserat":
            k += 1
        ax.plot(r["y_km"], r["over_background"], **style,
                label=f"{r['label']}: W {r['W_km']:.2f}, peak {r['peak']:.2f}")
    ax.axhline(1.0, color="#999999", lw=0.8, ls=":")
    ax.set_title(f"{pair} (ref {ref}, cut x = -15 km)", loc="left", fontsize=10)
    ax.set_xlabel("y (km)")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.grid(alpha=0.25)
axes[0].set_ylabel(r"$\dot\varepsilon_{II}$ / background (median outside $\pm$9 km)")
fig.suptitle("Matched band width: micromorphic (beta 0.1, solid) against Cosserat (dashed, "
             "dotted)", fontsize=11)
fig.savefig(os.path.join(FIG, f"matched_profiles_ref{ref}.png"), dpi=140)

eff = json.load(open(os.path.join(RES, "eff_table.json")))
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
for ax, r_ in zip(axes, (3, 4)):
    for r in eff:
        if r["pair"] != "P2" or r["ref"] != r_ or (r["model"] == "cosserat" and r["c"] != 1):
            continue
        if not r["residuals"]:
            continue
        style = STYLE["micromorphic"] if r["model"] == "micromorphic" else STYLE["cosserat"][0]
        label = (f"micromorphic l = {r['l_km']:g} km" if r["model"] == "micromorphic"
                 else f"Cosserat l = {r['l_km']:g} km, c = 1")
        ax.semilogy(range(len(r["residuals"])), r["residuals"], marker="o", ms=4, **style,
                    label=f"{label} (np {r['np']})")
    ax.set_title(f"P2, ref {r_} ({'cold' if r_ < 4 else 'grid-sequenced'}), tight FMG",
                 loc="left", fontsize=10)
    ax.set_xlabel("Newton step")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, fontsize=9)
axes[0].set_ylabel("|F|")
fig.savefig(os.path.join(FIG, "matched_residuals.png"), dpi=140)
print("written")
