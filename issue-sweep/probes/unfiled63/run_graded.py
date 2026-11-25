"""UNFILED 63 / option 2: a graded finest annulus (not a refine child) under a uniform coarse
tail, so the top coarse level has orphans where the finest is coarser than it. Stokes P2/P1,
rotated free-slip both walls, custom FMG. Compares the serial orphan repair on and off.

    python run_graded.py <repair|norepair> <inner size> <outer size> [tol]"""
import sys
import numpy as np
mode, h_in, h_out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
tol = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-8
sys.argv = sys.argv[:1]
from underworld3.utilities import custom_mg
_orig = custom_mg.barycentric_prolongation
ORPH = []
def _logged(coarse_coords, fine_coords, repair_orphans=True, stats=None):
    st = {}
    P = _orig(coarse_coords, fine_coords, repair_orphans=(mode == "repair") and repair_orphans, stats=st)
    empty = int((np.asarray((P != 0).sum(axis=0)).ravel() == 0).sum())
    # orphans before any repair: rebuild without it
    P0 = _orig(coarse_coords, fine_coords, repair_orphans=False)
    ORPH.append((P.shape, int((np.asarray((P0 != 0).sum(axis=0)).ravel() == 0).sum()), empty))
    if stats is not None:
        stats.update(st)
    return P
custom_mg.barycentric_prolongation = _logged
for k, v in list(custom_mg._BUILDERS.items()):
    if v is _orig:
        custom_mg._BUILDERS[k] = _logged

import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg

r_o, r_i = 1.0, 0.5
coarse = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=0.1, refinement=2, qdegree=3)
tail = coarse._coarse_level_meshes()[:-1] + [coarse]
fine = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=h_out, cellSizeInner=h_in,
                          cellSizeOuter=h_out, qdegree=3)
x, y = fine.X
r = sympy.sqrt(x ** 2 + y ** 2)
v = uw.discretisation.MeshVariable("V", fine, 2, degree=2)
p = uw.discretisation.MeshVariable("P", fine, 1, degree=1, continuous=True)
s = uw.systems.Stokes(fine, velocityField=v, pressureField=p)
s.constitutive_model = uw.constitutive_models.ViscousFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = 1.0
s.bodyforce = 1.0e3 * sympy.cos(3 * sympy.atan2(y, x)) * sympy.sin(sympy.pi * (r - r_i) / (r_o - r_i)) \
    * fine.CoordinateSystem.unit_e_0
s.add_rotated_freeslip_bc(0, "Upper", normal=fine.CoordinateSystem.unit_e_0)
s.add_rotated_freeslip_bc(0, "Lower", normal=fine.CoordinateSystem.unit_e_0)
s.petsc_use_pressure_nullspace = True
s.tolerance = tol
set_custom_fmg(s, tail, field_id=0)
s.solve(zero_init_guess=True)
info = s._rotated_freeslip_info
V = np.asarray(v.array).reshape(-1, 2)
np.save(f"vg_{mode}_{h_in}_{h_out}.npy", V)
cells = [m.dm.getHeightStratum(0)[1] for m in tail + [fine]]
print("ORPH", mode, [(o, e) for _sh, o, e in ORPH], "(orphans before repair, empty columns after)")
print("ITS", mode, "h", h_in, h_out, "cells", cells, "converged", info["converged"], "outer",
      info["ksp_its"], "vel", info["vel_its_last"], "pres", info["pres_its_last"],
      "rnorm/rnorm0 %.2e" % (float(info["rnorm"]) / float(info["rnorm0"])), "|v|", float(np.linalg.norm(V)))
