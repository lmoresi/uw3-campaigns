"""Import to log, for every barycentric build, the orphans before any repair and the empty
columns of what the build returned. Does not change the build."""
import numpy as np
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
