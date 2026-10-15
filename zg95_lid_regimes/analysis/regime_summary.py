"""Summarise the box runs over their late window and name each run's regime.

For every run directory under the study's runs/, take the last ``uw_window`` of
its time (diffusion times on the layer depth), check that the run has saturated,
and reduce the per-step diagnostics in records.json to window statistics. Prints a
table and writes regime_summary.json beside the runs.

    python regime_summary.py -uw_study ~/+Simulations/zg95/box_regimes -uw_window 0.1
"""
import glob
import json
import os

import numpy as np
import underworld3 as uw

params = uw.Params(
    uw_study="~/+Simulations/zg95/box_regimes",
    uw_window=0.1,              # length of the late window (diffusion times)
)
study = os.path.expanduser(params.uw_study)


def window_statistics(records, heating, window):
    """Statistics of the per-step diagnostics over the last ``window`` of time.

    Saturation is judged two ways: the drift between the two halves of the window
    (relative change of the mean temperature and of the surface heat flux), and the
    heat balance q_top = q_base + H, which holds on average only once the interior
    has stopped warming or cooling."""
    t = np.array([r["t"] for r in records])
    late = t >= t[-1] - window
    half = t >= t[-1] - 0.5 * window

    def series(key):
        return np.array([r[key] for r in records], dtype=float)

    mobility = series("mobility")[late]
    q_top, q_base = series("q_top"), series("q_base")
    T_mean = series("T_mean")
    stats = {
        "t_end": float(t[-1]),
        "window_covered": float(t[-1] - t[late][0]) >= 0.99 * window,
        "mobility_p10": float(np.percentile(mobility, 10)),
        "mobility_p50": float(np.percentile(mobility, 50)),
        "mobility_p90": float(np.percentile(mobility, 90)),
        "mobility_cv": float(mobility.std() / max(mobility.mean(), 1e-30)),
        "vrms_mean": float(series("vrms")[late].mean()),
        "lid_mean": float(np.nanmean(series("lid_depth")[late])),
        "T_mid_mean": float(series("T_mid")[late].mean()),
        "q_top_mean": float(q_top[late].mean()),
        "q_base_mean": float(q_base[late].mean()),
        "internal_fraction": float(heating / max(q_top[late].mean(), 1e-30)),
        "yield_frac_mean": float(series("yield_frac")[late].mean()),
        "yield_frac_lid_mean": float(series("yield_frac_lid")[late].mean()),
        "T_drift": float(abs(T_mean[half].mean() - T_mean[late & ~half].mean()) / T_mean[late].mean()),
        "q_top_drift": float(abs(q_top[half].mean() - q_top[late & ~half].mean()) / abs(q_top[late].mean())),
        "heat_imbalance": float((q_top[late].mean() - q_base[late].mean() - heating) / abs(q_top[late].mean())),
    }
    return stats


def classify_regime(stats):
    """Name the convection regime of one run from its late-window statistics.

    Returns one of "mobile", "sluggish", "stagnant", "episodic", "runaway" or
    "unsaturated". The statistics available are those of ``window_statistics``:
    mobility percentiles (p10/p50/p90) and coefficient of variation, mean lid depth,
    mean T_mid, mean yielded fraction overall and in the top third, and the
    saturation measures T_drift, q_top_drift and heat_imbalance.
    """
    # TODO(Louis): the regime boundaries. Moresi & Solomatov (1998) separate the
    # regimes by surface mobility; where the thresholds sit, and how episodic
    # overturns show in the mobility spread, is the call this function makes.
    return "unclassified"


summary = {}
for run in sorted(glob.glob(os.path.join(study, "runs", "*", "records.json"))):
    name = os.path.basename(os.path.dirname(run))
    with open(run) as f:
        records = json.load(f)
    states = sorted(glob.glob(os.path.join(os.path.dirname(run), "state_*.json")))
    with open(states[0]) as f:
        heating = float(json.load(f)["params"]["uw_heating"])
    stats = window_statistics(records, heating, params.uw_window)
    stats["regime"] = classify_regime(stats)
    summary[name] = stats

columns = ["t_end", "mobility_p10", "mobility_p50", "mobility_p90", "mobility_cv", "lid_mean",
           "T_mid_mean", "q_top_mean", "q_base_mean", "internal_fraction", "yield_frac_lid_mean",
           "T_drift", "heat_imbalance", "regime"]
uw.pprint(f"{'run':24s} " + " ".join(f"{c[:11]:>11s}" for c in columns), clean_display=False)
for name, stats in summary.items():
    cells = [f"{stats[c]:11.3f}" if isinstance(stats[c], float) else f"{str(stats[c]):>11s}" for c in columns]
    uw.pprint(f"{name:24s} " + " ".join(cells), clean_display=False)

with uw.selective_ranks(0) as selected:
    if selected:
        with open(os.path.join(study, "regime_summary.json"), "w") as f:
            json.dump(summary, f, indent=1)
