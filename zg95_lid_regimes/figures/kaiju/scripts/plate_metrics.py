"""Per-checkpoint plate and slab metrics for the faulted thermal set and its references, from the checkpointed
base fields alone (h5py; no underworld3). For every checkpoint of each run:

  trench      the angle (deg, from the initial trench) within +-25 deg of it where the surface tangential velocity
              drops most steeply (the convergence)
  v_plate     the median tangential surface speed over the subducting plate: from 170 deg behind the trench to
              5 deg short of it
  v_near      slab_metrics' v_plate: the surface speed 0.15 d behind the hinge (near the trench, the plate's fastest
              part; the number the earlier thermal reports quoted)
  P10         plateness: the fraction of that plate surface whose speed is within 10 % of v_plate
  med/max     plateness: v_plate over the largest speed on that plate surface
  hinge       slab_metrics' hinge: the mean angle of the cold (T < 0.5) band 0.14-0.19 deep within 90 deg of the
              initial trench (deg)
  tip         slab_metrics' tip: the deepest cold point below 0.14 within 90 deg (the P2 nodes; 0.95 = on the base)

With a continent (the over marker on the crust swarm, annulus.crust_swarm.over.<n>.h5), the surface is also split
into arcs, each with its signed median tangential velocity (v, positive toward +angle), P10 and med/max:

  ocean_in    the incoming oceanic plate: as v_plate, from 170 deg behind the trench to 5 deg short of it
  ocean_fore  the oceanic strip between the trench and the continent: 5 deg past the trench to 2 deg short of the
              continent's trench-side edge
  continent   the continent: 2 deg inside its edges (the over-marked particles shallower than 0.05, 0.1 % and
              99.9 % quantiles of their angle on the overriding side)

The whole-surface columns stay as they were, for comparison with the thermal set. "Surface" is the P2 velocity
nodes within 0.5 h of the outer wall. Angles run so that the subducting plate is at
negative angles (the slab state's convention, uw_dip < 90). Writes <out>/plate_metrics.json and prints a table.
    python3 plate_metrics.py <out dir> <run dir> [<run dir> ...]
"""
import glob
import json
import os
import re
import sys

import h5py
import numpy as np


def field(path, name):
    with h5py.File(path) as h:
        return h["fields/coordinates"][:], h[f"fields/{name}"][:]


def metrics(run, n, theta_t, h):
    xy, V = field(os.path.join(run, f"annulus.mesh.V.{n:05d}.h5"), "V")
    V = V.reshape(len(xy), -1)
    r = np.hypot(xy[:, 0], xy[:, 1])
    r_o = r.max()
    th = (np.arctan2(xy[:, 1], xy[:, 0]) - theta_t + np.pi) % (2 * np.pi) - np.pi
    vt = (-V[:, 0] * xy[:, 1] + V[:, 1] * xy[:, 0]) / r
    surf = r > r_o - 0.5 * h
    o = np.argsort(th[surf])
    ts, vs = np.degrees(th[surf][o]), vt[surf][o]
    # the trench: steepest drop of the surface tangential velocity near the initial trench
    near = np.abs(ts) < 25
    dv = np.gradient(vs, ts)
    trench = float(ts[near][np.argmin(dv[near])]) if near.any() else 0.0
    plate = (ts > trench - 170) & (ts < trench - 5)
    speed = np.abs(vs[plate])
    v_plate = float(np.median(speed))
    p10 = float(np.mean(np.abs(speed - v_plate) <= 0.1 * v_plate))
    medmax = float(v_plate / speed.max())
    xyT, T = field(os.path.join(run, f"annulus.mesh.T.{n:05d}.h5"), "T")
    T = T.ravel()
    rT = np.hypot(xyT[:, 0], xyT[:, 1])
    dT = rT.max() - rT
    thT = np.degrees((np.arctan2(xyT[:, 1], xyT[:, 0]) - theta_t + np.pi) % (2 * np.pi) - np.pi)
    cold = (T < 0.5) & (np.abs(thT) < 90)
    band = cold & (dT >= 0.14) & (dT < 0.19)
    hinge = float(np.mean(thT[band])) if band.any() else float("nan")
    deep = cold & (dT > 0.14)
    tip = float(dT[deep].max()) if deep.any() else float("nan")
    v_near = float(abs(vs[np.argmin(np.abs(ts - (hinge - np.degrees(0.15 / r_o))))])) if np.isfinite(hinge) else float("nan")
    out = {"trench": trench, "v_plate": v_plate, "v_near": v_near, "P10": p10, "med_max": medmax, "hinge": hinge,
           "tip": tip}
    edges = continent_edges(run, n, theta_t, r_o)
    if edges is not None:
        lo, hi = edges
        out["continent_edges"] = [lo, hi]
        for name, a, b in (("ocean_in", trench - 170, trench - 5), ("ocean_fore", trench + 5, lo - 2),
                           ("continent", lo + 2, hi - 2)):
            sel = (ts > a) & (ts < b)
            out[name] = arc_stats(vs[sel]) if sel.sum() >= 5 else None
    return out


