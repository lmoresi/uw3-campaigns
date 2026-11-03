"""Tangential surface velocity around the outer wall of an annulus run, at a set of
checkpoints, one curve per checkpoint, with the trench of each marked.

    python surface_profiles.py -uw_run <run dir> -uw_indices 2060,2100,2140
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import underworld3 as uw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
from annulus_model import annulus_mesh, annulus_radii, clamp_radii

params = uw.Params(
    uw_run="~/+Simulations/zg95/annulus_faults/runs/tau1x1.50_fault_th0_dip45_moving",
    uw_indices="2060,2100,2140",
    uw_out="",                  # image path (default: <run>/renders/surface_profiles.png)
)
run = os.path.expanduser(params.uw_run)
indices = [int(i) for i in str(params.uw_indices).split(",")]
with open(os.path.join(run, f"state_{indices[0]:05d}.json")) as f:
    p = json.load(f)["params"]
mesh = annulus_mesh(float(p["uw_cell"]), int(p["uw_refinement"]))
r_o, r_i = annulus_radii()
V = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
theta = np.linspace(-np.pi, np.pi, 1441)
points = clamp_radii(np.column_stack([r_o * np.cos(theta), r_o * np.sin(theta)]), r_o, r_i)

fig, ax = plt.subplots(figsize=(12, 4.5))
for index in indices:
    V.read_timestep("annulus", "V", index, outputPath=run)
    with open(os.path.join(run, f"state_{index:05d}.json")) as f:
        state = json.load(f)
    v = np.asarray(uw.function.evaluate(V.sym, points)).reshape(-1, 2)
    v_theta = -v[:, 0] * np.sin(theta) + v[:, 1] * np.cos(theta)
    line, = ax.plot(np.degrees(theta), v_theta, lw=1, label=f"step {index}, t {state['t']:.4f}")
    if "theta_trench" in state:
        ax.axvline(np.degrees(state["theta_trench"]), color=line.get_color(), lw=0.7, ls="--")
ax.axhline(0, color="k", lw=0.5)
ax.set_xlabel("theta (degrees)")
ax.set_ylabel("tangential surface velocity")
ax.set_xlim(-180, 180)
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
ax.set_title(os.path.basename(run) + ": surface velocity (dashed: trench)", fontsize=9, loc="left")
fig.tight_layout()
out = params.uw_out or os.path.join(run, "renders", "surface_profiles.png")
fig.savefig(out, dpi=130)
print("->", out)
