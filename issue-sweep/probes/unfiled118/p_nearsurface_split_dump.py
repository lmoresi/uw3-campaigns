"""A dipping fault whose split top lies k cells below the outer wall of an annulus.

The fixture is test_0865's (an annulus of outer radius 1 built with one
refinement, a ladder ribbon placed by ``place_fault_ribbon_2d``), with a
smaller cell (cellSize 0.05, so h = 0.025) and an inner radius of 0.4, so
that the fault's lower end stays clear of the inner wall at every k. Everything is in cells of the nominal size h:
the band width is 2 h, the trace is sampled every h (7 points, length 6 h),
the default tip margin of 2 rings extends the band 2 h past each end, and the
default clearance 0.3 is used. Only k, the depth of the trace's top below the
outer wall in cells, varies. The dip is from the local horizontal (the wall's
tangent), down towards decreasing angle.

Outcomes, one line per rank and per k:
  outcrop   placed, and band cells touch the outer wall
  interior  placed, and no band cell touches the outer wall
  REFUSED   the placement raised; the full message follows
"""
import argparse
import sys

import numpy as np

import underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d
import inspect
import underworld3.utilities.place_surface as _ps

# H1 parallel probe: record, per rank, which wall site fired (caller line) and
# the gap numbers, by wrapping the module-level helpers the sites call.
SITE_LOG = []


def _wrap(name):
    f = getattr(_ps, name, None)
    if f is None:
        return

    def g(*args, **kw):
        line = inspect.currentframe().f_back.f_lineno
        out = f(*args, **kw)
        if name == "_wall_gap_2d":
            gap, hh, at = out
            extra = ""
            if len(args) >= 7:
                ring, X, on_wall, bp = args[0], args[1], args[2], args[6]
                ring = [int(v) for v in ring]
                prs = [(a, b) for a, b in zip(ring, ring[1:] + ring[:1])
                       if a < len(X) and b < len(X)]
                nb = sum(frozenset(p) in bp for p in prs)
                nw = sum(bool(on_wall[a] and on_wall[b]) for a, b in prs)
                nseam = sum(frozenset((a, b)) in bp and not (on_wall[a] and on_wall[b])
                            for a, b in prs)
                extra = f" ringpairs_in_boundary={nb} ringpairs_both_on_wall={nw} boundary_not_wall={nseam}"
            SITE_LOG.append(f"{name}@L{line} gap={gap:.4g} h={hh:.4g} "
                            f"gap/h={gap / hh:.3f} at=({at[0]:.4g},{at[1]:.4g}){extra}")
        else:
            SITE_LOG.append(f"{name}@L{line}")
        return out
    setattr(_ps, name, g)


for _n in ("_wall_gap_2d", "_wall_refusal_2d"):
    _wrap(_n)

# H1: dump each fill's inputs, per rank, before gmsh sees them (DUMP_FILL=dir)
import os as _os0
if _os0.environ.get("DUMP_FILL"):
    _fill0 = _ps._gmsh_fill_2d
    _nfill = [0]

    def _fill_dump(Xall, ring, chain, holes=(), size_of=None):
        from mpi4py import MPI as _M
        r = _M.COMM_WORLD.rank
        fn = f"{_os0.environ['DUMP_FILL']}/fill_rank{r}_{_nfill[0]}.npz"
        _nfill[0] += 1
        np.savez(fn, Xall=np.asarray(Xall), ring=np.asarray(ring),
                 chain=np.asarray(chain if chain is not None else []),
                 holes=np.array([np.asarray(h) for h in holes], dtype=object),
                 has_size=size_of is not None)
        print(f"[rank {r}] fill dump {fn} ring {len(ring)} holes {len(holes)}", flush=True)
        return _fill0(Xall, ring, chain, holes=holes, size_of=size_of)
    _ps._gmsh_fill_2d = _fill_dump

