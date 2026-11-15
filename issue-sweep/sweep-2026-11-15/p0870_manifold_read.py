"""#870: MeshVariable.read_timestep on a manifold mesh, default (reconstructed-mesh) path."""
import os
import numpy as np
import underworld3 as uw

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_0870")
os.makedirs(out, exist_ok=True)
mesh = uw.meshing.SphericalManifold(radius=1.0, cellSize=0.4)
print("dim", mesh.dim, "cdim", mesh.cdim, flush=True)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1)
X = np.asarray(T.coords)
T.array[:, 0, 0] = X[:, 0] + 2 * X[:, 1] + 3 * X[:, 2]
mesh.write_timestep("m", index=0, outputPath=out, meshVars=[T])
R = uw.discretisation.MeshVariable("R", mesh, 1, degree=1)
try:
    R.read_timestep("m", "T", 0, outputPath=out)
    print("default path: max |R - T| =", np.abs(R.array - T.array).max(), flush=True)
except Exception as e:
    import traceback; traceback.print_exc()
