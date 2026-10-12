"""Visual check of the notch-only ramp mask (ramp_scope="notch"): the 3-D notch's
cells on a strike-normal slices (z = 0, Lz / 2, Lz), coloured strong / lower layer / notch bump, zoomed on
the notch with the analytic interface drawn over. One process, no solve.

Usage: python mask_check.py -uw_mesh <3-D .msh> -uw_ref 0
Writes ../results/mask_check_<mesh>_ref<k>.png (and ../figures/).
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
import notch_model as nm     # noqa: E402

pv.OFF_SCREEN = True
params = uw.Params(
    uw_mesh=uw.Param("", description="3-D gmsh file"),
    uw_ref=uw.Param(0, description="refinement"),
)
S = cn.build_notch(int(params.uw_ref), 0.0, seed=False, msh=str(params.uw_mesh),
                   weak_ramp=(8.0, 2.0), ramp_scope="notch")
code = 2 * np.asarray(S["bump"].data).ravel() + (1 - np.asarray(S["mat"].data).ravel())
counts = {k: int(np.sum(code == v)) for k, v in (("strong", 0), ("lower layer", 1), ("bump", 3))}
assert not np.any(code == 2), "a bump cell outside the Weak region"
grid = vis.mesh_to_pv_mesh(S["mesh"])
grid.cell_data["class"] = code
grid.points = np.asarray(grid.points) / 1.0e3
Lz = grid.bounds[5]
H = 30.0
b = 0.75 * H
th = np.linspace(0, np.pi / 2, 30)
images = []
for zc in (1.0e-3 * Lz, 0.5 * Lz, (1 - 1.0e-3) * Lz):
    sl = grid.slice(normal="z", origin=(0.0, -20.0, zc))
    pl = pv.Plotter(off_screen=True, window_size=(1000, 650))
    pl.set_background("white")
    pl.add_mesh(sl, scalars="class", cmap=["#d9d9d9", "#4a90d9", "#4a90d9", "#e8743b"],
                clim=(0, 3), show_edges=True, edge_color="black", line_width=0.4,
                lighting=False, show_scalar_bar=False)
    for cx, cy, sx, sy in nm.ARCS:
        p = np.column_stack([H * cx + nm.RC * H * sx * np.cos(th), H * cy + nm.RC * H * sy * np.sin(th),
                             np.full_like(th, zc + 0.01)])
        pl.add_mesh(pv.lines_from_points(p), color="red", line_width=3, lighting=False)
    pl.add_mesh(pv.lines_from_points(np.array([[-12, -b, zc + 0.01], [12, -b, zc + 0.01]])),
                color="red", line_width=1.5, lighting=False)
    pl.view_xy()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = (0.0, -21.25, zc)
    pl.camera.position = (0.0, -21.25, zc + 100.0)
    pl.camera.parallel_scale = 3.5
    images.append((zc, pl.screenshot(return_img=True)))
    pl.close()

import matplotlib            # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
fig, axes = plt.subplots(1, 3, figsize=(18, 4.2))
for ax, (zc, img) in zip(axes, images):
    ax.imshow(img)
    ax.set_axis_off()
    ax.set_title(f"z = {zc:.3f} km, ref {int(params.uw_ref)}: grey strong, blue lower layer, "
                 "orange ramped bump; red = analytic interface", fontsize=8, loc="left")
name = os.path.splitext(os.path.basename(str(params.uw_mesh)))[0]
out = os.path.join(_here, "..", "results", f"mask_check_{name}_ref{int(params.uw_ref)}.png")
fig.savefig(out, dpi=110, bbox_inches="tight")
os.makedirs(os.path.join(_here, "..", "figures"), exist_ok=True)
shutil.copy(out, os.path.join(_here, "..", "figures"))
print(out, counts)