ap = argparse.ArgumentParser()
ap.add_argument("--cellsize", type=float, default=0.05,
                help="Annulus cellSize; with refinement 1, h = cellsize / 2")
ap.add_argument("--rin", type=float, default=0.4,
                help="inner radius: deep enough that the fault's lower end stays clear")
ap.add_argument("--dip", type=float, default=30.0, help="degrees from horizontal")
ap.add_argument("--k", type=str, default="0:10.01:0.5",
                help="start:stop:step or comma list, in cells")
ap.add_argument("--clearance", type=float, default=0.3)
ap.add_argument("--width-cells", type=float, default=2.0)
ap.add_argument("--npts", type=int, default=7)
ap.add_argument("--margin", type=int, default=2)
ap.add_argument("--split", type=int, default=1)
ap.add_argument("--theta", type=float, default=90.0, help="angle of the top, degrees")
ap.add_argument("--mesher", default="ladder", help="ladder (gather path) or network")
ap.add_argument("--seams", default="gather", help="gather or conform (conform needs network)")
a = ap.parse_args()

comm = uw.mpi.comm
rank, size = comm.rank, comm.size


def p0(*s):
    if rank == 0:
        print(*s, flush=True)


if ":" in a.k:
    k0, k1, dk = (float(x) for x in a.k.split(":"))
    ks = np.arange(k0, k1, dk)
else:
    ks = np.array([float(x) for x in a.k.split(",")])

h = a.cellsize / 2.0
width = a.width_cells * h
p0(f"underworld3.__file__ = {uw.__file__}")
p0(f"place_surface.__file__ = {_ps.__file__}")
p0(f"mesher = {a.mesher}  seams = {a.seams}")
import os as _os
if rank == 0 and _os.environ.get("CMP_REPORT") and _os.path.exists(_os.environ["CMP_REPORT"]):
    print(open(_os.environ["CMP_REPORT"]).read(), flush=True)
p0(f"np = {size}  cellsize = {a.cellsize}  h = {h:.4g}  dip = {a.dip} deg  "
   f"width = {width:.4g} ({a.width_cells} h)  spacing = h  npts = {a.npts}  "
   f"margin_rings = {a.margin}  radiusInner = {a.rin}  clearance = {a.clearance}  split = {bool(a.split)}")
reach = max(a.clearance * h, 0.6 * width)
p0(f"carve reach = max(clearance*h, 0.6*width) = {reach:.4g} = {reach / h:.3g} h")

base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=a.rin, cellSize=a.cellsize,
                          refinement=1, qdegree=2)


def wall_h(dm):
    """Mean edge length on the outer wall within 0.2 of the top (local h)."""
    eS, eE = dm.getDepthStratum(1)
    vS, _vE = dm.getDepthStratum(0)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    th = np.radians(a.theta)
    top = np.array([np.cos(th), np.sin(th)])
    L = []
    for e in range(eS, eE):
        v = [int(q) - vS for q in dm.getCone(e)]
        r = np.linalg.norm(X[v], axis=1)
        if (r > 1.0 - 1e-6).all() and np.linalg.norm(X[v].mean(0) - top) < 0.2:
            L.append(np.linalg.norm(X[v[0]] - X[v[1]]))
    L = comm.allgather(L)
    L = [x for y in L for x in y]
    return float(np.mean(L)) if L else float("nan")


p0(f"measured wall edge length near the top = {wall_h(base.dm):.4g}")


def owned_mask(dm):
    pS, pE = dm.getChart()
    own = np.ones(pE - pS, dtype=bool)
    try:
        _nr, loc, _rem = dm.getPointSF().getGraph()
        if loc is not None and len(loc):
            own[np.asarray(loc) - pS] = False
    except Exception:
        pass
    return own, pS


