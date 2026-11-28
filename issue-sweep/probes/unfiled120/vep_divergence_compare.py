"""Compare two vep_divergence.py runs step by step.

    python vep_divergence_compare.py prefixA prefixB [steps]

Per step: the relative L2 difference of velocity and of the carried stress (against the
first run's norm), each also as a multiple of the solver tolerance, and both runs'
Newton and linear iteration counts.
"""
import sys
import numpy as np

a, b = sys.argv[1:3]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
print(f"{a} vs {b}")
print(f"{'step':>4s} {'rel dv':>10s} {'dv/tol':>8s} {'rel dstress':>12s} {'dS/tol':>8s}  its A (snes/lin)  its B")
for k in range(n):
    try:
        A, B = np.load(f"{a}-step{k}.npz"), np.load(f"{b}-step{k}.npz")
    except FileNotFoundError:
        break
    tol = float(A["tolerance"])
    dv = np.linalg.norm(A["v"] - B["v"]) / np.linalg.norm(A["v"])
    ds = np.linalg.norm(A["stress"] - B["stress"]) / max(np.linalg.norm(A["stress"]), 1e-300)
    print(f"{k:4d} {dv:10.2e} {dv / tol:8.2g} {ds:12.2e} {ds / tol:8.2g}  "
          f"{int(A['snes_its']):3d}/{int(A['linear_its']):<5d}     {int(B['snes_its']):3d}/{int(B['linear_its']):<5d}")
