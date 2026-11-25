"""Register row 29: a refinement reference for the max fault slip (sheared box, frictionless
fault), and the cell quality, under one pull rule. The four traces' geometry is fixed (6/12 long,
from pull22's generator at h = 1/12), sampled at one cell of each mesh.

    MODE=dev|new_light_sharp python refine29.py <trace index 0..3> <cells per side, e.g. 12 24 48>"""
import os, sys, json, warnings
import numpy as np
k_want = int(sys.argv[1]); Ns = [int(x) for x in sys.argv[2:]]
sys.argv = sys.argv[:1]
MODE = os.environ.get("MODE", "dev")
if MODE == "new_light_sharp":
    os.environ["THIN"] = "0"; os.environ.setdefault("SHARP_DEG", "90")
    import corners_plugin  # noqa
import underworld3 as uw
from underworld3.utilities import line_cut as lc
warnings.simplefilter("ignore")
rng = np.random.default_rng(22); h0 = 1 / 12
for k in range(k_want + 1):
    ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
    c = 0.5 + rng.uniform(-0.05, 0.05, 2)
L = 6 * h0; s = np.linspace(-L / 2, L / 2, 2000); th = ang + turn * s / L
d = np.column_stack([np.cos(th), np.sin(th)])
CURVE = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
def resample(P, ds):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    q = np.linspace(0, cum[-1], max(2, int(round(cum[-1] / ds))) + 1)
    return np.column_stack([np.interp(q, cum, P[:, 0]), np.interp(q, cum, P[:, 1])])
for N in Ns:
    h = 1.0 / N
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h, regular=False)
    Q = resample(CURVE, h)
    rec = dict(mode=MODE, trace=k_want, N=N, turn=float(turn), snap_frac=os.environ.get("SNAP_FRAC", "0.1"))
    try:
        snap = {k: float(v) for k, v in (("snap_frac", os.environ.get("SNAP_FRAC")),) if v}
        m2 = mesh.add_fault(("F", Q), **snap)
    except Exception as e:
        rec["error"] = str(e)[:90]; print("REF", json.dumps(rec), flush=True); continue
    ang_min = float(np.min(lc.min_angles(m2.dm))) if hasattr(lc, "min_angles") else float("nan")
    x, y = m2.X
    st = uw.systems.Stokes(m2)
    st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = 1
    st.tolerance = 1.0e-8
    st.petsc_use_pressure_nullspace = True
    for side in ("Top", "Bottom", "Left", "Right"):
        st.add_dirichlet_bc((y - 0.5, 0.0), side)
    st.add_fault_bc(0, "F")
    st.solve()
    info = st._rotated_freeslip_info
    from underworld3.utilities.fault_contact import fault_slip
    _s, V, _leak = fault_slip(st, "F", info)
    rec.update(slip_max=float(np.abs(V).max()), min_angle_deg=ang_min, outer=info.get("ksp_its"),
               vel=info.get("vel_its_last"), pres=info.get("pres_its_last"), converged=bool(info.get("converged")))
    print("REF", json.dumps(rec), flush=True)