def label_count(mesh, name):
    """Owned facets in label ``name`` at its boundary value: (local, global),
    and whether this rank's DM has the label."""
    dm = mesh.dm
    vals = {b.name: b.value for b in mesh.boundaries}
    has = bool(dm.hasLabel(name))
    if name not in vals or not has:
        return 0, comm.allreduce(0), has, name in vals
    own, pS = owned_mask(dm)
    eS, eE = dm.getDepthStratum(1)
    # an empty stratum gives a null IS on that rank: ask its size first
    if dm.getStratumSize(name, int(vals[name])) > 0:
        pts = np.asarray(dm.getStratumIS(name, int(vals[name])).getIndices())
    else:
        pts = np.zeros(0, dtype=np.int64)
    pts = pts[(pts >= eS) & (pts < eE)]
    n = int(own[pts - pS].sum())
    return n, comm.allreduce(n), has, True


def wall_geom(mesh, r0, name):
    """Facets geometrically on circle r0 (support 1): owned count, and local
    ones (owned or ghost) missing ``name``'s value."""
    dm = mesh.dm
    vals = {b.name: b.value for b in mesh.boundaries}
    own, pS = owned_mask(dm)
    vS, _vE = dm.getDepthStratum(0)
    eS, eE = dm.getDepthStratum(1)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    lab = dm.getLabel(name)
    geo, unl = 0, 0
    for e in range(eS, eE):
        if dm.getSupportSize(e) != 1:
            continue
        v = [int(q) - vS for q in dm.getCone(e)]
        if (np.abs(np.linalg.norm(X[v], axis=1) - r0) < 1e-6).all():
            if own[e - pS]:
                geo += 1
            if lab is None or lab.getValue(e) != vals[name]:
                unl += 1
    return geo, comm.allreduce(geo), unl, comm.allreduce(unl)


def stats(mesh):
    up_l, up_g, up_has, _ = label_count(mesh, "Upper")
    lo_l, lo_g, _h, _ = label_count(mesh, "Lower")
    geo_l, geo_g, unl_l, unl_g = wall_geom(mesh, 1.0, "Upper")
    fp = label_count(mesh, "FaultPlus")
    fm = label_count(mesh, "FaultMinus")
    fl = label_count(mesh, "Fault")
    return dict(up_l=up_l, up_g=up_g, up_has=up_has, lo_g=lo_g, geo_l=geo_l,
                geo_g=geo_g, unl_l=unl_l, unl_g=unl_g,
                fp_l=fp[0], fp_g=fp[1], fp_has=fp[2], fp_bnd=fp[3],
                fm_l=fm[0], fm_g=fm[1], fm_has=fm[2], fm_bnd=fm[3],
                f_g=fl[1])


BASE = stats(base)
_bs = comm.gather(BASE, root=0)
if rank == 0:
    for r, b in enumerate(_bs):
        print(f"  base rank {r}: Upper owned {b['up_l']} (global {b['up_g']}), "
              f"outer-circle facets owned {b['geo_l']} (global {b['geo_g']}), "
              f"unlabelled outer {b['unl_l']} (global {b['unl_g']}), Lower global {b['lo_g']}",
              flush=True)

th = np.radians(a.theta)
dip = np.radians(a.dip)
r_hat = np.array([np.cos(th), np.sin(th)])
t_hat = np.array([-np.sin(th), np.cos(th)])          # towards increasing angle
d_hat = -np.cos(dip) * t_hat - np.sin(dip) * r_hat    # down-dip
up = -d_hat


def band_touches_wall(mesh, band):
    dm = mesh.dm
    vS, vE = dm.getDepthStratum(0)
    cS, _cE = dm.getHeightStratum(0)
    X = dm.getCoordinatesLocal().array.reshape(-1, 2)
    hit = 0
    for c in np.flatnonzero(band):
        cl = dm.getTransitiveClosure(cS + int(c))[0]
        v = cl[(cl >= vS) & (cl < vE)] - vS
        if (np.linalg.norm(X[v], axis=1) > 1.0 - 1e-6).any():
            hit += 1
    return comm.allreduce(hit)


