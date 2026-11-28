import numpy as np
from petsc4py import PETSc
rng = np.random.default_rng(1)
n = 622
a = rng.standard_normal(n); b = rng.standard_normal(n)
dots, mdots, addrs = set(), set(), set()
keep = []
for k in range(200):
    pad = PETSc.Vec().createSeq(int(rng.integers(1, 64)))      # perturb the allocator
    x = PETSc.Vec().createWithArray(a.copy()) if k % 2 else PETSc.Vec().createSeq(n)
    if not k % 2:
        x.setArray(a)
    y = PETSc.Vec().createSeq(n); y.setArray(b)
    z = PETSc.Vec().createSeq(n); z.setArray(b[::-1].copy())
    dots.add(repr(x.dot(y)))
    mdots.add(tuple(repr(v) for v in x.mDot([y, z])))
    addrs.add(x.getArray().__array_interface__["data"][0] % 64)
    keep.append((pad, x, y, z))
print("distinct dot results", len(dots), "distinct mDot results", len(mdots), "address residues mod 64", sorted(addrs))
print("numpy dot reference", repr(float(a @ b)))
