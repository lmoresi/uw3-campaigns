"""#1134 review side probe: SphericalShell.adapt with max_levels=3, no wrapper.

Serial. Same call as adapt_route.py's ``shell`` case, with the installed
transfer untouched (``watch=0``) or with the condition removed in memory
(``mutant=1``), to see whether the refine error depends on either.
"""
import inspect
import textwrap
import traceback

import numpy as np
import underworld3 as uw
from underworld3.utilities import nvb

params = uw.Params(cell_size=0.5, refinement=1, max_levels=3, ratio=2.0, mutant=0)

if params.mutant:
    src = textwrap.dedent(inspect.getsource(nvb._nested_prolongation_local))
    old = " and in_one_cell(p_, q_)"
    assert src.count(old) == 1
    src = src.replace(old, "")
    if params.mutant == 2:          # also drop the vertex-to-cell table: development's text
        start = src.index("        ccS, ccE = coarse_dm.getHeightStratum(0)")
        stop = src.index("        nbr = [[] for _ in range(n_f)]")
        src = src[:start] + src[stop:]
    exec(compile(src, "<mutant>", "exec"), nvb.__dict__)

base = uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.5, cellSize=params.cell_size,
                                 refinement=(params.refinement or None), qdegree=2)


def metric(centroids):
    d = np.abs(np.linalg.norm(np.asarray(centroids), axis=1) - 0.75)
    return 1.0 / np.minimum(np.sqrt(0.05**2 + (2.0 * d) ** 2), 0.3) ** 2


print(f"shell adapt, no wrapper: cell_size={params.cell_size} max_levels={params.max_levels} "
      f"mutant={params.mutant}", flush=True)
try:
    child = base.adapt(metric, max_levels=params.max_levels, mg_coarsening_ratio=params.ratio)
    P = child._adapt_prolongation
    print(f"RESULT adapt returned; recorded transfers {len(P)}, None {sum(p is None for p in P)}",
          flush=True)
except Exception as exc:
    traceback.print_exc()
    print(f"RESULT adapt raised {type(exc).__name__}: {exc}", flush=True)
