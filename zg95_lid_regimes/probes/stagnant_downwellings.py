"""Where are the downwellings of the saturated stagnant box state (mobile_ref_H1.42,
checkpoint 1975)? Prints v_y and T along y = 0.75 and the surface velocity."""
import json, numpy as np, underworld3 as uw
import os
run = os.path.expanduser("~/+Simulations/zg95/box_regimes/runs/mobile_ref_H1.42")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(4.0, 1.0), cellSize=0.125,
                                         refinement=2, qdegree=3, regular=False)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
V = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
for var in (T, V):
    var.read_timestep("box", var.name, 1975, outputPath=run)
xs = np.linspace(0.0, 4.0, 81)
for y in (0.75, 0.999):
    pts = np.column_stack([xs, np.full_like(xs, y)])
    v = np.asarray(uw.function.global_evaluate(V.sym, pts)).reshape(-1, 2)
    t = np.asarray(uw.function.global_evaluate(T.sym[0], pts)).ravel()
    print(f"y = {y}")
    for x, vx, vy, tt in zip(xs[::2], v[::2, 0], v[::2, 1], t[::2]):
        print(f"  x {x:4.2f}  vx {vx:8.2f}  vy {vy:8.2f}  T {tt:.3f}")
