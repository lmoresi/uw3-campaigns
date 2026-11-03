"""The plastic-strain band of a downwelling as a fault: locate the saturated, cold,
descending band and fit a straight fault to it (trench angle, dip, dip direction).
Shared by the fault driver (which steers its fault with it) and the checkpoint
analysis (``analysis/strain_fault.py``)."""
import numpy as np
from scipy import ndimage


def polar_grid(r_o, n_theta=1440, depth_max=0.6, n_depth=78, centre=None, half_width=None):
    """Cartesian points of an unrolled grid: theta in [-pi, pi) (or a window of
    ``half_width`` radians about ``centre``), depth in [0, depth_max] (the outer wall
    pulled in by a hair). Returns (theta, depth, xy) with xy shaped
    (n_depth * n_theta, 2), depth-major."""
    if half_width is None:
        theta = np.linspace(-np.pi, np.pi, n_theta, endpoint=False)
    else:
        theta = centre + np.linspace(-half_width, half_width, n_theta)
    depth = np.linspace(1.0e-3, depth_max, n_depth)
    rr = r_o - depth[:, None]
    xy = np.stack([(rr * np.cos(theta)[None, :]).ravel(), (rr * np.sin(theta)[None, :]).ravel()], axis=1)
    return theta, depth, xy


def detect_fault(theta, depth, gamma, edot, T, v_r, r_o, gamma_sat=0.5, T_lith=0.6,
                 depth_max=0.45, depth_min=0.05, descent=0.1, min_points=20, periodic=True,
                 prefer=None, prefer_width=np.deg2rad(5.0), ridge=True):
    """The most active saturated, cold, descending plastic-strain band, fitted by a line.

    ``gamma``, ``edot``, ``T``, ``v_r`` are (n_depth, n_theta) arrays on the grid of
    ``polar_grid``. Returns a dict with the trench angle ``theta_t`` (radians), the dip
    (degrees below the local horizontal), the dip direction (+1: down toward +theta),
    the fitted segment ends, the band's points and weights, and a linearity measure
    (the ratio of the minor to the major principal spread), or None when no band
    qualifies."""
    # Below the surface layer (the subducting plate's strained skin lies along the wall,
    # where v_r -> 0 under free slip), within the lithosphere, and descending: v_r below
    # a fraction ``descent`` of the strongest downflow in the depth band.
    band = (depth[:, None] >= depth_min) & (depth[:, None] <= depth_max)
    v_down = max(float(-np.min(np.where(band, v_r, 0.0))), 1e-30)
    mask = (gamma >= gamma_sat) & (T <= T_lith) & band & (v_r <= -descent * v_down)
    if mask.sum() < min_points:
        return None
    # clusters connected in (depth, theta), with theta periodic: label, then merge the
    # labels that touch across the seam
    labels, n = ndimage.label(mask, structure=np.ones((3, 3)))
    for i in range(labels.shape[0] if periodic else 0):
        a, b = labels[i, 0], labels[i, -1]
        if a and b and a != b:
            labels[labels == b] = a
    # rank by accumulated strain: while an explicit fault takes the slip, the band beside
    # it stops straining, and ranking by the current rate picks a side branch
    activity = ndimage.sum(np.where(mask, gamma, 0.0), labels, index=np.arange(1, n + 1))
    if prefer is not None and n:
        # continuity: a fault keeps its own band, so clusters away from ``prefer`` count less
        cols = np.broadcast_to(theta[None, :], labels.shape)
        s = ndimage.sum(np.sin(cols), labels, index=np.arange(1, n + 1))
        c = ndimage.sum(np.cos(cols), labels, index=np.arange(1, n + 1))
        dth = (np.arctan2(s, c) - prefer + np.pi) % (2 * np.pi) - np.pi
        activity = activity * np.exp(-(dth / prefer_width) ** 2)
    best = int(np.argmax(activity)) + 1
    sel = labels == best
    if sel.sum() < min_points:
        return None
    ii, jj = np.nonzero(sel)
    th = theta[jj]
    dd = depth[ii]
    r = r_o - dd
    pts = np.stack([r * np.cos(th), r * np.sin(th)], axis=1)
    w = gamma[sel]
    w = w / w.sum()
    if ridge:
        # The band's ridge: at each depth row, the position of greatest strain within
        # the cluster, one point per row, equal weights. A cluster that also holds a
        # broad strained fan near the surface would otherwise tilt the fit toward it.
        rows = np.unique(ii)
        if len(rows) >= 3:
            ridge_pts = []
            for i in rows:
                cols = jj[ii == i]
                j = cols[np.argmax(gamma[i, cols])]
                ridge_pts.append([(r_o - depth[i]) * np.cos(theta[j]), (r_o - depth[i]) * np.sin(theta[j])])
            pts = np.asarray(ridge_pts)
            w = np.full(len(pts), 1.0 / len(pts))
    c = (w[:, None] * pts).sum(axis=0)
    X = pts - c
    cov = (w[:, None, None] * X[:, :, None] * X[:, None, :]).sum(axis=0)
    evals, evecs = np.linalg.eigh(cov)
    u = evecs[:, 1]                                   # major axis
    linearity = float(np.sqrt(max(evals[0], 0.0) / max(evals[1], 1e-30)))
    # intersect the line c + s u with the outer wall |x| = r_o; take the root nearer c
    b = c @ u
    disc = b * b - (c @ c - r_o ** 2)
    if disc < 0:
        return None
    s_roots = np.array([-b - np.sqrt(disc), -b + np.sqrt(disc)])
    s_wall = s_roots[np.argmin(np.abs(s_roots))]
    trench = c + s_wall * u
    theta_t = float(np.arctan2(trench[1], trench[0]))
    r_hat = trench / np.linalg.norm(trench)
    t_hat = np.array([-r_hat[1], r_hat[0]])
    down = -u if u @ r_hat > 0 else u                 # the direction pointing into the planet
    dip = float(np.degrees(np.arctan2(-down @ r_hat, abs(down @ t_hat))))
    direction = 1 if down @ t_hat > 0 else -1
    # the segment from the trench to the deepest band point along the axis
    s_pts = (pts - trench) @ down
    tip = trench + down * float(np.percentile(s_pts, 95))
    return {"theta_t": theta_t, "dip": dip, "direction": direction, "trench": trench, "tip": tip,
            "centroid": c, "linearity": linearity, "n_points": int(sel.sum()),
            "points": pts, "weights": w, "activity": float(activity[best - 1])}




