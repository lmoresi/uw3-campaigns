"""The Spiegelman notch extruded along strike (z) into a tetrahedral mesh.

The 2-D geometry is make_notch_mesh.py's (the benchmark's, verbatim) at
problem_size 1. Both surfaces are extruded by Lz and the volumes tet-meshed (UW3 needs
simplices, so not a layered prism extrusion). A Box size field grades the mesh: h_band
in the band region above the notch (|x| < 1.05 H, y > -0.8 H), the benchmark's
coarse sizes elsewhere. Uniform refinement k times in UW3 then gives h_band / 2^k in
the band and a k+1-level FMG hierarchy.

Physical groups, as the 2-D mesh where they exist: volumes Weak (100) and Strong
(101); surfaces Left (1), Right (2), Bottom (3), Top (4), Inner (5), and the
strike-normal faces Front (6, z = 0) and Back (7, z = Lz), classified by bounding box.

Usage:  python make_notch_mesh_3d.py <h_band_km> <Lz_km> [out_dir]
Writes: <out_dir>/notch3d_hb<h_band>_Lz<Lz>.msh
"""
import os
import sys

import gmsh

h_band = float(sys.argv[1]) if len(sys.argv) > 1 else 1.2
Lz = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
out_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser(
    "~/+Simulations/spiegelman_hardcase/meshes")
os.makedirs(out_dir, exist_ok=True)

S = 30.0
cl_1, cl_2, cl_2a, cl_3, cl_4 = 0.25 * S, 0.15 * S, 0.1 * S, 0.25 * S, 0.15 * S

gmsh.initialize()
gmsh.option.setNumber("General.Verbosity", 0)
gmsh.model.add("Notch3D")
g = gmsh.model.geo
P = lambda x, y, cl: g.addPoint(x, y, 0, cl)
p1, p3, p4 = P(-2 * S, -S, cl_1), P(2 * S, -S, cl_1), P(2 * S, -0.75 * S, cl_1)
p5, p6, p7 = P(2 * S, 0, cl_1), P(-2 * S, 0, cl_1), P(-2 * S, -0.75 * S, cl_1)
p25, p26, p27 = P(-0.75 * S, 0, cl_4), P(0.75 * S, 0, cl_4), P(0, 0, cl_3)
L1, L2, L3 = g.addLine(p1, p3), g.addLine(p3, p4), g.addLine(p4, p5)
L4, L8, L9, L10 = g.addLine(p5, p26), g.addLine(p26, p27), g.addLine(p27, p25), g.addLine(p25, p6)
L6, L7 = g.addLine(p6, p7), g.addLine(p7, p1)
rc = 0.02
q = lambda x, y: P(x * S, y * S, cl_2a)
p12, p13 = q(-(1 / 12 + rc), -3 / 4), q(-1 / 12, -(3 / 4 - rc))
p14, p15 = q(-1 / 12, -(2 / 3 + rc)), q(-(1 / 12 - rc), -2 / 3)
p16, p17 = q(1 / 12 - rc, -2 / 3), q(1 / 12, -(2 / 3 + rc))
p18, p19 = q(1 / 12, -(3 / 4 - rc)), q(1 / 12 + rc, -3 / 4)
p20, p21 = q(-(1 / 12 + rc), -(3 / 4 - rc)), q(-(1 / 12 - rc), -(2 / 3 + rc))
p22, p24 = q(1 / 12 - rc, -(2 / 3 + rc)), q(1 / 12 + rc, -(3 / 4 - rc))
C22, C23 = g.addCircleArc(p12, p20, p13), g.addCircleArc(p14, p21, p15)
C24, C25 = g.addCircleArc(p16, p22, p17), g.addCircleArc(p18, p24, p19)
L26, L27, L28 = g.addLine(p7, p12), g.addLine(p13, p14), g.addLine(p15, p16)
L29, L30 = g.addLine(p17, p18), g.addLine(p19, p4)
loop_weak = g.addCurveLoop([L1, L2, -L30, -C25, -L29, -C24, -L28, -C23, -L27, -C22, -L26, L7])
loop_strong = g.addCurveLoop([L6, L26, C22, L27, C23, L28, C24, L29, C25, L30, L3, L4, L8, L9, L10])
s_weak, s_strong = g.addPlaneSurface([loop_weak]), g.addPlaneSurface([loop_strong])
out_weak = g.extrude([(2, s_weak)], 0, 0, Lz)
out_strong = g.extrude([(2, s_strong)], 0, 0, Lz)
g.synchronize()
v_weak = [t for d, t in out_weak if d == 3]
v_strong = [t for d, t in out_strong if d == 3]

eps = 1e-6
groups = {"Left": [], "Right": [], "Bottom": [], "Top": [], "Inner": [], "Front": [], "Back": []}
for _, tag in gmsh.model.getEntities(2):
    x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(2, tag)
    if abs(z0) < eps and abs(z1) < eps:
        groups["Front"].append(tag)
    elif abs(z0 - Lz) < eps and abs(z1 - Lz) < eps:
        groups["Back"].append(tag)
    elif abs(x0 + 2 * S) < eps and abs(x1 + 2 * S) < eps:
        groups["Left"].append(tag)
    elif abs(x0 - 2 * S) < eps and abs(x1 - 2 * S) < eps:
        groups["Right"].append(tag)
    elif abs(y0 + S) < eps and abs(y1 + S) < eps:
        groups["Bottom"].append(tag)
    elif abs(y0) < eps and abs(y1) < eps:
        groups["Top"].append(tag)
    else:
        groups["Inner"].append(tag)     # the weak / strong interface
for name, tag in (("Left", 1), ("Right", 2), ("Bottom", 3), ("Top", 4), ("Inner", 5),
                  ("Front", 6), ("Back", 7)):
    gmsh.model.addPhysicalGroup(2, groups[name], tag=tag, name=name)
gmsh.model.addPhysicalGroup(3, v_weak, tag=100, name="Weak")
gmsh.model.addPhysicalGroup(3, v_strong, tag=101, name="Strong")

box = gmsh.model.mesh.field.add("Box")
gmsh.model.mesh.field.setNumber(box, "VIn", h_band)
gmsh.model.mesh.field.setNumber(box, "VOut", cl_1)
gmsh.model.mesh.field.setNumber(box, "XMin", -1.05 * S)
gmsh.model.mesh.field.setNumber(box, "XMax", 1.05 * S)
gmsh.model.mesh.field.setNumber(box, "YMin", -0.8 * S)
gmsh.model.mesh.field.setNumber(box, "YMax", 0.0)
gmsh.model.mesh.field.setNumber(box, "ZMin", -1.0)
gmsh.model.mesh.field.setNumber(box, "ZMax", Lz + 1.0)
gmsh.model.mesh.field.setNumber(box, "Thickness", 0.3 * S)
gmsh.model.mesh.field.setAsBackgroundMesh(box)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.option.setNumber("Mesh.Algorithm3D", 10)       # HXT, parallel
gmsh.model.mesh.generate(3)
out = f"{out_dir}/notch3d_hb{h_band:g}_Lz{Lz:g}.msh"
gmsh.write(out)
types, tags, _ = gmsh.model.mesh.getElements(3)
n_tet = sum(len(t) for t in tags)
gmsh.finalize()
print(f"wrote {out}  ({n_tet} tetrahedra; groups: " +
      ", ".join(f"{k} {len(v)}" for k, v in groups.items()) + ")")
