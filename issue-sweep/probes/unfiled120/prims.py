import hashlib
import numpy as np
from petsc4py import PETSc
b = np.load("rm3_before.npy"); B = np.load("rm3_basis.npy")
vecs = []
for row in B:
    v = PETSc.Vec().createSeq(len(row)); v.setArray(row); vecs.append(v)
x = PETSc.Vec().createSeq(len(b)); x.setArray(b)
d = x.mDot(vecs)                                  # the coefficients
d1 = [x.dot(v) for v in vecs]                     # one at a time
y = x.copy(); y.maxpy([-c for c in d], vecs)       # the update, with mDot's coefficients
npd = [float(np.dot(b, row)) for row in B]
print("mdot", [c.hex() for c in d], "dot", [c.hex() for c in d1], "numpy", [c.hex() for c in npd],
      "maxpy", hashlib.sha256(y.getArray().tobytes()).hexdigest()[:10])
