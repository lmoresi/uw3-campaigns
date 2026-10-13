"""The notch as a restricted BLOCK in 3-D: the benchmark's bump (5 x 2.5 km with its
0.6 km fillets) extruded only from z = 0 to z = Ln, on a weak lower layer that runs the
whole strike. With u_z = 0 on z = 0 (a symmetry plane) the notch is 2 Ln long, so the
bands can be followed away from the perturbation along strike (Louis, 2026-10-14: an
extruded notch roots the bands everywhere and hides the crossover).

OCC geometry: domain box, layer box and the extruded bump, fragmented into conforming
volumes. Groups, as the other notch meshes:
  volumes  Weak (100) = layer + block, Strong (101), Notch (102) = the block;
  surfaces Left 1, Right 2, Bottom 3, Top 4, Front 6 (z = 0), Back 7 (z = Lz), and
           Inner 5 = every surface between a weak and a strong volume (read from the
           volume adjacencies, so the block's sides, top and end face are all in it).
The layer / block interface carries no group.

Sizes (km): h_band in the band region (|x| < 1.05 H, y > -0.8 H, all z), h_near within
a few km of the block's surfaces, the benchmark's coarse sizes elsewhere; --coarsen f
scales them all (the crude levels of a non-nested FMG tail).

Usage: python make_notch_block_3d.py <h_band> <Lz> <Ln> [out_dir] [--near h] [--coarsen f]
Writes: <out_dir>/notchblock3d_hb<h_band>_Lz<Lz>_Ln<Ln>[_n<h_near>][_c<f>].msh
"""
import os
import sys

import gmsh


def _flag(name, default):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = float(sys.argv[i + 1])
        del sys.argv[i:i + 2]
        return v
    return default


coarsen = _flag("--coarsen", 1.0)
h_near = _flag("--near", 0.0)
h_band = float(sys.argv[1]) * coarsen
Lz = float(sys.argv[2])
Ln = float(sys.argv[3])
out_dir = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else os.path.expanduser(
    "~/+Simulations/spiegelman_hardcase/meshes")
os.makedirs(out_dir, exist_ok=True)

S = 30.0
a, b, rc = 1.0 / 12.0, 0.75, 0.02
cl_1 = 0.25 * S * coarsen

gmsh.initialize()
gmsh.option.setNumber("General.Verbosity", 0)
gmsh.model.add("NotchBlock3D")
occ = gmsh.model.occ

domain = occ.addBox(-2 * S, -S, 0, 4 * S, S, Lz)
layer = occ.addBox(-2 * S, -S, 0, 4 * S, (1 - b) * S, Lz)

# the bump profile in the z = 0 plane (make_notch_mesh.py's points), closed along the
# layer top y = -b between the two lower arc ends
P = lambda x, y: occ.addPoint(x * S, y * S, 0)
p12, p13 = P(-(a + rc), -b), P(-a, -(b - rc))
p14, p15 = P(-a, -(2 / 3 + rc)), P(-(a - rc), -2 / 3)
p16, p17 = P(a - rc, -2 / 3), P(a, -(2 / 3 + rc))
p18, p19 = P(a, -(b - rc)), P(a + rc, -b)
c20, c21 = P(-(a + rc), -(b - rc)), P(-(a - rc), -(2 / 3 + rc))
c22, c24 = P(a - rc, -(2 / 3 + rc)), P(a + rc, -(b - rc))
curves = [occ.addCircleArc(p12, c20, p13), occ.addLine(p13, p14),
          occ.addCircleArc(p14, c21, p15), occ.addLine(p15, p16),
          occ.addCircleArc(p16, c22, p17), occ.addLine(p17, p18),
          occ.addCircleArc(p18, c24, p19), occ.addLine(p19, p12)]
bump_face = occ.addPlaneSurface([occ.addCurveLoop(curves)])
bump = [t for d, t in occ.extrude([(2, bump_face)], 0, 0, Ln) if d == 3][0]

