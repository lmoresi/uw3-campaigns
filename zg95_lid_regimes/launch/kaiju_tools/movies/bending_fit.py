# kaiju_tools: offline bending-line fault fit to stored checkpoints, base/mid/top quantile (jobs 4088, 4089, 4093)
"""Offline prototype (Louis, 2026-11-06): the fault on a flexural bending line. For stored checkpoints, fit to the base of
the oceanic crust (the crust particles, the continent's excluded) a curve whose dip angle rises smoothly from 0 along the
incoming plate to a constant slab dip at depth,

    dip(s) = phi_slab * (1 + tanh((s - s_hinge) / w)) / 2,      s = arc length from a point on the incoming plate,

which starts flat at depth z0 (the crust base on the incoming plate, so it never meets the surface) and is integrated
along s. The base is the crust cloud's lower edge, so the fit is a quantile regression (the 10th percentile of signed
distance normal to the curve, as the envelope locator takes the 10th percentile), minimised by Nelder-Mead over
(s_hinge, w, phi_slab, z0). Each panel: temperature, crust particles, the current fault (the driver's envelope locator,
red), the bending-line fit (yellow) over the fault's depth range and its continuation (dashed). Fitted parameters per
checkpoint go to bending_fit.json, to see whether they evolve smoothly. Run in the container: python3 bending_fit.py"""
import json
import os

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

R = "/home/louis/+Claude/kaiju/runs"
OUT = "/home/louis/+Claude/kaiju/movies/out"
R_O = 2.2222222222222223
CAP = 0.15                      # the fault's depth cap (-uw_fault_depth_max)
FIT_DEPTH = 0.25                # crust used in the fit: to this depth (below the cap, so the slab dip is constrained)
U_FAR = 0.35                    # the curve starts this far along the incoming plate from the fault's trench
RUNS = [("Earth", "production crust (1 cell)", "slab_earth_run2_c", (10, 25, 40, 60, 80, 120)),
        ("Earth", "half-element crust", "crust_earth_c05", (10, 25, 40, 60, 80, 120)),
        ("Earth", "passive crust", "crust_earth_passive", (10, 25, 40, 60, 80, 120)),
        ("TAf", "production crust (1 cell)", "slab_thermal_fault_TAf_v2_c", (10, 25, 40, 55, 70, 85)),
        ("TAf", "half-element crust", "crust_TAf_c05", (10, 25, 40, 55, 70, 85)),
        ("TAf", "passive crust", "crust_TAf_passive", (10, 25, 40, 55, 70, 85))]
W_MIN, W_MAX = 0.02, 0.2        # hinge width bounds (layer depths; the base cell is 0.0156)
q = float(os.environ.get("BEND_Q", "0.10"))   # 0.10: the crust base (10 % below the curve); 0.90: the crust top
TAG = os.environ.get("BEND_TAG", "v2")


def curve(p, n=600):
    s_h, w, phi, z0 = p
    s = np.linspace(0.0, U_FAR + 0.6, n)
    dip = phi * 0.5 * (1.0 + np.tanh((s - s_h) / max(w, 1e-4)))
    ds = s[1] - s[0]
    u = U_FAR - np.concatenate([[0.0], np.cumsum(np.cos(dip[:-1]) * ds)])
    z = z0 + np.concatenate([[0.0], np.cumsum(np.sin(dip[:-1]) * ds)])
    return u, z, dip


def signed_distance(p, U, Z):
    u, z, dip = curve(p)
    tree = cKDTree(np.c_[u, z])
    d, i = tree.query(np.c_[U, Z])
    # the curve runs toward -u and down; its left normal (pointing up / toward the overriding side) is (sin dip, -cos dip)
    # in (u, z) with z down: positive distance = above the curve (shallower), i.e. inside the crust if the curve is its base
    nu, nz = -np.sin(dip[i]), -np.cos(dip[i])
    return (U - u[i]) * nu + (Z - z[i]) * nz


def pinball(r):
    return np.mean(np.maximum(q * r, (q - 1) * r))


def load(d, s):
    st = json.load(open(f"{R}/{d}/state_{s:05d}.json"))
    with h5py.File(f"{R}/{d}/annulus.crust_swarm.{s:05d}.h5", "r") as h:
        xy = h["coordinates"][:]
    with h5py.File(f"{R}/{d}/annulus.crust_swarm.crust.{s:05d}.h5", "r") as h:
        crust = h["data"][:].ravel() > 0.5
    over_f = f"{R}/{d}/annulus.crust_swarm.over.{s:05d}.h5"
    if os.path.exists(over_f):
        with h5py.File(over_f, "r") as h:
            crust &= ~(h["data"][:].ravel() > 0.5)
    with h5py.File(f"{R}/{d}/annulus.mesh.T.{s:05d}.h5", "r") as h:
        Txy = h["fields/coordinates"][:]
        T = h["fields/T"][:].ravel()
    f = st["faults"][0]
    return st, xy[crust], Txy, T, f


