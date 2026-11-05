# kaiju_tools: crust-test report data: tip, plates, trench, fault-in-slab, slab necking, the fixed dead/lock-up criteria
"""Data for the crust-test report (the hub for Louis, 2026-11-05): per case (TAf, Earth) and arm (control = the weak
production crust, passive = crust weak 0.9999, half = half-element crust), every complete checkpoint's model time, slab
tip depth (tip_depth.py), vrms, slip_max, the two plate speeds, trench angle and retreat rate, the fault-in-slab numbers
(analysis/fault_in_slab.py at 4f2fbaa: top and deep hot fractions of the built cut, gap in base cells), and the slab's
thickness along its length (the cold core, T < 0.5, measured normal to the slab's centreline at depths 0.15-0.9, for
necking). Then the fixed criteria: the dead criterion (the hub, 2026-11-05) and the lock-up check (Louis's definition;
ranges and thresholds fixed in advance). Writes crust_report.json. Run in the container."""
import glob
import json
import os
import subprocess

import h5py
import numpy as np

R = "/home/louis/+Claude/kaiju/runs"
FIS = "/home/louis/+Claude/kaiju/clones/zg95-v2-4f2fbaa/zg95_lid_regimes/analysis/fault_in_slab.py"
OUT = "/home/louis/+Claude/kaiju/movies/out/crust_report.json"
RUNS = {"TAf": {"control": "crust_TAf_c1", "passive": "crust_TAf_passive", "half": "crust_TAf_c05"},
        "Earth": {"control": "crust_earth_c1", "passive": "crust_earth_passive", "half": "crust_earth_c05"}}
LOCK = {"TAf": (0.50, 0.95, 221.0), "Earth": (0.40, 0.60, 113.0)}      # range and threshold, fixed in advance
BASE = 0.95
R_O = 2.2222222222222223


def complete(d, s):
    st = json.load(open(f"{d}/state_{s:05d}.json"))
    return all(os.path.exists(os.path.join(d, f)) for f in st.get("checkpoint_files", []))


def slab_profile(xy, T, theta_t):
    """The cold core's thickness against depth: at each depth, the angular width of T < 0.5 within 60 degrees of the
    trench, times the radius, then times sin(dip) from the centreline's local slope (thickness normal to the slab)."""
    r = np.hypot(xy[:, 0], xy[:, 1])
    depth = R_O - r
    dth = (np.arctan2(xy[:, 1], xy[:, 0]) - theta_t + np.pi) % (2 * np.pi) - np.pi
    near = np.abs(dth) < np.radians(60)
    cold = (T < 0.5) & near
    rows = []
    for d0 in np.arange(0.15, 0.91, 0.05):
        band = cold & (np.abs(depth - d0) < 0.0125)
        if band.sum() < 3:
            rows.append((float(d0), np.nan, np.nan))
            continue
        th = np.sort(dth[band])
        # the largest connected run of cold angles (gaps over 1.5 degrees split it): the slab, not a stray drip
        cuts = np.flatnonzero(np.diff(th) > np.radians(1.5))
        pieces = np.split(th, cuts + 1)
        p = max(pieces, key=len)
        rows.append((float(d0), float(np.mean(p)), float((p.max() - p.min()) * (R_O - d0))))
    rows = np.array(rows)
    # centreline slope -> local dip; thickness normal to the slab = horizontal width x sin(dip)
    x = rows[:, 1] * (R_O - rows[:, 0])
    out = []
    for i, (d0, c, w) in enumerate(rows):
        if not np.isfinite(w):
            out.append((d0, None))
            continue
        j0, j1 = max(i - 1, 0), min(i + 1, len(rows) - 1)
        dx = x[j1] - x[j0]
        dz = rows[j1, 0] - rows[j0, 0]
        dip = np.arctan2(dz, abs(dx)) if np.isfinite(dx) and dx != 0 else np.pi / 2
        out.append((d0, float(w * np.sin(dip))))
    return out


