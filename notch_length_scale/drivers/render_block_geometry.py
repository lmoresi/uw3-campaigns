"""Geometry check of a 3-D notch mesh, no solve: the weak region (lower layer + the
Notch block) as a solid body with the block coloured, and the mesh on the z = 0 face.
One process. Usage: python render_block_geometry.py -uw_mesh <3-D .msh>"""
import os
import sys

import numpy as np
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import notch_model as nm   # noqa: E402
from underworld3.utilities.dm_labels import label_stratum_indices   # noqa: E402

pv.OFF_SCREEN = True
params = uw.Params(uw_mesh=uw.Param("", description="3-D gmsh file"))
mesh = nm.load_notch_mesh(str(params.uw_mesh), 0)
cS, cE = mesh.dm.getHeightStratum(0)


def cells(label, value):
    q = label_stratum_indices(mesh.dm.getLabel(label), value)
    return q[(q >= cS) & (q < cE)] - cS


grid = vis.mesh_to_pv_mesh(mesh)
grid.points = np.asarray(grid.points) * 30.0              # non-dimensional -> km
cls = np.zeros(cE - cS)
cls[cells("Weak", 100)] = 1
cls[cells("Notch", 102)] = 2
grid.cell_data["cls"] = cls
Lz = float(grid.bounds[5])
layer = grid.extract_cells(np.flatnonzero(cls == 1)).extract_surface().clip_box(
    (-32, 32, -31, 1, -1, Lz + 1), invert=False)
block = grid.extract_cells(np.flatnonzero(cls == 2)).extract_surface()
pl = pv.Plotter(off_screen=True, window_size=(1600, 900))
pl.set_background("white")
pl.add_mesh(layer, color="#c9b48a", smooth_shading=True)
pl.add_mesh(block, color="#d9542b", smooth_shading=True, show_edges=True, edge_color="black",
            line_width=0.5)
pl.add_mesh(pv.Box(bounds=(-32, 32, -30, 0, 0, Lz)).extract_all_edges(), color="grey")
pl.camera_position = [(45.0, 25.0, -40.0), (0.0, -20.0, Lz / 3), (0.0, 1.0, 0.0)]
name = os.path.splitext(os.path.basename(str(params.uw_mesh)))[0]
out = os.path.join(_here, "..", "results", f"geometry_{name}.png")
pl.screenshot(out)
pl.close()
print(out, {"weak": int(np.sum(cls >= 1)), "block": int(np.sum(cls == 2)), "Lz": Lz})
