"""Generate the Spiegelman notch mesh at a given problem_size.

Geometry block copied VERBATIM from
  docs/examples/WIP/Benchmark/Ex_VP_Spiegelman_Benchmark.py
so the mesh is bit-faithful to the benchmark (diff the two to confirm).
problem_size 1=ultra-low, 2=low, 3=fine, 4=benchmark resolution.

Usage:  python make_notch_mesh.py <problem_size> [out_dir]
Writes: <out_dir>/notch_mesh<problem_size>.msh
"""
import sys, os
import gmsh

problem_size = int(sys.argv[1]) if len(sys.argv) > 1 else 3
out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
    "~/+Simulations/spiegelman_hardcase/meshes")
os.makedirs(out_dir, exist_ok=True)

S = 30.0  # H.magnitude — non-dimensional -> km
# Optional 3rd argument: coarsen the base by this factor (characteristic lengths x factor), so a
# coarse base refined k times reaches the same fine resolution with a DEEPER multigrid
# hierarchy (Louis, 2026-10-03). Refinement does not snap to the arcs, so the notch carries
# the coarse base's sharper corners.
coarsen = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

# --- characteristic lengths per resolution (verbatim from benchmark) ---
if problem_size <= 1:
    cl_1, cl_2, cl_2a, cl_3, cl_4 = 0.25*S, 0.15*S, 0.1*S, 0.25*S, 0.15*S
elif problem_size == 2:
    cl_1, cl_2, cl_2a, cl_3, cl_4 = 0.1*S, 0.05*S, 0.03*S, 0.1*S, 0.05*S
elif problem_size == 3:
    cl_1, cl_2, cl_2a, cl_3, cl_4 = 0.06*S, 0.03*S, 0.015*S, 0.04*S, 0.02*S
else:
    cl_1, cl_2, cl_2a, cl_3, cl_4 = 0.04*S, 0.005*S, 0.003*S, 0.02*S, 0.01*S

cl_1, cl_2, cl_2a, cl_3, cl_4 = (coarsen * c for c in (cl_1, cl_2, cl_2a, cl_3, cl_4))

gmsh.initialize()
gmsh.option.setNumber("General.Verbosity", 0)
gmsh.model.add("Notch")

Point1  = gmsh.model.geo.addPoint(-2 * S,      -1 * S,    0, cl_1)
Point3  = gmsh.model.geo.addPoint(+2 * S,      -1 * S,    0, cl_1)
Point4  = gmsh.model.geo.addPoint( 2 * S,    -3/4 * S,    0, cl_1)
Point5  = gmsh.model.geo.addPoint( 2 * S,           0,    0, cl_1)
Point6  = gmsh.model.geo.addPoint(-2 * S,           0,    0, cl_1)
Point7  = gmsh.model.geo.addPoint(-2 * S,    -3/4 * S,    0, cl_1)
Point25 = gmsh.model.geo.addPoint(-3/4 * S,         0,    0, cl_4)
Point26 = gmsh.model.geo.addPoint( 3/4 * S,         0,    0, cl_4)
Point27 = gmsh.model.geo.addPoint(       0,         0,    0, cl_3)

Line1 = gmsh.model.geo.addLine(Point1, Point3)
Line2 = gmsh.model.geo.addLine(Point3, Point4)
Line3 = gmsh.model.geo.addLine(Point4, Point5)
Line4 = gmsh.model.geo.addLine(Point5, Point26)
Line8 = gmsh.model.geo.addLine(Point26, Point27)
Line9 = gmsh.model.geo.addLine(Point27, Point25)
Line10 = gmsh.model.geo.addLine(Point25, Point6)
Line6 = gmsh.model.geo.addLine(Point6, Point7)
Line7 = gmsh.model.geo.addLine(Point7, Point1)

