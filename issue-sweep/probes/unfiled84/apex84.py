import sys, os, warnings
import numpy as np
warnings.simplefilter("ignore")
mk, ds, want = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", mk, ds, "kinks"]
g = {}
exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
uw, h = g["uw"], g["h"]
from underworld3.utilities.fault_contact import fault_pair_jumps
from underworld3.utilities.fault_split import _turns
Q = [q for t, q in g["traces"]() if t == want][0]
t = int(np.flatnonzero(_turns(Q))[0]); apex = Q[t]
t_in = (Q[t] - Q[t-1]) / np.linalg.norm(Q[t] - Q[t-1]); t_out = (Q[t+1] - Q[t]) / np.linalg.norm(Q[t+1] - Q[t])
n_in = np.array([-t_in[1], t_in[0]]); n_out = np.array([-t_out[1], t_out[0]])
m2 = g["mesh"].add_fault(("F", Q)); x, y = m2.X
st = uw.systems.Stokes(m2); st.constitutive_model = uw.constitutive_models.ViscousFlowModel
st.constitutive_model.Parameters.shear_viscosity_0 = 1; st.tolerance = 1e-8; st.petsc_use_pressure_nullspace = True
for side in ("Top", "Bottom", "Left", "Right"): st.add_dirichlet_bc((y - 0.5, 0.0), side)
st.add_fault_bc(0, "F"); st.solve()
coords, jumps, normals = fault_pair_jumps(st, "F", st._rotated_freeslip_info)
d = np.linalg.norm(coords - apex, axis=1); order = np.argsort(d)
print(f"A {want}: arms' normals differ by {np.degrees(np.arccos(np.clip(n_in @ n_out, -1, 1))):.0f} deg")
for i in order[:4]:
    j = jumps[i]; n = normals[i]
    print(f"A   pair {d[i]/h:.2f} cells from the apex: |jump| {np.linalg.norm(j):.4f}; along its own normal {j @ n:+.2e}; along arm-in normal {j @ n_in:+.4f}; along arm-out normal {j @ n_out:+.4f}; its normal vs arms {np.degrees(np.arccos(np.clip(abs(n @ n_in),0,1))):.0f}/{np.degrees(np.arccos(np.clip(abs(n @ n_out),0,1))):.0f} deg")
