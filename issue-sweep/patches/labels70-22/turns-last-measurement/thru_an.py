import json, glob, sys, collections, numpy as np
R=[json.loads(l) for f in sorted(glob.glob(sys.argv[1])) for l in open(f)]
print("rows", len(R), "with pulled count", sum("pulled" in r for r in R))
added=[r for r in R if r["outcome"]=="split" and r.get("pieces")==1 and r.get("excess",9)<=0.5]
print("added under the current guards (one piece, excess <= 0.5):", len(added))
off=[r for r in added if r.get("pulled_off_chain",0)>0]
print("  of those, a pulled vertex OFF the chain (the new check would refuse):", len(off))
J=lambda r: "slip_err" in r and r["ds"]!=1.0
for nm,S in (("would refuse",off),("would keep",[r for r in added if r.get("pulled_off_chain",0)==0])):
    j=[r for r in S if J(r)]
    bad=[r for r in j if abs(r["slip_err"])>0.10]
    print(f"  {nm}: {len(S)}, judged {len(j)}, bad (>10 %) {len(bad)}, sound {len(j)-len(bad)}")
print("  refused, sound (slip within 10 %):", sorted([(r["mesh"][4:], r["ds"], r["trace"], round(r["slip_err"],3), r["pulled_off_chain"], round(r["excess"],3)) for r in off if J(r) and abs(r["slip_err"])<=0.10]))
print("  refused, bad:", sorted([(r["mesh"][4:], r["ds"], r["trace"], round(r["slip_err"],3), r["pulled_off_chain"], round(r["excess"],3)) for r in off if J(r) and abs(r["slip_err"])>0.10]))
print("  refused, no reference:", sorted([(r["mesh"][4:], r["ds"], r["trace"], r["pulled_off_chain"]) for r in off if not J(r)]))
kept_bad=[r for r in added if r.get("pulled_off_chain",0)==0 and J(r) and abs(r["slip_err"])>0.10]
print("  still added and bad:", sorted([(r["mesh"][4:], r["ds"], r["trace"], round(r["slip_err"],3), round(r["excess"],3)) for r in kept_bad]))
k=[r for r in R if r["trace"]=="kink120_2" and r["mesh"]=="box_reg" and r["ds"]==0.5]
print("kink120_2 box_reg 0.5:", [(r["outcome"], r.get("pulled"), r.get("pulled_off_chain"), r.get("excess"), r.get("slip_err")) for r in k])
