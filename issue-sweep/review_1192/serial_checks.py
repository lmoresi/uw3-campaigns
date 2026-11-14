"""One rank, PR #1192 at fec6d95a: the facet restore against the previous code
(nearest point over every facet), the kd-tree's k nearest against a sort, the
dependence of the result on the facet order, and a graded corner."""
import numpy as np
import underworld3 as uw
from underworld3.discretisation.discretisation_mesh import _facets_that_can_hold_the_nearest_point
from underworld3.meshing.smoothing.graph import _nearest_on_facets_2d, _nearest_on_facets_3d

rng = np.random.default_rng(1192)


def previous_restore(mesh, coords, fpts, nrm):
    pts = np.ascontiguousarray(np.asarray(coords, dtype=float))
    closest = (_nearest_on_facets_2d if mesh.cdim == 2 else _nearest_on_facets_3d)(pts, fpts)
    tree = uw.kdtree.KDTree(np.ascontiguousarray(fpts.mean(axis=1)))
    owner = np.asarray(tree.query(np.ascontiguousarray(closest), 1)[1]).flatten()
    nvec = nrm[owner]
    outside = np.einsum("ij,ij->i", pts - closest, nvec) > 0.0
    eps = 1.0e-3 * float(mesh.get_min_radius())
    pts[outside] = closest[outside] - eps * nvec[outside]
    return pts, outside


def queries(fpts, n):
    dim = fpts.shape[2]
    lo, hi = fpts.reshape(-1, dim).min(axis=0), fpts.reshape(-1, dim).max(axis=0)
    span = hi - lo
    near = rng.uniform(lo - 0.1 * span, hi + 0.1 * span, (n, dim))
    far = rng.uniform(lo - 30.0 * span, hi + 30.0 * span, (n // 10, dim))
    vertices = fpts.reshape(-1, dim)
    on = vertices[rng.choice(len(vertices), min(n // 10, len(vertices)), replace=False)]
    mid = fpts.mean(axis=1)[rng.choice(len(fpts), min(n // 10, len(fpts)), replace=False)]
    return np.vstack([near, far, on, mid])


def stretched(mesh, power):
    X = np.asarray(mesh.X.coords, dtype=float).copy()
    X[:, 1] = X[:, 1] ** power
    mesh.deform(X)
    return mesh


cases = {
    "annulus, scaled 0.9": lambda: (lambda m: (m.deform(0.9 * np.asarray(m.X.coords, dtype=float)), m)[1])(
        uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.05)),
    "box 2-D, 4 cells a side, y -> y^2": lambda: stretched(
        uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.25), 2),
    "box 2-D, cell 0.05, y -> y^3": lambda: stretched(
        uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.05), 3),
    "box 3-D, cell 0.2, y -> y^2": lambda: stretched(
        uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=0.2), 2),
    "shell, scaled 0.9": lambda: (lambda m: (m.deform(0.9 * np.asarray(m.X.coords, dtype=float)), m)[1])(
        uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.5, cellSize=0.25)),
}
kept = {}
for name, build in cases.items():
    mesh = build()
    fpts, nrm = mesh._boundary_facet_geometry()
    pts = queries(fpts, 4000)
    new = np.asarray(mesh.return_coords_to_bounds(pts.copy()))
    old, outside = previous_restore(mesh, pts.copy(), fpts, nrm)
    # the kd-tree's k nearest centroids against a full sort
    centroids = np.ascontiguousarray(fpts.mean(axis=1))
    tree = uw.kdtree.KDTree(centroids)
    k = min(16, len(fpts))
    d, idx = tree.query(pts, k, sqr_dists=False)
    d = np.asarray(d).reshape(len(pts), k)
    full = np.sqrt(((pts[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2))
    kth = np.sort(full, axis=1)[:, :k]
    cand = _facets_that_can_hold_the_nearest_point(pts, fpts, centroids, tree)
    sizes = np.array([len(c) for c in cand])
    print(f"{name}: {len(fpts)} facets, {len(pts)} points, {int(outside.sum())} outside; "
          f"restore differs from the previous code at {int(np.any(new != old, axis=1).sum())} points; "
          f"kd-tree sorted {bool(np.all(np.diff(d, axis=1) >= 0))}, "
          f"largest |d - sorted| {np.abs(d - kth).max():.1e}; "
          f"facets searched per point: median {int(np.median(sizes))}, most {sizes.max()}", flush=True)
    kept[name] = (mesh, fpts, nrm, pts, new)

print("--- facet order (a different rank count gathers the facets in a different order)")
for name, (mesh, fpts, nrm, pts, new) in kept.items():
    stamp = mesh._bnd_restore_cache[0]
    worst, n_diff = 0.0, 0
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(fpts))
        mesh._bnd_restore_cache = (stamp, fpts[perm], nrm[perm])
        other = np.asarray(mesh.return_coords_to_bounds(pts.copy()))
        diff = np.linalg.norm(other - new, axis=1)
        n_diff = max(n_diff, int(np.count_nonzero(diff)))
        worst = max(worst, float(diff.max()))
    mesh._bnd_restore_cache = (stamp, fpts, nrm)
    print(f"{name}: over 5 orders, at most {n_diff} of {len(pts)} points restored differently, "
          f"largest difference {worst:.2e} (min cell radius {mesh.get_min_radius():.2e})", flush=True)

print("--- graded corner: the right wall's facets are longer than the top wall's at the top right corner")
mesh, fpts, nrm, _pts, _new = kept["box 2-D, cell 0.05, y -> y^3"]
right = fpts[np.all(np.abs(fpts[:, :, 0] - 1.0) < 1e-12, axis=1)]
top = fpts[np.all(np.abs(fpts[:, :, 1] - 1.0) < 1e-12, axis=1)]
L = np.abs(right[:, 1, 1] - right[:, 0, 1])[np.argmax(right[:, :, 1].max(axis=1))]
l = np.abs(top[:, 1, 0] - top[:, 0, 0])[np.argmax(top[:, :, 0].max(axis=1))]
s = np.linspace(0.02, 0.98, 49) * L
probe = np.column_stack([np.full_like(s, 1.02), 1.0 - s])
out = np.asarray(mesh.return_coords_to_bounds(probe.copy()))
left_outside = out[:, 0] > 1.0
print(f"corner facets: right wall {L:.4f}, top wall {l:.4f}; 49 points at x = 1.02 beside the top "
      f"facet of the right wall: {int(left_outside.sum())} left outside, "
      f"at depths below the corner up to {s[left_outside].max() if left_outside.any() else 0:.4f}")
