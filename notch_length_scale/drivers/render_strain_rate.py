"""Strain-rate maps of the converged notch runs: models down, refinement across.

Each run's saved velocity (``fields_<run>.npz``) is loaded back onto a rebuilt notch
mesh (same mesh file and refinement, so the nodes coincide), and edot_II is evaluated
at the mesh vertices and drawn on the mesh's own triangles. All panels share one
log10 colour scale. Writes ../results/strain_rate_maps.png (and ../figures/).
"""
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
params = uw.Params(
    uw_refs=uw.Param("1,2,3", description="refinements (columns)"),
    uw_half_width_km=uw.Param(32.0, description="half width of the cropped view (km)"),
)
RES = os.path.join(_here, "..", "results")
ROWS = [
    ("micromorphic  beta = 0.1, l = 1 km", "micromorphic/fields_micro_ref{r}_xi0_beta0.1_l1.npz"),
    ("micromorphic  beta = 0.1, l = 0.5 km", "micromorphic/fields_micro_ref{r}_xi0_beta0.1_l0.5.npz"),
    ("Cosserat  c = 1, l = 1 km", "cosserat/fields_cosserat_ref{r}_xi0_c1_l1_P1.npz"),
    ("Cosserat  c = 1, l = 0.5 km", "cosserat/fields_cosserat_ref{r}_xi0_c1_l0.5_P1.npz"),
]
refs = [int(v) for v in str(params.uw_refs).split(",")]


def strain_rate_mesh(ref, path):
    """The notch mesh at ``ref`` as a pyvista mesh carrying log10 edot_II, with
    edot_II non-dimensional (scaled by V/H = 5 mm/yr / 30 km = 5.3e-15 1/s)."""
    S = cn.build_notch(ref, 0.0, seed=False)
    saved = np.load(path)
    v = S["v"]
    if not np.allclose(np.asarray(v.coords), saved["v_coords"]):
        raise ValueError(f"{path}: saved velocity nodes do not match the rebuilt mesh")
    v.array[...] = saved["v"].reshape(v.array.shape)
    pvm = vis.mesh_to_pv_mesh(S["mesh"])
    model_xy = np.asarray(pvm.points)[:, :2] / (cn.H_KM * 1.0e3)
    edot = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, model_xy)).ravel()
    pvm.point_data["log10 edot_II"] = np.log10(np.maximum(edot, 1.0e-30))
    pvm.points = np.asarray(pvm.points) / 1.0e3          # metres -> km for the camera
    return pvm


panels = {}
for row, (label, pattern) in enumerate(ROWS):
    for col, ref in enumerate(refs):
        path = os.path.join(RES, pattern.format(r=ref))
        if os.path.exists(path):
            panels[(row, col)] = (label, ref, strain_rate_mesh(ref, path))
            uw.pprint(f"loaded {os.path.basename(path)}")

values = np.concatenate([m.point_data["log10 edot_II"] for _, _, m in panels.values()])
clim = (float(np.percentile(values, 2)), float(np.percentile(values, 99.9)))



def panel_image(pvm, half_width, size=(1240, 660)):
    """One cropped, unlit, white-background render of a strain-rate mesh."""
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.add_mesh(pvm, scalars="log10 edot_II", cmap="inferno", clim=clim,
                show_edges=False, lighting=False, show_scalar_bar=False)
    pl.view_xy()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = (0.0, -15.0, 0.0)
    pl.camera.position = (0.0, -15.0, 100.0)
    pl.camera.parallel_scale = half_width * size[1] / size[0]
    image = pl.screenshot(return_img=True)
    pl.close()
    return image


if uw.mpi.rank == 0:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    half = float(params.uw_half_width_km)
    fig, axes = plt.subplots(len(ROWS), len(refs), figsize=(6.2 * len(refs), 3.6 * len(ROWS)),
                             squeeze=False)
    for row, (label, _) in enumerate(ROWS):
        for col, ref in enumerate(refs):
            ax = axes[row, col]
            ax.set_xticks([])
            ax.set_yticks([])
            for side in ax.spines.values():
                side.set_visible(False)
            if (row, col) in panels:
                ax.imshow(panel_image(panels[(row, col)][2], half))
                ax.set_title(f"{label},  ref {ref}", fontsize=10, loc="left")
            else:
                ax.text(0.0, 0.9, f"{label},  ref {ref}: not run", fontsize=10,
                        transform=ax.transAxes)
    mappable = plt.cm.ScalarMappable(cmap="inferno", norm=plt.Normalize(*clim))
    cbar = fig.colorbar(mappable, ax=axes, orientation="horizontal", fraction=0.025,
                        pad=0.02, aspect=50)
    cbar.set_label(r"$\log_{10}\,\dot\varepsilon_{II}\,/\,(V/H)$,  "
                   r"$V/H$ = 5 mm/yr / 30 km = 5.3e-15 s$^{-1}$;  "
                   f"view {2 * half:.0f} km wide, full depth 30 km")
    out = os.path.join(RES, "strain_rate_maps.png")
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(out, "clim", clim)
