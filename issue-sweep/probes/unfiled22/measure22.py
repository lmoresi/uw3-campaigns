"""UNFILED 22, before building: (1) the distance between the user's polyline and the cut chain,
and (3a) how much of the mesh changes, under development's rule (every sample pulled) and the
thinned rule (tips, turns > 45 deg, samples >= THIN cells apart).

    python measure22.py <mesh> <n traces> <seed>"""
import sys, os, warnings, json
import numpy as np
mesh_kind, ntr, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sys.argv = sys.argv[:1]
import underworld3 as uw
from underworld3.utilities import line_cut as lc
import corners_plugin as cp
warnings.simplefilter("ignore")
exec(open("hunt.py").read().split("counts = {")[0].split("warnings.simplefilter(\"ignore\")")[1])  # mesh, h, rng, trace()

def seg_dist(P, A, B):
    """distance from points P to the segment set (A, B)"""
    best = np.full(len(P), np.inf)
    for a, b in zip(A, B):
        e = b - a; L = e @ e
        u = np.clip(((P - a) @ e) / L, 0, 1) if L > 0 else np.zeros(len(P))
        best = np.minimum(best, np.linalg.norm(P - (a + u[:, None] * e), axis=1))
    return best

def chain(dm):
    vS, _ = dm.getDepthStratum(0)
    X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dm.getCoordinateDim())
    lab = dm.getLabel(lc.CUT_LABEL)
    if lab is None or lab.handle == 0 or lab.getStratumSize(1) == 0:
        raise RuntimeError("no cut edges")
    E = lab.getStratumIS(1).getIndices()
    ends = np.array([dm.getCone(int(e)) for e in E]) - vS
    return X, ends

def cut(Q, rule):
    tg = Q if rule == "all" else cp.thinned(Q, mesh.dm)
    dm = cp._orig(mesh.dm, tg, on_shared="note")
    dm2, _info = lc.cut_along_lines(dm, [Q])
    return dm2

def hausdorff(Q, X, ends):
    t = np.linspace(0, 1, 21)[1:-1]
    dense = np.vstack([Q] + [Q[:-1] + s * (Q[1:] - Q[:-1]) for s in t])
    d_poly = seg_dist(dense, Q[:-1], Q[1:]) * 0           # (on the polyline by construction)
    a = seg_dist(dense, X[ends[:, 0]], X[ends[:, 1]])    # polyline -> chain
    cv = np.unique(ends.ravel())
    b = seg_dist(X[cv], Q[:-1], Q[1:])                   # chain -> polyline
    return max(a.max(), b.max()), a.mean()

rows = []
REASONS = {}
for k in range(ntr):
    Q = trace()
    res = {}
    for rule in ("all", "thin"):
        try:
            dm2 = cut(Q, rule)
            X, ends = chain(dm2)
            H, Hm = hausdorff(Q, X, ends)
            res[rule] = dict(H=H / h, Hm=Hm / h, ncell=int(dm2.getHeightStratum(0)[1]), X=X)
        except Exception as e:
            res[rule] = None
            REASONS.setdefault(rule, {}).setdefault(str(e)[:50], 0)
            REASONS[rule][str(e)[:50]] += 1
    if res["all"] is not None and res["thin"] is not None:
        Xa, Xt = res["all"]["X"], res["thin"]["X"]
        # vertices of the base mesh that end where they did not (moved by a pull) under each rule
        X0 = np.asarray(mesh.dm.getCoordinatesLocal().array).reshape(-1, 2)
        n0 = len(X0)
        moved_a = int((np.linalg.norm(Xa[:n0] - X0, axis=1) > 1e-12).sum())
        moved_t = int((np.linalg.norm(Xt[:n0] - X0, axis=1) > 1e-12).sum())
        same_cells = res["all"]["ncell"] == res["thin"]["ncell"]
        rows.append(dict(k=k, Ha=res["all"]["H"], Ht=res["thin"]["H"], Hma=res["all"]["Hm"], Hmt=res["thin"]["Hm"],
                         moved_a=moved_a, moved_t=moved_t, cells_a=res["all"]["ncell"], cells_t=res["thin"]["ncell"]))
    for rule in ("all", "thin"):
        if res[rule] is not None:
            rows.append(dict(k=k, rule=rule, H=res[rule]["H"], Hm=res[rule]["Hm"]))
both = [r for r in rows if "Ha" in r]
single = [r for r in rows if "rule" in r]
def stats(rule, key):
    v = np.array([r[key] for r in single if r["rule"] == rule]); return f"max {v.max():.3f} mean {v.mean():.3f} (n {len(v)})"
print(f"M22 {mesh_kind} THIN {cp.SPACING}: Hausdorff/h dev {stats('all','H')} | thin {stats('thin','H')}; "
      f"mean dist/h dev {stats('all','Hm')} | thin {stats('thin','Hm')}", flush=True)
print("REASONS", REASONS, flush=True)
if both:
    ma = np.array([r["moved_a"] for r in both]); mt = np.array([r["moved_t"] for r in both])
    dc = np.array([r["cells_t"] - r["cells_a"] for r in both])
    print(f"M22 {mesh_kind} traces placing under both: {len(both)}; vertices moved by pulls dev mean {ma.mean():.1f} "
          f"thin mean {mt.mean():.1f}; cell count differs in {(dc != 0).sum()} (range {dc.min()}..{dc.max()})", flush=True)
