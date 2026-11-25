import runpy, numpy as np
from underworld3.utilities import custom_mg
ns = {"np": np, "_record": custom_mg._record}; exec(open("old_bary.py").read(), ns)
T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_0893_custom_mg_orphan_repair_memory.py")
c, f = T["_clouds"]()
P0 = custom_mg.barycentric_prolongation(c, f, repair_orphans=False)
orph = np.flatnonzero(np.asarray((P0 != 0).sum(axis=0)).ravel() == 0)
ref = T["_greedy_reference"](c, f, orph)
print("orphans", len(orph), "claims", len(ref), "development == reference:", T["_claims"](ns["_old_barycentric_prolongation"](c, f), P0) == ref,
      "| new == reference:", T["_claims"](custom_mg.barycentric_prolongation(c, f), P0) == ref)
