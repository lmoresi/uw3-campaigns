"""Where each matched-width band sits: the y of the edot_II peak on each of the 8
vertical cuts (x = +-12 .. 21 km), for the matched pairs at ref 3, from checkpoints.
The limb's dip is the slope of y_peak against |x| (arctan, per side); its origin the
intercept at x = 0. Collective (global_evaluate). Writes ../results/peak_positions.json."""
import json
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

RES = os.path.join(_here, "..", "results")
RUNS = [("P1", "micromorphic l = 0.25", "micromorphic", "micro_ref3_xi0_beta0.1_l0.25"),
        ("P1", "Cosserat (0.14, 1)", "cosserat", "cosserat_ref3_xi0_c1_l0.14_P1_np4_cmatch"),
        ("P2", "micromorphic l = 0.5", "micromorphic", "micro_ref3_xi0_beta0.1_l0.5"),
        ("P2", "Cosserat (0.236, 1)", "cosserat", "cosserat_ref3_xi0_c1_l0.236_P1_np4_cmatch"),
        ("P2", "Cosserat (0.25, 0.1)", "cosserat", "cosserat_ref3_xi0_c0.1_l0.25_P1_np4_cmap"),
        ("P3", "micromorphic l = 1", "micromorphic", "micro_ref3_xi0_beta0.1_l1"),
        ("P3", "Cosserat (0.37, 1)", "cosserat", "cosserat_ref3_xi0_c1_l0.37_P1_np4_cmatch"),
        ("P3", "Cosserat (0.5, 0.054)", "cosserat", "cosserat_ref3_xi0_c0.054_l0.5_P1_np4_cmatch")]
rows = []
y = np.linspace(-0.68, -0.02, 4001)
for pair, label, model, name in RUNS:
    S = cn.build_notch(3, 0.0, seed=False)
    S["v"].read_timestep(name, S["v"].name, 0, outputPath=os.path.join(RES, model, "checkpoints"))
    peaks = {}
    for xs in cn.STATIONS:
        f = np.asarray(uw.function.global_evaluate(
            S["stokes"].Unknowns.Einv2, np.column_stack([np.full_like(y, xs), y]))).ravel()
        peaks[f"{xs * cn.H_KM:g}"] = float(y[int(np.argmax(f - np.median(f)))] * cn.H_KM)
    fit = {}
    for side, sign in (("left", -1), ("right", 1)):
        xs = np.array([float(k) for k in peaks if np.sign(float(k)) == sign])
        ys = np.array([peaks[f"{x:g}"] for x in xs])
        slope, intercept = np.polyfit(np.abs(xs), ys, 1)
        fit[side] = dict(dip_deg=float(np.degrees(np.arctan(slope))), y_at_x0_km=float(intercept))
    rows.append(dict(pair=pair, label=label, run=name, peak_y_km=peaks, fit=fit))
    uw.pprint(f"{label:24s} " + " ".join(f"{peaks[k]:6.2f}" for k in peaks) +
              "  dip L/R " + " / ".join(f"{fit[s]['dip_deg']:.1f}" for s in ("left", "right")) +
              "  y(x=0) " + " / ".join(f"{fit[s]['y_at_x0_km']:.2f}" for s in ("left", "right")))
    del S
with uw.selective_ranks(0) as rank0:
    if rank0:
        json.dump(rows, open(os.path.join(RES, "peak_positions.json"), "w"), indent=1)
