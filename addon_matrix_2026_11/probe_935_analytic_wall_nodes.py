"""#935 probe: at a given rank count, does the analytic-normal path miss an owned wall
node that the geometric path finds?

rotated_bc._boundary_velocity_nodes takes a rank's wall nodes from the facets labelled
on that rank; the geometric path (normal=None) also sums over the point SF and walks
every support-1 facet's closure. A node in the geometric set and not in the analytic
set, owned by this rank, gets no constraint row. Kaiju saw it on the zg95 annulus at
np 24-52. This looks for a small mesh and rank count that show it, for a CI test.

Each case sets a small Stokes solver's DM up (no boundary conditions: an essential
condition on a wall takes its DOFs out of the global vector, and the geometric path
then drops exactly the node in question), then compares the two node sets per wall
on every rank:

    mpirun -np 4 python probe_935_analytic_wall_nodes.py

PROBE935_SIZES  comma-separated cell sizes (0.2,0.1,0.07,0.05)
PROBE935_MESHES annulus, box, boxregular, comma-separated (annulus,box)

One line per case: the case, then per rank and wall the geometric path's node count,
the nodes the analytic path misses, and the owned ones among them.
"""
import os

import sympy

import underworld3 as uw
from underworld3.utilities import rotated_bc as rbc


def stokes_on(mesh):
    v = uw.discretisation.MeshVariable("V", mesh, mesh.dim, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    s._setup_pointwise_functions()
    s._setup_discretisation()
    return s


def owned_points(dm):
    p0, p1 = dm.getChart()
    if uw.mpi.size == 1:
        return set(range(p0, p1))
    _nroots, leaves, _remote = dm.getPointSF().getGraph()
    ghost = set() if leaves is None else {int(q) for q in leaves}
    return {q for q in range(p0, p1) if q not in ghost}


def compare(name, s, normals):
    owned = owned_points(s.dm)
    report = {}
    for wall, normal in normals.items():
        geometric = {q for q, _n in rbc._boundary_velocity_nodes(s, wall, normal=None)}
        analytic = {q for q, _n in rbc._boundary_velocity_nodes(s, wall, normal=normal)}
        missing = geometric - analytic
        report[wall] = (len(geometric), len(missing), len(missing & owned))
    every = uw.mpi.comm.gather(report, root=0)
    if uw.mpi.rank == 0:
        hit = any(m[2] for r in every for m in r.values())
        print(f"CASE935 {name} np {uw.mpi.size} {'MISSES' if hit else 'clean'} "
              f"(wall nodes, missed, missed and owned) per rank: {every}", flush=True)


SIZES = [float(c) for c in os.environ.get("PROBE935_SIZES", "0.2,0.1,0.07,0.05").split(",")]
MESHES = os.environ.get("PROBE935_MESHES", "annulus,box").split(",")

for cs in SIZES if "annulus" in MESHES else ():
    mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=cs, qdegree=2)
    x, y = mesh.X
    radial = sympy.Matrix([[x, y]]) / sympy.sqrt(x**2 + y**2)
    s = stokes_on(mesh)
    compare(f"annulus cellSize {cs}", s, {"Upper": radial, "Lower": radial})

BOX_NORMALS = {"Top": (0.0, 1.0), "Bottom": (0.0, -1.0),
               "Left": (-1.0, 0.0), "Right": (1.0, 0.0)}
for kind, regular in (("box", False), ("boxregular", True)):
    if kind not in MESHES:
        continue
    for cs in SIZES:
        mesh = uw.meshing.UnstructuredSimplexBox(
            minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=cs, regular=regular,
            qdegree=2)
        s = stokes_on(mesh)
        compare(f"{kind} cellSize {cs}", s, BOX_NORMALS)
