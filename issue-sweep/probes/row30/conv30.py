"""Row 30 convergence: base and pinned at 12/24/48/96 cells per side. The largest slip, and the slip
one cell from the apex on each arm (interpolated along the trace), for up to N kinks of the given
turn that are added at every resolution.
    python conv30.py <box_irr|box_reg> <angle> <n>   |   python conv30.py <mesh> 150 1 kink150_3 0.3"""
import sys, os, json, warnings
import numpy as np
warnings.simplefilter("ignore")
sys.argv = sys.argv[:4] + ["0"] if len(sys.argv) == 4 else sys.argv
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "row30.py")).read()
src = src.split("coarse = uw.meshing.UnstructuredSimplexBox")[0]
_argv = list(sys.argv)
sys.argv = _argv[:4] if len(_argv) < 6 else _argv
exec(src)
n_want = int(_argv[3])
if len(_argv) >= 6:
    g = {}
    sys.argv = ["x", mk, _argv[5], "kinks"]
    exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
    pool = [q for t_, q in g["traces"]() if t_ == _argv[4]]
else:
    pool = [kink() for _ in range(12)]
from underworld3.utilities.fault_split import _turns
def slip_profile(mesh, Q, mode):
    TURNS["on"] = mode == "pin"; TURNS["pts"] = Q[_turns(Q)]
    m2 = mesh.add_fault(("F", Q)); x, y = m2.X
    st = uw.systems.Stokes(m2); st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = 1; st.tolerance = 1e-9; st.petsc_use_pressure_nullspace = True
    for side in ("Top", "Bottom", "Left", "Right"): st.add_dirichlet_bc((y - 0.5, 0.0), side)
    st.add_fault_bc(0, "F", **({"normal": "trace"} if mode == "trace" else {}))
    st.solve(); info = st._rotated_freeslip_info
    coords, jumps, normals = fc.fault_pair_jumps(st, "F", info)
    seg = np.diff(Q, axis=0); sl = np.linalg.norm(seg, axis=1); cum = np.concatenate([[0], np.cumsum(sl)])
    def arc(p):
        u = np.clip(((p - Q[:-1]) * seg).sum(1) / sl**2, 0, 1); d = np.linalg.norm(Q[:-1] + u[:, None] * seg - p, axis=1); i = int(np.argmin(d)); return cum[i] + u[i] * sl[i]
    s = np.array([arc(p) for p in coords]); v = np.linalg.norm(jumps, axis=1); o = np.argsort(s)
    s_apex = arc(TURNS["pts"][0])
    one = [float(np.interp(s_apex + k * h, s[o], v[o])) for k in (-1, 1)]
    ia = int(np.argmin(np.linalg.norm(coords - TURNS["pts"][0], axis=1)))
    return dict(max=float(v.max()), one_cell=one, apex=float(v[ia]), apex_normal=[float(a) for a in normals[ia]],
                vel=max(info.get("vel_its_last") or [0]), converged=bool(info.get("converged")))
meshes = {k: uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h / k, regular=(mk == "box_reg")) for k in (1, 2, 4, 8)}
done = 0
for t, Q in enumerate(pool):
    rec = dict(mesh=mk, angle=ang, trial=t)
    try:
        for k, mesh in meshes.items():
            for mode in ("base", "pin") + (("trace",) if k == 1 else ()):
                rec[f"{12*k}_{mode}"] = slip_profile(mesh, Q, mode)
    except Exception as e:
        continue
    a, b = Q[_turns(Q)][0] - Q[int(np.flatnonzero(_turns(Q))[0]) - 1], Q[int(np.flatnonzero(_turns(Q))[0]) + 1] - Q[_turns(Q)][0]
    rec["arm_normals"] = [[-a[1] / np.linalg.norm(a), a[0] / np.linalg.norm(a)], [-b[1] / np.linalg.norm(b), b[0] / np.linalg.norm(b)]]
    print("C30 " + json.dumps(rec), flush=True)
    done += 1
    if done >= n_want: break
