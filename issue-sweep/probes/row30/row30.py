"""Register row 30 (proposed): hold a fault's jump to zero along BOTH arms' normals at a turn
vertex. In 2-D that is the whole jump, so the probe adds the jump-TANGENT row of every pair at a
turn vertex to the constrained set (a wrapper round rotated_bc.build_rotation). For kinks of the
given angle: apex slip, near-apex slip and largest slip at 12 cells per side, as built ("base"),
patched ("pin") and with the trace's own normal ("trace"), against 48 cells per side (base and
pin), with iteration counts.
    python row30.py <box_irr|box_reg> <angle> <trials>"""
import sys, json, warnings
import numpy as np
warnings.simplefilter("ignore")
mk, ang, trials = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
FROM_GRID = len(sys.argv) > 4      # <mesh> 0 1 <trace> <ds>: one trace of pull22's kink grid
import underworld3 as uw
from underworld3.utilities import rotated_bc as rb, fault_contact as fc
from underworld3.utilities.fault_split import _turns
h = 1 / 12
TURNS = {"pts": np.zeros((0, 2))}
_orig = rb.build_rotation
def _pinned(solver, boundaries, datum_specs=None):
    Q, Qt, rows, datum = _orig(solver, boundaries, datum_specs)
    if not TURNS.get("on"):
        return Q, Qt, rows, datum
    dm = solver.dm; dim = 2; lsec = dm.getLocalSection(); l2g = dm.getLGMap()
    csec = dm.getCoordinateSection(); cvec = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dim)
    v0, v1 = dm.getDepthStratum(0)
    extra = []
    for fname in getattr(solver, "_fault_contact_faults", []):
        for q_plus, q_minus, nrm in fc._fault_pair_nodes(solver, fname):
            x = np.asarray(rb._point_coord(dm, dim, cvec, csec, v0, v1, q_minus), dtype=float)
            if len(TURNS["pts"]) and np.min(np.linalg.norm(TURNS["pts"] - x, axis=1)) < 1e-9:
                lo = lsec.getFieldOffset(q_minus, 0)
                extra.append(int(l2g.apply([lo + 1])[0]))
    TURNS["pinned"] = len(extra)
    return Q, Qt, sorted(set(rows) | set(extra)), datum
rb.build_rotation = _pinned
rng = np.random.default_rng(30 + int(ang))
def kink():
    c = rng.uniform(0.4, 0.6, 2); a0 = rng.uniform(0, 2 * np.pi)
    d1 = np.array([np.cos(a0), np.sin(a0)]); a1 = a0 + np.radians(180 - ang) * rng.choice([-1, 1])
    d2 = np.array([np.cos(a1), np.sin(a1)]); arm = np.linspace(0, 2.5 * h, 6)
    return np.vstack([c + arm[::-1, None] * d1, c + arm[1:, None] * d2])
def solve(mesh, Q, mode):
    TURNS["on"] = mode == "pin"; TURNS["pts"] = Q[_turns(Q)]
    m2 = mesh.add_fault(("F", Q)); x, y = m2.X
    st = uw.systems.Stokes(m2); st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = 1; st.tolerance = 1e-8; st.petsc_use_pressure_nullspace = True
    for side in ("Top", "Bottom", "Left", "Right"): st.add_dirichlet_bc((y - 0.5, 0.0), side)
    st.add_fault_bc(0, "F", **({"normal": "trace"} if mode == "trace" else {}))
    st.solve(); info = st._rotated_freeslip_info
    coords, jumps, _n = fc.fault_pair_jumps(st, "F", info)
    slip = np.linalg.norm(jumps, axis=1); d = np.linalg.norm(coords - TURNS["pts"][0], axis=1) / h
    return dict(apex=float(slip[d < 1e-6].max()) if (d < 1e-6).any() else None,
                near=float(slip[(d > 1e-6) & (d < 1.0)].max()) if ((d > 1e-6) & (d < 1.0)).any() else None,
                beyond=float(slip[d >= 1.0].max()) if (d >= 1.0).any() else None,
                max=float(slip.max()), vel=info.get("vel_its_last"), outer=info.get("ksp_its"),
                converged=bool(info.get("converged")), pinned=TURNS.get("pinned") if mode == "pin" else None)
coarse = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h, regular=(mk == "box_reg"))
fine = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h / 4, regular=(mk == "box_reg"))
if FROM_GRID:
    import os
    g = {}
    _argv = sys.argv
    sys.argv = ["x", mk, _argv[5], "kinks"]
    exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("import underworld3 as uw")[0] + "\n", g)
    sys.argv = ["x", mk, _argv[5], "kinks"]
    src = open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0]
    exec(src, g)
    GRID = [q for t_, q in g["traces"]() if t_ == _argv[4]]
for t in range(trials):
    Q = GRID[0] if FROM_GRID else kink(); rec = dict(mesh=mk, angle=ang, trial=t)
    for tag, mesh, modes in (("12", coarse, ("base", "pin", "trace")), ("48", fine, ("base", "pin"))):
        for mode in modes:
            try:
                rec[f"{tag}_{mode}"] = solve(mesh, Q, mode)
            except Exception as e:
                rec[f"{tag}_{mode}"] = dict(error=str(e)[:90])
    print("R30 " + json.dumps(rec), flush=True)
