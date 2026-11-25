"""pytest plugin: every barycentric_prolongation call also runs development's
builder and asserts the two CSR matrices are bit-identical."""
import json, os
import numpy as np
from underworld3.utilities import custom_mg

_ns = {"np": np, "_record": custom_mg._record}
exec(open(os.path.join(os.path.dirname(__file__), "old_bary.py")).read(), _ns)
_old = _ns["_old_barycentric_prolongation"]
_new = custom_mg.barycentric_prolongation
LOG = os.path.join(os.path.dirname(__file__), "ab_calls.jsonl")


def _wrapped(coarse_coords, fine_coords, repair_orphans=True, stats=None):
    s1, s2 = {}, {}
    Pn = _new(coarse_coords, fine_coords, repair_orphans=repair_orphans, stats=s1)
    Po = _old(coarse_coords, fine_coords, repair_orphans=repair_orphans, stats=s2)
    same = (Pn.shape == Po.shape and (Pn != Po).nnz == 0
            and s1["orphans_repaired"] == s2["orphans_repaired"])
    with open(LOG, "a") as fh:
        fh.write(json.dumps({"shape": list(Pn.shape), "repair": bool(repair_orphans),
                             "orphans": s1["orphans_repaired"], "nnz": int(Pn.nnz),
                             "same": bool(same)}) + "\n")
    assert same, "bounded orphan query changed the transfer"
    if stats is not None:
        stats.update(s1)
    return Pn


custom_mg.barycentric_prolongation = _wrapped
for key, val in list(custom_mg._BUILDERS.items()):
    if val is _new:
        custom_mg._BUILDERS[key] = _wrapped