rc = 0.02
Point12 = gmsh.model.geo.addPoint(-(1/12 + rc) * S,   -3/4 * S,        0, cl_2a)
Point13 = gmsh.model.geo.addPoint( -1/12 * S,        -(3/4 - rc) * S,  0, cl_2a)
Point14 = gmsh.model.geo.addPoint( -1/12 * S,        -(2/3 + rc) * S,  0, cl_2a)
Point15 = gmsh.model.geo.addPoint(-(1/12 - rc) * S,   -2/3 * S,        0, cl_2a)
Point16 = gmsh.model.geo.addPoint( (1/12 - rc) * S,   -2/3 * S,        0, cl_2a)
Point17 = gmsh.model.geo.addPoint(  1/12 * S,        -(2/3 + rc) * S,  0, cl_2a)
Point18 = gmsh.model.geo.addPoint(  1/12 * S,        -(3/4 - rc) * S,  0, cl_2a)
Point19 = gmsh.model.geo.addPoint( (1/12 + rc) * S,   -3/4 * S,        0, cl_2a)
Point20 = gmsh.model.geo.addPoint(-(1/12 + rc) * S,  -(3/4 - rc) * S,  0, cl_2a)
Point21 = gmsh.model.geo.addPoint(-(1/12 - rc) * S,  -(2/3 + rc) * S,  0, cl_2a)
Point22 = gmsh.model.geo.addPoint( (1/12 - rc) * S,  -(2/3 + rc) * S,  0, cl_2a)
Point24 = gmsh.model.geo.addPoint( (1/12 + rc) * S,  -(3/4 - rc) * S,  0, cl_2a)

Circle22 = gmsh.model.geo.addCircleArc(Point12, Point20, Point13)
Circle23 = gmsh.model.geo.addCircleArc(Point14, Point21, Point15)
Circle24 = gmsh.model.geo.addCircleArc(Point16, Point22, Point17)
Circle25 = gmsh.model.geo.addCircleArc(Point18, Point24, Point19)

Line26 = gmsh.model.geo.addLine(Point7, Point12)
Line27 = gmsh.model.geo.addLine(Point13, Point14)
Line28 = gmsh.model.geo.addLine(Point15, Point16)
Line29 = gmsh.model.geo.addLine(Point17, Point18)
Line30 = gmsh.model.geo.addLine(Point19, Point4)

LineLoop31 = gmsh.model.geo.addCurveLoop(
    [Line1, Line2, -Line30, -Circle25, -Line29, -Circle24, -Line28,
     -Circle23, -Line27, -Circle22, -Line26, Line7])
LineLoop33 = gmsh.model.geo.addCurveLoop(
    [Line6, Line26, Circle22, Line27, Circle23, Line28, Circle24, Line29,
     Circle25, Line30, Line3, Line4, Line8, Line9, Line10])

Surface32 = gmsh.model.geo.addPlaneSurface([LineLoop31])
Surface34 = gmsh.model.geo.addPlaneSurface([LineLoop33])
gmsh.model.geo.synchronize()

gmsh.model.addPhysicalGroup(1, [Line1], tag=3, name="Bottom")
gmsh.model.addPhysicalGroup(1, [Line2, Line3], tag=2, name="Right")
gmsh.model.addPhysicalGroup(1, [Line7, Line6], tag=1, name="Left")
gmsh.model.addPhysicalGroup(1, [Line4, Line8, Line9, Line10], tag=4, name="Top")
gmsh.model.addPhysicalGroup(
    1, [Line26, Circle22, Line27, Circle23, Line28, Circle24, Line29, Circle25, Line30],
    tag=5, name="Inner")
gmsh.model.addPhysicalGroup(2, [Surface32], tag=100, name="Weak")
gmsh.model.addPhysicalGroup(2, [Surface34], tag=101, name="Strong")

gmsh.model.mesh.generate(2)
out = (f"{out_dir}/notch_mesh{problem_size}.msh" if coarsen == 1.0
       else f"{out_dir}/notch_mesh{problem_size}c{coarsen:g}.msh")
gmsh.write(out)
n_tri = len(gmsh.model.mesh.getElements(2)[1][0]) if gmsh.model.mesh.getElements(2)[1] else 0
gmsh.finalize()
print(f"wrote {out}  ({n_tri} triangles)")
