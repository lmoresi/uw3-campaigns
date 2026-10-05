"""Ringing check: the carried log-conformation, the stress decoded from it and the
projected tau_II the checkpoints hold, along rings round the cylinder, from a
-uw_dump_history run. python ring_profiles.py <run>"""
import sys, glob, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
run = sys.argv[1]
Z = [np.load(f) for f in sorted(glob.glob(f"runs/{run}/history_rank*.npz"))]
X = np.vstack([z["X"] for z in Z]); L = np.vstack([z["log_conf"] for z in Z])
D = np.vstack([z["decoded"] for z in Z]); TP = np.concatenate([z["tau_proj"] for z in Z])
_, keep = np.unique(np.round(X, 9), axis=0, return_index=True); X, L, D, TP = X[keep], L[keep], D[keep], TP[keep]
r = np.hypot(X[:, 0] - 0.2, X[:, 1] - 0.2); th = np.degrees(np.arctan2(X[:, 1] - 0.2, X[:, 0] - 0.2))
tau_dec = np.sqrt(0.5 * (D[:, 0] ** 2 + 2 * D[:, 1] ** 2 + D[:, 2] ** 2))
tr = L[:, 0] + L[:, 2]                      # trace of the log-conformation (xx + yy)
bands = ((0.0490, 0.0505, "wall nodes (0.049 < r < 0.0505)"), (0.055, 0.0695, "first ring out (0.055 < r < 0.07)"), (0.07, 0.09, "second ring (0.07 < r < 0.09)"))
def rough(y):
    y = np.asarray(y); d2 = y[2:] - 2 * y[1:-1] + y[:-2]
    return np.sqrt(np.mean(d2 ** 2)) / max(np.sqrt(np.mean((y - y.mean()) ** 2)), 1e-300)
fig, axes = plt.subplots(len(bands), 1, figsize=(11, 9), sharex=True)
for ax, (lo, hi, name) in zip(axes, bands):
    m = (r >= lo) & (r < hi); o = np.argsort(th[m]); t = th[m][o]
    for y, lab, c in ((tr[m][o], "trace of log-conformation (carried)", "k"), (tau_dec[m][o], "tau_II decoded at the nodes", "C3"), (TP[m][o], "tau_II projected (what is plotted)", "C0")):
        ax.plot(t, y / np.abs(y).max(), ".-", ms=3, lw=0.8, color=c, label=f"{lab}; roughness {rough(y):.2f}")
    ax.set_title(f"{name}: {m.sum()} nodes, each curve scaled by its own maximum"); ax.legend(fontsize=8, loc="upper right"); ax.axhline(0, color="0.7", lw=0.5)
    print(f"{name:40s} n {m.sum():4d}  roughness: log-conf {rough(tr[m][o]):.2f}  decoded {rough(tau_dec[m][o]):.2f}  projected {rough(TP[m][o]):.2f}")
axes[-1].set_xlabel("angle round the cylinder (degrees; 0 = rear, +-180 = front)")
fig.suptitle(f"{run}: ringing of the carried stress against its decoded and projected invariants"); fig.tight_layout()
fig.savefig(f"runs/{run}/ring_profiles.png", dpi=110); print("wrote", f"runs/{run}/ring_profiles.png")
