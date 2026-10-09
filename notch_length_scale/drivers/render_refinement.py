"""Strain-rate maps across refinement, from checkpoints (no re-solve): rows l = 1 and
0.5 km (micromorphic beta = 0.1, xi = 0), columns refs 3 / 4 / 5.

Two figures, one shared log10 colour scale whose range covers every panel's extremes
(nothing clipped):

* ``refinement_maps.png``: the band region above the notch (x = +-32 km, y = -22..0 km);
* ``refinement_zoom.png``: a close window on the left band where it crosses the
  profile cut x = -15 km, with the mesh drawn, and the cells across the band counted
  (W over the mean edge length in the window).

edot_II is evaluated at the mesh vertices and drawn on the mesh's own triangles
(uw-visualisation house style: PyVista, white, unlit). Draws on one process: pyvista
renders one rank's mesh, so this refuses mpirun with more than one rank (the
checkpoints it reads were written by any decomposition).
"""
import json
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
    raise RuntimeError("render_refinement.py draws on one process: run it without mpirun")

RES = os.path.join(_here, "..", "results")
FIG = os.path.join(_here, "..", "figures")
CHECKPOINTS = os.path.join(RES, "micromorphic", "checkpoints")
L_ROWS = [1.0, 0.5]
REFS = [3, 4, 5]
MAP_BOX = (-32.0, 32.0, -22.0, 0.0)            # x0, x1, y0, y1 in km
ZOOM_HALF = 4.0                                # km: an 8 km x 8 km window (the band is ~6 km tall here)
CUT_X = -15.0                                  # km, the profile cut
widths = {(r["ref"], r["l_km"]): r["W_km"]
          for r in json.load(open(os.path.join(RES, "current_widths.json")))}


def load(ref, l_km):
    """The run's mesh as pyvista (km) with log10 edot_II / (V/H) at its vertices, and
    the y (km) of the band's peak on the cut x = -15 km."""
    name = cn.canonical_run(ref, l_km)
    S = cn.build_notch(ref, 0.0, seed=False)
    S["v"].read_timestep(name, S["v"].name, 0, outputPath=CHECKPOINTS)
    pvm = vis.mesh_to_pv_mesh(S["mesh"])
    xy = np.asarray(pvm.points)[:, :2] / (cn.H_KM * 1.0e3)
    edot = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, xy)).ravel()
    # a few vertices at the weak inclusion's corners (|x| ~ 3 km, y ~ -22 km) evaluate
    # to edot_II < 0 on the rebuilt model; they are kept out of the colour range
    # (NaN, drawn grey) and counted
    pvm.point_data["log10 edot"] = np.where(edot > 0, np.log10(np.abs(edot) + 1.0e-300), np.nan)
    if (edot <= 0).any():
        corner = np.asarray(pvm.points)[edot <= 0] / 1.0e3
        uw.pprint(f"  {int((edot <= 0).sum())} vertices with edot_II <= 0, "
                  f"|x| {np.abs(corner[:, 0]).min():.1f}-{np.abs(corner[:, 0]).max():.1f} km, "
                  f"y {corner[:, 1].min():.1f}-{corner[:, 1].max():.1f} km")
    pvm.points = np.asarray(pvm.points) / 1.0e3
    y = np.linspace(-0.68, -0.02, 2001)
    cut = np.asarray(uw.function.global_evaluate(
        S["stokes"].Unknowns.Einv2, np.column_stack([np.full_like(y, CUT_X / cn.H_KM), y]))).ravel()
    y_peak = float(y[int(np.argmax(cut))] * cn.H_KM)
    uw.pprint(f"loaded {name}: {pvm.n_points} vertices, peak at y = {y_peak:.2f} km")
    del S
    return pvm, y_peak


def in_box(pvm, box):
    p = np.asarray(pvm.points)
    return (p[:, 0] >= box[0]) & (p[:, 0] <= box[1]) & (p[:, 1] >= box[2]) & (p[:, 1] <= box[3])


