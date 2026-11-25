import json, glob, numpy as np
rows = []
for case in ["loop", "ti", "ti_mu1", "shell", "shell_mu1", "shell_n", "shell_mu1_n"]:
    def load(t):
        return [json.loads(l.split(" ", 3)[3]) for l in open(f"f27_{t}_{case}.log") if l.startswith("F27")]
    B, A = load("before"), load("after")
    for b, a in zip(B, A):
        k = b["step"]
        vb, va = np.load(f"f27_before_{case}_{k}.npy"), np.load(f"f27_after_{case}_{k}.npy")
        d = np.linalg.norm(va - vb) / np.linalg.norm(vb)
        rows.append((case, k, b["modes"], f"{b['outer']}/{b['vel']}/{b['pres']}", b["capped"]["velocity"], b["wall"],
                     f"{a['outer']}/{a['vel']}/{a['pres']}", a["capped"]["velocity"], a["wall"], d))
print("| case | step | modes | before o/v/p | capped | wall | after o/v/p | capped | wall | rel. change of v |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print("| %s | %d | %s | %s | %d | %.2f s | %s | %d | %.2f s | %.1e |" % r)
