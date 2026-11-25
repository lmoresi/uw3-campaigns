"""UNFILED 3, serial: does a cell-located transfer row depend on WHICH fine cell owns the node?
The parallel build takes the last local cell listing a node (_fine_cell_of_node), and local cell
order follows the partition. For each fine node shared by several fine cells, every candidate
owner's centroid is located and the row it would give is compared with the serial choice.

    python owner_choice.py <refinement> <chain> <split>"""
import sys, os, runpy
import numpy as np
ref, chain, split = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["p_893_k1.py", "-uw_refinement", ref, "-uw_chain", chain, "-uw_split", split, "-uw_solve", "0"]
g = runpy.run_path(os.path.expanduser("~/+Simulations/uw3-campaigns-w1/issue-sweep/probes/p_893_k1.py"), run_name="__main__")
from underworld3.utilities import fault_mg as fm
levels = g["tail"] + [g["fine"]]
POLY = g["POLY"]
from scipy.spatial import cKDTree
trace_tree = cKDTree(POLY)
degree = 2
for i in range(1, len(levels)):
    coarse, fine = levels[i - 1], levels[i]
    split_c, split_f = fm.is_split_level(coarse), fm.is_split_level(fine)
    cn = np.asarray(coarse._cell_node_indices(degree, True))
    fn = np.asarray(fine._cell_node_indices(degree, True))
    Xc = np.asarray(coarse._get_coords_for_basis(degree, True))
    Xf = np.asarray(fine._get_coords_for_basis(degree, True))
    vxy_c, cv_c = fm._cell_vertex_table(coarse)
    vxy_f, cv_f = fm._cell_vertex_table(fine)
    fcent = vxy_f[cv_f].mean(axis=1)
    pc, lamc = fm.locate_in_cells(fcent, vxy_c, cv_c)
    owner = fm._fine_cell_of_node(fn, Xf.shape[0])
    # every fine cell listing each node
    lists = [[] for _ in range(Xf.shape[0])]
    for k in range(fn.shape[0]):
        for nd in fn[k]:
            lists[nd].append(k)
    nodes, cand_cells = [], []
    for nd, ks in enumerate(lists):
        cs = sorted({int(pc[k]) for k in ks})
        if len(cs) > 1:
            nodes.append(nd); cand_cells.append([(k, int(pc[k])) for k in ks])
    diff_nodes = []
    for nd, kc in zip(nodes, cand_cells):
        rows = {}
        for k, c in kc:
            lam = fm._barycentric(Xf[nd:nd + 1], vxy_c[cv_c[[c]]])
            W = fm._node_weights(Xf[nd:nd + 1], np.array([c]), lam, Xc, cn, vxy_c, cv_c, degree)[0]
            row = {}
            for col, w in zip(cn[c], W):
                if abs(w) > 1e-13:
                    row[int(col)] = row.get(int(col), 0.0) + w
            rows[c] = (row, float(lam.min()))
        cs = list(rows)
        r0 = rows[cs[0]][0]
        worst, kinds = 0.0, set()
        for c in cs[1:]:
            r1 = rows[c][0]
            keys = set(r0) | set(r1)
            d = max(abs(r0.get(q, 0.0) - r1.get(q, 0.0)) for q in keys)
            worst = max(worst, d)
            if set(r0) != set(r1):
                kinds.add("columns")
        if worst > 1e-12:
            clamped = any(v[1] < -fm._INSIDE_TOL for v in rows.values())
            if clamped:
                kinds.add("clamped")
            diff_nodes.append((nd, worst, sorted(kinds), float(trace_tree.query(Xf[nd])[0])))
    dmax = max([d[3] for d in diff_nodes], default=float("nan"))
    print(f"PAIR {i - 1}->{i} split coarse {split_c} fine {split_f}: fine nodes {Xf.shape[0]}, "
          f"nodes whose candidate owners locate in different coarse cells {len(nodes)}, "
          f"of which rows differ {len(diff_nodes)} (kinds {sorted({k for d in diff_nodes for k in d[2]})}), "
          f"max |dW| {max([d[1] for d in diff_nodes], default=0):.2e}, farthest from the trace {dmax:.3g}", flush=True)