def mean_edge_km(pvm, box):
    """Mean length of the mesh edges with both ends inside ``box``."""
    edges = pvm.extract_all_edges()
    lines = edges.lines.reshape(-1, 3)[:, 1:]
    p = np.asarray(edges.points)
    inside = in_box(edges, box)
    keep = inside[lines[:, 0]] & inside[lines[:, 1]]
    return float(np.linalg.norm(p[lines[keep, 0]] - p[lines[keep, 1]], axis=1).mean())


def render(pvm, box, clim, with_mesh, pixels=1400):
    x0, x1, y0, y1 = box
    size = (pixels, int(pixels * (y1 - y0) / (x1 - x0)))
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.add_mesh(pvm, scalars="log10 edot", cmap="inferno", clim=clim, show_edges=False,
                lighting=False, show_scalar_bar=False, nan_color="#bbbbbb")
    if with_mesh:
        clipped = pvm.clip_box([x0 - 0.5, x1 + 0.5, y0 - 0.5, y1 + 0.5, -1, 1], invert=False)
        pl.add_mesh(clipped.extract_all_edges(), color="white", line_width=0.6,
                    opacity=0.55, lighting=False)
    pl.view_xy()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = ((x0 + x1) / 2, (y0 + y1) / 2, 0.0)
    pl.camera.position = ((x0 + x1) / 2, (y0 + y1) / 2, 100.0)
    pl.camera.parallel_scale = (y1 - y0) / 2
    image = pl.screenshot(return_img=True)
    pl.close()
    return image


panels = {(l_km, ref): load(ref, l_km) for l_km in L_ROWS for ref in REFS}
zoom_boxes = {k: (CUT_X - ZOOM_HALF, CUT_X + ZOOM_HALF, y - ZOOM_HALF, y + ZOOM_HALF)
              for k, (_, y) in panels.items()}

import matplotlib   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402


def figure(boxes, with_mesh, out, title, annotate):
    values = np.concatenate([m.point_data["log10 edot"][in_box(m, boxes[k])]
                             for k, (m, _) in panels.items()])
    clim = (float(np.nanmin(values)), float(np.nanmax(values)))
    x0, x1, y0, y1 = next(iter(boxes.values()))
    aspect = (y1 - y0) / (x1 - x0)
    fig, axes = plt.subplots(len(L_ROWS), len(REFS),
                             figsize=(5.4 * len(REFS), 5.4 * aspect * len(L_ROWS) + 1.4),
                             squeeze=False)
    for i, l_km in enumerate(L_ROWS):
        for j, ref in enumerate(REFS):
            ax = axes[i, j]
            pvm, _ = panels[(l_km, ref)]
            box = boxes[(l_km, ref)]
            ax.imshow(render(pvm, box, clim, with_mesh), extent=box)
            ax.set_xlabel("x (km)")
            if j == 0:
                ax.set_ylabel("y (km)")
            label = f"l = {l_km:g} km, ref {ref}"
            if annotate:
                h = mean_edge_km(pvm, box)
                label += f":  edge {1e3 * h:.0f} m,  W/edge = {widths[(ref, l_km)] / h:.0f}"
            ax.set_title(label, fontsize=10, loc="left")
    mappable = plt.cm.ScalarMappable(cmap="inferno", norm=plt.Normalize(*clim))
    cbar = fig.colorbar(mappable, ax=axes, orientation="horizontal", fraction=0.04,
                        pad=0.12 if not with_mesh else 0.08, aspect=50)
    cbar.set_label(r"$\log_{10}\,\dot\varepsilon_{II}\,/\,(V/H)$,  $V/H$ = 5.3e-15 s$^{-1}$;"
                   "  range = the extremes over all panels"
                   + ("\n(grey: the few vertices at the weak inclusion's corners where edot_II "
                      "evaluates <= 0)" if not with_mesh else ""))
    fig.suptitle(title, fontsize=12)
    path = os.path.join(FIG, out)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    print(path, "clim", clim)


figure({k: MAP_BOX for k in panels}, False, "refinement_maps.png",
       "Micromorphic notch, beta = 0.1, xi = 0: edot_II across refinement (refs 3, 4, 5)",
       annotate=False)
figure(zoom_boxes, True, "refinement_zoom.png",
       f"The left band where it crosses x = {CUT_X:g} km, with the mesh "
       f"({2 * ZOOM_HALF:g} km window centred on the band's peak)", annotate=True)
