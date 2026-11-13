"""#449: which rows of the nested vertex transfer are wrong in 3-D, and why.

Serial. A tetrahedral box is refined by repeated passes of the bisection engine
with the cells in a band about z = 0.5 marked. For every pass the vertex
transfer is built three ways and compared, row by row, with the coarse P1
function evaluated in the coarse cell that holds the fine vertex:

- ``dms``    : ``nvb._nested_prolongation_local`` (parents inferred from
               coordinate bytes; first matching pair of resolved neighbours);
- ``rule``   : the same inference, accepting a pair only when the supports of
               its two rows lie in the vertex set of ONE coarse cell;
- ``record`` : (python engine only) ``nvb.nested_prolongation`` from the
               engine's own ``edge2mid``.

For each wrong row it prints the support, whether the support lies in one
coarse cell, and whether the row reproduces the vertex's coordinates.
"""
import numpy as np
import scipy.sparse as sp
import underworld3 as uw
from underworld3.utilities import nvb

params = uw.Params(cell_size=0.5, passes=6, band=0.2, route="native", refinement=1, show=6)


def verts_of_cells(dm):
    vS, vE = dm.getDepthStratum(0)
    cS, cE = dm.getHeightStratum(0)
    return np.array([[int(p) - vS for p in dm.getTransitiveClosure(c)[0] if vS <= p < vE]
                     for c in range(cS, cE)], dtype=np.int64)


def coords_of(dm):
    return np.ascontiguousarray(dm.getCoordinatesLocal().array.reshape(-1, dm.getCoordinateDim()))


def p1_truth(cx, cells, data, fx, tol=1e-9):
    """Coarse P1 value at every fine vertex, from the first coarse cell that holds it."""
    out = np.full(len(fx), np.nan)
    for verts in cells:
        X = cx[verts]
        lo, hi = X.min(axis=0) - 1e-12, X.max(axis=0) + 1e-12
        cand = np.flatnonzero(np.isnan(out) & (fx >= lo).all(axis=1) & (fx <= hi).all(axis=1))
        if not len(cand):
            continue
        M = (X[1:] - X[0]).T
        lam = np.linalg.solve(M, (fx[cand] - X[0]).T).T
        bary = np.hstack([1.0 - lam.sum(axis=1, keepdims=True), lam])
        inside = (bary > -tol).all(axis=1) & (bary < 1.0 + tol).all(axis=1)
        out[cand[inside]] = bary[inside] @ data[verts]
    return out


def as_matrix(entry, n_f, n_c):
    rows, cols, vals = entry
    return sp.csr_matrix((vals, (rows, cols)), shape=(n_f, n_c))


def cells_at_vertex(cells, n_c):
    at = [set() for _ in range(n_c)]
    for k, verts in enumerate(cells):
        for v in verts:
            at[v].add(k)
    return at


def in_one_cell(support, at):
    return bool(set.intersection(*[at[v] for v in support]))


def inferred(cdm, fdm, at, one_cell_rule):
    """`_nested_prolongation_local` with the pair choice exposed.

    Returns (weights, info): info[r] = (round, pair taken, number of matching
    pairs, number of matching pairs whose supports lie in one coarse cell).
    """
    cvS, cvE = cdm.getDepthStratum(0)
    ceS, ceE = cdm.getDepthStratum(1)
    cx, fx = coords_of(cdm), coords_of(fdm)
    edges = np.array([[q - cvS for q in cdm.getCone(e)] for e in range(ceS, ceE)], dtype=np.int64)
    fvS, fvE = fdm.getDepthStratum(0)
    feS, feE = fdm.getDepthStratum(1)
    n_f = fvE - fvS

    known = {row.tobytes(): ("v", i) for i, row in enumerate(cx)}
    mids = np.ascontiguousarray(0.5 * (cx[edges[:, 0]] + cx[edges[:, 1]]))
    for i, row in enumerate(mids):
        known.setdefault(row.tobytes(), ("e", i))
    weights, info = [None] * n_f, {}
    for r, row in enumerate(fx):
        hit = known.get(row.tobytes())
        if hit is None:
            continue
        kind, i = hit
        weights[r] = {int(i): 1.0} if kind == "v" else {int(edges[i][0]): 0.5, int(edges[i][1]): 0.5}

    unresolved = [r for r in range(n_f) if weights[r] is None]
    nbr = [[] for _ in range(n_f)]
    for e in range(feS, feE):
        c = fdm.getCone(e)
        u, v = int(c[0] - fvS), int(c[1] - fvS)
        nbr[u].append(v)
        nbr[v].append(u)
    rnd = 1
    while unresolved:
        rnd += 1
        still, new = [], {}
        for r in unresolved:
            target = fx[r].tobytes()
            cand = [q for q in nbr[r] if weights[q] is not None]
            pairs = [(cand[i], cand[j]) for i in range(len(cand)) for j in range(i + 1, len(cand))
                     if np.ascontiguousarray(0.5 * (fx[cand[i]] + fx[cand[j]])).tobytes() == target]
            good = [pq for pq in pairs
                    if in_one_cell(set(weights[pq[0]]) | set(weights[pq[1]]), at)]
            take = (good[0] if good else None) if one_cell_rule else (pairs[0] if pairs else None)
            if take is None:
                still.append(r)
                continue
            w = {}
            for src in take:
                for pt, ww in weights[src].items():
                    w[pt] = w.get(pt, 0.0) + 0.5 * ww
            # as the library does: a row resolved in this sweep is visible to the next vertex
            weights[r] = w
            info[r] = (rnd, take, len(pairs), len(good))
        if len(still) == len(unresolved):
            return None, info
        unresolved = still
    return weights, info


