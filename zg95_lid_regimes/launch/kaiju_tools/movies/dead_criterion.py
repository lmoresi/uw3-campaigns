# kaiju_tools: the dead-slab criterion's numbers from the controls (2026-11-05)
"""The dead-slab criterion's numbers from the controls (the hub for Louis, 2026-11-05): per case, the control's slab tip
depth and subducting-plate speed against model time, its time to the base (tip 0.95, tip_depth.py's definition), its
descent rate at matched depths and its time from each depth to the base; the passive arm's progress so far, matched by
depth. Run in the container: python3 dead_criterion.py"""
import glob
import json
import os

import h5py
import numpy as np

R = "/home/louis/+Claude/kaiju/runs"
CASES = {"TAf": ("crust_TAf_c1", "slab_thermal_fault_TAf_v2_c", "crust_TAf_passive"),
         "Earth": ("crust_earth_c1", "slab_earth_run2_c", "crust_earth_passive")}
BASE = 0.95


def complete(d, s):
    st = json.load(open(f"{d}/state_{s:05d}.json"))
    return all(os.path.exists(os.path.join(d, f)) for f in st.get("checkpoint_files", []))


def tip_series(d):
    out = []
    recs = {r["step"]: r for r in json.load(open(f"{d}/records.json")) if "vrms" in r}
    for f in sorted(glob.glob(f"{d}/state_*.json")):
        s = int(f[-10:-5])
        if not complete(d, s):
            continue
        st = json.load(open(f))
        with h5py.File(f"{d}/annulus.mesh.T.{s:05d}.h5", "r") as h:
            xy = h["fields/coordinates"][:]
            T = h["fields/T"][:].ravel()
        r = np.hypot(xy[:, 0], xy[:, 1])
        depth = r.max() - r
        dth = (np.arctan2(xy[:, 1], xy[:, 0]) - float(st["params"]["uw_theta_trench"]) + np.pi) % (2 * np.pi) - np.pi
        cold = (T < 0.5) & (depth > 0.14) & (np.abs(dth) < np.pi / 2)
        rec = recs.get(s, {})
        pl = list((rec.get("plates") or {}).values())
        out.append((s, st["t"], float(depth[cold].max()) if cold.any() else np.nan, pl[0][0] if pl else np.nan))
    return np.array(out)


for case, (ctl, prod, pas) in CASES.items():
    C = tip_series(f"{R}/{ctl}")
    P = tip_series(f"{R}/{prod}")
    X = tip_series(f"{R}/{pas}")
    src, S = (ctl, C) if (C[:, 2] >= BASE).any() else (prod + " (the control has not reached the base: production used)", P)
    k = int(np.argmax(S[:, 2] >= BASE))
    t_base = S[k, 1]
    print(f"== {case}: control {src}; base (tip >= {BASE}) at checkpoint {int(S[k,0])}, t {t_base:.3e}; "
          f"3x limit t {3*t_base:.3e}")
    print("   depth | control t, descent rate d(tip)/dt, plate | time from here to base | 10% thresholds (rate, plate) "
          "| passive t at this depth (ratio)")
    for dep in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        if dep > S[:k + 1, 2].max():
            continue
        tc = float(np.interp(dep, S[:k + 1, 2], S[:k + 1, 1]))
        j = int(np.searchsorted(S[:, 1], tc))
        j = min(max(j, 1), len(S) - 1)
        rate = (S[j, 2] - S[j - 1, 2]) / (S[j, 1] - S[j - 1, 1])
        plate = float(np.interp(tc, S[:, 1], S[:, 3]))
        xt = float(np.interp(dep, X[:, 2], X[:, 1])) if X[:, 2].max() >= dep else np.nan
        print(f"   {dep:.1f}   | t {tc:.3e}, rate {rate:7.0f}, plate {plate:5.0f} | {t_base - tc:.3e} | "
              f"{0.1*rate:6.0f}, {0.1*plate:5.0f} | " + (f"t {xt:.3e} ({xt/tc:.2f}x)" if np.isfinite(xt) else "not yet"))
    print(f"   passive so far: checkpoint {int(X[-1,0])}, t {X[-1,1]:.3e}, tip {X[-1,2]:.3f}, plate {X[-1,3]:.0f}")
