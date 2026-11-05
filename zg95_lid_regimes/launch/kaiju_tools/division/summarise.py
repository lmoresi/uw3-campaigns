# kaiju_tools: summarises the division study's outputs
"""Summary of the fault-division offline check (division_offline.py): per arm, placements built (by attempt) and
refused, W, rungs and rung length, band cell aspect (rung length over the half-width, W/2: two cells across), the cut
top's depth, and element quality (smallest angle; placements with any cell under 20 / 10 / 5 deg) in the band and in
the fill round it. Prints a table and writes summary.json next to the jsonl files.
    python3 summarise.py <dir>
"""
import glob
import json
import os
import sys

import numpy as np

d = sys.argv[1]
recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))) for l in open(f)]
out = {}
for arm in ["v2", "D0", "D1", "D2"]:
    R = [r for r in recs if r["arm"] == arm]
    B = [r for r in R if r.get("built")]
    att = {}
    for r in B:
        att[r["attempt"]] = att.get(r["attempt"], 0) + 1
    widen = [1.0, 1.25, 1.0, 1.5]
    aspect = [r["rung_len"][1] / (0.5 * r["W"] * widen[r["attempt"]]) for r in B]
    s = {"placements": len(R), "built": len(B), "by_attempt": att,
         "refused": [(r["state"].split("/")[-2], r["state"][-10:-5], r.get("errors")) for r in R if not r.get("built")],
         "W": [min(r["W"] for r in R), float(np.mean([r["W"] for r in R])), max(r["W"] for r in R)],
         "rungs": [min(r["rungs"] for r in R), float(np.mean([r["rungs"] for r in R])), max(r["rungs"] for r in R)],
         "rung_len_mean": float(np.mean([r["rung_len"][1] for r in R])),
         "rung_len_range": [min(r["rung_len"][0] for r in R), max(r["rung_len"][2] for r in R)],
         "h_trace": [min(r["h_trace"][0] for r in R), float(np.mean([r["h_trace"][1] for r in R])),
                     max(r["h_trace"][2] for r in R)],
         "band_aspect": [min(aspect), float(np.mean(aspect)), max(aspect)] if aspect else None,
         "cut_top_depth": [min(r["cut_top_depth"] for r in R), float(np.mean([r["cut_top_depth"] for r in R])),
                           max(r["cut_top_depth"] for r in R)],
         "seconds_mean": float(np.mean([r["seconds"] for r in R]))}
    for zone in ("band", "fill", "all"):
        a = np.array([r["quality"][zone]["min_angle"] for r in B if r["quality"][zone]["min_angle"] is not None])
        s[zone] = {"min_angle_min": float(a.min()), "min_angle_median": float(np.median(a)),
                   "min_angle_p10": float(np.percentile(a, 10)),
                   "placements_under": {t: int((a < t).sum()) for t in (20, 10, 5)},
                   "cells_under20_total": int(sum(r["quality"][zone]["under20"] for r in B)),
                   "cells_mean": float(np.mean([r["quality"][zone]["cells"] for r in B]))}
    out[arm] = s
    print(f"{arm}: built {len(B)}/{len(R)} {att}; W {s['W'][1]:.5f}; rungs {s['rungs'][1]:.1f} "
          f"(len {s['rung_len_mean']:.5f}); aspect {s['band_aspect'][1]:.2f}; top {s['cut_top_depth'][1]:.4f}; "
          f"band min angle min/p10/median {s['band']['min_angle_min']:.1f}/{s['band']['min_angle_p10']:.1f}/"
          f"{s['band']['min_angle_median']:.1f} under 20/10/5: {s['band']['placements_under']}; "
          f"fill {s['fill']['min_angle_min']:.1f}/{s['fill']['min_angle_p10']:.1f}/{s['fill']['min_angle_median']:.1f} "
          f"under {s['fill']['placements_under']}; all {s['all']['min_angle_min']:.1f}")
    for x in s["refused"]:
        print("   refused", x)
json.dump(out, open(os.path.join(d, "summary.json"), "w"), indent=1)