def boundary_layer_depth(theta, depth, T, theta_t, T_bl=0.7, exclude=np.deg2rad(4.0),
                         reach=np.deg2rad(25.0), clean_T=0.75, clean_depth=0.5):
    """The thermal boundary layer's thickness beside the trench: the median depth of the
    ``T_bl`` isotherm over the columns within ``reach`` of the trench, skipping the
    slab (columns within ``exclude`` of it, or still colder than ``clean_T`` at
    ``clean_depth``). ``T`` is (n_depth, n_theta) on the grid of ``polar_grid``.
    Returns None when no column qualifies."""
    dth = (theta - theta_t + np.pi) % (2 * np.pi) - np.pi
    i_clean = int(np.argmin(np.abs(depth - clean_depth)))
    found = []
    for j in np.flatnonzero((np.abs(dth) >= exclude) & (np.abs(dth) <= reach)):
        column = T[:, j]
        if column[i_clean] < clean_T:
            continue
        above = np.flatnonzero(column >= T_bl)
        if above.size and above[0] > 0:
            i = above[0]
            # linear interpolation between the bracketing samples
            f = (T_bl - column[i - 1]) / max(column[i] - column[i - 1], 1e-30)
            found.append(depth[i - 1] + f * (depth[i] - depth[i - 1]))
    return float(np.median(found)) if found else None


