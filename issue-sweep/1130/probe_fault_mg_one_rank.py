"""Review of PR #1130: the parallel cell-located transfer called on ONE rank.

On one rank the hierarchy takes the serial transfer, so the parallel function
is called here directly, with the level layouts the parallel build would make,
on the fixture of the PR's test (a fault cut into an adapt child, Stokes).
Failures are then forced in memory (nothing installed is edited) and the
exception that leaves the function is recorded: RuntimeError through
fault_contact._collective_raise is the collective route; anything else left
the function on the rank's own, which is the pattern that hangs at np > 1.

    OMP_NUM_THREADS=1 pixi run -e runtime python <this file>
"""
import subprocess
import traceback
import types

import numpy as np

import underworld3 as uw
from underworld3.utilities import custom_mg, fault_mg

params = uw.Params(
    uw_dev_ref=uw.Param("origin/development", description="git ref of the comparison"),
    uw_cell_size=uw.Param(0.1, description="base cell size of the fixture"),
)
assert uw.mpi.size == 1
print("uw:", uw.__file__)

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
    h = float(params.uw_cell_size)
    base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                             cellSize=h, refinement=1, qdegree=2)
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

pairs = captured.get("pairs", [])
print("serial cell-located transfers built by the solve:", len(pairs))
assert pairs, "the fixture built no split-level transfer on one rank"
solver, field_id = captured["solver"], captured["field_id"]
pair = pairs[0]
coarse, fine = pair["coarse"], pair["fine"]
lay_c = custom_mg._coarse_dof_layout(solver, coarse, field_id)
finest = fine is solver.mesh or fine.dm.handle == solver.mesh.dm.handle
lay_f = (custom_mg._level_dof_layout(solver.dm, field_id) if finest
         else custom_mg._coarse_dof_layout(solver, fine, field_id))
ncomp = lay_c.n_full // np.asarray(pair["Xc"]).shape[0]
print("pair 0: coarse cells", fault_mg._cell_vertex_table(coarse)[1].shape[0],
      "| fine cells", fault_mg._cell_vertex_table(fine)[1].shape[0],
      "| degree", pair["degree"], "| components", ncomp, "| fine level is the finest:", finest)
ARGS = (coarse, fine, pair["degree"], pair["continuous"], pair["Xc"], pair["Xf"],
        lay_c, lay_f, ncomp, solver.dm.comm)


def run(module, label):
    """What leaves ``module.cell_located_transfer_parallel`` and from where."""
    try:
        P = module.cell_located_transfer_parallel(*ARGS)
        out = f"returned a {P.getSize()} matrix, stats {module.last_transfer_stats}"
    except Exception as err:
        frames = [f.name for f in traceback.extract_tb(err.__traceback__)]
        out = (f"{type(err).__name__}: {str(err)[:90]}\n"
               f"{'':>12}raised through: {' > '.join(frames)}")
    print(f"  {label:<58} -> {out}")


def with_patch(module, name, replacement, label):
    original = getattr(module, name)
    setattr(module, name, replacement(original))
    try:
        run(module, label)
    finally:
        setattr(module, name, original)


def node_weights_fails_on_call(n, error):
    def make(original):
        count = {"n": 0}

        def failing(*a, **k):
            count["n"] += 1
            if count["n"] == n:
                raise error
            return original(*a, **k)
        return failing
    return make


def orphan_node(original):
    def owner(fn, n_nodes):
        out = original(fn, n_nodes)
        out[0] = -1
        return out
    return owner


def degenerate_coarse_cell(module):
    """One coarse cell listed with a repeated vertex (zero area exactly)."""
    def make(original):
        def table(mesh):
            vxy, cv = original(mesh)
            if mesh is coarse:
                cv = cv.copy()
                cv[cv.shape[0] // 2, 2] = cv[cv.shape[0] // 2, 1]
            return vxy, cv
        return table
    return make


def point_coarse_cell(original):
    """One coarse cell collapsed to a point (its three vertices the same)."""
    def table(mesh):
        vxy, cv = original(mesh)
        if mesh is coarse:
            cv = cv.copy()
            cv[cv.shape[0] // 2, :] = cv[cv.shape[0] // 2, 0]
        return vxy, cv
    return table


def first_location_misses(original):
    """The rank's own location reports a tenth of its nodes outside (so they
    become misses); the answer stage then finds them."""
    count = {"n": 0}

    def locate(points, vxy, cv, k=16):
        cell, lam = original(points, vxy, cv, k)
        count["n"] += 1
        if count["n"] == 1:
            lam = lam.copy()
            lam[::10] -= 1.0
        return cell, lam
    return locate


def every_location_misses(original):
    """A tenth of the nodes are outside for the rank and for the answers: the
    clamped rest."""
    def locate(points, vxy, cv, k=16):
        cell, lam = original(points, vxy, cv, k)
        lam = lam.copy()
        lam[::10] -= 1.0
        return cell, lam
    return locate


src = subprocess.run(
    ["git", "show", f"{params.uw_dev_ref}:src/underworld3/utilities/fault_mg.py"],
    check=True, capture_output=True, text=True).stdout
DEV = types.ModuleType("underworld3.utilities.fault_mg_development")
DEV.__dict__["__name__"] = "underworld3.utilities.fault_mg_development"
exec(compile(src, "fault_mg_development.py", "exec"), DEV.__dict__)

singular = np.linalg.LinAlgError("Singular matrix (forced)")
for name, module in (("PR head", fault_mg), ("development", DEV)):
    print(f"\n{name}")
    run(module, "as built")
    for n in (1, 2, 3):
        with_patch(module, "_node_weights", node_weights_fails_on_call(n, singular),
                   f"_node_weights raises LinAlgError on its call {n}")
    with_patch(module, "_node_weights",
               node_weights_fails_on_call(1, RuntimeError("fault_mg: 6 nodes per cell against 3 monomials")),
               "_node_weights raises its RuntimeError (node count)")
    with_patch(module, "_node_weights", node_weights_fails_on_call(1, IndexError("index out of bounds (forced)")),
               "_node_weights raises IndexError")
    with_patch(module, "_fine_cell_of_node", orphan_node, "a fine node belongs to no cell")
    with_patch(module, "_cell_vertex_table", degenerate_coarse_cell(module),
               "a coarse cell of zero area (repeated vertex)")
    with_patch(module, "_cell_vertex_table", point_coarse_cell,
               "a coarse cell collapsed to a point")
    for stage, patch in (("answer stage", first_location_misses), ("clamped rest", every_location_misses)):
        original_locate = module.locate_in_cells
        module.locate_in_cells = patch(original_locate)
        try:
            run(module, f"{stage}: as built")
        finally:
            module.locate_in_cells = original_locate
        module.locate_in_cells = patch(original_locate)
        try:
            with_patch(module, "_node_weights", node_weights_fails_on_call(2, singular),
                       f"{stage}: _node_weights raises LinAlgError on its call 2")
        finally:
            module.locate_in_cells = original_locate

# the serial transfer and the one-rank parallel transfer agree?
Pn = serial_original(coarse, fine, pair["degree"], pair["continuous"], pair["Xc"], pair["Xf"])
P = fault_mg.cell_located_transfer_parallel(*ARGS)
ia, ja, va = P.getValuesCSR()
print("\nparallel transfer on one rank:", P.getSize(), "nnz", len(va),
      "| serial node transfer", Pn.shape, "nnz", Pn.nnz)
