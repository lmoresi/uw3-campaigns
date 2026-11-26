import sys, numpy as np, warnings
warnings.simplefilter("ignore")
sys.argv = ["x", "box_irr", "0.3", "kinks"]
exec(open("pull22.py").read().split("for n, (tag, Q) in enumerate(traces()):")[0])
from underworld3.utilities import line_cut as lc
from underworld3.utilities.fault_split import _in_pull_order, _turns
from underworld3.utilities._plex_topology import closure_points
def cells(dm):
    cS, cE = dm.getHeightStratum(0); vS, _ = dm.getDepthStratum(0); X = lc._coords(dm)
    idx = closure_points(dm, np.arange(cS, cE), 0) - vS; P = X[idx]
    ang = []
    for k in range(3):
        a = P[:, (k + 1) % 3] - P[:, k]; b = P[:, (k + 2) % 3] - P[:, k]
        ang.append(np.degrees(np.arccos(np.clip((a * b).sum(1) / np.linalg.norm(a, axis=1) / np.linalg.norm(b, axis=1), -1, 1))))
    return X, idx, np.min(ang, axis=0)
for tag, Q in traces():
    if tag != "kink90_9": continue
    t = int(np.flatnonzero(_turns(Q))[0]); print(f"K9 samples {len(Q)}, turn at {t}, turn angle", np.round(np.degrees(np.arccos(np.clip(((Q[t]-Q[t-1])@(Q[t+1]-Q[t]))/np.linalg.norm(Q[t]-Q[t-1])/np.linalg.norm(Q[t+1]-Q[t]),-1,1))),1))
    X0 = lc._coords(mesh.dm)
    for name, order in (("0006", np.vstack([Q[1:-1], Q[[0, -1]]])), ("0007", _in_pull_order(Q))):
        dm = lc.pull_vertex_onto(mesh.dm, order, on_shared="note")
        Xp = lc._coords(dm)
        has = [bool(np.any(np.all(Xp == q, axis=1))) for q in Q]
        moved_pull = int((np.abs(Xp - X0) > 0).any(axis=1).sum())
        cut, info = lc.cut_along_lines(dm, [Q], label="F", label_value=7)
        X, idx, amin = cells(cut)
        near = np.linalg.norm(X[idx].mean(axis=1) - Q[t], axis=1) < 1.5 * h
        Xa, ia, ap = cells(dm)
        near_p = np.linalg.norm(Xa[ia].mean(axis=1) - Q[t], axis=1) < 1.5 * h
        print(f"K9 {name}: samples with a vertex {[i for i,x in enumerate(has) if x]}; vertices moved by the pull {moved_pull}")
        print(f"K9 {name}: smallest angle near the turn (1.5 cells): after pull {ap[near_p].min():.1f} deg, after cut {amin[near].min():.1f} deg; whole mesh after cut {amin.min():.1f} deg; cells under 15 deg near the turn {int((amin[near] < 15).sum())}")
        bp = np.flatnonzero(np.all(Xp == Q[t], axis=1))
        if bp.size:
            v = int(bp[0]); print(f"K9 {name}: the turn's vertex moved by the pull {np.linalg.norm(Xp[v]-X0[v])/h:.3f} cells")
