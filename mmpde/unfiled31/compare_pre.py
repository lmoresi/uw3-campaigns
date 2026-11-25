"""Pre-#1258 runs against the serial run, matched by original vertex position."""
import numpy as np
ref = np.load("out/pre_np1.npy")
ref_new = np.load("out/np1.npy")
print(f"serial pre-#1258 vs serial development: max {np.abs(ref - ref_new).max():.3e}")
for tag in ["pre_np2", "pre_np3", "pre_np4", "pre_rand3np4", "pre_emptynp4"]:
    a = np.load(f"out/{tag}.npy")
    assert np.array_equal(a[:, :2], ref[:, :2])
    d = np.linalg.norm(a[:, 2:] - ref[:, 2:], axis=1)
    print(f"{tag:13s} max |x - x_serial| {d.max():.3e}  vertices off > 1e-6: {(d > 1e-6).sum()}")