def rank_bands(theta, depth, gamma, edot, T, v_r, gamma_sat=0.5, T_lith=0.6, depth_max=0.45,
               depth_min=0.05, descent=0.1, min_points=20, periodic=True, r_o=None):
    """Every candidate band (saturated, cold, descending, below the surface layer), as
    [(theta_centroid, sum of gamma, sum of edot_plastic, n_points, damage), ...] in
    decreasing order of accumulated strain: where the lid is failing, and how much.
    ``damage`` is the strain integrated over the band's area (sum of gamma r dtheta
    ddepth, grid-independent), given ``r_o``; NaN without it."""
    band = (depth[:, None] >= depth_min) & (depth[:, None] <= depth_max)
    v_down = max(float(-np.min(np.where(band, v_r, 0.0))), 1e-30)
    mask = (gamma >= gamma_sat) & (T <= T_lith) & band & (v_r <= -descent * v_down)
    labels, n = ndimage.label(mask, structure=np.ones((3, 3)))
    for i in range(labels.shape[0] if periodic else 0):
        a, b = labels[i, 0], labels[i, -1]
        if a and b and a != b:
            labels[labels == b] = a
    out = []
    for k in np.unique(labels[labels > 0]):
        sel = labels == k
        if sel.sum() < min_points:
            continue
        jj = np.nonzero(sel)[1]
        # circular mean of the column angles
        th = float(np.arctan2(np.sin(theta[jj]).mean(), np.cos(theta[jj]).mean()))
        damage = float("nan")
        if r_o is not None:
            ii = np.nonzero(sel)[0]
            dA = (r_o - depth[ii]) * abs(theta[1] - theta[0]) * abs(depth[1] - depth[0])
            damage = float((gamma[sel] * dA).sum())
        out.append((th, float(gamma[sel].sum()), float(edot[sel].sum()), int(sel.sum()), damage))
    return sorted(out, key=lambda b: -b[1])


