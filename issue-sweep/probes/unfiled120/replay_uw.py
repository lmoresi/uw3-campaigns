import hashlib, sys
import numpy as np
import underworld3 as uw
from petsc4py import PETSc
if len(sys.argv) > 1:
    m = uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.5, cellSize=0.5) if sys.argv[1] == "shell" \
        else uw.meshing.UnstructuredSimplexBox(cellSize=0.2)
b = np.load("rm3_before.npy"); B = np.load("rm3_basis.npy")
vecs = []
for row in B:
    v = PETSc.Vec().createSeq(len(row)); v.setArray(row); vecs.append(v)
ns = PETSc.NullSpace().create(vectors=vecs)
x = PETSc.Vec().createSeq(len(b)); x.setArray(b)
ns.remove(x)
print(hashlib.sha256(x.getArray().tobytes()).hexdigest()[:10], flush=True)
