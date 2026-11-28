"""Hash every NullSpace.remove: the vector before and after, and the basis."""
import hashlib, sys
import numpy as np
from petsc4py import PETSc
import pytest

out = open(sys.argv[1], "w")
_remove = PETSc.NullSpace.remove
n = [0]


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:10]


def remove(self, vec):
    before = h(vec.getArray(readonly=True))
    basis = " ".join(h(v.getArray(readonly=True)) for v in self.getVecs())
    if n[0] == 2 and len(self.getVecs()) == 2:          # the third remove: the varying one
        np.save("rm3_before.npy", vec.getArray(readonly=True).copy())
        np.save("rm3_basis.npy", np.array([v.getArray(readonly=True).copy() for v in self.getVecs()]))
    r = _remove(self, vec)
    n[0] += 1
    al = lambda v: v.getArray(readonly=True).__array_interface__["data"][0] % 64
    out.write(f"align vec {al(vec)} basis {[al(v) for v in self.getVecs()]} type {vec.getType()} "
              f"remove {n[0]} nvec {len(self.getVecs())} const {self.hasConstant()} "
              f"before {before} after {h(vec.getArray(readonly=True))} basis {basis}\n")
    return r


PETSc.NullSpace.remove = remove
code = pytest.main(sys.argv[2:] + ["-q", "-p", "no:cacheprovider"])
out.close()
sys.exit(code)
