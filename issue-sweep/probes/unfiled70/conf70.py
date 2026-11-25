"""UNFILED 70: is Mesh.add_conforming_surface's cut ever empty or partial? The same smooth traces
as UNFILED 68 (6 cells, lines and gentle arcs, forward and reversed), sampled at DS cells; each
result is classified with 68's check (_refuse_an_empty_or_partial_cut on the child's label).

    python conf70.py <box_irr|box_reg> <DS>"""
import sys, warnings
import numpy as np
mesh_kind, DS = sys.argv[1], float(sys.argv[2])
sys.argv = sys.argv[:1]
import underworld3 as uw
from underworld3.utilities.fault_split import _refuse_an_empty_or_partial_cut
warnings.simplefilter("ignore")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12,
                                         regular=(mesh_kind == "box_reg"))
h = 1 / 12
rng = np.random.default_rng(22)
import os
CROSS = bool(int(os.environ.get("CROSS", "0")))
out = {"raised": 0, "empty": 0, "partial": 0, "complete": 0}
reasons = {}
KIND = []
for k in range(20):
    ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
    c = 0.5 + rng.uniform(-0.05, 0.05, 2)
    L = (1.6 if CROSS else 6 * h); n = max(2, int(round(L / (DS * h))))
    s = np.linspace(-L / 2, L / 2, n + 1)
    th = ang + turn * s / L
    d = np.column_stack([np.cos(th), np.sin(th)])
    P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
    ins = np.all((P >= 0) & (P <= 1), axis=1)
    runs = np.flatnonzero(np.diff(ins.astype(int)) != 0)
    if CROSS and (ins[0] or ins[-1] or len(runs) != 2):
        out["skipped (leaves and re-enters)"] = out.get("skipped (leaves and re-enters)", 0) + 2
        continue
    for j, Q in enumerate((P, P[::-1].copy())):
        name = f"S{k}_{j}"
        try:
            child = mesh.add_conforming_surface(uw.meshing.Surface(name, mesh, Q))
        except Exception as e:
            out["raised"] += 1; r = str(e)[:60]; reasons[r] = reasons.get(r, 0) + 1; continue
        b = [bb for bb in child.boundaries if bb.name == name][0]
        try:
            inside = np.all((Q >= 0) & (Q <= 1), axis=1)
            _refuse_an_empty_or_partial_cut(child.dm, name, b.value, Q[inside] if CROSS else Q)
            out["complete"] += 1; KIND.append((k, j, "complete"))
        except ValueError as e:
            out["empty" if "no facet" in str(e) else "partial"] += 1; KIND.append((k, j, ("empty" if "no facet" in str(e) else "partial") + " " + str(e)[60:150]))
print(f"CONF70 {'crossing' if CROSS else 'interior'} {mesh_kind} ds {DS}: {out}", flush=True)
print(f"CONF70REASONS {reasons}", flush=True)
for x in KIND[:12]:
    print("KIND", x, flush=True)
