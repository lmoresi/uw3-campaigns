def _old_barycentric_prolongation(coarse_coords, fine_coords, repair_orphans=True,
                             stats=None):
    """Prolongation by linear interpolation over a Delaunay triangulation of the
    coarse DOF cloud. Partition of unity (row sums = 1) and linear fields are
    reproduced exactly; fine points outside the coarse hull fall back to the
    nearest coarse DOF, and orphaned coarse DOFs are repaired below.

    .. note::

       This is **not** the coarse FE space's embedding, despite what this
       docstring claimed until 2026-07. It triangulates the coarse DOF *point
       cloud* from scratch and never consults the coarse mesh's cells, so
       "the coarse element containing the fine DOF" is only what gets used when
       the Delaunay triangulation happens to coincide with the mesh. Measured
       agreement between the two:

       ===========================  ==========  ==========  ==========
       case                         mesh cells  Delaunay    agreement
       ===========================  ==========  ==========  ==========
       2D uniform base, P1                 168         168       100 %
       2D adapt child, P1                  238         238      90.8 %
       3D uniform base, P1                 800         812      58.8 %
       3D adapt child, P1                 4685        5201      17.1 %
       3D adapt child, P2                 4685       39597         --
       ===========================  ==========  ==========  ==========

       Reproducing linears is enough for multigrid to converge well, which is
       why this works. But two limits follow. For P2 and above the coarse
       space is not represented exactly. And because Delaunay simplices do not
       respect mesh topology, on a non-convex domain or one with an internal
       interface (a fault) a simplex can bridge across the discontinuity and
       smear the coarse correction over it — predicted from the algorithm,
       not yet measured.

       Where a parent/child relation exists, prefer the exact nested transfer
       (#425), which is the true FE embedding, cannot bridge across features,
       and cannot orphan a coarse DOF.
    """
    import scipy.sparse as sp
    from scipy.spatial import Delaunay, cKDTree

    tri = Delaunay(coarse_coords)
    simp = tri.find_simplex(fine_coords)
    tree = cKDTree(coarse_coords)
    dim = coarse_coords.shape[1]
    rows, cols, vals = [], [], []
    for i in range(fine_coords.shape[0]):
        s = simp[i]
        if s < 0:  # outside coarse hull → nearest coarse DOF
            rows.append(i)
            cols.append(int(tree.query(fine_coords[i])[1]))
            vals.append(1.0)
            continue
        verts = tri.simplices[s]
        T = tri.transform[s]
        bary = T[:dim].dot(fine_coords[i] - T[dim])
        w = np.append(bary, 1.0 - bary.sum())
        for k in range(dim + 1):
            rows.append(i)
            cols.append(int(verts[k]))
            vals.append(float(w[k]))
    P = sp.csr_matrix((vals, (rows, cols)),
                      shape=(fine_coords.shape[0], coarse_coords.shape[0]))

    # Repair orphaned coarse DOFs (columns with no fine image). Point location
    # has LOCAL support, so a coarse DOF is reached only if some fine DOF lands
    # in a simplex touching it; move the fine coordinates (mesh.relax, boundary
    # snapping, free-surface deformation) and a coarse DOF can lose every fine
    # image. Its column goes to zero and the Galerkin coarse operator PᵀAP is
    # singular (#424).
    #
    # Give each orphan its nearest fine DOF as a pure injection (weight 1) —
    # exactly the fallback already used above for fine points outside the
    # coarse hull. Partition of unity is preserved (the row still sums to 1),
    # sparsity is preserved (~d+1 nnz/row), and the column is no longer empty.
    # Distinct rows are used so two orphans cannot claim the same fine DOF.
    # The alternative — switching to the global-support RBF builder — removes
    # the singularity but returns a DENSE transfer (nnz/row == n_coarse), which
    # makes PᵀAP dense and is unusable at production sizes.
    # In PARALLEL the repair is wrong by construction and is switched off by
    # the parallel builders: a rank sees only its own fine nodes, so a coarse
    # column reached from another rank (a ghost at a partition boundary, or
    # most of an all-gathered coarse cloud) looks orphaned here and the repair
    # overwrote a local fine row with a weight-one injection onto a coarse node
    # far away (measured: thousands of rows at distance 0.6-0.9 on a box of
    # length 3, and a velocity multigrid that needed 55 iterations on 8 ranks
    # against 4 in serial). Genuine orphans are dropped at install instead.
    orphans = (np.nonzero(np.asarray((P != 0).sum(axis=0)).ravel() == 0)[0]
               if repair_orphans else np.zeros(0, dtype=np.int64))
    _record(stats, np.nonzero(simp < 0)[0], orphans.size)
    if orphans.size:
        k = int(min(orphans.size + 8, fine_coords.shape[0]))
        _, cand = cKDTree(fine_coords).query(coarse_coords[orphans], k=k)
        cand = np.atleast_2d(cand)
        claimed, fixes = set(), {}
        for i, c in enumerate(orphans):
            for f in cand[i]:
                f = int(f)
                if f not in claimed:
                    claimed.add(f)
                    fixes[f] = int(c)
                    break
        if fixes:
            keep = ~np.isin(np.asarray(rows), list(fixes))
            rows = list(np.asarray(rows)[keep]) + list(fixes.keys())
            cols = list(np.asarray(cols)[keep]) + list(fixes.values())
            vals = list(np.asarray(vals)[keep]) + [1.0] * len(fixes)
            P = sp.csr_matrix((vals, (rows, cols)),
                              shape=(fine_coords.shape[0],
                                     coarse_coords.shape[0]))
    return P


