"""Mesh-scale content of the wake vorticity: RMS of (omega - mean over the node's
neighbours) over RMS omega, in the wake x > 0.5, from the P1 omega checkpoints.
A field resolved by the mesh scores low; cell-to-cell structure scores near one."""
import os, sys, glob; os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
import h5py, numpy as np
from scipy.spatial import cKDTree, Delaunay
for run in sys.argv[1:]:
    files = sorted(glob.glob(f"runs/{run}/checkpoints/checkpoint.mesh.omega.*.h5"))
    files = [f for f in files if int(f[-8:-3]) >= 400][-6:]
    if not files: continue
    out = []
    for f in files:
        with h5py.File(f) as h: xy = h["fields/coordinates"][()]; w = h["fields/omega"][()]
        tri = Delaunay(xy); indptr, nbrs = tri.vertex_neighbor_vertices
        m = (xy[:, 0] > 0.5) & (xy[:, 1] > 0.02) & (xy[:, 1] < 0.39)
        mean_nb = np.array([w[nbrs[indptr[i]:indptr[i + 1]]].mean() for i in range(len(w))])
        out.append(np.sqrt(np.mean((w[m] - mean_nb[m]) ** 2)) / np.sqrt(np.mean(w[m] ** 2)))
    a = np.genfromtxt(f"runs/{run}/forces.csv", delimiter=",", names=True)
    over = f"{np.nanmax(a['fit_overshoot']):.3f}" if "fit_overshoot" in a.dtype.names else "-"
    tm = a['tau_max'][a['t'] > a['t'][-1] - 1]; tm = f"{np.nanmax(tm):.1f}" if np.isfinite(tm).any() else "-"
    print(f"{run:26s} roughness {np.mean(out):.3f} (steps {files[0][-8:-3]}..{files[-1][-8:-3]}); max overshoot {over}; tau_max over last unit {tm}")
