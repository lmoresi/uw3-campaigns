"""UNFILED 22, end to end: add_fault on random traces sampled finer than the mesh, forward and
reversed. Outcome per cut: raised, empty (no fault facet), partial (the fault chain is more than
half a cell from some point of the trace), or complete. RULE: dev | thin (tips, turns > 45 deg,
samples >= 1 cell apart) | corners (tips, turns > 45 deg).

    RULE=... python hunt2.py <mesh> <n traces> <seed>"""
import os, sys, warnings
import numpy as np
mesh_kind, ntr, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sys.argv = sys.argv[:1]
RULE = os.environ.get("RULE", "dev")
if RULE == "thin":
    os.environ["THIN"] = "1.0"
elif RULE == "corners":
    os.environ["THIN"] = "0"
import underworld3 as uw
if RULE != "dev":
    import corners_plugin  # noqa: patches add_fault's pull
warnings.simplefilter("ignore")
exec(open("hunt.py").read().split("counts = {")[0].split("warnings.simplefilter(\"ignore\")")[1])

def seg_dist(P, A, B):
    best = np.full(len(P), np.inf)
    for a, b in zip(A, B):
        e = b - a; L = e @ e
        u = np.clip(((P - a) @ e) / L, 0, 1) if L > 0 else np.zeros(len(P))
        best = np.minimum(best, np.linalg.norm(P - (a + u[:, None] * e), axis=1))
    return best

out = {"raised": 0, "empty": 0, "partial": 0, "complete": 0}
H_all, Hm_all, reasons = [], [], {}
for k in range(ntr):
    P = trace()
    for Q in (P, P[::-1].copy()):
        try:
            m2 = mesh.add_fault(("F", Q))
        except Exception as e:
            out["raised"] += 1
            r = str(e)[:50]; reasons[r] = reasons.get(r, 0) + 1
            continue
        dm = m2.dm
        b = [bb for bb in m2.boundaries if bb.name == "F"][0]
        lab = dm.getLabel("F")
        n = lab.getStratumSize(b.value) if lab is not None and lab.handle else 0
        if n == 0:
            out["empty"] += 1; continue
        vS, _ = dm.getDepthStratum(0)
        X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
        E = lab.getStratumIS(b.value).getIndices()
        ends = np.array([dm.getCone(int(e)) for e in E]) - vS
        t = np.linspace(0, 1, 11)
        dense = np.vstack([Q[:-1] + s * (Q[1:] - Q[:-1]) for s in t] + [Q[-1:]])
        a = seg_dist(dense, X[ends[:, 0]], X[ends[:, 1]])
        c = seg_dist(X[np.unique(ends.ravel())], Q[:-1], Q[1:])
        H = max(a.max(), c.max()) / h
        H_all.append(H); Hm_all.append(a.mean() / h)
        out["partial" if a.max() > 0.5 * h else "complete"] += 1
H = np.array(H_all or [np.nan]); Hm = np.array(Hm_all or [np.nan])
print(f"HUNT2 {RULE} {mesh_kind}: {out}; trace-to-fault Hausdorff/h max {np.nanmax(H):.3f} median {np.nanmedian(H):.3f}; "
      f"mean distance/h median {np.nanmedian(Hm):.3f}", flush=True)
print(f"HUNT2REASONS {RULE} {mesh_kind}: {reasons}", flush=True)
