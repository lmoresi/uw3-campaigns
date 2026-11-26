"""UNFILED 84 mechanism: are the apex wedge cells (all three vertices on the split chain) carried
as a rigid block, and is the slip high near them, against the same trace on a 4x finer mesh?
    python wedge84.py <box_irr|box_reg> <DS> <trace>"""
import sys, os, warnings
import numpy as np
warnings.simplefilter("ignore")
mk, ds, want = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", mk, ds, "kinks"]
g = {}
exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
uw, h, lc = g["uw"], g["h"], g["lc"]
import sympy
from underworld3.utilities.fault_contact import fault_pair_jumps
from underworld3.utilities._plex_topology import closure_points
from underworld3.utilities.fault_split import _turns
Q = [q for t, q in g["traces"]() if t == want][0]
apex = Q[int(np.flatnonzero(_turns(Q))[0])]
seg = np.diff(Q, axis=0); sl = np.linalg.norm(seg, axis=1); cum = np.concatenate([[0], np.cumsum(sl)])
def arc(p):
    u = np.clip(((p - Q[:-1]) * seg).sum(1) / sl**2, 0, 1); d = np.linalg.norm(Q[:-1] + u[:, None] * seg - p, axis=1); i = int(np.argmin(d)); return cum[i] + u[i] * sl[i]
s_apex = arc(apex)
def run(mesh):
    m2 = mesh.add_fault(("F", Q))
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
    coords, jumps, _n = fault_pair_jumps(st, "F", st._rotated_freeslip_info)
    s = np.array([arc(p) for p in coords]); slip = np.linalg.norm(jumps, axis=1)
    return m2, st, s, slip
m12, st12, s12, v12 = run(g["mesh"])
fine = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h / 4, regular=(mk == "box_reg"))
m48, st48, s48, v48 = run(fine)
o = np.argsort(s48); ref = np.interp(s12, s48[o], v48[o])
ratio = v12 / np.maximum(ref, 1e-12)
k = int(np.argmax(v12))
print(f"W {want} {mk} {ds}: max slip 12 {v12.max():.5f} at {abs(s12[k]-s_apex)/h:.2f} cells from the apex; max slip 48 {v48.max():.5f} at {abs(s48[np.argmax(v48)]-s_apex)/h:.2f} cells")
for band in ((0, 1), (1, 2), (2, 3), (3, 99)):
    sel = (np.abs(s12 - s_apex) / h >= band[0]) & (np.abs(s12 - s_apex) / h < band[1])
    if sel.any(): print(f"W   pairs {band[0]}-{band[1]} cells from the apex: n {int(sel.sum())}, slip 12/48 median {np.median(ratio[sel]):.3f} max {ratio[sel].max():.3f}")
# wedge cells: all three vertices on the fault (either side)
dm = m12.dm; X = lc._coords(dm); vS, _ = dm.getDepthStratum(0); eS, _ = dm.getDepthStratum(1); ends = lc._edge_vertices(dm)
fv = set()
for b in m12.boundaries:
    if b.name in ("F", "FPlus", "FMinus") and dm.getLabel(b.name).getStratumSize(b.value):
        e = np.asarray(dm.getLabel(b.name).getStratumIS(b.value).getIndices()) - eS; e = e[(e >= 0) & (e < len(ends))]
        fv |= set(ends[e].ravel().tolist())
cS, cE = dm.getHeightStratum(0); C = closure_points(dm, np.arange(cS, cE), 0) - vS
wedge = np.array([all(v in fv for v in c) for c in C])
cent = X[C].mean(axis=1)
u = st12.u.sym; G = u.jacobian(m12.X); E = (G + G.T) / 2
inv = sympy.sqrt(E[0, 0]**2 + E[1, 1]**2 + 2 * E[0, 1]**2)
e = np.asarray(uw.function.evaluate(inv, cent)).reshape(-1)
d_apex = np.linalg.norm(cent - apex, axis=1) / h
near = (d_apex < 2) & ~wedge
print(f"W   wedge cells {int(wedge.sum())} at {np.round(d_apex[wedge], 2).tolist()} cells from the apex")
print(f"W   strain rate: wedge cells {np.round(e[wedge], 3).tolist()}; other cells within 2 cells of the apex median {np.median(e[near]):.3f}; all cells median {np.median(e):.3f}")
