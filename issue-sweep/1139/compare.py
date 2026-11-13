import json, sys
def load(p):
    d = {}
    for line in open(p):
        line = line.strip()
        if not line or line == "DONE": continue
        r = json.loads(line); d[r["case"]] = r
    return d
b, a = load(sys.argv[1]), load(sys.argv[2])
keys = [k for k in b]
flip, same, diff = [], [], []
def strip(r):
    r = dict(r); r.pop("deprecation", None); return r
for k in keys:
    rb, ra = strip(b[k]), strip(a.get(k, {}))
    if rb == ra: same.append(k)
    elif str(ra.get("add", "")).startswith("ValueError: add_condition"): flip.append(k)
    else: diff.append(k)
print("cases", len(keys), "identical", len(same), "now refused", len(flip), "other differences", len(diff))
print("\nNOW REFUSED:")
for k in flip:
    rb = b[k]
    print(f"  {k:26s} before: add={str(rb.get('add'))[:40]} solve={str(rb.get('solve'))[:60]} err={rb.get('max_err', rb.get('err'))}")
    print(f"  {'':26s} after : {a[k]['add']}")
print("\nOTHER DIFFERENCES:")
for k in diff:
    print("  ", k); print("     before", json.dumps(b[k])[:500]); print("     after ", json.dumps(a.get(k))[:500])
