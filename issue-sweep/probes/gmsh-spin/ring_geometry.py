import pickle, sys
import numpy as np
import underworld3.utilities.place_surface as ps
d = pickle.load(open(sys.argv[1], "rb"))
X = np.asarray(d["Xall"])[list(d["ring"])]
n = len(X); L = np.linalg.norm(np.roll(X, -1, 0) - X, axis=1)
print(f"edges: min {L.min():.3e} max {L.max():.3e} ratio {L.max()/L.min():.1f}")
# smallest distance from a vertex to a non-adjacent edge, relative to the local edge length
best = (np.inf, None)
for i in range(n):
    for j in range(n):
        if j in (i, (i - 1) % n): continue
        A, B = X[j], X[(j + 1) % n]; e = B - A
        u = np.clip((X[i] - A) @ e / (e @ e), 0, 1); dd = np.linalg.norm(X[i] - A - u * e)
        rel = dd / min(L[j], L[(i - 1) % n], L[i])
        if rel < best[0]: best = (rel, (i, j, dd))
print(f"closest vertex to a non-adjacent edge: {best[0]:.3e} of the local edge (vertex {best[1][0]}, edge {best[1][1]}, distance {best[1][2]:.3e})")
ang = []
for i in range(n):
    a, b = X[(i - 1) % n] - X[i], X[(i + 1) % n] - X[i]
    ang.append(np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))
print(f"smallest interior corner angle: {min(ang):.3f} deg at vertex {int(np.argmin(ang))}")
try:
    print("self crossings:", ps._loop_self_crossings(X))
except Exception as e:
    print("self crossings check:", type(e).__name__, e)
