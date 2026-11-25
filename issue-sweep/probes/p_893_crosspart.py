"""#893: memory of the cross-partition node transfer's builder, serially, on the
gathered cloud a rank would hold: a placed coarse level's whole P2 node cloud
against the finest's nodes. python p_893_crosspart.py <cellSize> <fraction of the
finest nodes a rank holds> [top radius, default 0.9]

Serial only: it measures the builder on one process. ru_maxrss is bytes on
macOS, kilobytes on Linux."""
import resource
import sys
import time
import numpy as np
import underworld3 as uw
from underworld3.utilities import custom_mg
from underworld3.utilities.place_surface import place_fault_ribbon_2d

cell, frac = float(sys.argv[1]), float(sys.argv[2])
r_top = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
_scale = 1e6 if sys.platform == "darwin" else 1e3
peak = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / _scale
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=cell, refinement=2, qdegree=2)
L0, L1 = base._coarse_level_meshes()[:2]
h = cell / 4
th, dip = np.radians(80.0), np.radians(35.0)
top = np.array([np.cos(th), np.sin(th)]) * r_top
inward = -np.array([np.cos(th - dip), np.sin(th - dip)])
n = int(0.3 / h)
fine = place_fault_ribbon_2d(base, [("Fault", top + (np.arange(n + 1) * h)[:, None] * inward)],
                             2 * h, margin_rings=1, clearance=0.7, split=False, mesher="ladder")[0]
mid = place_fault_ribbon_2d(L1, [("Fault", top + (np.arange(n // 2 + 1) * 2 * h)[:, None] * inward)],
                            4 * h, margin_rings=1, clearance=0.7, split=False, mesher="ladder")[0]
Xc = np.asarray(mid._get_coords_for_basis(2, True))
Xf = np.asarray(fine._get_coords_for_basis(2, True))
Xf = Xf[: int(frac * len(Xf))]
m0, t0 = peak(), time.time()
P = custom_mg._node_transfer_no_repair(custom_mg.barycentric_prolongation, Xc, Xf)
print(f"RES cell {cell} top {r_top} coarse nodes {len(Xc)} fine nodes {len(Xf)} nnz {P.nnz} "
      f"peak {m0:.0f} -> {peak():.0f} MB in {time.time() - t0:.1f}s", flush=True)
