"""Tabulate the ROW lines of traction.py logs: errors at each h, observed order,
and the recovery cost relative to the solve.

    python table.py LOGDIR
"""
import glob
import json
import sys
from collections import defaultdict

import numpy as np

rows = []
for path in glob.glob(f"{sys.argv[1] if len(sys.argv) > 1 else '.'}/*.log"):
    with open(path) as handle:
        seen = set()
        for line in handle:
            if line.startswith("ROW "):
                d = json.loads(line[4:])
                key = (d["build"], d["case"], d["cell"], d["route"], d["wall"], d["quantity"])
                if key not in seen:
                    seen.add(key)
                    rows.append(d)

table = defaultdict(dict)
for d in rows:
    label = d["route"] if d["route"].startswith("857") else f"{d['route']} [{d['build']} solve]"
    table[(d["case"], d["quantity"], d["wall"], label)][d["cell"]] = d

for case in ("free", "zero"):
    for quantity in ("sigma_rr", "sigma_rt"):
        keys = sorted(k for k in table if k[0] == case and k[1] == quantity)
        if not keys:
            continue
        print(f"\n### {case} slip, {quantity}\n")
        print("| wall | route | L2 h=1/8 | L2 h=1/16 | L2 h=1/32 | order | max h=1/32 "
              "| L2 midpoints h=1/32 | cost / solve h=1/32 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for key in keys:
            cells = table[key]
            hs = sorted(cells, reverse=True)
            l2 = [cells[h]["l2"] for h in hs]
            order = np.polyfit(np.log(hs), np.log(l2), 1)[0] if len(hs) > 1 else np.nan
            fine = cells[min(hs)]
            cost = fine["cost_s"] / fine["solve_s"] if fine["cost_s"] is not None else np.nan
            print(f"| {key[2]} | {key[3]} | " + " | ".join(f"{e:.2e}" for e in l2)
                  + f" | {order:.2f} | {fine['max']:.2e} | {fine['l2_mid']:.2e} | {cost:.3f} |")
