"""Wall chord lengths on the annulus the ZG95 drivers build: unit depth, radius ratio
0.55 (r_o = 1/0.45, r_i = 0.55/0.45), uw.meshing.Annulus(cellSize=0.5, refinement=4)
(refined boundary nodes snapped to the circles). Equal chords make the given radial
normal consistent at the vertices (r_i = (|f1|^2 - |f2|^2)/(12 R) = 0).

    python chords_refined.py -uw_refinement 4
"""
import numpy as np
import underworld3 as uw

params = uw.Params(uw_refinement=4, uw_cell=0.5)
r_o, r_i = 1 / 0.45, 0.55 / 0.45
mesh = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=float(params.uw_cell),
                          refinement=int(params.uw_refinement), qdegree=3)
dm = mesh.dm
coords = dm.getCoordinatesLocal().array.reshape(-1, 2)
csec = dm.getCoordinateSection()
fS, fE = dm.getHeightStratum(1)
for wall, R in (("Upper", r_o), ("Lower", r_i)):
    facets = [int(q) for q in dm.getLabel(wall).getStratumIS(mesh.boundaries[wall].value).getIndices()
              if fS <= q < fE]
    L = np.array([np.linalg.norm(coords[csec.getOffset(int(dm.getCone(f)[1])) // 2]
                                 - coords[csec.getOffset(int(dm.getCone(f)[0])) // 2]) for f in facets])
    uw.pprint(f"refinement {params.uw_refinement}, {wall} (R {R:.4f}): {len(L)} chords, length "
              f"{L.min():.6e} to {L.max():.6e}, relative spread {(L.max() - L.min()) / L.mean():.3e}")
