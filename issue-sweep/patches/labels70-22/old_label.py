def _old_label_cut_edges(dm, lines, tol, name, value):
    """Mark the edges lying along the cut; return the edge points marked.

    An edge is on the cut when both its endpoints and its midpoint lie on a line.
    The midpoint test is what distinguishes the cut from a chord: where a polyline
    turns, two vertices on different segments can be joined by an edge that is not
    part of the line at all.

    The points are returned rather than counted here because a shared edge is held
    by every rank on the seam: counting locally and summing would report it once
    per sharer. The caller counts the OWNED ones.
    """
    X = _coords(dm)
    on = _distance_to_lines(X, lines) < tol
    eS, _eE = dm.getDepthStratum(1)
    ends = _edge_vertices(dm)
    mid_on = _distance_to_lines(0.5 * (X[ends[:, 0]] + X[ends[:, 1]]), lines) < tol
    keep = on[ends[:, 0]] & on[ends[:, 1]] & mid_on

    if not dm.hasLabel(name):
        dm.createLabel(name)
    label = dm.getLabel(name)
    label.setDefaultValue(0)
    marked = np.flatnonzero(keep) + eS
    for e in marked:
        label.setValue(int(e), int(value))
    return marked