def series(d):
    recs = {r["step"]: r for r in json.load(open(f"{d}/records.json")) if "vrms" in r}
    rows = []
    for f in sorted(glob.glob(f"{d}/state_*.json")):
        s = int(f[-10:-5])
        if not complete(d, s) or s not in recs:
            continue
        st = json.load(open(f))
        with h5py.File(f"{d}/annulus.mesh.T.{s:05d}.h5", "r") as h:
            xy = h["fields/coordinates"][:]
            T = h["fields/T"][:].ravel()
        theta0 = float(st["params"]["uw_theta_trench"])
        r = np.hypot(xy[:, 0], xy[:, 1])
        depth = r.max() - r
        dth = (np.arctan2(xy[:, 1], xy[:, 0]) - theta0 + np.pi) % (2 * np.pi) - np.pi
        cold = (T < 0.5) & (depth > 0.14) & (np.abs(dth) < np.pi / 2)
        rec = recs[s]
        pl = list((rec.get("plates") or {}).values())
        try:
            fis = json.loads(subprocess.run(["python3", FIS, d, "--ckpt", str(s), "--json", "--top", "0.09"],
                                            capture_output=True, text=True).stdout.strip().split("\n")[-1])
        except Exception:
            fis = {}
        rows.append({"step": s, "t": st["t"], "tip": float(depth[cold].max()) if cold.any() else None,
                     "vrms": rec["vrms"], "slip_max": rec.get("slip_max"),
                     "plate_sub": pl[0][0] if pl else None, "plate_over": pl[0][1] if pl else None,
                     "trench_deg": float(np.degrees(rec["theta_trench"])),
                     "fis_top": fis.get("built_hot_top_max"), "fis_deep": fis.get("built_hot_deep_max"),
                     "fis_gap_cells": fis.get("gap_cells_max"),
                     "profile": slab_profile(xy, T, float(rec["theta_trench"]))})
    t = np.array([x["t"] for x in rows])
    th = np.radians(np.array([x["trench_deg"] for x in rows])) * R_O
    tip = np.array([x["tip"] for x in rows], dtype=float)
    retreat = -np.gradient(th, t)
    descent = np.gradient(tip, t)
    for x, a, b in zip(rows, retreat, descent):
        x["retreat_rate"] = float(a)
        x["descent_rate"] = float(b)
    return rows


def at_depth(rows, key, dep):
    tip = np.array([x["tip"] for x in rows], dtype=float)
    v = np.array([x[key] for x in rows], dtype=float)
    if np.nanmax(tip) < dep:
        return None
    return float(np.interp(dep, tip, v))


report = {}
for case, arms in RUNS.items():
    data = {arm: series(f"{R}/{d}") for arm, d in arms.items()}
    C = data["control"]
    k = next(i for i, x in enumerate(C) if x["tip"] >= BASE)
    t_base_c = C[k]["t"]
    crit = {"control_base_t": t_base_c, "limit_t": 3 * t_base_c}
    for arm in ("passive", "half"):
        X = data[arm]
        kb = next((i for i, x in enumerate(X) if x["tip"] is not None and x["tip"] >= BASE), None)
        crit[f"{arm}_base_t"] = X[kb]["t"] if kb is not None else None
        crit[f"{arm}_base_ratio"] = X[kb]["t"] / t_base_c if kb is not None else None
        lo, hi, thr = LOCK[case]
        t_lo, t_hi = at_depth(X, "t", lo), at_depth(X, "t", min(hi, max(x["tip"] for x in X)))
        th_lo, th_hi = at_depth(X, "trench_deg", lo), at_depth(X, "trench_deg", min(hi, max(x["tip"] for x in X)))
        if t_lo is not None and t_hi is not None and t_hi > t_lo:
            mean_retreat = float(-np.radians(th_hi - th_lo) * R_O / (t_hi - t_lo))
        else:
            mean_retreat = None
        ct_lo, ct_hi = at_depth(C, "t", lo), at_depth(C, "t", hi)
        cth_lo, cth_hi = at_depth(C, "trench_deg", lo), at_depth(C, "trench_deg", hi)
        crit[f"{arm}_lock"] = {"range": [lo, hi], "threshold": thr, "mean_retreat": mean_retreat,
                               "control_mean_retreat": float(-np.radians(cth_hi - cth_lo) * R_O / (ct_hi - ct_lo)),
                               "locked": bool(mean_retreat is not None and abs(mean_retreat) < thr)}
    report[case] = {"data": data, "criteria": crit}
    print(case, json.dumps(crit, indent=1))
json.dump(report, open(OUT, "w"))
print("->", OUT)
