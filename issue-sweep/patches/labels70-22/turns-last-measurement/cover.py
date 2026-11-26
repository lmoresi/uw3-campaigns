"""Coverage threshold for the empty-or-partial refusal (labels70-22 round 2).
For every trace of the box grid, with the refusal RECORDING instead of raising: the chain's
pieces (by global vertex number), the worst trace-to-chain distance in base-mesh cells (median of
the 6 nearest base edges, the library's _base_cell_size), and the frictionless-fault max slip,
against the same curve sampled one cell apart on the same mesh (the reference, kept only when it
is one piece within 0.25 cells). One JSON line per (trace, sampling).

    python cover.py <box_irr|box_reg> <lines_arcs|kinks>"""
import os, sys, json, warnings
import numpy as np
mesh_kind, family = sys.argv[1], sys.argv[2]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pull22.py")).read()
pre = src.split("for n, (tag, Q) in enumerate(traces()):")[0]
from underworld3.utilities import fault_split as fs
rec_box = {}
def recorder(dm, name, value, poly, caller="add_fault", domain=None, base_dm=None):
    from underworld3.utilities.line_cut import _coords, _edge_vertices
    X = _coords(dm); eS, _ = dm.getDepthStratum(1); ends = _edge_vertices(dm)
    lab = dm.getLabel(name)
    marked = (np.asarray(lab.getStratumIS(int(value)).getIndices(), dtype=np.int64) - eS
              if lab is not None and lab.getStratumSize(int(value)) else np.zeros(0, dtype=np.int64))
    rec_box["facets"] = int(marked.size)
    if not marked.size:
        return
    vnum = np.asarray(dm.getVertexNumbering().getIndices(), dtype=np.int64); vnum = np.where(vnum >= 0, vnum, -vnum - 1)
    parent = {}
    def root(v):
        while parent.get(v, v) != v: v = parent[v]
        return v
    for a, b in ends[marked]:
        ra, rb = root(int(vnum[a])), root(int(vnum[b])); parent.setdefault(ra, ra); parent.setdefault(rb, rb)
        if ra != rb: parent[ra] = rb
    rec_box["pieces"] = len({root(v) for v in parent})
    if dm.hasLabel("UW_PulledVertex"):
        lab_p = dm.getLabel("UW_PulledVertex"); vS0 = dm.getDepthStratum(0)[0]
        marked_v = [int(v) for v in np.asarray(lab_p.getStratumIS(1).getIndices()) - vS0] if lab_p.getStratumSize(1) else []
        chain_v = {int(v) for v in ends[marked].ravel()}
        rec_box["pulled"] = len(marked_v)
        rec_box["pulled_off_chain"] = sum(v not in chain_v for v in marked_v)
        Q = _trace_now.get("Q")
        if Q is not None and len(Q) > 2:
            a = Q[1:-1] - Q[:-2]; b = Q[2:] - Q[1:-1]
            turn = np.degrees(np.arccos(np.clip((a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)), -1, 1)))
            tq = Q[1:-1][turn > 45.0]
            Xc = X[sorted(chain_v)] if chain_v else np.zeros((0, X.shape[1]))
            rec_box["turns"] = int(len(tq))
            rec_box["turns_off_chain"] = int(sum(not np.any(np.all(Xc == q, axis=1)) for q in tq))
    dense = np.vstack([poly[:-1] + x * (poly[1:] - poly[:-1]) for x in np.linspace(0, 1, 11)])
    hh = fs._base_cell_size(dm if base_dm is None else base_dm, dense)
    d = np.full(len(dense), np.inf)
    for a, b in zip(X[ends[marked, 0]], X[ends[marked, 1]]):
        e = b - a; L = e @ e; u = np.clip(((dense - a) @ e) / L, 0, 1)
        d = np.minimum(d, np.linalg.norm(dense - (a + u[:, None] * e), axis=1))
    # GEOMETRY: each chain edge's ends projected onto the trace's arc length; the
    # union of those intervals over [0, L]; its gaps are the uncovered stretches,
    # the end gaps the shortfalls. In base k=6 cells at the gap.
    seg = np.diff(poly, axis=0); sl = np.linalg.norm(seg, axis=1); cum = np.concatenate([[0], np.cumsum(sl)])
    def arc(p):
        u = np.clip(((p - poly[:-1]) * seg).sum(1) / (sl * sl), 0, 1)
        dd = np.linalg.norm(poly[:-1] + u[:, None] * seg - p, axis=1); i = int(np.argmin(dd))
        return cum[i] + u[i] * sl[i]
    iv = sorted(tuple(sorted((arc(X[a]), arc(X[b])))) for a, b in ends[marked])
    gaps, reach = [], 0.0
    for lo, hi in iv:
        if lo > reach: gaps.append((reach, lo))
        reach = max(reach, hi)
    if reach < cum[-1]: gaps.append((reach, cum[-1]))
    def at(s_):
        i = min(int(np.searchsorted(cum, s_, side="right")) - 1, len(sl) - 1); return poly[i] + (s_ - cum[i]) / sl[i] * seg[i]
    def cells(g):
        return (g[1] - g[0]) / float(fs._base_cell_size(dm if base_dm is None else base_dm, at(0.5 * (g[0] + g[1]))[None, :])[0])
    start = [g for g in gaps if g[0] <= 1e-12]; end = [g for g in gaps if g[1] >= cum[-1] - 1e-12]
    inner = [g for g in gaps if g not in start and g not in end]
    rec_box.update(short_start=cells(start[0]) if start else 0.0, short_end=cells(end[0]) if end else 0.0,
                   uncovered_max=max([cells(g) for g in gaps], default=0.0),
                   uncovered_inner=max([cells(g) for g in inner], default=0.0))
    ex = d / hh; w = int(np.argmax(ex))
    rec_box.update(excess=float(ex[w]), at_tip=bool(min(np.linalg.norm(dense[w] - poly[0]), np.linalg.norm(dense[w] - poly[-1])) < 1e-12))
