"""Strain-rate maps of the matched-width pairs at ref 4, from checkpoints (no re-solve):
rows P1 / P2 / P3 (W about 2.6 / 3.6 / 4.65 km), columns micromorphic (beta 0.1) /
Cosserat c = 1 / the third run of the pair (Cosserat small c; for P1, micromorphic
beta 0.3). Every panel of a figure shares ONE colour scale, so the panels compare
directly (the earlier refinement maps each had their own range).

edot_II is projected onto a discontinuous P0 field (the cell mean) and drawn as cell
data on the mesh's own triangles. A continuous projection rings at the material interface,
where the strain rate jumps, and at the notch's corners, where it is singular: it went
negative there (-3.4 V/H) and set the colour range. Three figures:

* ``matched_maps_ref4.png``: log10 edot_II / (V/H) over the band region;
* ``matched_maps_ref4_linear.png``: the same region, edot_II / (V/H) on a linear scale,
  which shows the concentration the way the profiles do;
* ``matched_roots_ref4.png``: a linear close-up of the left band from the notch to the
  profile cut x = -15 km.

The weak material (the notch bump and the layer below it, the model's ``Weak`` region,
cell by cell) is drawn grey and left out of the colour range: the comparison is the band
in the strong layer. Draws on
one process. Fields are cached in ``CACHE`` after the first projection."""
import os
import sys

import numpy as np
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

pv.OFF_SCREEN = True
if uw.mpi.size > 1:
    raise RuntimeError("render_matched_maps.py draws on one process: run it without mpirun")

REF = 4
RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
CACHE = os.path.expanduser("~/+Simulations/notch_matched_maps")
MAP_BOX = (-32.0, 32.0, -22.0, 0.0)            # x0, x1, y0, y1 in km
ROOT_BOX = (-19.0, -1.0, -21.0, -5.0)          # the left band, notch to beyond the cut
CUT_X = -15.0

# (pair, column, model directory, run, label); W and peak from matched_profiles_ref4.json
# and eff_table.json (integral width, background outside +-9 km)
RUNS = [
    ("P1", 0, "micromorphic", "micro_ref4_xi0_beta0.1_l0.25_production_np2",
     "micromorphic beta 0.1, l = 0.25 km"),
    ("P1", 1, "cosserat", "cosserat_ref4_xi0_c1_l0.14_P1_production_tight_np8_eff",
     "Cosserat c = 1, l = 0.14 km"),
    ("P1", 2, "micromorphic", "micro_ref4_xi0_beta0.3_l0.138_production_tight_np8_eff",
     "micromorphic beta 0.3, l = 0.138 km"),
    ("P2", 0, "micromorphic", "micro_ref4_xi0_beta0.1_l0.5_production_tight_np8_eff",
     "micromorphic beta 0.1, l = 0.5 km"),
    ("P2", 1, "cosserat", "cosserat_ref4_xi0_c1_l0.236_P1_production_tight_np8_eff",
     "Cosserat c = 1, l = 0.236 km"),
    ("P2", 2, "cosserat", "cosserat_ref4_xi0_c0.1_l0.25_P1_production_tight_np8_eff",
     "Cosserat c = 0.1, l = 0.25 km"),
    ("P3", 0, "micromorphic", "micro_ref4_xi0_beta0.1_l1_production_tight_np8_eff",
     "micromorphic beta 0.1, l = 1 km"),
    ("P3", 1, "cosserat", "cosserat_ref4_xi0_c1_l0.37_P1_production_tight_np8_eff",
     "Cosserat c = 1, l = 0.37 km"),
    ("P3", 2, "cosserat", "cosserat_ref4_xi0_c0.054_l0.5_P1_production_tight_np8_eff",
     "Cosserat c = 0.054, l = 0.5 km"),
]
PAIRS = ["P1", "P2", "P3"]


def load(directory, name):
    """The run's mesh as pyvista (km) with edot_II / (V/H) on its cells, from a P0
    projection (cell means) of the strain-rate invariant of the saved velocity."""
    cached = os.path.join(CACHE, name + ".p0.vtu")
    if os.path.exists(cached):
        return pv.read(cached)
    S = cn.build_notch(REF, 0.0, seed=False)
    S["v"].read_timestep(name, S["v"].name, 0,
                         outputPath=os.path.join(RES, directory, "checkpoints"))
    mesh = S["mesh"]
    edot = uw.discretisation.MeshVariable(f"E_{abs(hash(name)) % 10**8}", mesh, 1,
                                          degree=0, continuous=False)
    proj = uw.systems.Projection(mesh, edot)
    proj.uw_function = S["stokes"].Unknowns.Einv2
    proj.smoothing = 0.0
    proj.solve()
    pvm = vis.mesh_to_pv_mesh(mesh)
    xy = np.asarray(pvm.cell_centers().points)[:, :2] / (cn.H_KM * 1.0e3)
    pvm.cell_data["edot"] = np.asarray(uw.function.evaluate(edot.sym[0], xy)).ravel()
    pvm.points = np.asarray(pvm.points) / 1.0e3
    os.makedirs(CACHE, exist_ok=True)
    pvm.save(cached)
    uw.pprint(f"projected {name}: {pvm.n_cells} cells")
    del S, proj
    return pvm


