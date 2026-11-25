"""Option 2 in 3-D: a uniform box tail (cell 0.25, refinement 2) under an independently meshed
finest box. Stokes P2/P1, no-slip walls, a buoyancy; custom FMG on the velocity.

    python run_box3d.py <label> <fine cell size>"""
import sys
import numpy as np
label, hf = sys.argv[1], float(sys.argv[2])
sys.argv = sys.argv[:1]
from underworld3.utilities import custom_mg
_orig = custom_mg.barycentric_prolongation
ORPH = []
def _logged(c, f, repair_orphans=True, stats=None):
    P = _orig(c, f, repair_orphans=repair_orphans, stats=stats)
    P0 = _orig(c, f, repair_orphans=False) if repair_orphans else P
    ORPH.append((int((np.asarray((P0 != 0).sum(axis=0)).ravel() == 0).sum()),
                 int((np.asarray((P != 0).sum(axis=0)).ravel() == 0).sum()), bool(repair_orphans)))
    return P
custom_mg.barycentric_prolongation = _logged
for k, v in list(custom_mg._BUILDERS.items()):
    if v is _orig:
        custom_mg._BUILDERS[k] = _logged
import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg

coarse = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=0.25,
                                           regular=False, refinement=2, qdegree=3)
tail = coarse._coarse_level_meshes()[:-1] + [coarse]
fine = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=hf,
                                         regular=False, qdegree=3)
x, y, z = fine.X
v = uw.discretisation.MeshVariable("V", fine, 3, degree=2)
p = uw.discretisation.MeshVariable("P", fine, 1, degree=1, continuous=True)
s = uw.systems.Stokes(fine, velocityField=v, pressureField=p)
s.constitutive_model = uw.constitutive_models.ViscousFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = 1.0
s.bodyforce = sympy.Matrix([0, 0, 1.0e2 * sympy.cos(sympy.pi * x) * sympy.cos(sympy.pi * y) * sympy.sin(sympy.pi * z)]).T
for wall in ("Bottom", "Top", "Left", "Right", "Front", "Back"):
    s.add_dirichlet_bc((0.0, 0.0, 0.0), wall)
s.tolerance = 1.0e-8
set_custom_fmg(s, tail, field_id=0)
s.solve(zero_init_guess=True)
V = np.asarray(v.array).ravel()
np.save(f"v3_{label}_{hf}.npy", V)
cells = [m.dm.getHeightStratum(0)[1] for m in tail + [fine]]
print("ORPH", label, ORPH, "(orphans, empty after, repair flag)")
subs = [int(k.getIterationNumber()) for k in s.snes.getKSP().getPC().getFieldSplitSubKSP()]
print("ITS", label, "hf", hf, "cells", cells, "sub (vel, pres)", subs, "snes", s.snes.getIterationNumber(), "lin",
      s.snes.getLinearSolveIterations(), "reason", s.snes.getConvergedReason(), "|v|", float(np.linalg.norm(V)))
