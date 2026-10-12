"""Does the library's label-driven refinement callback (spherical / annulus) leave
shared vertices inconsistent between ranks, as the notch's arc snap did in 3-D?

Builds an Annulus (2-D) and a SphericalShell (3-D) with refinement, and at every
hierarchy level reports:
  - mismatch: max |local coordinate - owner's coordinate| over every local vertex
    (ghosts included), from the coordinate DM's localToGlobal / globalToLocal;
  - label: max |r - r_o| over the vertices this rank finds in the Upper closure
    (petsc_dm_find_labeled_points_local, what the callback uses), and |r - r_i| for
    Lower;
  - or-label: the same over the Upper / Lower flag OR-ed over all ranks, which also
    catches a vertex some other rank labels but this one does not.

Usage: mpirun -n 4 python library_snap_probe.py -uw_ref 2
"""
import numpy as np
import underworld3 as uw
from mpi4py import MPI
from petsc4py import PETSc

params = uw.Params(uw_ref=uw.Param(2, description="refinement"))
comm = uw.mpi.comm
ro, ri = 1.0, 0.547


def mismatch(dm):
    cdm = dm.getCoordinateDM()
    loc = dm.getCoordinatesLocal()
    g = cdm.createGlobalVec()
    cdm.localToGlobal(loc, g)
    back = cdm.createLocalVec()
    cdm.globalToLocal(g, back)
    d = float(np.max(np.abs(back.array - loc.array))) if loc.getLocalSize() else 0.0
    return comm.allreduce(d, op=MPI.MAX)


def closure(dm, name):
    if not dm.getLabel(name):
        return np.array([], int)
    idx = uw.cython.petsc_discretisation.petsc_dm_find_labeled_points_local(dm, name)
    return np.unique(np.asarray(idx, int))


def or_flag(dm, idx, cdim):
    cdm = dm.getCoordinateDM()
    lf = cdm.createLocalVec()
    lf.set(0.0)
    if len(idx):
        lf.array.reshape(-1, cdim)[idx, 0] = 1.0
    gf = cdm.createGlobalVec()
    gf.set(0.0)
    cdm.localToGlobal(lf, gf, addv=PETSc.InsertMode.ADD_VALUES)
    cdm.globalToLocal(gf, lf, addv=PETSc.InsertMode.INSERT_VALUES)
    return np.flatnonzero(lf.array.reshape(-1, cdim)[:, 0] > 0.5)


def rmax(R, idx, r0):
    v = float(np.max(np.abs(R[idx] - r0))) if len(idx) else 0.0
    return comm.allreduce(v, op=MPI.MAX)


def probe(label, mesh):
    for level, dm in enumerate(mesh.dm_hierarchy):
        cdim = dm.getCoordinateDim()
        X = dm.getCoordinatesLocal().array.reshape(-1, cdim)
        R = np.linalg.norm(X, axis=1)
        up, lo = closure(dm, "Upper"), closure(dm, "Lower")
        up_or, lo_or = or_flag(dm, up, cdim), or_flag(dm, lo, cdim)
        extra = comm.allreduce(int(len(np.setdiff1d(up_or, up)) + len(np.setdiff1d(lo_or, lo))))
        row = (label, level, mismatch(dm), rmax(R, up, ro), rmax(R, lo, ri),
               rmax(R, up_or, ro), rmax(R, lo_or, ri), extra)
        uw.pprint("{:8s} lvl {}  mismatch {:.2e}  label |r-ro| {:.2e} |r-ri| {:.2e}  "
                  "or-label |r-ro| {:.2e} |r-ri| {:.2e}  vertices labelled only elsewhere {}"
                  .format(*row))


ref = int(params.uw_ref)
probe("Annulus", uw.meshing.Annulus(radiusOuter=ro, radiusInner=ri, cellSize=0.1, refinement=ref))
probe("Shell", uw.meshing.SphericalShell(radiusOuter=ro, radiusInner=ri, cellSize=0.3,
                                         refinement=ref))
uw.pprint(f"np {uw.mpi.size}")
