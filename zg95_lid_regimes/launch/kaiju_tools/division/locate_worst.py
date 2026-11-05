# kaiju_tools: finds the checkpoints where the locator is worst (the division study)
"""Where the slivers are: re-place given (state, fault, arm) cases exactly as division_offline.py did (same attempt)
and report every cell under 20 deg within 2W + 2 cells of the spine, with its depth below the outer wall, its distance
from the spine, its position along the spine (0 at the wall crossing; past the tip > the spine's length) and whether it
is a band cell; also the cut top's depth and the spine's in-domain length. No solve. Serial.
    python3 locate_worst.py <out.jsonl> <cases.json>      (cases: [{"state", "fault", "arm", "attempt"}, ...])
"""
import json
import sys

import numpy as np
from scipy.spatial import cKDTree

import division_offline as dv
from underworld3.utilities.line_cut import _coords
from underworld3.utilities.place_surface import place_fault_ribbon_2d

out, cases = sys.argv[1], json.load(open(sys.argv[2]))
for c in cases:
    st = json.load(open(c["state"]))
    p = st.get("params", {})
    cell, ref = float(p.get("uw_cell", 0.5)), int(p.get("uw_refinement", 4))
    base, r_o, tree, hv = dv.base_mesh(cell, ref)
    h_nom = cell / 2 ** ref

    def h_of(x):
        return dv.local_h(tree, hv, x)

    f = [g for g in st["faults"] if g.get("name") == c["fault"]][0]
    stored = np.asarray(f["points"], dtype=float)
    arm = c["arm"]
    if arm == "v2":
        spine = dv.uniform(stored, h_nom)
        W, inset_len = 2.0 * h_nom, h_nom
    else:
        spine = dv.divide(stored, h_of, 0.5 if arm == "D2" else 1.0)
        inside = np.hypot(spine[:, 0], spine[:, 1]) <= r_o
        h_f = dv.arc_mean(spine[inside], h_of(spine)[inside])
        W = 2.0 * h_f if arm == "D0" else h_f
        inset_len = float(h_of(spine[int(np.argmax(inside)):int(np.argmax(inside)) + 1])[0])
    trace = spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - inset_len]
    rings, clearance, widen = dv.ATTEMPTS[c.get("attempt", 0)]
    mesh, info = place_fault_ribbon_2d(base, [(f["name"], trace)], W * widen, spines=[(f["name"], spine)],
                                       margin_rings=rings, clearance=clearance, split=True, mesher="ladder",
                                       seams="gather")
    dm = mesh.dm
    X = _coords(dm)
    vS, vE = dm.getDepthStratum(0)
    cS, cE = dm.getHeightStratum(0)
    tri = np.array([[q - vS for q in dm.getTransitiveClosure(k)[0] if vS <= q < vE] for k in range(cS, cE)])
    P = X[tri]
    ang = []
    for i in range(3):
        a, b, cc = P[:, i], P[:, (i + 1) % 3], P[:, (i + 2) % 3]
        u, v = b - a, cc - a
        ang.append(np.degrees(np.arccos(np.clip((u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1)),
                                                -1, 1))))
    amin = np.min(ang, axis=0)
    cen = P.mean(axis=1)
    # the spine finely sampled with its arc length from the wall crossing
    radius = np.hypot(spine[:, 0], spine[:, 1])
    seg = np.linalg.norm(np.diff(spine, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    k = int(np.argmax(radius <= r_o))
    s_wall = s[k - 1] + (radius[k - 1] - r_o) / max(radius[k - 1] - radius[k], 1e-12) * seg[k - 1] if k else 0.0
    t = np.linspace(0.0, s[-1], 4000)
    fine = np.c_[np.interp(t, s, spine[:, 0]), np.interp(t, s, spine[:, 1])]
    dist, idx = cKDTree(fine).query(cen)
    hloc = np.median(np.linalg.norm(P[:, 0] - P[:, 1], axis=1))
    band = np.asarray(info["band"], dtype=bool)
    near = dist < 2.0 * W * widen + 2.0 * hloc
    bad = np.flatnonzero(near & (amin < 20.0))
    L_in = s[-1] - s_wall
    rec = dict(c, W=W * widen, spine_in_domain=round(float(L_in), 5), cut_top_depth=round(float(r_o - np.hypot(*trace[0])), 5),
               rungs=int(len(spine)),
               cells=[{"min_angle": round(float(amin[q]), 2), "depth": round(float(r_o - np.hypot(*cen[q])), 5),
                       "from_spine": round(float(dist[q]), 5), "along": round(float(t[idx[q]] - s_wall), 5),
                       "band": bool(band[q])} for q in bad[np.argsort(amin[bad])]])
    with open(out, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(c["state"].split("/")[-2], c["state"][-10:-5], arm, "L", rec["spine_in_domain"], "top", rec["cut_top_depth"],
          [(x["min_angle"], x["depth"], x["along"], x["from_spine"], x["band"]) for x in rec["cells"][:6]], flush=True)