def frame(theta_f, side, xy):
    """(u, z): u the surface arc from the fault's trench, positive on the incoming plate; z depth."""
    th = np.arctan2(xy[:, 1], xy[:, 0])
    u = side * ((th - theta_f + np.pi) % (2 * np.pi) - np.pi) * R_O
    return u, R_O - np.hypot(xy[:, 0], xy[:, 1])


results = {}
for case in ("Earth", "TAf"):
    rows = [r for r in RUNS if r[0] == case]
    fig, axes = plt.subplots(len(rows), len(rows[0][3]), figsize=(4.6 * len(rows[0][3]), 4.4 * len(rows)), squeeze=False)
    for i, (_, label, d, ckpts) in enumerate(rows):
        prev = None
        for j, s in enumerate(ckpts):
            ax = axes[i, j]
            if not os.path.exists(f"{R}/{d}/state_{s:05d}.json"):
                ax.set_axis_off()
                continue
            st, P, Txy, T, f = load(d, s)
            theta_f = float(f["theta"])
            # the incoming plate is the side where the surface crust lies
            u0, z0 = frame(theta_f, 1.0, P)
            side = 1.0 if np.median(u0[(z0 < 0.02) & (np.abs(u0) > 0.05) & (np.abs(u0) < 0.5)]) > 0 else -1.0
            U, Z = frame(theta_f, side, P)
            sel = (Z <= FIT_DEPTH) & (U <= U_FAR) & (U >= -0.5)
            U, Z = U[sel], Z[sel]
            phi0 = np.radians(float(f.get("dip", 45.0)))
            phi0 = phi0 if phi0 < np.pi / 2 else np.pi - phi0
            ct = np.percentile(Z[U > 0.15], 90) if (U > 0.15).sum() > 10 else 0.0156
            guess = prev if prev is not None else (U_FAR - 0.02, 0.05, phi0, ct)
            # the hinge width bounded to [W_MIN, W_MAX] (a kink is not a bend; the passive TAf fit went to 0 unbounded)
            def obj(p):
                pen = 0.0 if W_MIN <= p[1] <= W_MAX else 1e3 * (min(abs(p[1] - W_MIN), abs(p[1] - W_MAX))) ** 2 + 1e-3
                return pinball(signed_distance(p, U, Z)) + pen
            g = np.array(guess, dtype=float)
            g[1] = np.clip(g[1], W_MIN, W_MAX)
            res = minimize(obj, g, method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-9, "maxiter": 4000})
            p = res.x
            prev = p
            results.setdefault(f"{case}/{label}", []).append(
                {"step": s, "t": st["t"], "s_hinge": float(p[0]), "w": float(p[1]), "phi_slab_deg": float(np.degrees(p[2])),
                 "z0": float(p[3]), "misfit": float(res.fun)})
            # draw: temperature, crust particles, current fault (red), bending line (yellow)
            Tu, Tz = frame(theta_f, side, Txy)
            k = (Tz < 0.26) & (Tu > -0.40) & (Tu < 0.30)
            ax.tricontourf(Tu[k], Tz[k], T[k], levels=np.linspace(0, 1, 21), cmap="RdBu_r")
            ax.scatter(U, Z, s=0.6, c="#145a32", linewidths=0)
            fp = np.asarray(f["points"])
            fu, fz = frame(theta_f, side, fp)
            ax.plot(fu, fz, color="#e74c3c", lw=1.6, label="current fault (envelope)")
            cu, cz, _ = curve(p)
            inside = cz <= CAP
            ax.plot(cu[inside], cz[inside], color="#f1c40f", lw=1.8, label="bending-line fit")
            ax.plot(cu[~inside], cz[~inside], color="#f1c40f", lw=1.0, ls="--")
            ax.set_xlim(0.25, -0.35)
            ax.set_ylim(0.24, -0.005)
            ax.set_aspect("equal")
            ax.set_title(f"{label}: step {s}, t {st['t']:.2e}\nhinge s {p[0]:.3f}, w {p[1]:.3f}, dip {np.degrees(p[2]):.0f}, "
                         f"z0 {p[3]:.3f}", fontsize=7)
            ax.tick_params(labelsize=6)
            if i == 0 and j == 0:
                ax.legend(fontsize=6, loc="lower left")
    fig.suptitle(f"{case}: the fault on a bending line fitted to the crust {'top' if q > 0.5 else 'base'} (yellow) against the current envelope locator (red); "
                 "u along the surface from the trench (incoming plate to the left), z depth", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = f"{OUT}/bending_fit_{case}_{TAG}.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print("->", out)
json.dump(results, open(f"{OUT}/bending_fit_{TAG}.json", "w"), indent=1)
for k, v in results.items():
    print(k)
    for x in v:
        print(f"   step {x['step']:3d}: hinge {x['s_hinge']:.3f} w {x['w']:.3f} dip {x['phi_slab_deg']:5.1f} z0 {x['z0']:.4f} misfit {x['misfit']:.2e}")
