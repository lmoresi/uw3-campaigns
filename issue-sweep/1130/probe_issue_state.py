"""Review of PR #1130: probes for the state of the neighbouring open issues,
on one rank, PR head against development (development's modules are read with
``git show`` and executed into module objects of their own).

  #559   two targets of one pull that choose the same vertex
  #1089  (the part left open) the snap of a cut moves a domain-boundary vertex
  #1120  the split-level transfer's weights (unchanged by this branch?)

    OMP_NUM_THREADS=1 pixi run -e runtime python <this file>
"""
import subprocess
import types

import numpy as np

import underworld3 as uw
from underworld3.utilities import custom_mg, fault_mg, line_cut as HEAD

params = uw.Params(
    uw_n_calls=uw.Param(150, description="pull calls of the #559 sweep"),
    uw_seed=uw.Param(559, description="seed of the #559 sweep"),
    uw_dev_ref=uw.Param("origin/development", description="git ref of the comparison"),
)


def development(path, name):
    src = subprocess.run(["git", "show", f"{params.uw_dev_ref}:{path}"],
                         check=True, capture_output=True, text=True).stdout
    mod = types.ModuleType(f"underworld3.utilities.{name}")
    exec(compile(src, f"{name}.py", "exec"), mod.__dict__)
    return mod


DEV = development("src/underworld3/utilities/line_cut.py", "line_cut_development")
print("uw:", uw.__file__)

# ---------------------------------------------------------------- #559
box = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                        cellSize=1.0 / 12.0, regular=False)
rng = np.random.default_rng(int(params.uw_seed))
h = 1.0 / 12.0
rows = {}
for spacing in (1.0, 0.5, 0.25):
    for name, module in (("PR head", HEAD), ("development", DEV)):
        unplaced_calls = refused = 0
        sub = np.random.default_rng(int(params.uw_seed))
        for _ in range(int(params.uw_n_calls)):
            start = sub.uniform(0.25, 0.75, size=2)
            angle = sub.uniform(0.0, 2 * np.pi)
            step = spacing * h * np.array([np.cos(angle), np.sin(angle)])
            targets = start + np.arange(5)[:, None] * step
            try:
                out = module._coords(module.pull_vertex_onto(box.dm, targets))
            except ValueError:
                refused += 1
                continue
            d = np.linalg.norm(out[None, :, :] - targets[:, None, :], axis=2).min(axis=1)
            unplaced_calls += int((d > 1e-9).any())
        rows[(spacing, name)] = (unplaced_calls, refused)
print(f"\n#559: five targets in a row in one call, {int(params.uw_n_calls)} calls, interior of an irregular 1/12 box")
print("  spacing (cells) | calls leaving a target without a vertex (refused): PR head | development")
for spacing in (1.0, 0.5, 0.25):
    a, b = rows[(spacing, "PR head")], rows[(spacing, "development")]
    print(f"  {spacing:>5} | {a[0]} ({a[1]}) | {b[0]} ({b[1]})")

# ---------------------------------------------------------------- #1089, the part left open
line = np.array([[0.31, -0.1], [0.62, 1.1]])
for name, module in (("PR head", HEAD), ("development", DEV)):
    cut, info = module.cut_along_lines(box.dm, [line])
    on_wall_before = int(uw.utilities.place_surface._true_wall_vertex_mask(
        box.dm, len(HEAD._coords(box.dm))).sum())
    print(f"#1089 (snap part), {name}: area of the unit box after a wall-to-wall cut at the default "
          f"snap = {float(module.cell_areas(cut).sum()):.6f}")

# ---------------------------------------------------------------- #1120: are the transfer's weights changed?
TRACE = np.array([[0.3, 0.45], [0.7, 0.55]])
captured = {}
serial_original = fault_mg.cell_located_prolongation
coarse_map_original = custom_mg._coarse_reduced_map


def serial_spy(coarse, fine, degree, continuous=True, coarse_coords=None, fine_coords=None):
    captured.setdefault("pairs", []).append(
        dict(coarse=coarse, fine=fine, degree=degree, continuous=continuous,
             Xc=coarse_coords, Xf=fine_coords))
    return serial_original(coarse, fine, degree, continuous, coarse_coords, fine_coords)


def coarse_map_spy(solver, coarse_mesh, field_id=None):
    captured["solver"], captured["field_id"] = solver, field_id
    return coarse_map_original(solver, coarse_mesh, field_id)


fault_mg.cell_located_prolongation = serial_spy
custom_mg._coarse_reduced_map = coarse_map_spy
try:
    base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                             cellSize=0.1, refinement=1, qdegree=2)
    pts = np.column_stack([np.linspace(*TRACE[:, 0], 9), np.linspace(*TRACE[:, 1], 9), np.zeros(9)])
    guide = uw.meshing.Surface("guide_0874", base, pts)
    guide.discretize()
    child = base.adapt(guide.refinement_metric_function(
        h_near=0.05 / 4, h_far=0.05, width=0.08, profile="linear"), max_levels=2)
    mesh = child.add_fault([("Flt", TRACE)])
    x, y = mesh.X
    s = uw.systems.Stokes(mesh)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    s.petsc_use_pressure_nullspace = True
    for wall in ("Top", "Bottom", "Left", "Right"):
        s.add_dirichlet_bc((y - 0.5, 0.0), wall)
    s.add_fault_bc(0, "Flt")
    s.solve()
finally:
    fault_mg.cell_located_prolongation = serial_original
    custom_mg._coarse_reduced_map = coarse_map_original

DEV_MG = development("src/underworld3/utilities/fault_mg.py", "fault_mg_development")
solver, field_id = captured["solver"], captured["field_id"]
print(f"\n#1120: {len(captured['pairs'])} split-level pair(s); parallel transfer on one rank, PR head against development")
for k, pair in enumerate(captured["pairs"]):
    coarse, fine = pair["coarse"], pair["fine"]
    lay_c = custom_mg._coarse_dof_layout(solver, coarse, field_id)
    finest = fine.dm.handle == solver.mesh.dm.handle
    lay_f = (custom_mg._level_dof_layout(solver.dm, field_id) if finest
             else custom_mg._coarse_dof_layout(solver, fine, field_id))
    ncomp = lay_c.n_full // np.asarray(pair["Xc"]).shape[0]
    args = (coarse, fine, pair["degree"], pair["continuous"], pair["Xc"], pair["Xf"],
            lay_c, lay_f, ncomp, solver.dm.comm)
    a = fault_mg.cell_located_transfer_parallel(*args).getValuesCSR()
    b = DEV_MG.cell_located_transfer_parallel(*args).getValuesCSR()
    same = all(np.array_equal(p, q) for p, q in zip(a, b))
    Sa = serial_original(coarse, fine, pair["degree"], pair["continuous"], pair["Xc"], pair["Xf"])
    Sb = DEV_MG.cell_located_prolongation(coarse, fine, pair["degree"], pair["continuous"],
                                          pair["Xc"], pair["Xf"])
    same_serial = (np.array_equal(Sa.indptr, Sb.indptr) and np.array_equal(Sa.indices, Sb.indices)
                   and np.array_equal(Sa.data, Sb.data))
    print(f"  pair {k}: finest={finest} nnz {len(a[2])} | parallel transfer bit-identical: {same} "
          f"| serial transfer bit-identical: {same_serial}")
