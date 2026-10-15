"""3-D notch run seen from above: the strain rate on HORIZONTAL slices through the strong
layer (constant depth y), x across strike against z along it. Each band of the pair
cuts a slice in a line parallel to the strike, so a slice shows where the bands run,
how far past the end of the notch block they carry, and where they die.

Strong cells only, each slice cell sampled at its centroid (cell data: no point sits on
a weak/strong face). The block outline (|x| < 2.5 km, z < Ln) is drawn on every panel.

Writes <run>_planview.png and <run>_planview.npz (the slice triangles and values, for
side-by-side figures across runs: render_3d_plan_compare.py).

One process. Usage:
  python render_3d_plan_view.py -uw_run <checkpoint name> -uw_mesh <3-D .msh> -uw_ref 3
        -uw_ln 5 [-uw_ys -5,-10,-15] [-uw_field edot|yield]
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
    uw_ln=uw.Param(5.0, description="the block's half-length Ln in km (outline only)"),
    uw_ys=uw.Param("-5,-10,-15", description="depths of the slices (km, negative down)"),
    uw_half_width=uw.Param(32.0, description="half width in x of the view (km)"),
    uw_field=uw.Param("edot", description="edot = strain rate / (V/H); yield = "
                                           "eta_eff / eta_lin (1 = below yield)"),
    uw_clim=uw.Param("", description="colour range 'lo,hi' (empty: 2nd-99.5th percentile "
                                      "for edot, 0-1 for yield)"),
)
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
run = str(params.uw_run)
ys = [float(v) for v in str(params.uw_ys).split(",")]
half = float(params.uw_half_width)
Ln = float(params.uw_ln)
FIELD = str(params.uw_field)
clim = tuple(float(v) for v in str(params.uw_clim).split(",")) if str(params.uw_clim) else None

if uw.mpi.size > 1:
    raise RuntimeError("render_3d_plan_view.py draws on one process: run it without mpirun")

S = cn.build_notch(int(params.uw_ref), 0.0, seed=False, msh=str(params.uw_mesh))
CK = os.path.join(RES, "micromorphic", "checkpoints")
S["v"].read_timestep(run, S["v"].name, 0, outputPath=CK)
if FIELD == "yield":
    S["p"].read_timestep(run, S["p"].name, 0, outputPath=CK)
    # two viscosities, the same units by construction (#843: a stress / yield-stress
    # ratio from evaluate() mixes unit systems)
    VALUE = (S["cm"].viscosity, S["cm"].Parameters.shear_viscosity_0)
    LABEL = r"$\eta_{eff}\,/\,\eta_{lin}$ (1 = below yield)"
else:
    VALUE = S["stokes"].Unknowns.Einv2
    LABEL = r"$\dot\varepsilon_{II}\,/\,(V/H)$"
L = cn.H_KM * 1.0e3

grid = vis.mesh_to_pv_mesh(S["mesh"])
strong_cell = np.asarray(S["mat"].data).ravel() > 0.5       # P0, plex cell order
grid.points = np.asarray(grid.points) / 1.0e3               # km
Lz = float(grid.bounds[5])
strong = grid.extract_cells(np.flatnonzero(strong_cell))


def sampled(surface):
    """The field at each slice polygon's centroid, as cell data (each polygon is the
    cut through one tetrahedron, so its centroid is strictly inside that cell)."""
    surface = surface.extract_surface().triangulate()
    pts = np.asarray(surface.cell_centers().points) * 1.0e3 / L
    if isinstance(VALUE, tuple):
        num, den = (np.asarray(uw.function.evaluate(v, pts), dtype=float).ravel() for v in VALUE)
        surface.cell_data["f"] = num / den
    else:
        surface.cell_data["f"] = np.asarray(uw.function.evaluate(VALUE, pts)).ravel()
    return surface


slices = [sampled(strong.slice(normal="y", origin=(0.0, y, Lz / 2))
                  .clip_box((-half, half, -31, 1, -1, Lz + 1), invert=False)) for y in ys]
for y, s in zip(ys, slices):
    v = s.cell_data["f"]
    uw.pprint(f"[{FIELD}] y = {y:g}: min {np.min(v):.4g}  p50 {np.median(v):.4g}  max {np.max(v):.4g}")
if clim is None:
    clim = (0.0, 1.0) if FIELD == "yield" else tuple(
        float(np.percentile(np.concatenate([s.cell_data["f"] for s in slices]), q)) for q in (2, 99.5))

tag = "" if FIELD == "edot" else "_yield"
np.savez(os.path.join(RES, f"{run}_planview{tag}.npz"), ys=np.array(ys), Ln=Ln, Lz=Lz,
         clim=np.array(clim), field=FIELD,
         **{f"pts{k}": np.asarray(s.points)[:, [0, 2]] for k, s in enumerate(slices)},
         **{f"tri{k}": s.faces.reshape(-1, 4)[:, 1:] for k, s in enumerate(slices)},
         **{f"f{k}": s.cell_data["f"] for k, s in enumerate(slices)})

import matplotlib            # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

fig, axes = plt.subplots(1, len(ys), figsize=(4.2 * len(ys), 5.2), sharey=True, squeeze=False)
for ax, y, s in zip(axes[0], ys, slices):
    P = np.asarray(s.points)
    im = ax.tripcolor(P[:, 0], P[:, 2], s.faces.reshape(-1, 4)[:, 1:],
                      facecolors=s.cell_data["f"], cmap="inferno",
                      vmin=clim[0], vmax=clim[1], shading="flat")
    ax.plot([-2.5, -2.5, 2.5, 2.5], [0, Ln, Ln, 0], color="white", lw=0.8, ls="--")
    ax.set_title(f"y = {y:g} km", fontsize=10, loc="left")
    ax.set_xlim(-half, half)
    ax.set_ylim(0, Lz)
    ax.set_aspect("equal")
    ax.set_xlabel("x (km)")
axes[0, 0].set_ylabel("z, along strike (km)")
cb = fig.colorbar(im, ax=axes[0], orientation="horizontal", fraction=0.05, pad=0.12,
                  aspect=40, shrink=0.7, extend="max" if FIELD == "edot" else "neither")
cb.set_label(LABEL + f", strong layer; dashed: the notch block (2 Ln = {2 * Ln:g} km "
             "long with the z = 0 mirror)")
out = os.path.join(RES, f"{run}_planview{tag}.png")
fig.savefig(out, dpi=120, bbox_inches="tight")
plt.close(fig)
os.makedirs(FIG, exist_ok=True)
shutil.copy(out, FIG)
print(out)
