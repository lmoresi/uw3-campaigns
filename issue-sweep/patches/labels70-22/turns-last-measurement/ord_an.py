import json, glob, sys, collections, numpy as np
def load(p): return {(r["mesh"],r["ds"],r["trace"]):r for f in sorted(glob.glob(p)) for l in open(f) for r in [json.loads(l)]}
A=load(sys.argv[1]); B=load(sys.argv[2])
def summ(R, tag):
    added=[r for r in R.values() if r["outcome"]=="split" and r.get("pieces")==1 and r.get("excess",9)<=0.5]
    j=[r for r in added if "slip_err" in r and r["ds"]!=1.0]
    bad=[r for r in j if abs(r["slip_err"])>0.10]
    toff=[r for r in added if r.get("turns_off_chain",0)>0]
    tj=[r for r in toff if r in j]
    print(f"{tag}: outcomes {dict(collections.Counter(r['outcome'] for r in R.values()))}; added {len(added)}; judged {len(j)}, bad {len(bad)}, |err| median {np.median([abs(r['slip_err']) for r in j]):.4f}")
    print(f"   added with a turn OFF the chain: {len(toff)} (judged {len(tj)}, bad {sum(abs(r['slip_err'])>0.1 for r in tj)}, sound {sum(abs(r['slip_err'])<=0.1 for r in tj)})")
    print(f"   added and bad WITH every turn on the chain: {len([r for r in bad if r.get('turns_off_chain',0)==0])}")
    return added
a=summ(A, "current order"); b=summ(B, "turns last   ")
k=("box_reg",0.5,"kink120_2"); print("kink120_2:", {t: (R[k]["outcome"], R[k].get("turns_off_chain"), round(R[k].get("excess",-1),3), round(R[k].get("slip_err",float('nan')),3)) for t,R in (("current",A),("turns_last",B))})
# meshes/outcomes changed among faults development-placed-like (added under current)
ch=collections.Counter((A[k]["outcome"], B[k]["outcome"]) for k in A if k in B and A[k]["outcome"]!=B[k]["outcome"])
print("outcome changes current -> turns last:", dict(ch))
both=[k for k in A if k in B and "slip_err" in A[k] and "slip_err" in B[k] and k[1]!=1.0]
d=np.array([abs(B[k]["slip_err"])-abs(A[k]["slip_err"]) for k in both])
print(f"|err| change on {len(both)} judged in both: better {int((d<-1e-9).sum())}, worse {int((d>1e-9).sum())}, worse by >2 pts {int((d>0.02).sum())}: {sorted([(k, round(A[k]['slip_err'],3), round(B[k]['slip_err'],3)) for k,x in zip(both,d) if x>0.02])[:8]}")
