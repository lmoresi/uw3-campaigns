"""Prototype of a graded annulus base mesh for the slab workbench (geometry only).

Sizes are the FINEST mesh's target cell sizes in km, chosen so that MMPDE, which
can concentrate about a factor of four, can reach the resolution needed:
  - trench window (+-750 km of arc, to 700 km depth): 16 km  -> MMPDE to ~4 km
  - top thermal boundary layer (top 200 km) elsewhere: 40 km -> MMPDE to ~10 km
  - rest of the upper mantle (to 660 km): 80 km
  - lower mantle: grading to H_LM km
Lengths in the model are layer depths (1 = 2,900 km); r_o = 1/0.45, r_i = 0.55/0.45,
as annulus_model.annulus_radii.
"""
import sys
import numpy as np
import gmsh

D = 2900.0                       # km per layer depth
R_O, R_I = 1 / 0.45, 0.55 / 0.45
THETA_T = np.pi / 2              # trench at the top of the figure

H_TRENCH, BOX_DEPTH = 16.0, 700.0
HALF_ARC = float(sys.argv[4]) if len(sys.argv) > 4 else 750.0   # 0: no trench window
H_TBL, TBL = 40.0, 200.0
H_UM, UM = 80.0, 660.0
H_LM = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
H_CMB = float(sys.argv[2]) if len(sys.argv) > 2 else H_LM
GROW = 0.25                      # km of cell size per km outside the trench window


def ramp(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def size_km(x, y):
    r = np.hypot(x, y)
    d = (R_O - r) * D                                   # depth, km
    h = H_TBL + (H_UM - H_TBL) * ramp(d, TBL, TBL + 150.0)
    lm = H_UM + (H_LM - H_UM) * ramp(d, UM, UM + 600.0)
    h = np.where(d > UM, lm, h)
    if H_CMB != H_LM:                                   # optional lower boundary layer
        h = np.minimum(h, H_CMB + (H_LM - H_CMB) * ramp((R_O - R_I) * D - d, 150.0, 600.0))
    dth = np.arctan2(np.sin(np.arctan2(y, x) - THETA_T), np.cos(np.arctan2(y, x) - THETA_T))
    s = abs(dth) * R_O * D                              # arc from the trench at the surface, km
    out = np.hypot(max(s - HALF_ARC, 0.0), max(d - BOX_DEPTH, 0.0))
    return float(h if HALF_ARC <= 0 else min(h, H_TRENCH + GROW * out))


def build(path):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("graded_annulus")
    outer = gmsh.model.occ.addDisk(0, 0, 0, R_O, R_O)
    inner = gmsh.model.occ.addDisk(0, 0, 0, R_I, R_I)
    gmsh.model.occ.cut([(2, outer)], [(2, inner)])
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.setSizeCallback(lambda dim, tag, x, y, z, lc: size_km(x, y) / D)
    gmsh.model.mesh.generate(2)
    _, coords, _ = gmsh.model.mesh.getNodes()
    xy = coords.reshape(-1, 3)[:, :2]
    types, _, conn = gmsh.model.mesh.getElements(2)
    tri = conn[list(types).index(2)].reshape(-1, 3).astype(int) - 1
    gmsh.finalize()
    np.savez(path, xy=xy, tri=tri)
    return xy, tri


if __name__ == "__main__":
    out = sys.argv[3] if len(sys.argv) > 3 else "graded_base.npz"
    xy, tri = build(out)
    print(f"{len(tri)} triangles, {len(xy)} nodes")
