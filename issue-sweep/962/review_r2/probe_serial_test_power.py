"""Review r2 probe (serial): what the serial test_0786 can and cannot see.

1. Is stokes.dm the DM the SNES assembles on?
2. DMPlexJacobianFE events per computeJacobian under each routine.
3. One matrix handed for both (J == P): is it the Jacobian of the two-matrix call?
4. The matrices P - J: which blocks differ (what a wrong-table mutant could hide in).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from petsc4py import PETSc

import underworld3 as uw

PETSc.Log.begin()
worktree = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "t0786", worktree / "tests/test_0786_stokes_jacobian_and_preconditioner_one_call_each.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def events():
    return PETSc.Log.Event("DMPlexJacobianFE").getPerfInfo()["count"]


for build in (t._plain, t._nitsche, t._constrained):
    stokes = build()
    stokes.solve()
    snes_dm = stokes.snes.getDM()
    print(f"== {build.__name__}: stokes.dm handle == snes dm handle: {stokes.dm.handle == snes_dm.handle}; "
          f"routine on snes dm is PETSc's: {t._has_the_one_pass_assembly_of_petsc(snes_dm)}")
    J, P, _ = stokes.snes.getJacobian()
    x = stokes.snes.getSolution()

    n0 = events()
    stokes.snes.computeJacobian(x, J, P)
    n1 = events()
    Ju, Pu = J.copy(), P.copy()
    print(f"   branch routine: DMPlexJacobianFE events per computeJacobian = {n1 - n0}")

    # one matrix for both, through the branch's routine (its J == P early return)
    J1 = J.copy()
    stokes.snes.computeJacobian(x, J1, J1)
    d = J1.copy(); d.axpy(-1.0, Ju)
    print(f"   one matrix (J == P): |J_one - J_two| / |J_two| = {d.norm() / Ju.norm():.6e}")
    d = J1.copy(); d.axpy(-1.0, Pu)
    print(f"   one matrix (J == P): |J_one - P_two| / |P_two| = {d.norm() / Pu.norm():.6e}")

    d = Pu.copy(); d.axpy(-1.0, Ju)
    print(f"   |P - J| / |J| = {d.norm() / Ju.norm():.6e}")
    # which field blocks differ
    names = []
    isets = {}
    nf = stokes.dm.getNumFields()
    for f in range(nf):
        iset, sub = stokes.dm.createSubDM(f)
        isets[f] = iset
        sub.destroy()
    for a in range(nf):
        for b in range(nf):
            blk = d.createSubMatrix(isets[a], isets[b])
            if blk.norm() > 0:
                names.append((a, b, float(blk.norm())))
    print(f"   blocks where P != J: {names}")

    t._use_the_one_pass_assembly_of_petsc(stokes.dm)
    n0 = events()
    stokes.snes.computeJacobian(x, J, P)
    n1 = events()
    print(f"   PETSc routine: DMPlexJacobianFE events per computeJacobian = {n1 - n0}; "
          f"J equal {J.equal(Ju)}, P equal {P.equal(Pu)}")
    J1b = J.copy()
    stokes.snes.computeJacobian(x, J1b, J1b)
    print(f"   PETSc routine, one matrix: equals the branch's one-matrix result: {J1b.equal(J1)}")
