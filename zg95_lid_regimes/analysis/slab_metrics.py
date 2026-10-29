"""How a slab founders: for every checkpoint of one or more runs, the slab's hinge
(the neck of the cold anomaly just below the plates), its tip, the chord from hinge
to tip (length and dip), its cold mass and its coldest core, all from T on a polar
grid; printed per run and plotted against time, with the hinge rate (negative: the
hinge moves toward the subducting plate, roll-back) and the subducting plate's speed.

    python slab_metrics.py -uw_runs <run dir>,<run dir> -uw_every 5
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strain_band import polar_grid


def slab_state(theta, depth, T, v_t, r_o, T_i, T_slab, plate_depth, neck, hinge_0):
    """The metrics of one checkpoint (see the module docstring)."""
    dth = (theta - hinge_0 + np.pi) % (2 * np.pi) - np.pi            # relative to the initial hinge
    D, TH = np.meshgrid(depth, dth, indexing="ij")
    cold = (T < T_slab) & (D > plate_depth) & (np.abs(TH) < np.pi / 2)
    out = {"cold_mass": 0.0, "hinge": np.nan, "tip_depth": np.nan, "tip_theta": np.nan,
           "chord": np.nan, "dip": np.nan, "T_core": np.nan, "v_plate": np.nan}
    if not cold.any():
        return out
    r = r_o - D
    dA = r * (depth[1] - depth[0]) * (theta[1] - theta[0])
    out["cold_mass"] = float(np.sum((T_i - T)[cold] * dA[cold]))
    band = cold & (D >= plate_depth) & (D < plate_depth + neck)
    if band.any():
        out["hinge"] = float(np.degrees(np.mean(TH[band])))
    i, j = np.unravel_index(np.argmax(np.where(cold, D, -1)), D.shape)
    out["tip_depth"], out["tip_theta"] = float(D[i, j]), float(np.degrees(TH[i, j]))
    deep = cold & (D > plate_depth + neck)
    if deep.any():
        out["T_core"] = float(T[deep].min())
    if band.any():
        h = np.array([(r_o - plate_depth) * np.cos(np.radians(out["hinge"])),
                      (r_o - plate_depth) * np.sin(np.radians(out["hinge"]))])
        tip = np.array([(r_o - out["tip_depth"]) * np.cos(np.radians(out["tip_theta"])),
                        (r_o - out["tip_depth"]) * np.sin(np.radians(out["tip_theta"]))])
        chord = tip - h
        out["chord"] = float(np.linalg.norm(chord))
        t_hat = np.array([-h[1], h[0]]) / np.linalg.norm(h)             # +theta direction at the hinge
        r_hat = h / np.linalg.norm(h)
        out["dip"] = float(np.degrees(np.arctan2(-chord @ r_hat, abs(chord @ t_hat))))
        # the subducting plate's surface speed 0.15 d behind the hinge (on its -theta side)
        k = int(np.argmin(np.abs(dth - (np.radians(out["hinge"]) - 0.15 / r_o))))
        out["v_plate"] = float(v_t[0, k])
    return out


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import underworld3 as uw
    from annulus_model import annulus_mesh, annulus_radii, clamp_radii

    params = uw.Params(
        uw_runs="~/+Simulations/zg95/annulus_faults/runs/slab_A0",
        uw_every=1,                 # every n-th checkpoint
        uw_T_slab=0.5,              # the slab is colder than this
        uw_plate_depth=0.12,        # and below the plates
        uw_neck=0.05,               # the neck band below the plates that locates the hinge
        uw_out="",
        # physical columns: a units run (-uw_scaled 1) carries its scales in its state; for
        # any other run they follow from these two (one velocity kappa/d, one time d^2/kappa)
        uw_depth=uw.Param(2900.0, units="km", description="layer depth d"),
        uw_kappa=uw.Param(1.0e-6, units="m**2/s", description="thermal diffusivity"),
    )
    runs = [os.path.expanduser(r) for r in str(params.uw_runs).split(",")]
    r_o, r_i = annulus_radii()
    theta, depth, xy = polar_grid(r_o, n_theta=720, depth_max=0.95, n_depth=120)
    shape = (len(depth), len(theta))
    pts = clamp_radii(xy, r_o, r_i, 1e-10)
    mesh = fields = None
    fig, axes = plt.subplots(2, 3, figsize=(15, 7))
    axes = axes.ravel()
    for n, run in enumerate(runs):
        states = sorted(glob.glob(os.path.join(run, "state_*.json")))[::int(params.uw_every)]
        with open(states[0]) as f:
            p = json.load(f)["params"]
        if mesh is None:
            mesh = annulus_mesh(float(p["uw_cell"]), int(p["uw_refinement"]))
            fields = {"T": uw.discretisation.MeshVariable("T", mesh, 1, degree=2),
                      "V": uw.discretisation.MeshVariable("V", mesh, 2, degree=2)}
            slab_marker = uw.discretisation.MeshVariable("slab", mesh, 1, degree=1)
        hinge_0 = float(p["uw_theta_trench"])
        with open(states[0]) as f:
            scales = json.load(f).get("scales")
        source = "the run's units"
        if scales is None:
            d, kappa = params.uw_depth, params.uw_kappa
            scales = {"cm_per_yr": float((kappa / d).to("cm/year").magnitude),
                      "Myr": float((d ** 2 / kappa).to("Myr").magnitude), "km": float(d.to("km").magnitude)}
            source = f"d {d}, kappa {kappa}"
        rows = []
        for sp in states:
            trench = np.nan
            with open(sp) as f:
                state = json.load(f)
            index = int(state["step"])
            for name, var in fields.items():
                var.read_timestep("annulus", name, index, outputPath=run)
            T = np.asarray(uw.function.evaluate(fields["T"].sym[0], pts)).ravel().reshape(shape)
            if os.path.exists(os.path.join(run, f"annulus.mesh.slab.{index:05d}.h5")):
                # a compositional slab: the marker is the body, T a passive picture
                slab_marker.read_timestep("annulus", "slab", index, outputPath=run)
                marker = np.clip(np.asarray(uw.function.evaluate(slab_marker.sym[0], pts)).ravel(), 0, 1)
                T = float(p["uw_T_interior"]) * (1 - marker.reshape(shape))
                # the trench: the marker's +theta edge at the surface, relative to its start
                dth = (theta - hinge_0 + np.pi) % (2 * np.pi) - np.pi
                D, TH = np.meshgrid(depth, dth, indexing="ij")
                at_surface = (marker.reshape(shape) > 0.5) & (D < 0.06) & (np.abs(TH) < np.pi / 2)
                trench = float(np.degrees(TH[at_surface].max())) if at_surface.any() else np.nan
            v = np.asarray(uw.function.evaluate(fields["V"].sym, pts)).reshape(-1, 2)
            v_t = ((-v[:, 0] * pts[:, 1] + v[:, 1] * pts[:, 0]) / np.hypot(pts[:, 0], pts[:, 1])).reshape(shape)
            m = slab_state(theta, depth, T, v_t, r_o, float(p["uw_T_interior"]), params.uw_T_slab,
                           params.uw_plate_depth, params.uw_neck, hinge_0)
            m.update({"step": index, "t": float(state["t"]), "trench": trench})
            rows.append(m)
        label = os.path.basename(run.rstrip("/"))
        t = np.array([m["t"] for m in rows])
        hinge = np.array([m["hinge"] for m in rows])
        rate = np.gradient(np.radians(hinge) * r_o, t) if len(t) > 1 else np.full_like(t, np.nan)
        print(f"== {label}: slab length {p['uw_slab_length']}, tau1/Ra {float(p['uw_tau1']) / float(p['uw_ra']):.3g}, "
              f"deta {float(p['uw_deta']):.3g}")
        print("  step      t   hinge(deg)  hinge_rate  v_plate  tip_depth  chord   dip  T_core  cold_mass  trench(deg)")
        for m, rt in zip(rows, rate):
            print(f"  {m['step']:4d} {m['t']:.4f} {m['hinge']:9.2f} {rt:10.1f} {m['v_plate']:8.1f} "
                  f"{m['tip_depth']:9.3f} {m['chord']:6.3f} {m['dip']:5.1f} {m['T_core']:7.3f} {m['cold_mass']:9.4f} "
                  f"{m['trench']:8.2f}")
        for ax, key, title in zip(axes, ("hinge", "tip_depth", "chord", "dip", "T_core", "cold_mass"),
                                  ("hinge (deg from its start; negative = roll-back)", "tip depth",
                                   "hinge-to-tip chord", "chord dip (deg)", "coldest core T", "cold mass")):
            ax.plot(t, [m[key] for m in rows], "-o", ms=3, lw=1.2, label=label)
            ax.set_title(title, fontsize=9)
        if np.isfinite([m["trench"] for m in rows]).any():
            axes[0].plot(t, [m["trench"] for m in rows], "--", lw=1.0, label=label + " trench")
        # the physical columns
        for m, rt in zip(rows, rate):
            m.update({"t_Myr": m["t"] * scales["Myr"], "v_plate_cm_yr": m["v_plate"] * scales["cm_per_yr"],
                      "hinge_rate": float(rt),
                      "hinge_rate_km_Myr": float(rt) * scales["km"] / scales["Myr"],
                      "tip_depth_km": m["tip_depth"] * scales["km"], "chord_km": m["chord"] * scales["km"]})
        print(f"  physical ({source}: one velocity {scales['cm_per_yr']:.4g} cm/yr, one time {scales['Myr']:.4g} Myr)")
        print("  step   t(Myr)  v_plate(cm/yr)  hinge_rate(km/Myr)  tip_depth(km)  chord(km)")
        for m in rows:
            print(f"  {m['step']:4d} {m['t_Myr']:8.2f} {m['v_plate_cm_yr']:14.3f} {m['hinge_rate_km_Myr']:18.2f} "
                  f"{m['tip_depth_km']:13.0f} {m['chord_km']:10.0f}")
        with open(os.path.join(run, "slab_metrics.json"), "w") as f:
            json.dump(rows, f, indent=1)
    for ax in axes:
        ax.set_xlabel("t")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    out = params.uw_out or os.path.join(runs[0], "slab_metrics.png")
    fig.savefig(out, dpi=110)
    print("->", out)


if __name__ == "__main__":
    main()