def fit_fault_lines(theta, depth, gamma, T, r_o, gamma_sat=0.5, T_lith=0.6, depth_min=0.02,
                    depth_max=0.45, n_max=6, min_damage=0.01, width=0.035, gap=0.05,
                    trials=400, seed=1, dip_min=30.0, surface_reach=0.05):
    """Straight faults fitted to the damage: up to ``n_max`` lines extracted one at a time
    (RANSAC) from the saturated lithospheric points (gamma >= gamma_sat, T <= T_lith,
    depth_min <= depth <= depth_max). A candidate line scores the strain-area (damage)
    of its inliers (within ``width``) along its longest run without a gap wider than
    ``gap``; the best is refined by a weighted fit to that run, its inliers are removed,
    and the search repeats while the damage of the next line exceeds ``min_damage``.
    A fault is continuous to the surface: a line whose shallowest damage lies deeper
    than ``surface_reach`` is discarded, and its depth is that of the run of damage
    connected to the surface (the run is already gap-free along the line, to ``gap``).
    Each line gives the trench angle (its intersection with the outer wall), the dip
    angle phi below the local horizontal from +theta, its depth range (shallowest and
    deepest inlier) and its damage. Deterministic for a given ``seed``, so every rank
    that sees the same field makes the same choice."""
    TH, DD = np.meshgrid(theta, depth)
    ok = (gamma >= gamma_sat) & (T <= T_lith) & (DD >= depth_min) & (DD <= depth_max)
    if ok.sum() < 10:
        return []
    r = r_o - DD[ok]
    pts = np.stack([r * np.cos(TH[ok]), r * np.sin(TH[ok])], axis=1)
    w = gamma[ok] * r * abs(theta[1] - theta[0]) * abs(depth[1] - depth[0])   # damage per point
    rng = np.random.default_rng(seed)
    alive = np.ones(len(pts), dtype=bool)
    lines = []

    def best_run(c, u, idx):
        """Inliers of the line (c, u) among ``idx``, cut to their heaviest gap-free run."""
        d = np.abs((pts[idx] - c) @ np.array([-u[1], u[0]]))
        inl = idx[d <= width]
        if inl.size < 5:
            return inl[:0], 0.0
        s = (pts[inl] - c) @ u
        order = np.argsort(s)
        inl, s = inl[order], s[order]
        cuts = np.flatnonzero(np.diff(s) > gap) + 1
        runs = np.split(np.arange(len(inl)), cuts)
        scores = [w[inl[run]].sum() for run in runs]
        k = int(np.argmax(scores))
        return inl[runs[k]], float(scores[k])

    for _ in range(n_max):
        idx = np.flatnonzero(alive)
        if idx.size < 10:
            break
        p = w[idx] / w[idx].sum()
        best = (None, 0.0, None)
        for _t in range(trials):
            a, b = rng.choice(idx, size=2, replace=False, p=p)
            v = pts[b] - pts[a]
            L = np.linalg.norm(v)
            if L < 0.05:
                continue
            u = v / L
            # a line within dip_min of the local horizontal is the strained skin along
            # the surface, not a fault
            mid = 0.5 * (pts[a] + pts[b])
            r_hat = mid / np.linalg.norm(mid)
            if abs(u @ r_hat) < np.sin(np.deg2rad(dip_min)):
                continue
            inl, score = best_run(pts[a], u, idx)
            if score > best[1]:
                best = (inl, score, (pts[a], u))
        inl, score, _ = best
        if inl is None or score < min_damage:
            break
        # refine on the run (weighted principal axis), then re-collect the run once
        for _r in range(2):
            ww = w[inl] / w[inl].sum()
            c = (ww[:, None] * pts[inl]).sum(axis=0)
            X = pts[inl] - c
            cov = (ww[:, None, None] * X[:, :, None] * X[:, None, :]).sum(axis=0)
            u = np.linalg.eigh(cov)[1][:, 1]
            inl2, score2 = best_run(c, u, idx)
            if score2 < min_damage or inl2.size < 5:
                break
            inl, score = inl2, score2
        # a refined line can rotate toward the horizontal: the skin again, not a fault
        r_hat_c = c / np.linalg.norm(c)
        if abs(u @ r_hat_c) < np.sin(np.deg2rad(dip_min)):
            alive[inl] = False
            continue
        # the trench: the line's crossing of the outer wall nearest the band
        bq = c @ u
        disc = bq * bq - (c @ c - r_o ** 2)
        if disc < 0:
            alive[inl] = False
            continue
        s_roots = np.array([-bq - np.sqrt(disc), -bq + np.sqrt(disc)])
        trench = c + s_roots[np.argmin(np.abs(s_roots))] * u
        r_hat = trench / np.linalg.norm(trench)
        t_hat = np.array([-r_hat[1], r_hat[0]])
        down = -u if u @ r_hat > 0 else u
        phi = float(np.degrees(np.arctan2(-down @ r_hat, down @ t_hat)))     # 0..180
        dep = r_o - np.hypot(pts[inl, 0], pts[inl, 1])
        # retire the run's points either way; only a surface-reaching run is a fault
        d_all = np.abs((pts - c) @ np.array([-u[1], u[0]]))
        s_all = (pts - c) @ u
        s_in = (pts[inl] - c) @ u
        alive &= ~((d_all <= 1.5 * width) & (s_all >= s_in.min() - gap) & (s_all <= s_in.max() + gap))
        if dep.min() > surface_reach:
            continue
        lines.append({"theta_t": float(np.arctan2(trench[1], trench[0])), "phi": phi,
                      "depth_top": float(dep.min()), "depth_bottom": float(dep.max()),
                      "damage": score, "n_points": int(inl.size), "trench": trench, "down": down})
    return lines


def spine_separation(a, b):
    """The smallest distance between two fault spines (dense polylines of points, each
    straight), taken both ways: the points of one against the segment of the other."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)

    def to_segment(points, p, q):
        pq = q - p
        s = np.clip(((points - p) @ pq) / max(pq @ pq, 1e-30), 0.0, 1.0)
        return np.linalg.norm(points - (p + s[:, None] * pq), axis=1).min()

    return float(min(to_segment(a, b[0], b[-1]), to_segment(b, a[0], a[-1])))
