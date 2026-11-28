import numpy as np


def _loop_self_crossings(P):
    """Crossings between non-adjacent edges of the closed polygon P: proper
    crossings, touchings, and collinear overlaps; two disjoint collinear edges
    (a straight run sampled at several points) are not one. Orientation is
    judged against a tolerance scaled by the edges' lengths."""
    P = np.asarray(P, dtype=float)
    n = len(P)
    if n < 4:
        return 0

    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    count = 0
    for i in range(n):
        A, B = P[i], P[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            C, D = P[j], P[(j + 1) % n]
            tol = 1e-12 * np.linalg.norm(B - A) * np.linalg.norm(D - C)
            s = [0 if abs(o) <= tol else (1 if o > 0 else -1)
                 for o in (orient(A, B, C), orient(A, B, D), orient(C, D, A), orient(C, D, B))]
            if s[0] * s[1] > 0 or s[2] * s[3] > 0:
                continue                      # one wholly on one side of the other
            if s == [0, 0, 0, 0]:             # collinear: do they overlap?
                t = B - A
                a0, a1 = sorted((0.0, float(t @ t)))
                c0, c1 = sorted((float((C - A) @ t), float((D - A) @ t)))
                if c0 <= a1 and c1 >= a0:
                    count += 1
                continue
            count += 1                        # proper, or touching
    return count
