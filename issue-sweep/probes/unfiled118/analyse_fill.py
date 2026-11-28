"""Geometry of a dumped fill: ring and hole self/inter-crossings, touchings, close approaches."""
import sys, numpy as np
from underworld3.utilities import place_surface as ps
d = np.load(sys.argv[1], allow_pickle=True)
X = d["Xall"]; ring = [int(v) for v in d["ring"]]; holes = [[int(v) for v in h] for h in d["holes"]]
print("ring", len(ring), "unique", len(set(ring)), "holes", [len(h) for h in holes])
loops = [("ring", ring)] + [(f"hole{i}", h) for i, h in enumerate(holes)]
for n, L in loops:
    print(n, "self crossings (library count):", ps._loop_self_crossings(X[np.asarray(L)]))
def segs(L): return [(L[i], L[(i + 1) % len(L)]) for i in range(len(L))]
def segdist(p, q, r, s):
    def pd(a, b, c):
        ab = b - a; t = np.clip(np.dot(c - a, ab) / np.dot(ab, ab), 0, 1); return np.linalg.norm(a + t * ab - c)
    return min(pd(p, q, r), pd(p, q, s), pd(r, s, p), pd(r, s, q))
def orient(a, b, c): return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
allsegs = [(n, a, b) for n, L in loops for a, b in segs(L)]
h = np.median([np.linalg.norm(X[a]-X[b]) for _n, a, b in allsegs])
print("median segment", h)
shared_v = set(ring) & set(v for hh in holes for v in hh)
print("vertices shared by ring and holes:", sorted(shared_v))
close = []
for i in range(len(allsegs)):
    for j in range(i + 1, len(allsegs)):
        n1, a, b = allsegs[i]; n2, c, e = allsegs[j]
        if len({a, b, c, e}) < 4: continue
        dd = segdist(X[a], X[b], X[c], X[e])
        o1, o2 = orient(X[a], X[b], X[c]), orient(X[a], X[b], X[e])
        o3, o4 = orient(X[c], X[e], X[a]), orient(X[c], X[e], X[b])
        cross = (o1 * o2 < 0) and (o3 * o4 < 0)
        if dd < 0.2 * h or cross:
            close.append((dd / h, cross, n1, (a, b), n2, (c, e)))
for c in sorted(close)[:20]: print("  close/cross: d/h=%.3g cross=%s %s%s %s%s" % c)
print("n close (<0.2 h) or crossing pairs:", len(close))
