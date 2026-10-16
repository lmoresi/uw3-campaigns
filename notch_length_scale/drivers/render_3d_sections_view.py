"""Re-draw the oblique 3-D view of a set of notch sections from the cache that
render_3d_notch_sections.py writes (<run>_notchsections<tag>.vtm), without rebuilding
the model: for choosing the camera, colour map and opacity.

The weak body is solid; every section but the farthest from the camera is drawn
see-through. Light-background colour maps (Blues, YlOrRd) let the bands read through
the near planes; the default dark one hides them.

Usage:
  python render_3d_sections_view.py <cache.vtm> <out.png> [--cmap Blues] [--opacity 0.45]
        [--camera x,y,z] [--focus x,y,z] [--zoom 1.0] [--label "edot_II / (V/H)"]
"""
import argparse

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
ap = argparse.ArgumentParser()
ap.add_argument("cache")
ap.add_argument("out")
ap.add_argument("--cmap", default="Blues")
ap.add_argument("--opacity", type=float, default=0.45)
ap.add_argument("--camera", default="60,30,-60")
ap.add_argument("--focus", default="")
ap.add_argument("--zoom", type=float, default=1.0)
ap.add_argument("--label", default="edot_II / (V/H), strong layer")
ap.add_argument("--clim", default="")
a = ap.parse_args()

cache = pv.read(a.cache)
zs = np.asarray(cache.field_data["zs"])
clim = (tuple(float(v) for v in a.clim.split(",")) if a.clim
        else tuple(np.asarray(cache.field_data["clim"])))
Lz = float(np.asarray(cache.field_data["Lz"])[0])
half = float(np.asarray(cache.field_data["half"])[0])
eye = tuple(float(v) for v in a.camera.split(","))
focus = (tuple(float(v) for v in a.focus.split(",")) if a.focus
         else (0.0, -14.0, 0.5 * (zs.min() + zs.max())))
far = int(np.argmax([np.linalg.norm(np.subtract(eye, (0.0, -14.0, z))) for z in zs]))

pl = pv.Plotter(off_screen=True, window_size=(1800, 1100))
pl.set_background("white")
pl.add_mesh(cache["weak"], color="#c9b48a", smooth_shading=True)
for k, z in enumerate(zs):
    pl.add_mesh(cache[f"s{k}"], scalars="edot", preference="cell", cmap=a.cmap, clim=clim,
                lighting=False, opacity=(1.0 if k == far else a.opacity),
                show_scalar_bar=(k == 0),
                scalar_bar_args=dict(title=a.label, color="black", vertical=False,
                                     position_x=0.3, position_y=0.04, width=0.4))
pl.add_mesh(pv.Box(bounds=(-half, half, -30, 0, 0, Lz)).extract_all_edges(), color="grey",
            line_width=1)
pl.camera_position = [eye, focus, (0.0, 1.0, 0.0)]
pl.camera.zoom(a.zoom)
pl.screenshot(a.out)
pl.close()
print(a.out)
