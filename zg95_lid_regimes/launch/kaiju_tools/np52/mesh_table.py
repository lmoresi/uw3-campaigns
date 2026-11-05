# kaiju_tools: the mesh table for the np 52 / scaling comparison (levels, cells, wall points)
"""The resolution table for the two TAf-v2 meshes (the hub, 2026-11-04): production -uw_cell 0.5 -uw_refinement 5 against
the coarse base -uw_cell 0.25 -uw_refinement 4. Builds each hierarchy as the driver does (annulus_model.annulus_mesh),
serially, and reports per level the cells; for the finest: cells, vertices, P2 velocity dofs (2 x (vertices + edges)),
wall vertices and P2 points on Upper and Lower, and the edge lengths (mean, min, max) overall, along each wall, and in
the trench region (within 0.2 deep and 10 degrees of theta 0, where the fault sits). Prints JSON.
    python3 mesh_table.py <driver dir>"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
from annulus_model import annulus_mesh, annulus_radii  # noqa: E402
from underworld3.utilities.line_cut import _coords, _edge_vertices  # noqa: E402

r_o, r_i = annulus_radii()
out = {}
for cell, ref in ((0.5, 5), (0.25, 4)):
    base = annulus_mesh(cell, ref)
    levels = base._coarse_level_meshes()[:-1] + [base]
    dm = base.dm
    X = _coords(dm)
    E = _edge_vertices(dm)
    L = np.linalg.norm(X[E[:, 0]] - X[E[:, 1]], axis=1)
    mid = 0.5 * (X[E[:, 0]] + X[E[:, 1]])
    r = np.hypot(mid[:, 0], mid[:, 1])
    th = np.degrees(np.arctan2(mid[:, 1], mid[:, 0]))
    rv = np.hypot(X[:, 0], X[:, 1])
    up_v = int((np.abs(rv - r_o) < 1e-6).sum())
    lo_v = int((np.abs(rv - r_i) < 1e-6).sum())
    up_e = np.abs(r - r_o) < 1e-3 * cell
    up_e &= (np.abs(np.hypot(X[E[:, 0], 0], X[E[:, 0], 1]) - r_o) < 1e-6) & (np.abs(np.hypot(X[E[:, 1], 0], X[E[:, 1], 1]) - r_o) < 1e-6)
    lo_e = (np.abs(np.hypot(X[E[:, 0], 0], X[E[:, 0], 1]) - r_i) < 1e-6) & (np.abs(np.hypot(X[E[:, 1], 0], X[E[:, 1], 1]) - r_i) < 1e-6)
    trench = (r_o - r < 0.2) & (np.abs(th) < 10.0)
    interior = (r_o - r > 0.05) & (r - r_i > 0.05)

    def stats(m):
        return [round(float(L[m].mean()), 5), round(float(L[m].min()), 5), round(float(L[m].max()), 5)]

    out[f"{cell}/{ref}"] = {
        "levels_cells": [int(m.dm.getHeightStratum(0)[1] - m.dm.getHeightStratum(0)[0]) for m in levels],
        "finest_vertices": int(len(X)), "finest_edges": int(len(E)),
        "P2_velocity_dofs": int(2 * (len(X) + len(E))),
        "upper_wall_vertices": up_v, "upper_wall_P2_points": up_v + int(up_e.sum()),
        "lower_wall_vertices": lo_v, "lower_wall_P2_points": lo_v + int(lo_e.sum()),
        "edge_all": stats(np.ones_like(L, dtype=bool)), "edge_upper_wall": stats(up_e), "edge_lower_wall": stats(lo_e),
        "edge_trench_region": stats(trench), "edge_interior": stats(interior),
        "h_b_nominal": cell / 2 ** ref}
print(json.dumps(out, indent=1))
