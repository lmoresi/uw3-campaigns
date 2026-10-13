"""3-D notch run, drawn so the bands can be seen: the weak region (lower layer and
notch) extracted as its own sub-mesh and drawn as a solid body, and the strain rate of
the STRONG cells only, on planes of constant x through the bands. Each x-plane cuts a
band at the depth where it crosses that x, so the plane shows the band against depth
and along strike at once.

Linear colour scale (the bands are 2-3x the background). Two figures from one checkpoint:
  <run>_xsections3d.png  oblique 3-D view: weak body + x-planes (strong cells only)
  <run>_xsections.png    the same x-sections laid flat, depth against strike

One process (pyvista draws one rank's mesh). Usage:
  python render_3d_xsections.py -uw_run <checkpoint name> -uw_mesh <3-D .msh> -uw_ref 2
        [-uw_weak_ramp 8,2 -uw_ramp_scope weak] [-uw_xs -24,-18,-12,-6,6,12,18,24]
"""
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
    uw_weak_ramp=uw.Param("", description="the run's 'z0,w' in km (empty = uniform)"),
    uw_ramp_scope=uw.Param("weak", description="the run's ramp scope"),
    uw_xs=uw.Param("-24,-18,-12,-6,6,12,18,24", description="x positions of the sections (km)"),
    uw_clim=uw.Param("", description="edot_II/(V/H) colour range 'lo,hi' (empty = the "
                                      "2nd-99.5th percentile over the sections)"),
)
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
run = str(params.uw_run)
ramp = tuple(float(v) for v in str(params.uw_weak_ramp).split(",")) if str(params.uw_weak_ramp) else None
xs = [float(v) for v in str(params.uw_xs).split(",")]
clim = tuple(float(v) for v in str(params.uw_clim).split(",")) if str(params.uw_clim) else None

if uw.mpi.size > 1:
    raise RuntimeError("render_3d_xsections.py draws on one process: run it without mpirun")

S = cn.build_notch(int(params.uw_ref), 0.0, seed=False, msh=str(params.uw_mesh),
                   weak_ramp=ramp, ramp_scope=str(params.uw_ramp_scope))
S["v"].read_timestep(run, S["v"].name, 0,
                     outputPath=os.path.join(RES, "micromorphic", "checkpoints"))
L = cn.H_KM * 1.0e3

grid = vis.mesh_to_pv_mesh(S["mesh"])                       # metres
strong_cell = np.asarray(S["mat"].data).ravel() > 0.5       # P0, plex cell order
grid.cell_data["strong"] = strong_cell.astype(float)
grid.points = np.asarray(grid.points) / 1.0e3               # km for the camera
weak_body = grid.extract_cells(np.flatnonzero(~strong_cell)).extract_surface()
strong = grid.extract_cells(np.flatnonzero(strong_cell))
Lz = float(grid.bounds[5])


def with_edot(surface):
    """``surface`` (km) carrying edot_II / (V/H) at its points (a LINEAR scale: the
    bands are a factor of 2-3 over background, which a log scale flattens)."""
    pts = np.asarray(surface.points) * 1.0e3 / L
    edot = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, pts)).ravel()
    surface.point_data["edot"] = edot
    return surface


sections = [with_edot(strong.slice(normal="x", origin=(x, -15.0, Lz / 2))) for x in xs]
if clim is None:
    allv = np.concatenate([s.point_data["edot"] for s in sections])
    clim = (float(np.percentile(allv, 2)), float(np.percentile(allv, 99.5)))
xmax = max(abs(x) for x in xs) + 6.0
weak_body = weak_body.clip_box((-xmax, xmax, -31, 1, -1, Lz + 1), invert=False)

# --- oblique 3-D view -------------------------------------------------------------
pl = pv.Plotter(off_screen=True, window_size=(1800, 1100))
pl.set_background("white")
pl.add_mesh(weak_body, color="#c9b48a", opacity=1.0, smooth_shading=True)
for k, s in enumerate(sections):
    pl.add_mesh(s, scalars="edot", cmap="inferno", clim=clim, lighting=False,
                show_scalar_bar=(k == 0),
                scalar_bar_args=dict(title="edot_II / (V/H), strong cells", color="black",
                                     vertical=False, position_x=0.3, position_y=0.04,
                                     width=0.4))
pl.add_mesh(pv.Box(bounds=(-xmax, xmax, -30, 0, 0, Lz)).extract_all_edges(), color="grey",
            line_width=1)
pl.camera_position = [(70.0, 35.0, Lz + 70.0), (0.0, -15.0, Lz / 2), (0.0, 1.0, 0.0)]
pl.camera.zoom(1.1)
outs = [os.path.join(RES, f"{run}_xsections3d.png")]
pl.screenshot(outs[-1])
pl.close()

# --- the sections laid flat: depth (y) against strike (z) ----------------------
import matplotlib            # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

order = np.argsort(xs)
ncol = len(xs) // 2
fig, axes = plt.subplots(2, ncol, figsize=(3.6 * ncol, 6.4), sharex=True, sharey=True,
                         squeeze=False)
for ax, k in zip(axes.ravel(), order):
    x, s = xs[k], sections[k]
    tri = s.triangulate()
    faces = tri.faces.reshape(-1, 4)[:, 1:]
    P = np.asarray(tri.points)
    im = ax.tripcolor(P[:, 2], P[:, 1], faces, tri.point_data["edot"],
                      cmap="inferno", vmin=clim[0], vmax=clim[1], shading="gouraud")
    ax.set_title(f"x = {x:g} km", fontsize=10, loc="left")
    ax.set_xlim(0, Lz)
    ax.set_ylim(-22.5, 0)
    if ramp:
        ax.axvline(ramp[0], color="white", lw=0.8, ls="--")
for ax in axes[-1]:
    ax.set_xlabel("z, along strike (km)")
for ax in axes[:, 0]:
    ax.set_ylabel("y (km)")
cb = fig.colorbar(im, ax=axes, orientation="horizontal", fraction=0.05, pad=0.12, aspect=50)
cb.set_label(r"$\dot\varepsilon_{II}\,/\,(V/H)$, strong layer only"
             + (f"; dashed: z0 = {ramp[0]:g} km" if ramp else ""))
outs.append(os.path.join(RES, f"{run}_xsections.png"))
fig.savefig(outs[-1], dpi=120, bbox_inches="tight")
plt.close(fig)

os.makedirs(FIG, exist_ok=True)
for o in outs:
    shutil.copy(o, FIG)
    print(o)
