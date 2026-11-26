"""Dump every manifold mesh's cell radii and time the cell-size call (UNFILED 80).
python radii_dump.py <out.npz>; run once on development's build and once on the fix's."""
import sys, time, warnings, numpy as np
warnings.simplefilter("ignore")
import underworld3 as uw
from underworld3.cython import petsc_discretisation as pd
sys.path.insert(0, "/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests")
from test_1079_thin_sheet_sphere_faults import _faulted_sphere
meshes = {}
for h in (0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.12, 0.1):
    meshes[f"sphere_{h}"] = uw.meshing.SphericalManifold(radius=1.0, cellSize=h, degree=1, qdegree=5)
meshes["sphere_0.1_ref1"] = uw.meshing.SphericalManifold(radius=1.0, cellSize=0.1, refinement=1, qdegree=2)
meshes["sphere_0.05"] = uw.meshing.SphericalManifold(radius=1.0, cellSize=0.05, degree=1, qdegree=3)
for h, a in ((0.2, np.pi / 6), (0.15, np.pi / 8)):
    meshes[f"faulted_{h}"] = _faulted_sphere(h, a)
out, rows = {}, []
for k, m in meshes.items():
    r, c = pd.petsc_fvm_get_local_cell_sizes(m)
    out[k] = r; out[k + "_centroids"] = c
    ts = []
    for _ in range(15):
        t0 = time.perf_counter(); pd.petsc_fvm_get_local_cell_sizes(m); ts.append(time.perf_counter() - t0)
    rows.append((k, len(r), float(np.median(ts))))
    print(f"RADII {k}: cells {len(r)} median time {np.median(ts)*1e3:.3f} ms")
np.savez(sys.argv[1], **out)
