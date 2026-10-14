"""3-D notch run: strike-normal sections ACROSS the notch, one where the notch is live
and one where it has faded out along strike.

The weak region (lower layer and notch) is extracted as its own sub-mesh and drawn as
a solid body; the strain rate is drawn on the STRONG cells only, on planes of constant
z, so each section shows the whole band pair rising from the notch, as in 2-D.
Linear colour scale (the bands are 2-3x the background).

Two figures from one checkpoint:
  <run>_notchsections3d.png  oblique 3-D view: weak body + the z-planes
  <run>_notchsections.png    the same sections laid flat, x against depth

One process (pyvista draws one rank's mesh). Usage:
  python render_3d_notch_sections.py -uw_run <checkpoint name> -uw_mesh <3-D .msh>
        -uw_ref 2 [-uw_weak_ramp 8,2 -uw_ramp_scope weak] [-uw_zs 2,14]
"""
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
    uw_weak_ramp=uw.Param("", description="the run's 'z0,w' in km (empty = uniform)"),
    uw_ramp_scope=uw.Param("weak", description="the run's ramp scope"),
    uw_zs=uw.Param("2,14", description="z positions of the sections (km): live notch, faded"),
    uw_half_width=uw.Param(32.0, description="half width in x of the view (km)"),
    uw_clim=uw.Param("", description="edot_II/(V/H) colour range 'lo,hi' (empty = the "
                                      "2nd-99.5th percentile over the sections above y = -20 km)"),
)
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
run = str(params.uw_run)
ramp = tuple(float(v) for v in str(params.uw_weak_ramp).split(",")) if str(params.uw_weak_ramp) else None
zs = [float(v) for v in str(params.uw_zs).split(",")]
half = float(params.uw_half_width)
clim = tuple(float(v) for v in str(params.uw_clim).split(",")) if str(params.uw_clim) else None

if uw.mpi.size > 1:
    raise RuntimeError("render_3d_notch_sections.py draws on one process: run it without mpirun")

S = cn.build_notch(int(params.uw_ref), 0.0, seed=False, msh=str(params.uw_mesh),
                   weak_ramp=ramp, ramp_scope=str(params.uw_ramp_scope))
S["v"].read_timestep(run, S["v"].name, 0,
                     outputPath=os.path.join(RES, "micromorphic", "checkpoints"))
L = cn.H_KM * 1.0e3

grid = vis.mesh_to_pv_mesh(S["mesh"])                       # metres
strong_cell = np.asarray(S["mat"].data).ravel() > 0.5       # P0, plex cell order
grid.points = np.asarray(grid.points) / 1.0e3               # km
Lz = float(grid.bounds[5])
weak_body = (grid.extract_cells(np.flatnonzero(~strong_cell)).extract_surface()
             .clip_box((-half, half, -31, 1, -1, Lz + 1), invert=False))
strong = grid.extract_cells(np.flatnonzero(strong_cell))


def with_edot(surface):
    pts = np.asarray(surface.points) * 1.0e3 / L
    surface.point_data["edot"] = np.asarray(
        uw.function.evaluate(S["stokes"].Unknowns.Einv2, pts)).ravel()
    return surface


sections = [with_edot(strong.slice(normal="z", origin=(0.0, -15.0, z))
                      .clip_box((-half, half, -31, 1, -1, Lz + 1), invert=False))
            for z in zs]
if clim is None:
    # the range from the BAND region only (y above -20 km): the strip along the top of
    # the weak layer and the notch-top hot spot would otherwise take the range, and
    # they saturate instead
    allv = np.concatenate([s.point_data["edot"][np.asarray(s.points)[:, 1] > -20.0]
                           for s in sections])
    clim = (float(np.percentile(allv, 2)), float(np.percentile(allv, 99.5)))


def eta_label(z):
    if not ramp:
        return ""
    return f", log10 eta_b = {21 + 1 - math.tanh((ramp[0] - z) / ramp[1]):.2f}"


# --- oblique 3-D view ----------------------------------------------------------
pl = pv.Plotter(off_screen=True, window_size=(1800, 1100))
pl.set_background("white")
pl.add_mesh(weak_body, color="#c9b48a", smooth_shading=True)
far = int(np.argmax(zs))                  # the camera sits on the low-z side: every
for k, s in enumerate(sections):          # plane but the farthest is see-through
    pl.add_mesh(s, scalars="edot", cmap="inferno", clim=clim, lighting=False,
                opacity=(1.0 if k == far or len(zs) == 1 else 0.55),
                show_scalar_bar=(k == 0),
                scalar_bar_args=dict(title="edot_II / (V/H), strong layer", color="black",
                                     vertical=False, position_x=0.3, position_y=0.04,
                                     width=0.4))
pl.add_mesh(pv.Box(bounds=(-half, half, -30, 0, 0, Lz)).extract_all_edges(), color="grey",
            line_width=1)
pl.camera_position = [(55.0, 28.0, -55.0), (0.0, -14.0, Lz / 2), (0.0, 1.0, 0.0)]
outs = [os.path.join(RES, f"{run}_notchsections3d.png")]
pl.screenshot(outs[-1])
pl.close()

# --- the sections laid flat: x against depth --------------------------------------
import matplotlib            # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

fig, axes = plt.subplots(len(zs), 1, figsize=(11, 3.4 * len(zs)), sharex=True,
                         squeeze=False)
for ax, z, s in zip(axes[:, 0], zs, sections):
    tri = s.extract_surface().triangulate()
    faces = tri.faces.reshape(-1, 4)[:, 1:]
    P = np.asarray(tri.points)
    im = ax.tripcolor(P[:, 0], P[:, 1], faces, tri.point_data["edot"], cmap="inferno",
                      vmin=clim[0], vmax=clim[1], shading="gouraud")
    ax.set_title(f"z = {z:g} km{eta_label(z)}", fontsize=10, loc="left")
    ax.set_xlim(-half, half)
    ax.set_ylim(-30, 0)
    ax.set_aspect("equal")
    ax.set_facecolor("#c9b48a")            # the weak region, not drawn: its own colour
    ax.set_ylabel("y (km)")
axes[-1, 0].set_xlabel("x (km)")
cb = fig.colorbar(im, ax=axes[:, 0], orientation="horizontal", fraction=0.05, pad=0.1,
                  aspect=40, shrink=0.75, extend="max")
cb.set_label(r"$\dot\varepsilon_{II}\,/\,(V/H)$, strong layer only (tan: the weak region)")
outs.append(os.path.join(RES, f"{run}_notchsections.png"))
fig.savefig(outs[-1], dpi=120, bbox_inches="tight")
plt.close(fig)

os.makedirs(FIG, exist_ok=True)
for o in outs:
    shutil.copy(o, FIG)
    print(o)
