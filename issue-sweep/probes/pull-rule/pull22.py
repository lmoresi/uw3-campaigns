"""The lighter add_fault pull rule, measured for a register row. MODE: dev (development build:
every sample pulled) | new_all (labelling-fix build: every sample pulled) | new_light
(labelling-fix build: tips and turns above 45 degrees pulled). Writes one JSON line per trace:
outcome, facets, trace<->chain distances, base vertices moved and how far, cell count, and for the
first SOLVE traces a sheared-box Stokes solve with a frictionless fault (max slip, iterations).

    MODE=... python pull22.py <box_irr|box_reg> <DS> <family: lines_arcs|kinks> [SOLVE]"""
import os, sys, json, warnings
import numpy as np
mesh_kind, DS, family = sys.argv[1], float(sys.argv[2]), sys.argv[3]
SOLVE = int(sys.argv[4]) if len(sys.argv) > 4 else 0
sys.argv = sys.argv[:1]
MODE = os.environ.get("MODE", "dev")
if MODE == "new_light_sharp":
    os.environ["THIN"] = "0"; os.environ.setdefault("SHARP_DEG", "90")
    import corners_plugin  # noqa
if MODE == "new_light":
    os.environ["THIN"] = "0"
    import corners_plugin  # noqa
import underworld3 as uw
from underworld3.utilities import line_cut as lc
warnings.simplefilter("ignore")
h = 1 / 12
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h, regular=(mesh_kind == "box_reg"))
X0 = np.asarray(mesh.dm.getCoordinatesLocal().array).reshape(-1, 2).copy()
rng = np.random.default_rng(22)

def resample(P, ds):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], max(2, int(round(cum[-1] / ds))) + 1)
    return np.column_stack([np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])])

def traces():
    out = []
    if family == "lines_arcs":
        for k in range(20):
            ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
            c = 0.5 + rng.uniform(-0.05, 0.05, 2)
            L = 6 * h; s = np.linspace(-L / 2, L / 2, 400); th = ang + turn * s / L
            d = np.column_stack([np.cos(th), np.sin(th)])
            P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
            out.append((f"la{k}", resample(P, DS * h)))
    else:   # two arms of 2.5 cells meeting at a turn, sampled every DS cells
        for angle in (10, 30, 60, 90, 120, 150):
            for trial in range(10):
                c = rng.uniform(0.4, 0.6, 2); a0 = rng.uniform(0, 2 * np.pi)
                d1 = np.array([np.cos(a0), np.sin(a0)]); a1 = a0 + np.radians(180 - angle) * rng.choice([-1, 1])
                d2 = np.array([np.cos(a1), np.sin(a1)])
                arm = np.linspace(0, 2.5 * h, int(round(2.5 / DS)) + 1)
                out.append((f"kink{angle}_{trial}", np.vstack([c + arm[::-1, None] * d1, c + arm[1:, None] * d2])))
    return out

def seg_dist(P, A, B):
    best = np.full(len(P), np.inf)
    for a, b in zip(A, B):
        e = b - a; L = e @ e
        u = np.clip(((P - a) @ e) / L, 0, 1) if L > 0 else np.zeros(len(P))
        best = np.minimum(best, np.linalg.norm(P - (a + u[:, None] * e), axis=1))
    return best

def solve(m2, name):
    x, y = m2.X
    st = uw.systems.Stokes(m2)
    st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = 1
    st.tolerance = 1.0e-6
    st.petsc_use_pressure_nullspace = True
    for side in ("Top", "Bottom", "Left", "Right"):
        st.add_dirichlet_bc((y - 0.5, 0.0), side)
    st.add_fault_bc(0, name)
    st.solve()
    info = st._rotated_freeslip_info
    from underworld3.utilities.fault_contact import fault_slip
    _s, V, _leak = fault_slip(st, name, info)
    return dict(slip_max=float(np.abs(V).max()), outer=info.get("ksp_its"), vel=info.get("vel_its_last"),
                pres=info.get("pres_its_last"), converged=bool(info.get("converged")))

for n, (tag, Q) in enumerate(traces()):
    rec = dict(mode=MODE, mesh=mesh_kind, ds=DS, trace=tag)
    try:
        m2 = mesh.add_fault(("F", Q))
    except Exception as e:
        msg = str(e)
        rec["outcome"] = ("empty" if "no facet" in msg else "partial" if "misses part" in msg else "raised")
        rec["reason"] = msg[:80]
        print("PULL", json.dumps(rec), flush=True); continue
    dm = m2.dm; b = [bb for bb in m2.boundaries if bb.name == "F"][0]
    lab = dm.getLabel("F"); nf = lab.getStratumSize(b.value) if lab is not None and lab.handle else 0
    rec["facets"] = int(nf)
    if nf == 0:
        rec["outcome"] = "empty"; print("PULL", json.dumps(rec), flush=True); continue
    vS, _ = dm.getDepthStratum(0)
    X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
    ends = np.array([dm.getCone(int(e)) for e in lab.getStratumIS(b.value).getIndices()]) - vS
    dense = np.vstack([Q[:-1] + x * (Q[1:] - Q[:-1]) for x in np.linspace(0, 1, 11)])
    a = seg_dist(dense, X[ends[:, 0]], X[ends[:, 1]])
    cv = np.unique(ends.ravel()); c = seg_dist(X[cv], Q[:-1], Q[1:])
    rec.update(outcome="partial" if a.max() > 0.5 * h else "complete", trace_to_chain_max=float(a.max() / h),
               trace_to_chain_mean=float(a.mean() / h), chain_to_trace_max=float(c.max() / h), cells=int(dm.getHeightStratum(0)[1]))
    # the base mesh's own vertices that a pull or a snap moved (the split adds vertices after them)
    n0 = min(len(X0), len(X)); mv = np.linalg.norm(X[:n0] - X0[:n0], axis=1)
    rec.update(moved=int((mv > 1e-12).sum()), moved_max=float(mv.max() / h))
    if n < SOLVE and rec["outcome"] == "complete":
        try:
            rec.update(solve(m2, "F"))
        except Exception as e:
            rec["solve_error"] = str(e)[:80]
    print("PULL", json.dumps(rec), flush=True)
