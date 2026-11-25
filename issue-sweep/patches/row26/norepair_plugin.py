"""Import to switch the barycentric builder's serial orphan repair off everywhere (option 2)."""
from underworld3.utilities import custom_mg
_orig = custom_mg.barycentric_prolongation
CALLS = []
def _norepair(coarse_coords, fine_coords, repair_orphans=True, stats=None):
    st = {} if stats is None else stats
    P = _orig(coarse_coords, fine_coords, repair_orphans=False, stats=st)
    CALLS.append(P.shape)
    return P
custom_mg.barycentric_prolongation = _norepair
for k, v in list(custom_mg._BUILDERS.items()):
    if v is _orig:
        custom_mg._BUILDERS[k] = _norepair
