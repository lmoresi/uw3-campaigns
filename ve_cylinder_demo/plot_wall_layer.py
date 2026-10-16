"""The elastic layer on the cylinder wall at step 48 (t 0.80, just before the
failing step), Oldroyd-B against FENE-P (L^2 100): conformation trace and first
normal stress difference along the wall in the wall frame, at the sampling
distance nearest the wall (1e-4). From the wall reports (-uw_wall_report).

python plot_wall_layer.py <output.png>
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [("Oldroyd-B", "c40w_wall2", "#2a78d6"), ("FENE-P, $L^2 = 100$", "c40w_fene", "#eb6834")]


def wall(run, step=48):
    data = np.genfromtxt(os.path.join(HERE, "runs", run, f"wall_{step:05d}.csv"), delimiter=",", names=True)
    near = data["d"] == data["d"].min()
    return data["angle"][near], data["trc"][near], data["N1"][near]


fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6), dpi=150)
for label, run, colour in RUNS:
    angle, trc, n1 = wall(run)
    axes[0].semilogy(angle, trc, color=colour, lw=1.6, marker="o", ms=3, label=label)
    axes[1].plot(angle, n1, color=colour, lw=1.6, marker="o", ms=3, label=label)
axes[0].axhline(100, color="#52514e", lw=0.8, ls="--")
axes[0].text(5, 115, "$L^2$", color="#52514e", fontsize=8)
axes[0].set_ylabel("tr c at the wall")
axes[1].set_ylabel(r"$N_1 = \sigma_{tt} - \sigma_{nn}$ at the wall ($\rho U^2$)")
for ax in axes:
    ax.set_xlabel("angle from the downstream axis (deg)")
    ax.set_xticks(range(0, 361, 90))
    ax.axvline(180, color="#c3c2b7", lw=0.8)
    ax.grid(color="#e4e3df", lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(sys.argv[1] if len(sys.argv) > 1 else "wall_layer.png")
