"""UNFILED 84: what separates the 150-degree hairpins whose slip is wrong. For each kink trace of
the given angle: slip at 12 cells per side against the same trace at 48 (converged), and the
geometry at the apex: cells with a vertex on each arm, cells with all three vertices on the chain,
the smallest angle among the cells touching the apex.
    python hp84.py <box_irr|box_reg> <DS> <angle>"""
import sys, os, json, warnings
import numpy as np
warnings.simplefilter("ignore")
mk, ds, ang = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.argv = ["x", mk, ds, "kinks"]
g = {}
exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
uw, h, lc = g["uw"], g["h"], g["lc"]
from underworld3.utilities._plex_topology import closure_points
from underworld3.utilities.fault_split import _turns
fine = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h / 4, regular=(mk == "box_reg"))
for tag, Q in g["traces"]():
    if not tag.startswith(f"kink{ang}_"): continue
    rec = dict(mesh=mk, ds=float(ds), trace=tag)
    t = int(np.flatnonzero(_turns(Q))[0]) if _turns(Q).any() else len(Q) // 2
    try:
        m2 = g["mesh"].add_fault(("F", Q))
        rec["slip"] = g["solve"](m2, "F")["slip_max"]
        dm = m2.dm; X = lc._coords(dm); ends = lc._edge_vertices(dm); eS, _ = dm.getDepthStratum(1); vS, _ = dm.getDepthStratum(0)
        mkd = np.asarray(dm.getLabel("F").getStratumIS([b.value for b in m2.boundaries if b.name == "F"][0]).getIndices()) - eS
        mkd = mkd[(mkd >= 0) & (mkd < len(ends))]
        on = set(ends[mkd].ravel().tolist())
        # which arm a chain vertex lies on: nearer segment index before or after the apex
        def arm(v):
            p = X[v]; d = [np.linalg.norm(p - (Q[i] + np.clip(((p - Q[i]) @ (Q[i+1] - Q[i])) / ((Q[i+1] - Q[i]) @ (Q[i+1] - Q[i])), 0, 1) * (Q[i+1] - Q[i]))) for i in range(len(Q) - 1)]
            i = int(np.argmin(d)); return 0 if i < t else 1
        apex = int(np.argmin(np.linalg.norm(X - Q[t], axis=1)))
        armv = {v: arm(v) for v in on if v != apex}
        cS, cE = dm.getHeightStratum(0)
        C = closure_points(dm, np.arange(cS, cE), 0) - vS
        both = sum(1 for c in C if {armv[v] for v in c if v in armv} == {0, 1})
        allon = sum(1 for c in C if all(v in on for v in c))
        P = X[C]; amin = []
        for k in range(3):
            a = P[:, (k + 1) % 3] - P[:, k]; b = P[:, (k + 2) % 3] - P[:, k]
            amin.append(np.degrees(np.arccos(np.clip((a * b).sum(1) / np.linalg.norm(a, axis=1) / np.linalg.norm(b, axis=1), -1, 1))))
        amin = np.min(amin, axis=0)
        at_apex = np.array([apex in c for c in C])
        rec.update(cells_on_both_arms=both, cells_all_on_chain=allon, min_angle_at_apex=float(amin[at_apex].min()) if at_apex.any() else None,
                   apex_vertex_on_trace=float(np.linalg.norm(X[apex] - Q[t]) / h))
    except Exception as e:
        rec["error"] = str(e)[:100]
    try:
        rec["slip_fine"] = g["solve"](fine.add_fault(("F", Q)), "F")["slip_max"]
    except Exception as e:
        rec["fine_error"] = str(e)[:100]
    if "slip" in rec and "slip_fine" in rec:
        rec["err"] = rec["slip"] / rec["slip_fine"] - 1
    print("HP " + json.dumps(rec), flush=True)