def arc_stats(v):
    """Signed median tangential velocity of an arc, and its plateness (P10, med/max) on the speeds."""
    med = float(np.median(v))
    sp = np.abs(v)
    return {"v": med, "P10": float(np.mean(np.abs(v - med) <= 0.1 * abs(med))) if med else 0.0,
            "med_max": float(abs(med) / sp.max()) if sp.max() > 0 else 0.0, "n": int(len(v))}


def continent_edges(run, n, theta_t, r_o):
    """The continent's edges (deg from the initial trench) from the over-marked particles shallower than 0.05 on the
    overriding side, or None without an over marker."""
    path = os.path.join(run, f"annulus.crust_swarm.over.{n:05d}.h5")
    if not os.path.exists(path):
        return None
    with h5py.File(os.path.join(run, f"annulus.crust_swarm.{n:05d}.h5")) as h:
        X = h["coordinates"][:]
    with h5py.File(path) as h:
        m = h["data"][:, 0]
    th = np.degrees((np.arctan2(X[:, 1], X[:, 0]) - theta_t + np.pi) % (2 * np.pi) - np.pi)
    sel = (m > 0.5) & (r_o - np.hypot(X[:, 0], X[:, 1]) < 0.05) & (th > 0)
    if sel.sum() < 10:
        return None
    return float(np.quantile(th[sel], 0.001)), float(np.quantile(th[sel], 0.999))


out_dir, runs = sys.argv[1], sys.argv[2:]
os.makedirs(out_dir, exist_ok=True)
res = {}
for run in runs:
    name = os.path.basename(run.rstrip("/")).replace("slab_", "")
    rows = []
    for sp in sorted(glob.glob(os.path.join(run, "state_[0-9]*.json"))):
        n = int(re.search(r"state_(\d+)\.json$", sp).group(1))
        if not os.path.exists(os.path.join(run, f"annulus.mesh.V.{n:05d}.h5")):
            continue
        s = json.load(open(sp))
        p = s["params"]
        h = float(p["uw_cell"]) / 2 ** int(p["uw_refinement"])
        m = metrics(run, n, float(p["uw_theta_trench"]), h)
        rows.append({"step": n, "t": s["t"], **m})
    for a, b in zip(rows[:-1], rows[1:]):        # hinge rate, deg per unit time (negative: toward the subducting plate)
        b["hinge_rate"] = (b["hinge"] - a["hinge"]) / max(b["t"] - a["t"], 1e-30)
    res[name] = rows
    print(f"== {name}")
    print("  step       t   trench  v_plate  v_near   P10  med/max   hinge     tip")
    for r in rows:
        print(f"  {r['step']:4d} {r['t']:.5f} {r['trench']:7.2f} {r['v_plate']:8.1f} {r['v_near']:7.1f} {r['P10']:.2f}   {r['med_max']:.2f}  "
              f"{r['hinge']:6.2f}  {r['tip']:.3f}")
        if "continent_edges" in r:
            arcs = "  ".join(f"{k} v {r[k]['v']:7.1f} P10 {r[k]['P10']:.2f} med/max {r[k]['med_max']:.2f}"
                             if r.get(k) else f"{k} -" for k in ("ocean_in", "ocean_fore", "continent"))
            print(f"         continent {r['continent_edges'][0]:6.2f}..{r['continent_edges'][1]:6.2f} deg  {arcs}")
with open(os.path.join(out_dir, "plate_metrics.json"), "w") as f:
    json.dump(res, f, indent=1)
