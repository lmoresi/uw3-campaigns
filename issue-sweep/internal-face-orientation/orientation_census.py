"""One rank: the orientation of every labelled face in its first support cell.
PETSc's boundary residual maps quadrature points correctly only when this is 0
(or the face is an edge)."""
from collections import Counter

import underworld3 as uw


def census(name, mesh):
    dm = mesh.dm
    f_start, f_end = dm.getHeightStratum(1)
    label = dm.getLabel("UW_Boundaries")
    out = []
    for boundary in mesh.boundaries:
        stratum = label.getStratumIS(boundary.value)
        if not stratum or stratum.getSize() == 0:
            continue
        seen = Counter()
        for p in stratum.getIndices():
            if f_start <= p < f_end:
                cell = dm.getSupport(p)[0]
                seen[int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(p)])] += 1
        if seen:
            out.append(f"{boundary.name} {dict(sorted(seen.items()))}")
    print(f"{name}: " + "; ".join(out), flush=True)


box = dict(minCoords=(0, 0, 0), maxCoords=(1, 1, 1))
census("3-D simplex box, no refinement", uw.meshing.UnstructuredSimplexBox(cellSize=0.25, **box))
census("3-D simplex box, refinement 1", uw.meshing.UnstructuredSimplexBox(cellSize=0.25, refinement=1, **box))
census("3-D simplex box, refinement 2", uw.meshing.UnstructuredSimplexBox(cellSize=0.25, refinement=2, **box))
census("3-D hex box, no refinement", uw.meshing.StructuredQuadBox(elementRes=(3, 3, 3), **box))
census("spherical shell, refinement 1", uw.meshing.SphericalShell(radiusInner=0.55, radiusOuter=1.0, cellSize=0.4, refinement=1))
census("shell with internal surface, refinement 1", uw.meshing.SphericalShellInternalBoundary(
    radiusOuter=1.0, radiusInternal=0.775, radiusInner=0.55, cellSize=0.4, refinement=1))
