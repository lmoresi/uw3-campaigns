# #1158 review (copied from #1145 review, + emptyband): shell partition of every gmsh mesh, only in MPI ranks.
#   LAYOUT=band   cells by centroid height into equal bands, rank 0 at the bottom
#                 (at np >= 3 the middle ranks hold no Top or Bottom facet)
#   LAYOUT=randN  random assignment, seed N
import os
import sys
# 2026-11-16 copy: skip in the JIT build subprocess (setup.py), which inherits PMI_RANK
if os.environ.get("LAYOUT") and os.environ.get("PMI_RANK") is not None and not sys.argv[0].endswith("setup.py"):
    import numpy as np
    from petsc4py import PETSc
    import underworld3 as uw
    dmod = uw.discretisation.discretisation_mesh
    _orig = dmod._from_plexh5
    def _hook(*a, **k):
        res = _orig(*a, **k)
        if not isinstance(res, tuple):
            return res
        sf0, dm = res
        cS, cE = dm.getHeightStratum(0); n = cE - cS
        size = uw.mpi.size
        lay = os.environ["LAYOUT"]
        if lay == "band":
            vS, vE = dm.getDepthStratum(0)
            X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dm.getCoordinateDim())
            ymid = np.array([X[[p - vS for p in dm.getTransitiveClosure(c)[0] if vS <= p < vE], 1].mean()
                             for c in range(cS, cE)]) if n else np.zeros(0)
            yn = (ymid - ymid.min()) / max(np.ptp(ymid), 1e-300) if n else ymid
            assign = np.minimum((yn * size).astype(int), size - 1) if n else np.zeros(0, int)
        elif lay == "emptyband":
            # bands over size-1 ranks; the LAST rank gets no cells
            vS, vE = dm.getDepthStratum(0)
            X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dm.getCoordinateDim())
            ymid = np.array([X[[p - vS for p in dm.getTransitiveClosure(c)[0] if vS <= p < vE], 1].mean()
                             for c in range(cS, cE)]) if n else np.zeros(0)
            m = max(size - 1, 1)
            yn = (ymid - ymid.min()) / max(np.ptp(ymid), 1e-300) if n else ymid
            assign = np.minimum((yn * m).astype(int), m - 1) if n else np.zeros(0, int)
        else:
            assign = np.random.default_rng(int(lay[4:] or 0)).integers(0, size, n)
        part = dm.getPartitioner(); part.setType(PETSc.Partitioner.Type.SHELL)
        part.setShellPartition(size, sizes=np.bincount(assign, minlength=size).astype(np.int32),
                               points=np.argsort(assign, kind="stable").astype(np.int32))
        return sf0, dm
    dmod._from_plexh5 = _hook
