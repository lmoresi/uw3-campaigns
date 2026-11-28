import numpy as np, sys
d = np.load(sys.argv[1], allow_pickle=True)
X, ring = d["Xall"], d["ring"]
P = X[ring]; n = len(P)
def orient(a, b, c): return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
nx = int((ring >= 0).sum())
for i in range(n):
    A, B = P[i], P[(i+1)%n]
    for j in range(i+2, n):
        if i == 0 and j == n-1: continue
        C, D = P[j], P[(j+1)%n]
        d1, d2, d3, d4 = orient(A,B,C), orient(A,B,D), orient(C,D,A), orient(C,D,B)
        if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
            print("edges", i, j, "orients %.3g %.3g %.3g %.3g" % (d1, d2, d3, d4))
            for k in (i, (i+1)%n, j, (j+1)%n):
                print("  pos %d id %d  (%.6f, %.6f) r=%.6f" % (k, ring[k], P[k][0], P[k][1], np.linalg.norm(P[k])))
print("n", n, "max id", ring.max(), "Xall", len(X))