occ.fragment([(3, domain)], [(3, layer), (3, bump)])
occ.synchronize()

# classify the volumes by their centres
weak, strong, block = [], [], []
for _, v in gmsh.model.getEntities(3):
    x, y, z = occ.getCenterOfMass(3, v)
    if y < -b * S:
        weak.append(v)                                   # the layer
    elif y < -2 / 3 * S and abs(x) < (a + rc) * S and z < Ln:
        weak.append(v)                                   # the block
        block.append(v)
    else:
        strong.append(v)

eps = 1e-6
groups = {k: [] for k in ("Left", "Right", "Bottom", "Top", "Inner", "Front", "Back")}
for _, s in gmsh.model.getEntities(2):
    x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(2, s)
    up, _down = gmsh.model.getAdjacencies(2, s)
    vols = set(up)
    if abs(z0) < eps and abs(z1) < eps:
        groups["Front"].append(s)
    elif abs(z0 - Lz) < eps and abs(z1 - Lz) < eps:
        groups["Back"].append(s)
    elif abs(x0 + 2 * S) < eps and abs(x1 + 2 * S) < eps:
        groups["Left"].append(s)
    elif abs(x0 - 2 * S) < eps and abs(x1 - 2 * S) < eps:
        groups["Right"].append(s)
    elif abs(y0 + S) < eps and abs(y1 + S) < eps:
        groups["Bottom"].append(s)
    elif abs(y0) < eps and abs(y1) < eps:
        groups["Top"].append(s)
    elif vols & set(weak) and vols & set(strong):
        groups["Inner"].append(s)                        # weak / strong interface
for name, tag in (("Left", 1), ("Right", 2), ("Bottom", 3), ("Top", 4), ("Inner", 5),
                  ("Front", 6), ("Back", 7)):
    gmsh.model.addPhysicalGroup(2, groups[name], tag=tag, name=name)
gmsh.model.addPhysicalGroup(3, weak, tag=100, name="Weak")
gmsh.model.addPhysicalGroup(3, strong, tag=101, name="Strong")
gmsh.model.addPhysicalGroup(3, block, tag=102, name="Notch")

f = gmsh.model.mesh.field
box = f.add("Box")
for k, v in (("VIn", h_band), ("VOut", cl_1), ("XMin", -1.05 * S), ("XMax", 1.05 * S),
             ("YMin", -0.8 * S), ("YMax", 0.0), ("ZMin", -1.0), ("ZMax", Lz + 1.0),
             ("Thickness", 0.3 * S)):
    f.setNumber(box, k, v)
fields = [box]
if h_near > 0:
    block_faces = sorted({s for v in block for s in gmsh.model.getAdjacencies(3, v)[1]})
    dist = f.add("Distance")
    f.setNumbers(dist, "SurfacesList", block_faces)
    thr = f.add("Threshold")
    for k, v in (("InField", dist), ("SizeMin", h_near * coarsen), ("SizeMax", cl_1),
                 ("DistMin", 0.0), ("DistMax", 0.2 * S)):
        f.setNumber(thr, k, v)
    fields.append(thr)
both = f.add("Min")
f.setNumbers(both, "FieldsList", fields)
f.setAsBackgroundMesh(both)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.option.setNumber("Mesh.Algorithm3D", 10)
gmsh.model.mesh.generate(3)
out = (f"{out_dir}/notchblock3d_hb{h_band / coarsen:g}_Lz{Lz:g}_Ln{Ln:g}"
       + (f"_n{h_near:g}" if h_near > 0 else "") + (f"_c{coarsen:g}" if coarsen != 1 else "")
       + ".msh")
gmsh.write(out)
n_tet = sum(len(t) for t in gmsh.model.mesh.getElements(3)[1])
gmsh.finalize()
print(f"wrote {out}  ({n_tet} tetrahedra; volumes weak {len(weak)} strong {len(strong)} "
      f"block {len(block)}; surfaces " + ", ".join(f"{k} {len(v)}" for k, v in groups.items()) + ")")
