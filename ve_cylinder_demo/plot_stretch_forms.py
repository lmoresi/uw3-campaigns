"""Drag on the confined cylinder (Wi 0.5, resolution 40, wall cells 1/8) for the
momentum's share of the viscoelastic stretch at large steps: the implicit
deformation step against "linear" with backward-Euler momentum and the per-step
switching policy. A cross marks where a run stopped because Newton stalled.

python plot_stretch_forms.py <output.png>
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [
    # label, run, colour, stalled
    ("implicit, dt 1/120 (reference)", "c40w_impl_h2", "#0b0b0b", True),
    ("implicit, dt 1/60", "c40w_impl", "#eb6834", True),
    ("linear + BE, dt 1/60", "c40w_lin_be", "#2a78d6", False),
    ("linear + BE, dt 1/30", "c40w_lin_be_2x", "#1baf7a", False),
    ("switching, dt 1/60", "c40w_switch2", "#4a3aa7", False),
]


def drag(run):
    data = np.genfromtxt(os.path.join(HERE, "runs", run, "forces.csv"), delimiter=",",
                         names=True, usecols=(0, 1, 2))
    return data["t"], data["cd"]


fig, ax = plt.subplots(figsize=(8.0, 4.2), dpi=150)
for label, run, colour, stalled in RUNS:
    t, cd = drag(run)
    ax.plot(t, cd, color=colour, lw=1.2 if run != "c40w_impl_h2" else 1.6, label=label)
    if stalled:
        ax.plot(t[-1], cd[-1], marker="x", ms=9, mew=2, color=colour)
ax.set_xlim(0, 3.05)
ax.set_ylim(0, 8)
ax.set_xlabel("t")
ax.set_ylabel("drag coefficient")
ax.grid(color="#e4e3df", lw=0.6)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(sys.argv[1] if len(sys.argv) > 1 else "stretch_forms_drag.png")