for k in ks:
    top = (1.0 - k * h) * r_hat
    trace = top + (h * np.arange(a.npts))[:, None] * d_hat
    ext_top = top + a.margin * h * up
    # the highest point of the ladder band: the extended end, raised by the
    # upper rail's half width
    rail = 0.5 * width * np.array([d_hat[1], -d_hat[0]])
    corners = [ext_top + rail, ext_top - rail]
    band_top_depth = 1.0 - max(np.linalg.norm(c) for c in corners)
    tag = (f"k = {k:4.1f}  top depth = {k * h:.4f} ({k:.1f} h)  "
           f"band top depth = {band_top_depth:+.4f} ({band_top_depth / h:+.2f} h)")
    try:
        mesh, info = place_fault_ribbon_2d(
            base, [("Fault", trace)], width, margin_rings=a.margin,
            clearance=a.clearance, split=bool(a.split), mesher=a.mesher,
            seams=a.seams)
        n = band_touches_wall(mesh, info["band"])
        out = (f"outcrop (band cells on the wall {n})" if n else "interior")
        out = "placed " + out
        # n_cells is this rank's count; the comparison across ranks is on the
        # outcome, so the count is reported after the gather, rank 0's only
        ncl = info["n_cells"]
        st = stats(mesh)
    except Exception as exc:              # noqa: BLE001 - the probe records it
        out = f"REFUSED {type(exc).__name__}: {exc}"
        ncl = None
        st = None
    sites = list(SITE_LOG)
    SITE_LOG.clear()
    outs = comm.gather(out, root=0)
    sts = comm.gather(st, root=0)
    sitess = comm.gather(sites, root=0)
    if rank == 0:
        same = all(o == outs[0] for o in outs)
        cells = f"  n_cells(rank 0) {ncl}" if ncl is not None else ""
        print(f"{tag}  | {outs[0]}{cells}", flush=True)
        if size > 1:
            print(f"    ranks agree: {same}", flush=True)
            for r, o in enumerate(outs):
                print(f"    rank {r}: {o}", flush=True)
        for r, (t, ss) in enumerate(zip(sts, sitess)):
            print(f"    rank {r} sites: {ss if ss else 'none'}", flush=True)
            if t is None:
                continue
            print(f"    rank {r} labels: Upper owned {t['up_l']} global {t['up_g']} "
                  f"(base {BASE['up_g']}) has={t['up_has']}; outer-circle facets owned "
                  f"{t['geo_l']} global {t['geo_g']} (base {BASE['geo_g']}); unlabelled "
                  f"outer local {t['unl_l']} global {t['unl_g']}; Lower global {t['lo_g']} "
                  f"(base {BASE['lo_g']}); FaultPlus has={t['fp_has']} bnd={t['fp_bnd']} owned "
                  f"{t['fp_l']} global {t['fp_g']}; FaultMinus has={t['fm_has']} bnd={t['fm_bnd']} "
                  f"owned {t['fm_l']} global {t['fm_g']}; Fault global {t['f_g']}", flush=True)
        ok = [t for t in sts if t is not None]
        if ok:
            keys = ("up_g", "geo_g", "unl_g", "lo_g", "fp_g", "fm_g", "f_g")
            glob_agree = all(all(t[k] == ok[0][k] for k in keys) for t in ok)
            t = ok[0]
            verdict = (t["up_g"] == BASE["up_g"] and t["geo_g"] == BASE["geo_g"]
                       and t["unl_g"] == 0 and t["lo_g"] == BASE["lo_g"]
                       and all(x["fp_has"] and x["fm_has"] for x in ok)
                       and t["fp_g"] > 0 and t["fp_g"] == t["fm_g"])
            print(f"    CHECK globals agree across ranks: {glob_agree}; wall intact "
                  f"and FaultPlus==FaultMinus>0 on all ranks: {verdict}; "
                  f"placed ranks {len(ok)}/{len(sts)}", flush=True)
p0("DONE")
sys.stdout.flush()
