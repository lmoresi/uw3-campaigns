"""116 checks: each point placed with the experiment off, then on; compared."""
import argparse, os
import numpy as np
import underworld3 as uw
import underworld3.utilities.place_surface as ps

ap = argparse.ArgumentParser()
ap.add_argument("--dip", type=float); ap.add_argument("--cellsize", type=float, default=0.05)
ap.add_argument("--k", type=str); ap.add_argument("--snap", default="0.5"); ap.add_argument("--cap", default="0.25")
a = ap.parse_args()
k0, k1, dk = (float(x) for x in a.k.split(":"))
h = a.cellsize / 2
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=a.cellsize, refinement=1, qdegree=2)
bX = base.dm.getCoordinatesLocal().array.reshape(-1, 2)
W = bX[np.linalg.norm(bX, axis=1) > 1 - 1e-9]; W = W[np.argsort(np.arctan2(W[:, 1], W[:, 0]))]
edges = [(i, (i + 1) % len(W)) for i in range(len(W))]
th, dip = np.radians(90), np.radians(a.dip)
r = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r
log = os.path.expanduser("~/+Simulations/unfiled116/checks/moves.tmp")


def run(k, on):
    os.environ["UW_EXP_SNAP"] = a.snap if on else "0"
    os.environ["UW_EXP_CAP_CELLS"] = a.cap if on else "0"
    os.environ["UW_EXP_MARGIN_ROWS"] = "2"
    os.environ["UW_EXP_SNAP_LOG"] = log
    open(log, "w").close()
    trace = (1 - k * h) * r + (h * np.arange(7))[:, None] * d
    try:
        mesh, info = ps.place_fault_ribbon_2d(base, [("F", trace)], 2 * h, margin_rings=2, clearance=0.3,
                                              split=True, mesher="ladder")
    except Exception as e:
        return {"out": "REFUSED " + str(e)[:70]}
    dm = mesh.dm; vS, vE = dm.getDepthStratum(0); eS, eE = dm.getDepthStratum(1); cS, cE = dm.getHeightStratum(0)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    up = [b for b in mesh.boundaries if b.name == "Upper"][0]
    unl, wallv = 0, set()
    for e in range(eS, eE):
        if dm.getSupportSize(e) != 1: continue
        v = [int(q) - vS for q in dm.getCone(e)]
        if (np.linalg.norm(X[v], axis=1) > 1 - 2e-4).all():
            wallv.update(v)
            unl += dm.getLabel("Upper").getValue(e) != up.value
    wv = np.array(sorted(wallv))
    off = float(ps._segments_distance(X[wv], W, edges).max())
    fault = {}
    short = np.inf
    b_ = [bb for bb in mesh.boundaries if bb.name == "FPlus"][0]
    for p in dm.getLabel("FPlus").getStratumIS(b_.value).getIndices():
        if eS <= int(p) < eE:
            vv = [int(q) - vS for q in dm.getCone(int(p))]
            short = min(short, float(np.linalg.norm(X[vv[0]] - X[vv[1]])) / h)
    for side in ("FPlus", "FMinus"):
        b = [bb for bb in mesh.boundaries if bb.name == side][0]
        pts = dm.getLabel(side).getStratumIS(b.value).getIndices()
        vs = sorted({int(q) - vS for p in pts for q in dm.getTransitiveClosure(int(p))[0] if vS <= q < vE})
        fault[side] = np.array(sorted(map(tuple, np.round(X[vs], 14))))
    band = np.asarray(info["band"]); onwall = 0; amin = 180
    for c in range(cS, cE):
        cl = dm.getTransitiveClosure(c)[0]; P = X[cl[(cl >= vS) & (cl < vE)] - vS]
        amin = min(amin, min(np.degrees(np.arccos(np.clip((P[(i+1)%3]-P[i]) @ (P[(i+2)%3]-P[i]) / np.linalg.norm(P[(i+1)%3]-P[i]) / np.linalg.norm(P[(i+2)%3]-P[i]), -1, 1))) for i in range(3)))
        if band[c - cS] and (np.linalg.norm(P, axis=1) > 1 - 1e-6).any(): onwall += 1
    moves = [float(x) for x in open(log).read().split()]
    Pn = fault["FPlus"]
    off_trace = float(ps._segments_distance(Pn, trace, [(i, i + 1) for i in range(len(trace) - 1)]).max()) if len(Pn) else np.nan
    paired = fault["FPlus"].shape == fault["FMinus"].shape and np.array_equal(fault["FPlus"], fault["FMinus"])
    return {"out": "outcrop" if onwall else "interior", "unl": unl, "off": off, "fault": fault,
            "amin": amin, "X": np.array(sorted(map(tuple, X))), "move": max(moves, default=0.0),
            "off_trace": off_trace, "paired": paired, "nfault": len(Pn), "short": short}


for k in np.arange(k0, k1, dk):
    A, B = run(k, False), run(k, True)
    if "fault" in A and "fault" in B:
        same_fault = all(A["fault"][s].shape == B["fault"][s].shape and np.array_equal(A["fault"][s], B["fault"][s]) for s in A["fault"])
        bit = A["X"].shape == B["X"].shape and np.array_equal(A["X"], B["X"])
        print(f"k {k:4.2f} | {A['out']:8s} -> {B['out']:8s} | angle {A['amin']:5.1f} -> {B['amin']:5.1f} | "
              f"fault same {same_fault} | mesh bit-identical {bit} | wall off {B['off']:.1e} unlabelled {B['unl']} | "
              f"snap move {B['move']:.3f} cells | fault nodes {A['nfault']}->{B['nfault']}, "
              f"off trace {B['off_trace']:.1e}, paired {A['paired']}/{B['paired']}, "
              f"shortest fault edge {A['short']:.2f}->{B['short']:.2f} cells", flush=True)
    else:
        print(f"k {k:4.2f} | {A['out'][:40]} -> {B['out'][:40]}", flush=True)