def in_box(pvm, box):
    p = np.asarray(pvm.cell_centers().points)
    return (p[:, 0] >= box[0]) & (p[:, 0] <= box[1]) & (p[:, 1] >= box[2]) & (p[:, 1] <= box[3])


def strong_cells(n_cells):
    """True for the cells of the strong layer (material 1), in the pyvista cell order of
    the ref-4 notch, read from the model's P0 material field at the cell centroids. Every
    run is on the same rebuilt mesh, so one mask serves all of them."""
    cached = os.path.join(CACHE, f"strong_cells_ref{REF}.npy")
    if os.path.exists(cached):
        mask = np.load(cached)
    else:
        S = cn.build_notch(REF, 0.0, seed=False)
        pvm = vis.mesh_to_pv_mesh(S["mesh"])
        xy = np.asarray(pvm.cell_centers().points)[:, :2] / (cn.H_KM * 1.0e3)
        mask = np.asarray(uw.function.evaluate(S["mat"].sym[0], xy)).ravel() > 0.5
        np.save(cached, mask)
        del S
    if mask.size != n_cells:
        raise RuntimeError(f"material mask has {mask.size} cells, the run's mesh {n_cells}")
    return mask


panels = {}
for pair, col, directory, name, label in RUNS:
    pvm = load(directory, name)
    e = np.asarray(pvm.cell_data["edot"])
    pvm.cell_data["linear"] = e
    pvm.cell_data["log10"] = np.where(e > 0, np.log10(np.abs(e) + 1.0e-300), np.nan)
    strong = strong_cells(pvm.n_cells)
    panels[(pair, col)] = (pvm.extract_cells(np.flatnonzero(strong)),
                           pvm.extract_cells(np.flatnonzero(~strong)), label)

import matplotlib   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402


def render(pvm, weak, scalars, box, clim, cmap, pixels=1400):
    x0, x1, y0, y1 = box
    size = (pixels, int(pixels * (y1 - y0) / (x1 - x0)))
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.add_mesh(pvm, scalars=scalars, preference="cell", cmap=cmap, clim=clim, show_edges=False,
                lighting=False, show_scalar_bar=False, nan_color="#bbbbbb")
    pl.add_mesh(weak, color="#bbbbbb", show_edges=False, lighting=False)
    pl.view_xy()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = ((x0 + x1) / 2, (y0 + y1) / 2, 0.0)
    pl.camera.position = ((x0 + x1) / 2, (y0 + y1) / 2, 100.0)
    pl.camera.parallel_scale = (y1 - y0) / 2
    image = pl.screenshot(return_img=True)
    pl.close()
    return image


def figure(scalars, box, out, title, scale_label, cut=False):
    values = np.concatenate([m.cell_data[scalars][in_box(m, box)]
                             for m, _, _ in panels.values()])
    lo, hi = float(np.nanmin(values)), float(np.nanmax(values))
    pad = 0.01 * (hi - lo)
    clim = (lo - pad, hi + pad)                 # just beyond the extremes: nothing clipped
    x0, x1, y0, y1 = box
    aspect = (y1 - y0) / (x1 - x0)
    width = 5.4 if aspect < 0.6 else 4.2
    fig, axes = plt.subplots(len(PAIRS), 3, figsize=(width * 3, width * aspect * 3 + 1.6),
                             squeeze=False)
    for i, pair in enumerate(PAIRS):
        for j in range(3):
            ax = axes[i, j]
            pvm, weak, label = panels[(pair, j)]
            ax.imshow(render(pvm, weak, scalars, box, clim, "inferno"), extent=box)
            if cut:
                ax.axvline(CUT_X, color="white", lw=0.8, ls="--", alpha=0.7)
            ax.set_title(f"{pair}: {label}", fontsize=9.5, loc="left")
            if i == len(PAIRS) - 1:
                ax.set_xlabel("x (km)")
            if j == 0:
                ax.set_ylabel("y (km)")
    mappable = plt.cm.ScalarMappable(cmap="inferno", norm=plt.Normalize(*clim))
    cbar = fig.colorbar(mappable, ax=axes, orientation="horizontal", fraction=0.035,
                        pad=0.09, aspect=50)
    cbar.set_label(scale_label + ";  one range for all nine panels, just beyond their "
                   "extremes\n(grey: the weak material, the notch bump and the layer below it, "
                   "left out of the range)")
    fig.suptitle(title, fontsize=12)
    path = os.path.join(FIG, out)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(path, "clim", clim)


TITLE = ("Matched band width at ref 4 (rows: W about 2.6 / 3.6 / 4.65 km): "
         "micromorphic | Cosserat c = 1 | third run of the pair")
VH = r"$V/H$ = 5.3e-15 s$^{-1}$"
figure("log10", MAP_BOX, "matched_maps_ref4.png", TITLE,
       r"$\log_{10}\,\dot\varepsilon_{II}\,/\,(V/H)$,  " + VH)
figure("linear", MAP_BOX, "matched_maps_ref4_linear.png", TITLE,
       r"$\dot\varepsilon_{II}\,/\,(V/H)$ (linear),  " + VH)
figure("linear", ROOT_BOX, "matched_roots_ref4.png",
       TITLE + "\nthe left band from the notch to the profile cut (dashed, x = -15 km)",
       r"$\dot\varepsilon_{II}\,/\,(V/H)$ (linear),  " + VH, cut=True)
