"""K1's #893 fixture, with or without the serial orphan repair; prints KSP iterations and the
velocity. python run_k1.py <repair|norepair> <refinement> <chain>"""
import sys, runpy, os
import numpy as np
mode, ref, chain = sys.argv[1], sys.argv[2], sys.argv[3]
if mode == "norepair":
    import norepair_plugin  # noqa
sys.argv = ["p_893_k1.py", "-uw_refinement", ref, "-uw_chain", chain, "-uw_tol", sys.argv[4] if len(sys.argv) > 4 else "1e-4"]
g = runpy.run_path(os.path.expanduser("~/+Simulations/uw3-campaigns-w1/issue-sweep/probes/p_893_k1.py"),
                   run_name="__main__")
s, v = g["s"], g["v"]
ksp = s.snes.getKSP()
V = np.asarray(v.array).reshape(-1, 2)
np.save(f"v_{mode}_r{ref}_c{chain}.npy", V)
info = s._rotated_freeslip_info
print("ITS", mode, "ref", ref, "chain", chain, "outer", info["ksp_its"], "vel", info["vel_its_last"],
      "pres", info["pres_its_last"], "reason", info["ksp_reason"], "rnorm/rnorm0",
      float(info["rnorm"]) / float(info["rnorm0"]), "|v|", float(np.linalg.norm(V)))
