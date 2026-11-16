"""Coarse multigrid levels and a moving wall: 20 steps of a rising top wall.

A box refined twice; Stokes with the custom FMG on the velocity block. Each
step raises the top wall by 2.5 % of the depth times sin(pi x) (multiplicative,
so the centre reaches 1.025**20 = 1.64 of the depth) and stretches the interior
with it. Arms (``-uw_arm``):

  kept           simplex, development as it stands: a moved level is read where
                 it was built, so the transfers are those of the unmoved pair
  rebuilt        simplex, transfers rebuilt from the moved coordinates (the
                 as-built read switched off); the coarse levels stay as built
  rebuilt_moved  as rebuilt, with every coarse level moved by the same map
                 (exact at shared vertices: the map acts on the coordinates)
  quad           quadrilaterals, development as it stands (rebuilt from the
                 moved coordinates); the coarse levels stay as built
  quad_moved     quadrilaterals, with every coarse level moved by the same map

Per step: velocity-block iterations (last solve), outer Krylov iterations, and
the fine level's velocity nodes above the next coarser level's top boundary
(outside its hull): above y = 1 when the coarse level is unmoved, above the
chord of its moved top vertices when it moves.
"""
import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities import custom_mg, fault_mg

params = uw.Params(arm="kept", steps=20, rise=0.025)
arm = str(params.arm)
quad = arm.startswith("quad")
move_coarse = arm.endswith("_moved")

if arm.startswith("rebuilt"):
    fault_mg.as_built_nodes = lambda *a, **k: None       # read the moved coordinates

if quad:
    mesh = uw.meshing.StructuredQuadBox(elementRes=(4, 4), minCoords=(0, 0), maxCoords=(1, 1),
                                        qdegree=2, refinement=2)
else:
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 4,
                                             regular=False, qdegree=2, refinement=2)
coarse = list(mesh.multigrid_levels[:-1])

x, y = mesh.X
s = uw.systems.Stokes(mesh)
s.constitutive_model = uw.constitutive_models.ViscousFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = 1
for wall in ("Bottom", "Left", "Right"):
    s.add_dirichlet_bc((0, 0), wall)
s.bodyforce = sympy.Matrix([0, sympy.sin(sympy.pi * x)])
s.tolerance = 1.0e-6
custom_mg.set_custom_fmg(s, coarse, field_id=0)


def raise_wall(m):
    c = np.asarray(m.X.coords).copy()
    c[:, 1] *= 1 + float(params.rise) * np.sin(np.pi * c[:, 0])
    m.deform(c)


def top_wall_vertices(m):
    """The coordinates of the vertices on m's "Top" label, sorted by x."""
    dm = m.dm
    v0, v1 = dm.getDepthStratum(0)
    label = dm.getLabel("Top")
    pts = label.getStratumIS(m.boundaries.Top.value).getIndices() if label else []
    verts = np.array([p for p in pts if v0 <= p < v1], dtype=np.int64)
    coords = dm.getCoordinatesLocal().array.reshape(-1, m.cdim)[verts - v0]
    return coords[np.argsort(coords[:, 0])]


def outside_next_coarse():
    """Fine velocity nodes above the top wall of the level below: above the
    chord through that level's top-wall vertices."""
    V = np.asarray(s.u.coords)
    top = top_wall_vertices(coarse[-1])
    chord = np.interp(V[:, 0], top[:, 0], top[:, 1])
    return int((V[:, 1] > chord + 1.0e-12).sum())


def velocity_its():
    return s.snes.getKSP().getPC().getFieldSplitSubKSP()[0].getIterationNumber()


rows = []
for step in range(int(params.steps) + 1):
    if step:
        raise_wall(mesh)
        if move_coarse:
            for level in coarse:
                raise_wall(level)
    s.solve()
    rows.append((step, s.snes.getConvergedReason(), velocity_its(),
                 s.snes.getKSP().getIterationNumber(), outside_next_coarse()))
    print(f"{arm} step {step:2d}: reason {rows[-1][1]}, velocity its {rows[-1][2]}, "
          f"outer its {rows[-1][3]}, fine velocity nodes outside the next level {rows[-1][4]}",
          flush=True)
