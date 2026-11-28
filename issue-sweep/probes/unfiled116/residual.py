"""116 residual: the worst cell of an outcrop placement and where its vertices come from."""
import os, sys
import numpy as np
import underworld3 as uw
import underworld3.utilities.place_surface as ps

os.environ.update(UW_EXP_SNAP="0.5", UW_EXP_CAP_CELLS="0.25", UW_EXP_MARGIN_ROWS="2", UW_EXP_RAIL_CELLS="0.25")
dip_deg, k = float(sys.argv[1]), float(sys.argv[2])
captured = {}
real = ps._ladder_outcrop_assembly_2d
def wrapped(S, R, width, size, domain):
    pts, tris, area = real(S, R, width, size, domain)
    captured.update(S=np.asarray(S), R=np.asarray(R), pts=pts, width=width, size=size)
    return pts, tris, area
ps._ladder_outcrop_assembly_2d = wrapped
base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.4, cellSize=0.05, refinement=1, qdegree=2)
bX = base.dm.getCoordinatesLocal().array.reshape(-1, 2)
wall = bX[np.linalg.norm(bX, axis=1) > 1 - 1e-9]; wall = wall[np.argsort(np.arctan2(wall[:, 1], wall[:, 0]))]
wedges = [(i, (i + 1) % len(wall)) for i in range(len(wall))]
h = 0.025; th, dip = np.radians(90), np.radians(dip_deg)
r = np.array([np.cos(th), np.sin(th)]); t = np.array([-np.sin(th), np.cos(th)]); d = -np.cos(dip) * t - np.sin(dip) * r
trace = (1 - k * h) * r + (h * np.arange(7))[:, None] * d
mesh, info = ps.place_fault_ribbon_2d(base, [("F", trace)], 2 * h, margin_rings=2, clearance=0.3, split=True, mesher="ladder")
dm = mesh.dm; vS, vE = dm.getDepthStratum(0); cS, cE = dm.getHeightStratum(0)
X = dm.getCoordinatesLocal().array.reshape(-1, 2)
band = np.asarray(info["band"])
worst = (180, None)
for c in range(cS, cE):
    cl = dm.getTransitiveClosure(c)[0]; v = cl[(cl >= vS) & (cl < vE)] - vS; P = X[v]
    angs = [np.degrees(np.arccos(np.clip((P[(i+1)%3]-P[i]) @ (P[(i+2)%3]-P[i]) / np.linalg.norm(P[(i+1)%3]-P[i]) / np.linalg.norm(P[(i+2)%3]-P[i]), -1, 1))) for i in range(3)]
    if min(angs) < worst[0]: worst = (min(angs), c, P, angs)
a, c, P, angs = worst
S = captured["S"]; R = captured["R"]; w = captured["width"]
rows = np.stack([S + 0.5 * w * R, S, S - 0.5 * w * R], axis=1)       # rail+, spine, rail-
n_rows = len(S)
# which of the S rows are trace samples: the trace's own points
is_trace = [np.linalg.norm(trace - s, axis=1).min() < 1e-12 for s in S]
print(f"dip {dip_deg} k {k}: worst {a:.2f} deg, in band {bool(band[c - cS])}, angles {[round(x, 1) for x in angs]}")
for p in P:
    dw = float(ps._segments_distance(p[None], wall, wedges)[0]) / h
    hit = np.argwhere(np.linalg.norm(rows - p, axis=2) < 1e-10)
    where = (f"ladder row {hit[0][0]} ({'trace' if is_trace[hit[0][0]] else 'margin'}) "
             f"{['rail+', 'spine', 'rail-'][hit[0][1]]}" if len(hit) else
             ("base wall vertex" if np.linalg.norm(wall - p, axis=1).min() < 1e-12 else
              ("assembly (cap) vertex" if np.linalg.norm(captured['pts'] - p, axis=1).min() < 1e-12 else "fill vertex")))
    print(f"   ({p[0]:+.5f},{p[1]:.5f})  {dw:.3f} cells from the wall  {where}")
E = [np.linalg.norm(P[i] - P[(i + 1) % 3]) / h for i in range(3)]
print("   edges/h", [round(x, 3) for x in E])
