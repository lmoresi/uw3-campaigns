"""UNFILED 3, serial bound on the effect: solve K1's split ladder with the fine-node owner chosen
as the LAST listing cell (development), the FIRST, or a seeded RANDOM one, and compare counts and
answers. python owner_effect.py <last|first|random:SEED> <refinement> <tol>"""
import sys, os, runpy
import numpy as np
mode, ref, tol = sys.argv[1], sys.argv[2], sys.argv[3]
from underworld3.utilities import fault_mg as fm
if mode != "last":
    def _owner(fn, n_nodes):
        lists = [[] for _ in range(n_nodes)]
        for k in range(fn.shape[0]):
            for nd in fn[k]:
                lists[nd].append(k)
        rng = np.random.default_rng(int(mode.split(":")[1])) if mode.startswith("random") else None
        out = np.full(n_nodes, -1, dtype=np.int64)
        for nd, ks in enumerate(lists):
            if ks:
                out[nd] = ks[0] if mode == "first" else ks[int(rng.integers(len(ks)))]
        return out
    fm._fine_cell_of_node = _owner
sys.argv = ["p_893_k1.py", "-uw_refinement", ref, "-uw_chain", "2", "-uw_split", "1", "-uw_tol", tol]
g = runpy.run_path(os.path.expanduser("~/+Simulations/uw3-campaigns-w1/issue-sweep/probes/p_893_k1.py"), run_name="__main__")
s, v = g["s"], g["v"]
i = s._rotated_freeslip_info
import underworld3 as uw
V = np.asarray(v.array).ravel()
if uw.mpi.size == 1:
    np.save(f"veff_{mode.replace(':', '')}_{ref}_{tol}.npy", V)
# the L2 norm by integration: independent of the partition (v.array holds ghost rows too)
vnorm = float(np.sqrt(uw.maths.Integral(g["fine"], v.sym.dot(v.sym)).evaluate()))
uw.pprint(f"EFF np {uw.mpi.size} {mode} ref {ref} tol {tol}: outer {i['ksp_its']} vel {i['vel_its_last']} pres {i['pres_its_last']} "
      f"capped {i.get('sub_capped')} converged {i['converged']} |v| {vnorm:.12e}")
