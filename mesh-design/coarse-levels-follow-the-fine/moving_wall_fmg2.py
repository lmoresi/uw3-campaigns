"""Coarse multigrid levels and a moving wall, by cell type and transfer read.

As moving_wall_fmg.py (20 steps; each raises the top wall by 2.5 % of the depth
times sin(pi x) and stretches the interior with it), with three switches:

  -uw_cells    simplex | quad | hex | adapt   (adapt: an adapt child of a
               refined simplex base, refined near the top wall; its tail is
               the base's levels, which do not nest in the child)
  -uw_read     dev      development as it stands
               rebuilt  the as-built read switched off: every transfer built
                        from the coordinates the levels stand on
               kept     the as-built read extended to every cell type: the
                        development function with its simplex test removed
  -uw_move_coarse  0 | 1  move every coarse level by the same map as the finest

Per step: velocity-block iterations of the solve, and outer Krylov iterations.
"""
import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities import custom_mg, fault_mg

params = uw.Params(cells="simplex", read="dev", move_coarse=0, steps=20, rise=0.025)
cells, read, move_coarse = str(params.cells), str(params.read), bool(int(params.move_coarse))

if read == "rebuilt":
    fault_mg.as_built_nodes = lambda *a, **k: None
elif read == "kept":
    def _as_built_every_cell_type(mesh, degree, continuous):
        if not mesh._moved_since_built or not mesh._moved_off_transfer_geometry():
            return None
        return np.asarray(mesh._get_coords_for_basis(
            degree, continuous, vertices=mesh._transfer_vertices))
    fault_mg.as_built_nodes = _as_built_every_cell_type

if cells == "quad":
    mesh = uw.meshing.StructuredQuadBox(elementRes=(4, 4), minCoords=(0, 0), maxCoords=(1, 1),
                                        qdegree=2, refinement=2)
elif cells == "hex":
    mesh = uw.meshing.StructuredQuadBox(elementRes=(2, 2, 2), minCoords=(0, 0, 0),
                                        maxCoords=(1, 1, 1), qdegree=2, refinement=2)
else:
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 4,
                                             regular=False, qdegree=2, refinement=2)
    if cells == "adapt":
        x, y = mesh.X
        metric = uw.discretisation.MeshVariable("metric", mesh, 1, degree=1)
        metric.array[:, 0, 0] = 1.0 + 3.0 * np.exp(-((np.asarray(metric.coords)[:, 1] - 1.0) / 0.2) ** 2)
        mesh = mesh.adapt(metric, max_levels=1)
coarse = list(mesh.multigrid_levels[:-1])
dim = mesh.dim

X = mesh.X
s = uw.systems.Stokes(mesh)
s.constitutive_model = uw.constitutive_models.ViscousFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = 1
walls = ("Bottom", "Left", "Right") + (("Front", "Back") if dim == 3 else ())
for wall in walls:
    s.add_dirichlet_bc((0,) * dim, wall)
s.bodyforce = sympy.Matrix([[0] * (dim - 1) + [sympy.sin(sympy.pi * X[0])]])
s.tolerance = 1.0e-6
custom_mg.set_custom_fmg(s, coarse, field_id=0)


def raise_wall(m):
    c = np.asarray(m.X.coords).copy()
    c[:, dim - 1] *= 1 + float(params.rise) * np.sin(np.pi * c[:, 0])
    m.deform(c)


def velocity_its():
    return s.snes.getKSP().getPC().getFieldSplitSubKSP()[0].getIterationNumber()


print(f"{cells} read={read} move_coarse={int(move_coarse)}: {len(coarse)} coarse levels", flush=True)
for step in range(int(params.steps) + 1):
    if step:
        raise_wall(mesh)
        if move_coarse:
            for level in coarse:
                raise_wall(level)
    s.solve()
    print(f"step {step:2d}: reason {s.snes.getConvergedReason()}, velocity its {velocity_its()}, "
          f"outer its {s.snes.getKSP().getIterationNumber()}", flush=True)
