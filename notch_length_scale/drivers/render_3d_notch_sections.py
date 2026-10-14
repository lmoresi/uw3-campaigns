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
    uw_field=uw.Param("edot", description="edot = strain rate / (V/H); yield = tau_II / "
                                           "tau_y with the micromorphic shift (1 = at yield)"),
    uw_beta=uw.Param(0.1, description="the run's beta (for the yield field)"),
    uw_l_km=uw.Param(1.0, description="the run's l in km (for the yield field)"),
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
CK = os.path.join(RES, "micromorphic", "checkpoints")
S["v"].read_timestep(run, S["v"].name, 0, outputPath=CK)
L = cn.H_KM * 1.0e3
FIELD = str(params.uw_field)
if FIELD == "yield":
    # the run's own yield law: Drucker-Prager in the checkpointed pressure, plus the
    # micromorphic shift H (e - chi) with chi from the checkpoint; tau_II from the
    # model's effective viscosity
    S["p"].read_timestep(run, S["p"].name, 0, outputPath=CK)
    chi = uw.discretisation.MeshVariable("chi", S["mesh"], 1, degree=1, units="1/s")
    chi.read_timestep(run, "chi", 0, outputPath=CK)
    m = S["mat"].sym[0]
    e = S["stokes"].Unknowns.Einv2
    H = uw.expression(r"H_{\chi}", uw.quantity(float(params.uw_beta) * cn.ETA_BG, "Pa*s"),
                      "micromorphic modulus")
    sigma_y = cn.yield_stress_with_shift(S, m * H * (e - chi.sym[0]))
    # eta_eff / eta_lin: two viscosities, the same units by construction (a stress /
    # yield-stress ratio built from evaluate() mixed unit systems, #843: eta and tau_y
    # came back dimensional, edot scaled). 1 = below yield, < 1 = yielding.
    VALUE = (S["cm"].viscosity, S["cm"].Parameters.shear_viscosity_0)
else:
    VALUE = S["stokes"].Unknowns.Einv2
LABEL = (r"$\eta_{eff}\,/\,\eta_{lin}$ (1 = below yield)" if FIELD == "yield"
         else r"$\dot\varepsilon_{II}\,/\,(V/H)$")

grid = vis.mesh_to_pv_mesh(S["mesh"])                       # metres
strong_cell = np.asarray(S["mat"].data).ravel() > 0.5       # P0, plex cell order
grid.points = np.asarray(grid.points) / 1.0e3               # km
Lz = float(grid.bounds[5])
weak_body = (grid.extract_cells(np.flatnonzero(~strong_cell)).extract_surface()
             .clip_box((-half, half, -31, 1, -1, Lz + 1), invert=False))
strong = grid.extract_cells(np.flatnonzero(strong_cell))


def with_edot(surface):
    pts = np.asarray(surface.points) * 1.0e3 / L
    if isinstance(VALUE, tuple):
        num, den = (np.asarray(uw.function.evaluate(v, pts), dtype=float).ravel() for v in VALUE)
        surface.point_data["edot"] = num / den
    else:
        surface.point_data["edot"] = np.asarray(uw.function.evaluate(VALUE, pts)).ravel()
    return surface


sections = [with_edot(strong.slice(normal="z", origin=(0.0, -15.0, z))
                      .clip_box((-half, half, -31, 1, -1, Lz + 1), invert=False))
            for z in zs]
for z, s in zip(zs, sections):
    v = s.point_data["edot"]
    uw.pprint(f"[{FIELD}] z = {z:g}: min {np.min(v):.4g}  p50 {np.median(v):.4g}  max {np.max(v):.4g}")
if FIELD == "yield":
    # the pieces of the ratio at one point mid-layer, far from the block
    probe = np.array([[0.0, -10.0e3 / L, 15.0e3 / L]])
    for nm_, ex in (("eta_eff", S["cm"].viscosity), ("edot", S["stokes"].Unknowns.Einv2),
                    ("tau_y", sigma_y)):
        uw.pprint(f"  probe {nm_}: {np.asarray(uw.function.evaluate(ex, probe)).ravel()}")
if clim is None and FIELD == "yield":
    clim = (0.0, 1.0)
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
                scalar_bar_args=dict(title=("eta_eff / eta_lin" if FIELD == "yield" else "edot_II / (V/H)")
                                     + ", strong layer", color="black",
                                     vertical=False, position_x=0.3, position_y=0.04,
                                     width=0.4))
pl.add_mesh(pv.Box(bounds=(-half, half, -30, 0, 0, Lz)).extract_all_edges(), color="grey",
            line_width=1)
pl.camera_position = [(55.0, 28.0, -55.0), (0.0, -14.0, Lz / 2), (0.0, 1.0, 0.0)]
tag = "" if FIELD == "edot" else "_yield"
outs = [os.path.join(RES, f"{run}_notchsections3d{tag}.png")]
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
cb.set_label(LABEL + ", strong layer only (tan: the weak region)")
outs.append(os.path.join(RES, f"{run}_notchsections{tag}.png"))
fig.savefig(outs[-1], dpi=120, bbox_inches="tight")
plt.close(fig)

os.makedirs(FIG, exist_ok=True)
for o in outs:
    shutil.copy(o, FIG)
    print(o)
