"""UNFILED 22: hunt for a trace where development's pull_vertex_onto rule (a later target takes a
shared vertex) makes the cut fail, forward or reversed. Random smooth traces sampled finer than the
mesh (so consecutive control points share vertices), on 2-D meshes; each trace is pulled and cut
as add_fault does (pull_vertex_onto then cut_along_lines), in both directions.

    python hunt.py <mesh> <n traces> <seed>"""
import sys, warnings
import numpy as np
mesh_kind, ntr, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sys.argv = sys.argv[:1]
import underworld3 as uw
from underworld3.utilities import line_cut as lc
warnings.simplefilter("ignore")
if mesh_kind == "box_irr":
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=False)
elif mesh_kind == "box_reg":
    mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=True)
else:
    mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.1)
h = 1 / 12 if mesh_kind.startswith("box") else 0.1
rng = np.random.default_rng(seed)

def trace():
    if mesh_kind.startswith("box"):
        p0 = rng.uniform(0.25, 0.75, 2)
    else:
        r0, t0 = rng.uniform(0.65, 0.85), rng.uniform(0, 2 * np.pi)
        p0 = r0 * np.array([np.cos(t0), np.sin(t0)])
    ang = rng.uniform(0, 2 * np.pi); curv = rng.uniform(-3, 3)
    L = rng.uniform(2, 4) * h; ds = rng.uniform(0.3, 0.7) * h
    n = max(3, int(L / ds) + 1)
    s = np.linspace(0, L, n)
    th = ang + curv * s
    pts = np.cumsum(np.column_stack([np.cos(th), np.sin(th)]) * ds, axis=0) - [np.cos(ang) * ds, np.sin(ang) * ds] + p0
    return pts

VARIANT = __import__("os").environ.get("VARIANT", "all")
counts = {"ok": 0, "fail": 0, "pull_refused": 0}
shared_calls = 0
fails = []
for t in range(ntr):
    P = trace()
    for direction, Q in (("fwd", P), ("rev", P[::-1].copy())):
        try:
            if VARIANT == "all":
                dm = lc.pull_vertex_onto(mesh.dm, Q, on_shared="note")
            elif VARIANT == "corners":
                import corners_plugin as cp
                dm = cp._orig(mesh.dm, cp.thinned(Q, mesh.dm), on_shared="note")
            elif VARIANT == "tips":
                dm = lc.pull_vertex_onto(mesh.dm, Q[[0, -1]], on_shared="note")
            else:
                dm = mesh.dm
                lc.last_shared_targets = {"count": 0, "first": []}
        except ValueError:
            counts["pull_refused"] += 1
            continue
        sh = lc.last_shared_targets["count"]
        shared_calls += sh > 0
        try:
            lc.cut_along_lines(dm, [Q])
            counts["ok"] += 1
        except Exception as e:
            counts["fail"] += 1
            fails.append((t, direction, sh, str(e)[:60]))
print("HUNT", VARIANT, mesh_kind, "seed", seed, counts, "calls with a shared vertex", shared_calls, flush=True)
for f in fails[:8]:
    print("FAIL", f, flush=True)
