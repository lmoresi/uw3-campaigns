import json, collections
import numpy as np
R = [json.loads(l) for f in ("pull_dev.jsonl", "pull_new.jsonl", "pull_sharp.jsonl") for l in open(f) if l.startswith("{")]
key = lambda r: (r["mesh"], r["ds"], r["trace"])
by = collections.defaultdict(dict)
for r in R:
    by[key(r)][r["mode"]] = r
modes = ("dev", "new_all", "new_light", "new_light_sharp")
print("## Outcomes (complete / partial / empty / raised)\n")
print("| family | mesh | spacing | " + " | ".join(modes) + " |"); print("|---|---|---|---|---|---|---|")
for fam in ("la", "kink"):
    for mk in ("box_irr", "box_reg"):
        for ds in (1.0, 0.5, 0.3):
            row = []
            for m in modes:
                c = collections.Counter(r["outcome"] for k, d in by.items() if k[0] == mk and k[1] == ds and k[2].startswith(fam) and m in d for r in [d[m]])
                row.append(f"{c['complete']}/{c['partial']}/{c['empty']}/{c['raised']}")
            print(f"| {'lines+arcs' if fam == 'la' else 'kinks'} | {mk} | {ds} | " + " | ".join(row) + " |")
print("\n## Kinks by turn angle, complete of 10 per spacing and mesh, summed (of 60)\n")
print("| turn | " + " | ".join(modes) + " |"); print("|---|---|---|---|---|")
for ang in (10, 30, 60, 90, 120, 150):
    row = []
    for m in modes:
        row.append(str(sum(1 for k, d in by.items() if k[2].startswith(f"kink{ang}_") and m in d and d[m]["outcome"] == "complete")))
    print(f"| {ang} | " + " | ".join(row) + " |")
print("\n## Traces complete on development: what changes (lines+arcs and kinks)\n")
for m in ("new_all", "new_light", "new_light_sharp"):
    pairs = [(d["dev"], d[m]) for d in by.values() if "dev" in d and m in d and d["dev"]["outcome"] == "complete"]
    still = [(a, b) for a, b in pairs if b["outcome"] == "complete"]
    lost = len(pairs) - len(still)
    dcell = np.array([b["cells"] - a["cells"] for a, b in still])
    mv_a = np.array([a["moved"] for a, b in still]); mv_b = np.array([b["moved"] for a, b in still])
    t2c_a = np.array([a["trace_to_chain_max"] for a, b in still]); t2c_b = np.array([b["trace_to_chain_max"] for a, b in still])
    print(f"- {m}: {len(pairs)} complete on dev; {len(still)} still complete, {lost} not. Cells differ in "
          f"{(dcell != 0).sum()} (range {dcell.min()}..{dcell.max()}); base vertices moved, mean dev {mv_a.mean():.2f} -> {mv_b.mean():.2f}; "
          f"trace-to-chain max/h, max over traces dev {t2c_a.max():.3f} -> {t2c_b.max():.3f}")
print("\n## Solves (sheared box, frictionless fault; traces complete under all three)\n")
print("| trace | mesh | spacing | slip max dev | new_all | new_light | new_light_sharp | vel its dev/all/light/sharp |"); print("|---|---|---|---|---|---|---|---|")
for k, d in sorted(by.items()):
    if all(m in d and "slip_max" in d[m] for m in modes):
        s = [d[m]["slip_max"] for m in modes]; v = [str(d[m]["vel"]) for m in modes]
        print(f"| {k[2]} | {k[0]} | {k[1]} | {s[0]:.6f} | {s[1]:.6f} ({(s[1]-s[0])/s[0]:+.1e}) | {s[2]:.6f} ({(s[2]-s[0])/s[0]:+.1e}) | {s[3]:.6f} ({(s[3]-s[0])/s[0]:+.1e}) | {'/'.join(v)} |")
