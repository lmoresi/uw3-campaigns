import numpy as np
def chi(tris):
    tris = np.asarray(tris)
    V = len(np.unique(tris)); E = len({tuple(sorted(e)) for t in tris for e in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0]))})
    return V - E + len(tris)
pts = np.array([[i, j] for i in range(9) for j in (0, 1)], float)
tris = []
for i in range(8):
    a, b, c, d = 2*i, 2*i+1, 2*i+2, 2*i+3; tris += [[a, c, b], [b, c, d]]
tris = np.array(tris)
print("strip chi", chi(tris))
a, b, c = tris[0]; q = len(pts)
full = np.vstack([[[a, b, q], [a, q, c], [b, c, q]], tris[1:]])
print("strip with sliver chi", chi(full), " sliver removed chi", chi(np.delete(full, 2, axis=0)))
print("strip notch (boundary triangle removed) chi", chi(tris[1:]))
