"""P3 against P2 for the same scheme (res 40, relaxed mesh), with the SUPG res-80 reference.

  python p3_compare.py <out.png>
"""
import os, sys, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
PAIRS = [  # (P3 label, P2 label, name, colour)
    ("c40_p3-grid_C1", "c40_grid_C1", "SUPG + Eulerian stress, C 1", "#222222"),
    ("c40_p3-bn_C1", "c40_bn_C1", "SUPG + backward-nodes stress, C 1", "#1f77b4"),
    ("c40_p3-slbn_C1", "c40_slbn_C1", "SL momentum + backward-nodes, C 1", "#ff7f0e"),
    ("c40_p3-slbn_C2", None, "SL momentum + backward-nodes, C 2", "#d62728"),
    ("c40_p3-slbip_C2", "c40_sl-bip_C2", "SL momentum + backward-IP, C 2", "#17becf"),
    ("c40_p3-slbip_C4", "c40_sl-bip_C4", "SL momentum + backward-IP, C 4", "#2ca02c"),
    ("c40_p3-lag_C1", "c40_lag_C1", "SUPG + Lagrangian stress, C 1", "#9467bd"),
]


def load(l):
    f = os.path.join(R, str(l), "forces.csv")
    if not l or not os.path.exists(f):
        return None
    d = np.genfromtxt(f, delimiter=",", names=True, invalid_raise=False)
    return d if d.size > 1 else None


def stopped(l):
    q = os.path.join(R, "night_queue.log")
    return l is not None and os.path.exists(q) and f" {l} KILLED" in open(q).read()


fig, ax = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
ref = load("re100_grid_Wi05_r80")
cds, cls = [], []
if ref is not None:
    k = ref["t"] <= 2.05
    ax[0].plot(ref["t"][k], ref["cd"][k], color="#c0392b", lw=2.6, alpha=0.35, label="SUPG res 80, P2 (reference)")
    ax[1].plot(ref["t"][k], ref["cl"][k], color="#c0392b", lw=2.6, alpha=0.35)
    cds.append(ref["cd"][k & (ref["t"] >= 0.5)]); cls.append(ref["cl"][k])
for p3, p2, name, col in PAIRS:
    d3, d2 = load(p3), load(p2)
    if d3 is not None:
        tag = " (stopped)" if stopped(p3) else f" (t {d3['t'][-1]:.2f})"
        ax[0].plot(d3["t"], d3["cd"], color=col, lw=2.0, label=f"P3 {name}{tag}")
        ax[1].plot(d3["t"], d3["cl"], color=col, lw=2.0)
        ax[0].plot(d3["t"][-1], d3["cd"][-1], "x" if stopped(p3) else "o", color=col, ms=7, mew=2)
        cds.append(d3["cd"][d3["t"] >= 0.5]); cls.append(d3["cl"])
    if d2 is not None:
        k = d2["t"] <= 2.05
        ax[0].plot(d2["t"][k], d2["cd"][k], color=col, lw=1.0, ls=":", label=f"P2 {name}" + (" (stopped)" if stopped(p2) else ""))
        ax[1].plot(d2["t"][k], d2["cl"][k], color=col, lw=1.0, ls=":")
        if d2["t"].max() >= 1.0:
            cds.append(d2["cd"][k & (d2["t"] >= 0.5)]); cls.append(d2["cl"][k])


def span(a, pad=0.06):
    v = np.concatenate([x[np.isfinite(x)] for x in a if len(x)])
    lo, hi = v.min(), v.max()
    return lo - pad * (hi - lo), hi + pad * (hi - lo)


ax[0].set_ylim(*span(cds)); ax[1].set_ylim(*span(cls)); ax[0].set_xlim(0, 2.05)
for a in ax:
    a.grid(alpha=0.3); a.axvspan(0, 0.5, color="0.93", zorder=0)
ax[0].set_ylabel("cd"); ax[1].set_ylabel("cl"); ax[1].set_xlabel("t")
ax[0].legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0)
ax[0].set_title("Res 40, Re 100, Wi 0.5: P3 (solid) against P2 (dotted) for each scheme; o latest step, x stopped", fontsize=10, loc="left")
fig.savefig(sys.argv[1], dpi=110, bbox_inches="tight")
print("wrote", sys.argv[1])