def to_entry(weights):
    rows, cols, vals = [], [], []
    for r, w in enumerate(weights):
        for pt, ww in w.items():
            rows.append(r), cols.append(pt), vals.append(ww)
    return np.asarray(rows), np.asarray(cols), np.asarray(vals, dtype=float)


def report(name, entry, cdm, fdm, cells, at, data, truth, info=None):
    cx, fx = coords_of(cdm), coords_of(fdm)
    if entry is None:
        print(f"    {name:7s}: declined (no transfer)")
        return
    P = as_matrix(entry, len(fx), len(cx))
    got = P @ data
    wrong = np.flatnonzero(np.abs(got - truth) > 1e-10)
    coord_err = np.abs(P @ cx - fx).max()
    spans = sum(1 for r in range(len(fx))
                if not in_one_cell(P.indices[P.indptr[r]:P.indptr[r + 1]].tolist(), at))
    print(f"    {name:7s}: wrong rows {len(wrong)} of {len(fx)}, worst {np.abs(got - truth).max():.3g}; "
          f"rows whose support is in no single coarse cell {spans}; "
          f"worst |P x_c - x_f| {coord_err:.2g}")
    for r in wrong[: params.show]:
        sl = slice(P.indptr[r], P.indptr[r + 1])
        sup = P.indices[sl].tolist()
        line = (f"      row {r} x={np.round(fx[r], 4).tolist()} support={sup} "
                f"weights={np.round(P.data[sl], 4).tolist()} in one coarse cell: {in_one_cell(sup, at)} "
                f"error {abs(got[r] - truth[r]):.3g}")
        if info and r in info:
            rnd, take, n_pairs, n_good = info[r]
            line += f" | round {rnd}, matching pairs {n_pairs}, of which in one coarse cell {n_good}"
        print(line)


def marked_cells(dm):
    cx = coords_of(dm)
    cen = cx[verts_of_cells(dm)].mean(axis=1)
    cS, _ = dm.getHeightStratum(0)
    return [int(cS + k) for k in np.flatnonzero(np.abs(cen[:, -1] - 0.5) < params.band)]


def native_passes(base_dm):
    from underworld3.utilities import _nvb_transform as nvbx
    nvb.write_tagged_state_label(base_dm)
    cur = base_dm
    for _ in range(params.passes):
        d = cur.clone()
        d.createLabel("adapt")
        lab = d.getLabel("adapt")
        lab.setDefaultValue(0)
        for c in marked_cells(cur):
            lab.setValue(c, 1)
        fine = nvbx.refine(d, "adapt")
        yield cur, fine, None
        cur = fine


def engine_passes(base_dm):
    eng = nvb.TaggedBisectionMesh.from_dm(base_dm)
    vS0, vE0 = base_dm.getDepthStratum(0)
    cmap = {i: i for i in range(vE0 - vS0)}          # engine id -> row of the coarse level
    cur = base_dm
    for _ in range(params.passes):
        cen, _h, cids = eng.centroids_h()
        marked = {int(cids[k]) for k in np.flatnonzero(np.abs(cen[:, -1] - 0.5) < params.band)}
        n_coarse = len(eng.coords)
        eng.refine(marked)
        fine = eng.to_dm()
        fvS, fvE = fine.getDepthStratum(0)
        fmap = dict(eng.dm_vertex_of_engine)
        rec = nvb.nested_prolongation(eng, cmap, fmap, n_coarse, fvS, fvE - fvS)
        yield cur, fine, rec
        cur, cmap = fine, {e: p - fvS for e, p in fmap.items()}


mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0),
                                         cellSize=params.cell_size, refinement=params.refinement,
                                         qdegree=2)
base = mesh.dm.clone()
print(f"route={params.route} cell_size={params.cell_size} refinement={params.refinement} "
      f"band={params.band}")
rng = np.random.default_rng(0)
passes = native_passes(base) if params.route == "native" else engine_passes(base)
for k, (cdm, fdm, rec) in enumerate(passes):
    cx, fx = coords_of(cdm), coords_of(fdm)
    cells = verts_of_cells(cdm)
    at = cells_at_vertex(cells, len(cx))
    data = rng.standard_normal(len(cx))
    truth = p1_truth(cx, cells, data, fx)
    assert not np.isnan(truth).any(), "a fine vertex lies in no coarse cell"
    print(f"  pass {k}: coarse vertices {len(cx)}, fine vertices {len(fx)}")
    report("dms", nvb._nested_prolongation_local(cdm, fdm), cdm, fdm, cells, at, data, truth)
    w, info = inferred(cdm, fdm, at, one_cell_rule=False)
    report("first", None if w is None else to_entry(w), cdm, fdm, cells, at, data, truth, info)
    n2 = sum(1 for v in info.values() if v[0] >= 2)
    amb = sum(1 for v in info.values() if v[2] > 1)
    bad_first = sum(1 for v in info.values() if v[2] > v[3])
    print(f"             rows resolved after round 1: {n2}; with more than one matching pair: {amb}; "
          f"with a matching pair that spans two coarse cells: {bad_first}")
    w, info = inferred(cdm, fdm, at, one_cell_rule=True)
    report("rule", None if w is None else to_entry(w), cdm, fdm, cells, at, data, truth, info)
    if rec is not None:
        report("record", rec, cdm, fdm, cells, at, data, truth)
