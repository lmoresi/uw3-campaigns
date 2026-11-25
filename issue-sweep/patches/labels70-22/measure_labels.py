"""UNFILED 22/70: the cut's edge labelling, old rule (midpoint on the line) against new
(consecutive along the line, chord >= 0.5 x arc), on the same build.

    RULE=old|new python measure_labels.py <path: fault|surface> <mesh: box_irr|box_reg> <family> <DS>
families: lines_arcs (68's interior traces for fault, 70's crossings for surface),
hairpin (two arms half a cell apart joined by a half circle), approach (an S that passes within
0.4 cells of itself). Outcome per call: raised / empty / partial / complete, and 'spurious' when
a labelled edge's arc along the trace between its ends exceeds twice its chord."""
import os, sys, warnings
import numpy as np
path, mesh_kind, family, DS = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
sys.argv = sys.argv[:1]
import underworld3 as uw
from underworld3.utilities import line_cut as lc
from underworld3.utilities.fault_split import _refuse_an_empty_or_partial_cut
if os.environ.get("RULE", "new") == "old":
    ns = dict(lc.__dict__)
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "old_label.py")).read(), ns)
    lc._label_cut_edges = ns["_old_label_cut_edges"]
PULL = os.environ.get("PULL", "all")
if PULL != "all":
    os.environ["THIN"] = "1.0" if PULL == "thin" else "0"
    import corners_plugin  # noqa: add_fault's pulls only (tips, turns > 45 deg[, ~1 cell apart])
warnings.simplefilter("ignore")
h = 1 / 12
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h, regular=(mesh_kind == "box_reg"))
rng = np.random.default_rng(22)

def resample(P, ds):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], max(2, int(round(cum[-1] / ds))) + 1)
    return np.column_stack([np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])])

def traces():
    out = []
    if family == "lines_arcs":
        for k in range(20):
            ang = rng.uniform(0, np.pi); turn = rng.uniform(-1, 1) if k % 2 else 0.0
            c = 0.5 + rng.uniform(-0.05, 0.05, 2)
            L = 1.6 if path == "surface" else 6 * h
            s = np.linspace(-L / 2, L / 2, 400); th = ang + turn * s / L
            d = np.column_stack([np.cos(th), np.sin(th)])
            P = c + np.cumsum(np.vstack([[0, 0], d[1:] * np.diff(s)[:, None]]), axis=0) - L / 2 * d[0]
            out.append(resample(P, DS * h))
    elif family == "hairpin":
        for k in range(10):
            gap = 0.5 * h; ang = rng.uniform(0, 2 * np.pi); c = 0.5 + rng.uniform(-0.05, 0.05, 2)
            arm = (0.7 if path == "surface" else 3 * h)
            a = np.linspace(0, arm, 100); psi = np.linspace(np.pi / 2, -np.pi / 2, 60)
            P = np.vstack([np.column_stack([-a[::-1], np.full(100, gap / 2)]),
                           np.column_stack([gap / 2 * np.cos(psi), gap / 2 * np.sin(psi)])[1:-1],
                           np.column_stack([-a, np.full(100, -gap / 2)])])
            R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
            out.append(resample(c + P @ R.T, DS * h))
    else:  # approach: an arc of 1.9 pi, radius 1.5 cells: its ends pass ~0.47 cells apart
        for k in range(10):
            ang = rng.uniform(0, 2 * np.pi); c = 0.5 + rng.uniform(-0.05, 0.05, 2)
            t = np.linspace(0, 1.9 * np.pi, 400); r = 1.5 * h
            P = np.column_stack([r * np.cos(t), r * np.sin(t)])
            if path == "surface":   # run both ends out past the walls
                P = np.vstack([P[0] + np.outer(np.linspace(0.8, 0, 80)[:-1], [0, -1]), P,
                               P[-1] + np.outer(np.linspace(0, 0.8, 80)[1:], [np.cos(1.9 * np.pi + np.pi / 2), np.sin(1.9 * np.pi + np.pi / 2)])])
            R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
            out.append(resample(c + P @ R.T, DS * h))
    return out

def arcs_of_chain(dm, lab, value, Q):
    vS, _ = dm.getDepthStratum(0)
    X = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, 2)
    E = lab.getStratumIS(value).getIndices()
    ends = np.array([dm.getCone(int(e)) for e in E]) - vS
    d, t = lc._line_parameters(X, Q) if hasattr(lc, "_line_parameters") else (None, None)
    if t is None:
        return 0
    chord = np.linalg.norm(X[ends[:, 0]] - X[ends[:, 1]], axis=1)
    arc = np.abs(t[ends[:, 0]] - t[ends[:, 1]])
    return int((arc > 2 * chord + 1e-9).sum())

out = {"raised": 0, "empty": 0, "partial": 0, "complete": 0, "spurious": 0}
for k, P in enumerate(traces()):
    for j, Q in enumerate((P, P[::-1].copy())):
        name = f"S{k}_{j}"
        try:
            child = (mesh.add_conforming_surface(uw.meshing.Surface(name, mesh, Q)) if path == "surface"
                     else mesh.add_fault((name, Q)))
        except Exception as e:
            if "labelled no facet" in str(e):
                out["empty"] += 1
            elif "misses part of the trace" in str(e):
                out["partial"] += 1
            else:
                out["raised"] += 1
            continue
        b = [bb for bb in child.boundaries if bb.name == name][0]
        lab = child.dm.getLabel(name)
        inside = np.all((Q >= 0) & (Q <= 1), axis=1)
        try:
            _refuse_an_empty_or_partial_cut(child.dm, name, b.value, Q[inside])
            out["complete"] += 1
        except ValueError as e:
            out["empty" if "no facet" in str(e) else "partial"] += 1
        if lab is not None and lab.getStratumSize(b.value):
            out["spurious"] += arcs_of_chain(child.dm, lab, b.value, Q) > 0
print(f"LAB {os.environ.get('RULE', 'new')} pull={PULL} {path} {mesh_kind} {family} ds {DS}: {out}", flush=True)
