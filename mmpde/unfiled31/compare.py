"""Moved vertex positions of each run against the serial run, matched by original position."""
import sys
import numpy as np
ref = np.load("out/np1.npy")
for tag in sys.argv[1:]:
    a = np.load(f"out/{tag}.npy")
    assert np.array_equal(a[:, :2], ref[:, :2]), tag
    d = np.linalg.norm(a[:, 2:] - ref[:, 2:], axis=1)
    moved = np.linalg.norm(ref[:, 2:] - ref[:, :2], axis=1)
    print(f"{tag:10s} vertices {len(a)}  max |x - x_serial| {d.max():.3e}  "
          f"median {np.median(d):.3e}  (largest serial move {moved.max():.3e})")
