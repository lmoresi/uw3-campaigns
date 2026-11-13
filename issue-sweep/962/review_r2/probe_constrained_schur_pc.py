"""Review r2 probe (serial): the constrained fixture of test_0786 with
multiplier_schur_pc = True. Does the multiplier block of P then differ from J's,
and do the two routines still agree bit for bit?"""
import importlib.util
import sys
from pathlib import Path

import underworld3 as uw

worktree = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "t0786", worktree / "tests/test_0786_stokes_jacobian_and_preconditioner_one_call_each.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

for flag in (False, True):
    uw.reset_default_model() if hasattr(uw, "reset_default_model") else None
    stokes = t._solver(uw.systems.Stokes_Constrained, "s" + str(int(flag)))
    stokes.add_essential_bc((0.0, 0.0), "Bottom")
    stokes.add_constraint_bc(0.0, "Left", normal=__import__("sympy").Matrix([[-1.0, 0.0]]))
    stokes.add_constraint_bc(0.0, "Right", normal=__import__("sympy").Matrix([[1.0, 0.0]]))
    stokes.multiplier_schur_pc = flag
    stokes.solve()
    print(f"== multiplier_schur_pc = {stokes.multiplier_schur_pc}: converged reason "
          f"{stokes.snes.getConvergedReason()}")
    J, P = t._assembled(stokes)
    d = P.copy(); d.axpy(-1.0, J)
    nf = stokes.dm.getNumFields()
    isets = {}
    for f in range(nf):
        iset, sub = stokes.dm.createSubDM(f)
        isets[f] = iset
        sub.destroy()
    blocks = []
    for a in range(nf):
        for b in range(nf):
            blk = d.createSubMatrix(isets[a], isets[b])
            if blk.norm() > 0:
                blocks.append((a, b, float(blk.norm())))
    print(f"   fields {nf}; blocks where P != J: {blocks}")
    t._use_the_one_pass_assembly_of_petsc(stokes.dm)
    J1, P1 = t._assembled(stokes)
    print(f"   PETSc one pass: J equal {J.equal(J1)}, P equal {P.equal(P1)}")
