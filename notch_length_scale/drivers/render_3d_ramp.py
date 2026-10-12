"""Figures of a 3-D along-strike ramp run: strike-normal sections of edot_II at three
positions along strike, a constant-depth map, and W / peak against z.

The velocity is read from the run's checkpoint (any decomposition) onto a rebuilt 3-D
notch; edot_II is evaluated at the vertices of pyvista slices of the mesh, so it is
drawn on the mesh's own cells. One process (pyvista draws one rank's mesh).

Usage: python render_3d_ramp.py -uw_run <checkpoint name> -uw_mesh <3-D .msh>
       -uw_ref 2 -uw_weak_ramp 8,2
Writes ../results/<run>_sections.png, _map.png, _alongstrike.png (and ../figures/).
"""
import json
import math
import os
import shutil
import sys

import numpy as np
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

pv.OFF_SCREEN = True
params = uw.Params(
    uw_run=uw.Param("", description="checkpoint name under results/micromorphic/checkpoints"),
    uw_mesh=uw.Param("", description="the run's 3-D gmsh file"),
    uw_ref=uw.Param(2, description="the run's refinement"),
    uw_weak_ramp=uw.Param("8,2", description="the run's 'z0,w' in km"),
    uw_depth_km=uw.Param(10.0, description="depth of the constant-depth map (km below the top)"),
)
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
run = str(params.uw_run)
z0, w = (float(v) for v in str(params.uw_weak_ramp).split(","))

if uw.mpi.size > 1:
    raise RuntimeError("render_3d_ramp.py draws on one process: run it without mpirun")

S = cn.build_notch(int(params.uw_ref), 0.0, seed=False, msh=str(params.uw_mesh),
                   weak_ramp=(z0, w))
S["v"].read_timestep(run, S["v"].name, 0,
                     outputPath=os.path.join(RES, "micromorphic", "checkpoints"))
volume = vis.mesh_to_pv_mesh(S["mesh"])                 # points in metres
L = cn.H_KM * 1.0e3


def with_edot(surface):
    """``surface`` (metres) carrying log10 edot_II / (V/H), points rescaled to km."""
    pts = np.asarray(surface.points) / L
    edot = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, pts)).ravel()
    surface.point_data["log10 edot"] = np.log10(np.maximum(edot, 1.0e-30))
    surface.points = np.asarray(surface.points) / 1.0e3
    return surface


Lz = float(volume.bounds[5]) / 1.0e3
z_cuts = [0.5, z0, Lz - 0.5]
sections = [with_edot(volume.slice(normal="z", origin=(0.0, -15.0e3, z * 1.0e3))) for z in z_cuts]
depth_map = with_edot(volume.slice(normal="y", origin=(0.0, -float(params.uw_depth_km) * 1.0e3,
                                                       Lz * 0.5e3)))
values = np.concatenate([s.point_data["log10 edot"] for s in sections])
clim = (-0.4, 0.4)          # the 3-D bands are weaker than 2-D: this range resolves them


def image(surface, view, focal, scale, size):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.add_mesh(surface, scalars="log10 edot", cmap="inferno", clim=clim,
                show_edges=False, lighting=False, show_scalar_bar=False)
    getattr(pl, view)()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = focal
    pl.camera.parallel_scale = scale
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


import matplotlib            # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402


def colourbar(fig, axes):
    m = plt.cm.ScalarMappable(cmap="inferno", norm=plt.Normalize(*clim))
    cb = fig.colorbar(m, ax=axes, orientation="horizontal", fraction=0.04, pad=0.2, aspect=50)
    cb.set_label(r"$\log_{10}\,\dot\varepsilon_{II}\,/\,(V/H)$")


def ramp(z):
    return 1.0 - math.tanh((z0 - z) / w)    # log10 of eta_b / 1e21


outs = []
# strike-normal sections (x-y planes at fixed z)
fig, axes = plt.subplots(1, 3, figsize=(18, 4.6))
for ax, z, s in zip(axes, z_cuts, sections):
    ax.imshow(image(s, "view_xy", (0.0, -11.0, z), 11.0, (1240, 430)),
              extent=(-32, 32, -22, 0))
    ax.set_title(f"z = {z:.1f} km   log10(eta_b) = {21 + ramp(z):.2f}", fontsize=10, loc="left")
    ax.set_xlabel("x (km)")
axes[0].set_ylabel("y (km)")
colourbar(fig, axes)
outs.append(os.path.join(RES, f"{run}_sections.png"))
fig.savefig(outs[-1], dpi=130, bbox_inches="tight")
plt.close(fig)

# constant-depth map (x-z plane)
fig, ax = plt.subplots(figsize=(12, 4.6))
ax.imshow(image(depth_map, "view_xz", (0.0, -float(params.uw_depth_km), Lz / 2), Lz / 2 + 0.5,
                (1600, int(1600 * (Lz + 1) / 64))),
          extent=(-32, 32, Lz + 0.5, -0.5), aspect="auto")
ax.axhline(z0, color="white", lw=0.8, ls="--")
ax.set_xlabel("x (km)")
ax.set_ylabel("z, along strike (km)")
ax.set_title(f"depth {float(params.uw_depth_km):g} km; dashed: z0 = {z0:g} km (ramp width {w:g} km)",
             fontsize=10, loc="left")
colourbar(fig, ax)
outs.append(os.path.join(RES, f"{run}_map.png"))
fig.savefig(outs[-1], dpi=130, bbox_inches="tight")
plt.close(fig)

# W and peak against z, from the run's record
record = json.load(open(os.path.join(RES, "micromorphic", run + ".json")))
zs = sorted(float(k) for k in record["along_strike"])
get = lambda key: [record["along_strike"][f"{z:.2f}"][key] for z in zs]
fig, axes = plt.subplots(3, 1, figsize=(6.5, 7.5), sharex=True)
axes[0].plot(zs, [21 + ramp(z) for z in zs], "k-", lw=2)
axes[0].set_ylabel("log10 eta_b (Pa s)")
axes[1].plot(zs, get("W_km"), "o-", lw=2, ms=8, color="#2a6fb0")
axes[1].set_ylabel("W (km)")
axes[2].plot(zs, get("peak"), "o-", lw=2, ms=8, color="#2a6fb0")
axes[2].set_ylabel("peak over background")
axes[2].set_xlabel("z, along strike (km)")
for ax in axes:
    ax.axvline(z0, color="0.6", lw=1, ls="--")
    ax.grid(color="0.9")
axes[0].set_title(run.replace("micro_", ""), fontsize=8, loc="left")
outs.append(os.path.join(RES, f"{run}_alongstrike.png"))
fig.savefig(outs[-1], dpi=130, bbox_inches="tight")
plt.close(fig)

os.makedirs(FIG, exist_ok=True)
for o in outs:
    shutil.copy(o, FIG)
    print(o)
