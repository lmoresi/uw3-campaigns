"""Before/after table from two recorder runs: per test, the solves' iteration counts and the
largest relative solution difference."""
import json, os, sys
from collections import defaultdict
import numpy as np

def load(d):
    by = defaultdict(list); orph = defaultdict(int)
    for l in open(os.path.join(d, "log.jsonl")):
        x = json.loads(l)
        if x["kind"] == "solve":
            by[x["test"]].append(x)
        elif x["orphans"]:
            orph[x["test"]] += x["orphans"]
    return by, orph

def its(x):
    if "vel_its_last" in x:
        return f"{x.get('ksp_its')}/{x.get('vel_its_last')}/{x.get('pres_its_last')}"
    return f"{x.get('snes')}:{x.get('lin')}" + (f" {x['sub_its']}" if "sub_its" in x else "")

B, OB = load("rot_before"); A, OA = load("rot_after")
rows, same_all, changed = [], 0, 0
for t in sorted(set(B) | set(A)):
    b, a = B.get(t, []), A.get(t, [])
    ib = "; ".join(its(x) for x in b); ia = "; ".join(its(x) for x in a)
    worst = 0.0
    for xb, xa in zip(b, a):
        if "npz" in xb and "npz" in xa:
            nb, na = np.load(os.path.join("rot_before", xb["npz"])), np.load(os.path.join("rot_after", xa["npz"]))
            for k in nb.files:
                if k in na.files and nb[k].shape == na[k].shape:
                    den = np.linalg.norm(nb[k]) or 1.0
                    worst = max(worst, float(np.linalg.norm(nb[k] - na[k]) / den))
    same = ib == ia and len(b) == len(a)
    same_all += same; changed += not same
    rows.append((t, OB.get(t, 0), len(b), ib, ia, worst, same))
print(f"tests with solves: {len(rows)}; iteration counts identical: {same_all}; changed: {changed}")
print("| test | orphans (before) | solves | its before | its after | max rel diff |")
print("|---|---|---|---|---|---|")
for t, o, n, ib, ia, w, same in rows:
    if not same or o or w > 1e-12:
        print(f"| {t} | {o} | {n} | {ib[:120]} | {ia[:120]} | {w:.1e} |")
print("max rel diff over all identical-count tests: %.1e" % max([w for *_, w, s in rows if s] or [0]))
