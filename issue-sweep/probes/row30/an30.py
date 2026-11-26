import json, glob, collections, numpy as np
R=[json.loads(l) for f in sorted(glob.glob("r30_*.jsonl")) for l in open(f)]
print("rows", len(R))
ok=lambda d: isinstance(d, dict) and "error" not in d
for ang in (60, 90, 120, 150, 160):
    S=[r for r in R if r["angle"]==ang]
    added=[r for r in S if ok(r.get("12_base")) and ok(r.get("48_base")) and ok(r.get("12_pin")) and ok(r.get("48_pin"))]
    print(f"== {ang} deg: {len(S)} traces, {len(added)} with all four solves (12/48 base and pin)")
    if not added: continue
    def rel(a, b): return a / b - 1 if (a is not None and b) else np.nan
    rows=[]
    for r in added:
        b12, p12, b48, p48 = r["12_base"], r["12_pin"], r["48_base"], r["48_pin"]
        t12 = r.get("12_trace") if ok(r.get("12_trace")) else {}
        rows.append(dict(
            max_b=rel(b12["max"], b48["max"]), max_p=rel(p12["max"], p48["max"]), max_t=rel(t12.get("max"), b48["max"]),
            beyond_b=rel(b12["beyond"], b48["beyond"]), beyond_p=rel(p12["beyond"], p48["beyond"]),
            apex12_b=b12["apex"], apex12_p=p12["apex"], apex48_b=b48["apex"], apex48_t=t12.get("apex"),
            ref_shift=rel(p48["max"], b48["max"]),
            vel_b=max(b12["vel"]) if b12.get("vel") else None, vel_p=max(p12["vel"]) if p12.get("vel") else None,
            out_b=b12.get("outer"), out_p=p12.get("outer"), conv_p=p12["converged"], pinned=p12.get("pinned")))
    q=lambda k: np.round(np.nanmedian([abs(x[k]) for x in rows]),3)
    mx=lambda k: np.round(np.nanmax([abs(x[k]) for x in rows]),3)
    print(f"   largest slip vs 48 (|err| median/max): base {q('max_b')}/{mx('max_b')}, pin {q('max_p')}/{mx('max_p')}, trace-normal {q('max_t')}/{mx('max_t')}")
    print(f"   slip beyond a cell from the apex vs 48: base {q('beyond_b')}/{mx('beyond_b')}, pin {q('beyond_p')}/{mx('beyond_p')}")
    print(f"   apex slip at 12: base median {np.nanmedian([x['apex12_b'] or np.nan for x in rows]):.4f}, pin {np.nanmedian([x['apex12_p'] or np.nan for x in rows]):.2e}; at 48 base {np.nanmedian([x['apex48_b'] or np.nan for x in rows]):.4f}; trace-normal at 12 {np.nanmedian([x['apex48_t'] or np.nan for x in rows]):.4f}")
    print(f"   pinning moves the 48-cell answer by (median/max) {q('ref_shift')}/{mx('ref_shift')}")
    print(f"   iterations at 12 (vel last / outer): base {[ (x['vel_b'], x['out_b']) for x in rows]}, pin {[ (x['vel_p'], x['out_p']) for x in rows]}, pin converged {all(x['conv_p'] for x in rows)}, rows pinned {[x['pinned'] for x in rows]}")
