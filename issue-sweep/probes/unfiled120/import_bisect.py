import hashlib, importlib, sys
for name in sys.argv[1:]:
    importlib.import_module(name)
import numpy as np
from petsc4py import PETSc
b = np.load("rm3_before.npy"); B = np.load("rm3_basis.npy")
vecs = []
for row in B:
    v = PETSc.Vec().createSeq(len(row)); v.setArray(row); vecs.append(v)
ns = PETSc.NullSpace().create(vectors=vecs)
x = PETSc.Vec().createSeq(len(b)); x.setArray(b)
ns.remove(x)
print(hashlib.sha256(x.getArray().tobytes()).hexdigest()[:10], flush=True)