fs._refuse_an_empty_or_partial_cut = recorder
# THROUGH check (hub's 0007 idea): every vertex a pulled sample landed on, matched exactly
# after the pull, must be on the chain. The targets the pull is given are captured here.
from underworld3.utilities import line_cut as _lc0
_pull0 = _lc0.pull_vertex_onto
_last_targets = {}
_trace_now = {}
def _pull_capture(dm, P, **kw):
    P = np.asarray(P, dtype=float)
    if os.environ.get("ORDER") == "turns_last" and _trace_now.get("Q") is not None and len(P) > 2:
        Q = _trace_now["Q"]
        a = Q[1:-1] - Q[:-2]; b = Q[2:] - Q[1:-1]
        turn = np.degrees(np.arccos(np.clip((a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)), -1, 1)))
        is_turn = np.zeros(len(Q), dtype=bool); is_turn[1:-1] = turn > 45.0
        is_tip = np.zeros(len(Q), dtype=bool); is_tip[[0, -1]] = True
        key = {tuple(q): (2 if t else 1 if r else 0) for q, t, r in zip(map(tuple, Q), is_tip, is_turn)}
        rank = np.array([key.get(tuple(p), 0) for p in P])
        P = P[np.argsort(rank, kind="stable")]
    out = _pull0(dm, P, **kw)
    _last_targets["P"] = np.asarray(P, dtype=float)
    _last_targets["X"] = _lc0._coords(out)
    _last_targets["vS"] = out.getDepthStratum(0)[0]
    _last_targets["dm"] = out
    return out
_lc0.pull_vertex_onto = _pull_capture
_mark0 = fs._mark_tip_vertices
def _mark_all(dm, tips):
    _mark0(dm, tips)
    if dm.hasLabel("UW_PulledVertex"):
        dm.removeLabel("UW_PulledVertex")
    dm.createLabel("UW_PulledVertex")
    lab = dm.getLabel("UW_PulledVertex")
    X = _lc0._coords(dm); vS = dm.getDepthStratum(0)[0]
    for p in _last_targets.get("P", np.zeros((0, X.shape[1]))):
        for v in np.flatnonzero(np.all(X == p, axis=1)):
            lab.setValue(int(v) + vS, 1)
fs._mark_tip_vertices = _mark_all
ROW29 = os.environ.get("ROW29") == "1"
if ROW29:   # row 29's pull rule (copied from its draft) and its snap fraction, on this build
    from underworld3.utilities import line_cut as _lc
    from mpi4py import MPI
    _orig_pull = _lc.pull_vertex_onto
    def _cell_size_near(dm, poly):
        X = _lc._coords(dm); ends = _lc._edge_vertices(dm)
        lo, hi = poly.min(axis=0), poly.max(axis=0); grow = 0.1 * float(np.linalg.norm(hi - lo))
        mid = 0.5 * (X[ends[:, 0]] + X[ends[:, 1]]); near = np.all((mid >= lo - grow) & (mid <= hi + grow), axis=1)
        L = np.linalg.norm(X[ends[near, 0]] - X[ends[near, 1]], axis=1)
        return float(L.mean()) if L.size else float("nan")
    def _pulled(dm, P):
        P = np.asarray(P, dtype=float)
        if len(P) <= 2: return P
        a = P[1:-1] - P[:-2]; b = P[2:] - P[1:-1]
        turn = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", a, b) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)), -1, 1)))
        keep = np.zeros(len(P), dtype=bool); keep[[0, -1]] = True; keep[1:-1] |= turn > 45.0
        h = _cell_size_near(dm, P)
        if np.median(np.linalg.norm(np.diff(P, axis=0), axis=1)) >= 1.1 * h: return P
        for i in 1 + np.flatnonzero(turn > 90.0): keep |= np.linalg.norm(P - P[i], axis=1) <= 1.5 * h
        return P[keep]
    def _pull(dm, P, **kw):
        return _orig_pull(dm, _pulled(dm, P), **kw)
    _lc.pull_vertex_onto = _pull
out = {}
for DS in (1.0, 0.5, 0.3):
    sys.argv = ["x", mesh_kind, str(DS), family]
    g = {"__name__": "cover"}
    exec(pre, g)
    for tag, Q in g["traces"]():
        rec_box.clear()
        _trace_now["Q"] = np.asarray(Q, dtype=float)
        r = dict(mesh=mesh_kind, ds=DS, trace=tag)
        try:
            m2 = g["mesh"].add_fault(("F", Q), **({"snap_frac": 0.3} if ROW29 else {}))
            r["outcome"] = "split"
        except Exception as e:
            r["outcome"] = "raised"; r["reason"] = str(e)[:120]
        r.update(rec_box)
        if r["outcome"] == "split" and os.environ.get("GEOM") != "1":
            try:
                r["slip"] = g["solve"](m2, "F")["slip_max"]
            except Exception as e:
                r["solve_error"] = str(e)[:100]
        out[(tag, DS)] = r
for (tag, DS), r in out.items():
    ref = out.get((tag, 1.0))
    if ref and ref.get("pieces") == 1 and ref.get("excess", 9) < 0.25 and "slip" in ref and "slip" in r:
        r["slip_ref"] = ref["slip"]; r["slip_err"] = r["slip"] / ref["slip"] - 1
    print("COVER " + json.dumps(r), flush=True)
