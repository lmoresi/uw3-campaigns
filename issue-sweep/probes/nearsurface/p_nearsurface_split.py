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
            clearance=a.clearance, split=bool(a.split), mesher="ladder")
        n = band_touches_wall(mesh, info["band"])
        out = (f"outcrop (band cells on the wall {n})" if n else "interior")
        out = "placed " + out
        # n_cells is this rank's count; the comparison across ranks is on the
        # outcome, so the count is reported after the gather, rank 0's only
        ncl = info["n_cells"]
    except Exception as exc:              # noqa: BLE001 - the probe records it
        out = f"REFUSED {type(exc).__name__}: {exc}"
        ncl = None
    outs = comm.gather(out, root=0)
    if rank == 0:
        same = all(o == outs[0] for o in outs)
        cells = f"  n_cells(rank 0) {ncl}" if ncl is not None else ""
        print(f"{tag}  | {outs[0]}{cells}", flush=True)
        if size > 1:
            print(f"    ranks agree: {same}", flush=True)
            if not same:
                for r, o in enumerate(outs):
                    print(f"    rank {r}: {o}", flush=True)
p0("DONE")
sys.stdout.flush()
