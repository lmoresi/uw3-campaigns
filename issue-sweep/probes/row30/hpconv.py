import sys, os, json, warnings
import numpy as np
warnings.simplefilter("ignore")
mk = sys.argv[1]
sys.argv = ["x", mk, "150", "1", "0"]
exec(open("row30.py").read().split("coarse = uw.meshing.UnstructuredSimplexBox")[0])
g = {}
sys.argv = ["x", mk, "0.3", "kinks"]
exec(open(os.path.expanduser("~/+Simulations/issue-sweep-pull/pull22.py")).read().split("for n, (tag, Q) in enumerate(traces()):")[0], g)
Q0 = [q for t, q in g["traces"]() if t == "kink150_3"][0]
from underworld3.utilities.fault_split import _turns
ia = int(np.flatnonzero(_turns(Q0))[0]); A, B, C = Q0[0], Q0[ia], Q0[-1]
def resample(hk):
    n1 = max(2, int(round(np.linalg.norm(B - A) / (0.5 * hk)))); n2 = max(2, int(round(np.linalg.norm(C - B) / (0.5 * hk))))
    a = A + np.linspace(0, 1, n1 + 1)[:, None] * (B - A); b = B + np.linspace(0, 1, n2 + 1)[1:, None] * (C - B)
    return np.vstack([a, b])
for k in (1, 2, 4, 8):
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h / k, regular=(mk == "box_reg"))
    Q = resample(h / k)
    for mode in ("base", "pin"):
        try:
            r = solve(mesh, Q, mode)
            print(f"HC {mk} {12*k} {mode}: largest {r['max']:.5f} apex {r['apex'] if r['apex'] is not None else -1:.4f} beyond-1-cell {r['beyond'] if r['beyond'] else -1:.5f} vel {max(r['vel'] or [0])}", flush=True)
        except Exception as e:
            print(f"HC {mk} {12*k} {mode}: refused {str(e)[:80]}", flush=True)
