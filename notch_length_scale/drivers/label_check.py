"""Label integrity across the refinement hierarchy of a notch mesh, no solve: global
counts of cells per volume group and faces per boundary group at every level (each
should grow 8x per level in 3-D, 4x in 2-D), plus cells carrying two groups."""
import os
import sys

import numpy as np
import underworld3 as uw
from mpi4py import MPI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notch_model as nm   # noqa: E402
from underworld3.utilities.dm_labels import label_stratum_indices   # noqa: E402

params = uw.Params(uw_mesh=uw.Param("", description="gmsh file"),
                   uw_ref=uw.Param(1, description="refinement levels"))
mesh = nm.load_notch_mesh(str(params.uw_mesh), int(params.uw_ref))
comm = uw.mpi.comm
groups = [("Weak", 100, "cell"), ("Strong", 101, "cell"), ("Notch", 102, "cell")] + \
    [(b.name, b.value, "face") for b in (nm.boundaries3d if mesh.dim == 3 else nm.boundaries)]
for level, dm in enumerate(mesh.dm_hierarchy):
    cS, cE = dm.getHeightStratum(0)
    fS, fE = dm.getHeightStratum(1)
    # owned cells only (no overlap here, but be explicit via the point SF)
    sf = dm.getPointSF()
    _, leaves, _ = sf.getGraph()
    ghost = np.zeros(dm.getChart()[1], bool)
    if leaves is not None and len(leaves):
        ghost[np.asarray(leaves)] = True
    row = [f"L{level}", f"cells {comm.allreduce(int(np.sum(~ghost[cS:cE])))}"]
    sets = {}
    for name, val, kind in groups:
        lab = dm.getLabel(name)
        if lab is None:
            row.append(f"{name}:-")
            continue
        q = np.asarray(label_stratum_indices(lab, val), int)
        lo, hi = (cS, cE) if kind == "cell" else (fS, fE)
        q = q[(q >= lo) & (q < hi)]
        q = q[~ghost[q]]
        sets[name] = set(q.tolist())
        row.append(f"{name}:{comm.allreduce(len(q))}")
    both = len(sets.get("Weak", set()) & sets.get("Strong", set()))
    none = sum(1 for c in range(cS, cE) if not ghost[c] and c not in sets.get("Weak", set())
               and c not in sets.get("Strong", set()))
    row.append(f"weak&strong:{comm.allreduce(both)} unlabelled:{comm.allreduce(none)}")
    notch_not_weak = len(sets.get("Notch", set()) - sets.get("Weak", set()))
    row.append(f"notch-not-weak:{comm.allreduce(notch_not_weak)}")
    uw.pprint("  ".join(row))
uw.pprint(f"np {uw.mpi.size}")
