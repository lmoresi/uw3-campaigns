"""Row 30 in 3-D: a creased sheet fault (two planar facets meeting along a line parallel to x at
the given turn), default constraint against a probe patch holding the jump along both sheets'
normals at crease vertices (slip free along the crease).
    python crease.py <turn deg> <cellSize> [modes]"""
import sys, json, time, warnings
import numpy as np
warnings.simplefilter("ignore")
turn, cs = float(sys.argv[1]), float(sys.argv[2])
modes = sys.argv[3].split(",") if len(sys.argv) > 3 else ["base", "pin"]
import underworld3 as uw
from underworld3.utilities import rotated_bc as rb, fault_contact as fc
from petsc4py import PETSc
C0 = np.array([0.5, 0.5, 0.5]); X1 = 0.25; W = 0.25; HS = 0.03       # crease half-length, facet width, sheet spacing
th = np.radians(turn)
dA = np.array([0.0, -1.0, 0.0])                                       # facet A runs from the crease towards -y
dB = np.array([0.0, np.cos(th), np.sin(th)])                          # facet B turned by `turn` out of A's plane
xs = np.linspace(C0[0] - X1, C0[0] + X1, int(round(2 * X1 / HS)) + 1)
ws = np.linspace(0.0, W, int(round(W / HS)) + 1)
pts, idx = [], {}
for f, d in ((0, dA), (1, dB)):
    for j, w in enumerate(ws):
        for i, x in enumerate(xs):
            key = (i, 0) if j == 0 else (i, f, j)
            if key not in idx:
                idx[key] = len(pts); pts.append(C0 + np.array([x - C0[0], 0, 0]) + w * d)
tris = []
for f in (0, 1):
    for j in range(len(ws) - 1):
        for i in range(len(xs) - 1):
            g = lambda ii, jj: idx[(ii, 0)] if jj == 0 else idx[(ii, f, jj)]
            a, b, c, e = g(i, j), g(i + 1, j), g(i + 1, j + 1), g(i, j + 1)
            rim = lambda ii, jj: ii in (0, len(xs) - 1) or jj == len(ws) - 1
            ra, rb_, rc, re = rim(i, j), rim(i + 1, j), rim(i + 1, j + 1), rim(i, j + 1)
            # the diagonal that leaves no all-rim triangle
            if (ra and rc and re) or (ra and rb_ and rc):
                tris += [(a, b, e), (b, c, e)]
            else:
                tris += [(a, b, c), (a, c, e)]
pts = np.array(pts); tris = np.array(tris)
nA = np.cross([1, 0, 0], dA); nB = np.cross([1, 0, 0], dB)
nA /= np.linalg.norm(nA); nB /= np.linalg.norm(nB)
cdir = np.array([1.0, 0.0, 0.0])
STATE = {"on": False}
_orig = rb.build_rotation
def _on_crease(x):
    r = x - C0; r_perp = r - (r @ cdir) * cdir
    return np.linalg.norm(r_perp) < 1e-6 and abs(r @ cdir) < X1 + 1e-9
def _pinned(solver, boundaries, datum_specs=None):
    Q, Qt, rows, datum = _orig(solver, boundaries, datum_specs)
    if not STATE["on"]:
        return Q, Qt, rows, datum
    dm = solver.dm; dim = 3; lsec = dm.getLocalSection(); l2g = dm.getLGMap()
    csec = dm.getCoordinateSection(); cvec = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dim)
    v0, v1 = dm.getDepthStratum(0); s2 = 1.0 / np.sqrt(2.0); extra = []
    for fname in getattr(solver, "_fault_contact_faults", []):
        for q_plus, q_minus, nrm in fc._fault_pair_nodes(solver, fname):
            x = np.asarray(rb._point_coord(dm, dim, cvec, csec, v0, v1, q_minus), dtype=float)
            if not _on_crease(x): continue
            n = np.asarray(nrm, dtype=float).ravel(); n /= np.linalg.norm(n)
            w = np.cross(n, cdir); w /= np.linalg.norm(w)
            frame = [n, w, cdir]
            gp = [int(l2g.apply([lsec.getFieldOffset(q_plus, 0) + c])[0]) for c in range(dim)]
            gm = [int(l2g.apply([lsec.getFieldOffset(q_minus, 0) + c])[0]) for c in range(dim)]
            for i, e in enumerate(frame):
                for row, sgn in ((gp[i], 1.0), (gm[i], -1.0)):
                    for j in range(dim):
                        Q.setValue(row, gp[j], s2 * e[j]); Q.setValue(row, gm[j], sgn * s2 * e[j])
            extra.append(gm[1])
    Q.assemble(); Qt = Q.transpose(PETSc.Mat())
    STATE["pinned"] = len(extra)
    return Q, Qt, sorted(set(rows) | set(extra)), datum
rb.build_rotation = _pinned
t0 = time.time()
box = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0,) * 3, maxCoords=(1.0,) * 3, cellSize=cs, regular=False, qdegree=2)
m2 = box.add_fault([("FC", pts, tris)])
t_build = time.time() - t0
for mode in modes:
    STATE["on"] = mode == "pin"
    st = uw.systems.Stokes(m2); st.constitutive_model = uw.constitutive_models.ViscousFlowModel
    st.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    for wall in ("Bottom", "Top", "Right", "Left", "Front", "Back"):
        st.add_dirichlet_bc((0.0, m2.X[2] - 0.5, 0.0), wall)
    st.petsc_use_pressure_nullspace = True; st.tolerance = 1e-8
    st.add_fault_bc(0, "FC")
    t1 = time.time(); st.solve(); info = st._rotated_freeslip_info
    coords, jumps, normals = fc.fault_pair_jumps(st, "FC", info)
    on = np.array([_on_crease(x) for x in coords])
    r = coords - C0; dist = np.linalg.norm(r - np.outer(r @ cdir, cdir), axis=1)
    inside = np.abs(r @ cdir) < X1 - 2 * cs                          # away from the crease ends
    slip = np.linalg.norm(jumps, axis=1)
    band = inside & (np.abs(dist - cs) < 0.25 * cs)
    rec = dict(turn=turn, cellSize=cs, mode=mode, cells=int(m2.dm.getHeightStratum(0)[1] - m2.dm.getHeightStratum(0)[0]),
               crease_pairs=int(on.sum()), pinned=STATE.get("pinned") if mode == "pin" else None,
               crease_open_A=float(np.abs(jumps[on] @ nA).max()) if on.any() else None,
               crease_open_B=float(np.abs(jumps[on] @ nB).max()) if on.any() else None,
               crease_slip=float(slip[on & inside].max()) if (on & inside).any() else None,
               max=float(slip[inside].max()), one_cell=float(np.median(slip[band])) if band.any() else None,
               vel=max(info.get("vel_its_last") or [0]), outer=info.get("ksp_its"), converged=bool(info.get("converged")),
               t_build=round(t_build, 1), t_solve=round(time.time() - t1, 1))
    print("CR " + json.dumps(rec), flush=True)
