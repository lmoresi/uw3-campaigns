"""Review of PR #1130: line_cut at the PR head against development's line_cut,
on one rank, same process.

development's module is read with ``git show`` and executed into a module
object of its own (nothing installed is edited). Each case is run through both
and the result compared bit for bit: the coordinates returned, the info record
of a cut, or the text of the refusal.

Run from the worktree:
    OMP_NUM_THREADS=1 pixi run -e runtime python <this file> [-uw_n_targets 300]
"""
import subprocess
import sys
import types

import numpy as np
from petsc4py import PETSc

import underworld3 as uw
from underworld3.utilities import line_cut as HEAD

params = uw.Params(
    uw_n_targets=uw.Param(300, description="random targets per mesh for the pull sweep"),
    uw_seed=uw.Param(1130, description="seed of the target sweep"),
    uw_dev_ref=uw.Param("origin/development", description="git ref of the comparison"),
)

src = subprocess.run(
    ["git", "show", f"{params.uw_dev_ref}:src/underworld3/utilities/line_cut.py"],
    check=True, capture_output=True, text=True).stdout
DEV = types.ModuleType("underworld3.utilities.line_cut_development")
DEV.__dict__["__name__"] = "underworld3.utilities.line_cut_development"
exec(compile(src, "line_cut_development.py", "exec"), DEV.__dict__)
assert not hasattr(DEV, "_global_flip") and hasattr(HEAD, "_global_flip")
print("uw:", uw.__file__)
print("development ref:", subprocess.run(["git", "rev-parse", str(params.uw_dev_ref)],
                                         capture_output=True, text=True).stdout.strip())


def outcome(module, kind, dm, *args, **kwargs):
    """('ok', bytes of coordinates, info) or ('raise', type, message)."""
    try:
        if kind == "pull":
            out = module.pull_vertex_onto(dm, *args, **kwargs)
            return ("ok", module._coords(out).tobytes(), None)
        out, info = module.cut_along_lines(dm, *args, **kwargs)
        return ("ok", module._coords(out).tobytes(), tuple(sorted(info.items())))
    except Exception as err:        # the refusal is the outcome compared
        return ("raise", type(err).__name__, str(err))


tally = {}


def compare(name, kind, dm, *args, **kwargs):
    a = outcome(HEAD, kind, dm, *args, **kwargs)
    b = outcome(DEV, kind, dm, *args, **kwargs)
    row = tally.setdefault(name, dict(n=0, equal=0, ok=0, refused=0, differ=[]))
    row["n"] += 1
    row["equal"] += int(a == b)
    row["ok"] += int(a[0] == "ok")
    row["refused"] += int(a[0] == "raise")
    if a != b:
        row["differ"].append((args, a[:2] if a[0] == "ok" else a, b[:2] if b[0] == "ok" else b))
    return a, b


def mirrored(dm):
    """The same mesh with x -> -x: every cell is listed clockwise."""
    out = dm.clone()
    X = HEAD._coords(dm).copy()
    X[:, 0] *= -1.0
    HEAD._set_coordinates(out, np.arange(len(X)), X)
    return out


def inside_out(dm):
    """A sphere surface mesh with X -> -X: every cell is wound inward."""
    out = dm.clone()
    X = HEAD._coords(dm).copy()
    HEAD._set_coordinates(out, np.arange(len(X)), -X)
    return out


rng = np.random.default_rng(int(params.uw_seed))
N = int(params.uw_n_targets)

# ---------------------------------------------------------------- 2-D boxes
for regular in (True, False):
    box = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                            cellSize=1.0 / 12.0, regular=regular)
    tag = f"box 1/12 {'regular' if regular else 'irregular'}"
    straight = np.array([[0.31, -0.1], [0.62, 1.1]])
    kinked = np.array([[-0.1, 0.33], [0.4, 0.41], [0.6, 0.72], [1.1, 0.66]])
    for line_name, line in (("straight", straight), ("kinked", kinked)):
        for frac in (0.0, 0.1, 0.3, 0.49):
            compare(f"{tag}: cut, {line_name}", "cut", box.dm, [line], snap_frac=frac)
            compare(f"{tag}: cut, {line_name} reversed", "cut", box.dm, [line[::-1].copy()],
                    snap_frac=frac)
    # a fault ending inside: tips pulled, then cut (what add_fault does)
    tips = np.array([[0.3, 0.45], [0.7, 0.55]])
    for order in (tips, tips[::-1].copy()):
        a, b = compare(f"{tag}: pull, two tips", "pull", box.dm, order)
        if a[0] == "ok":
            pulled = HEAD.pull_vertex_onto(box.dm, order)
            compare(f"{tag}: cut after the pull", "cut", pulled, [order])
    # the wall rule: targets inside the cells along the walls
    T = rng.uniform(0.0, 1.0, size=(N, 2))
    near = rng.integers(0, 4, size=N)
    depth = rng.uniform(0.0, 1.0 / 12.0, size=N)
    T[near == 0, 0] = depth[near == 0]
    T[near == 1, 0] = 1.0 - depth[near == 1]
    T[near == 2, 1] = depth[near == 2]
    T[near == 3, 1] = 1.0 - depth[near == 3]
    for t in T:
        compare(f"{tag}: pull, target beside a wall", "pull", box.dm, t)
    for t in rng.uniform(0.0, 1.0, size=(N, 2)):
        compare(f"{tag}: pull, target anywhere", "pull", box.dm, t)
    for k in range(N // 4):
        compare(f"{tag}: pull, four targets in one call", "pull", box.dm, T[4 * k:4 * k + 4])
    clock = mirrored(box.dm)
    for t in T:
        compare(f"{tag} mirrored (clockwise): pull beside a wall", "pull", clock,
                t * np.array([-1.0, 1.0]))
    compare(f"{tag} mirrored (clockwise): cut", "cut", clock,
            [straight * np.array([-1.0, 1.0])])

# ---------------------------------------------------------------- annulus
ann = uw.meshing.Annulus(radiusInner=0.5, radiusOuter=1.0, cellSize=0.1)
r = np.where(rng.uniform(size=N) < 0.5, rng.uniform(0.5, 0.6, size=N),
             rng.uniform(0.9, 1.0, size=N))
th = rng.uniform(0.0, 2 * np.pi, size=N)
for t in np.column_stack([r * np.cos(th), r * np.sin(th)]):
    compare("annulus 0.1: pull, target beside a curved wall", "pull", ann.dm, t)
arc = np.column_stack([0.75 * np.cos(np.linspace(0.2, 1.4, 9)),
                       0.75 * np.sin(np.linspace(0.2, 1.4, 9))])
for poly in (arc, arc[::-1].copy()):
    a, b = compare("annulus 0.1: pull, arc control points", "pull", ann.dm, poly)
    if a[0] == "ok":
        compare("annulus 0.1: cut along the arc", "cut",
                HEAD.pull_vertex_onto(ann.dm, poly), [poly])
radial = np.array([[0.4, 0.05], [1.1, 0.12]])
for frac in (0.0, 0.1, 0.3):
    compare("annulus 0.1: cut wall to wall", "cut", ann.dm, [radial], snap_frac=frac)

# ---------------------------------------------------------------- sphere surface (3-D coordinates)
sphere = uw.meshing.SphericalManifold(radius=1.0, cellSize=0.2, degree=1, qdegree=2)
P_s = HEAD._coords(sphere.dm)[HEAD._cell_vertices(sphere.dm)]
print("sphere surface: cells", len(P_s), "| wound inward", int((HEAD._outward_signed(P_s) < 0).sum()),
      "| vote", HEAD._global_flip(P_s))


def equator_arc(half_angle, n=9, tilt=0.0):
    phi = np.linspace(-half_angle, half_angle, n)
    P = np.column_stack([np.cos(phi), np.sin(phi), tilt * phi])
    return P / np.linalg.norm(P, axis=1)[:, None]


for label, dm, sign in (("sphere surface 0.2", sphere.dm, 1.0),
                        ("sphere surface 0.2 inside out", inside_out(sphere.dm), -1.0)):
    P_d = HEAD._coords(dm)[HEAD._cell_vertices(dm)]
    print(label, "| vote", HEAD._global_flip(P_d))
    for half, tilt in ((np.pi / 6, 0.0), (0.25, 0.3), (0.6, -0.2)):
        for arc3 in (sign * equator_arc(half, tilt=tilt), sign * equator_arc(half, tilt=tilt)[::-1].copy()):
            a, b = compare(f"{label}: pull, arc control points", "pull", dm, arc3)
            if a[0] == "ok":
                pulled = HEAD.pull_vertex_onto(dm, arc3)
                for frac in (0.0, 0.1, 0.3, 0.45):
                    compare(f"{label}: cut along the arc", "cut", pulled, [arc3], snap_frac=frac)
    U = rng.normal(size=(N, 3))
    for t in sign * U / np.linalg.norm(U, axis=1)[:, None]:
        compare(f"{label}: pull, target anywhere", "pull", dm, t)

# a sphere surface that already holds a split fault: the fault's sides are
# boundary, so the wall rule (the quality test) is reached in 3-D
split = sphere.add_fault(("Flt", equator_arc(np.pi / 6)))
on_wall = uw.utilities.place_surface._true_wall_vertex_mask(split.dm, len(HEAD._coords(split.dm)))
print("split sphere: boundary vertices", int(on_wall.sum()))
phi = rng.uniform(-np.pi / 6, np.pi / 6, size=N)
off = rng.uniform(-0.12, 0.12, size=N)
beside = np.column_stack([np.cos(phi) * np.cos(off), np.sin(phi) * np.cos(off), np.sin(off)])
for label, dm, sign in (("split sphere surface", split.dm, 1.0),
                        ("split sphere surface inside out", inside_out(split.dm), -1.0)):
    for t in sign * beside:
        compare(f"{label}: pull, target beside the fault", "pull", dm, t)

# ---------------------------------------------------------------- the 18-triangle grid of test_0844, flat and lifted
def grid(clockwise=False, mixed=False, lifted=False, wall_vertex_at=2.0):
    def row(i, j):
        return 4 * j + i
    V = np.array([[i, j] for j in range(4) for i in range(4)], dtype=float)
    V[row(0, 2)] = (0.0, wall_vertex_at)
    cells = []
    for j in range(3):
        for i in range(3):
            cells.append([row(i, j), row(i + 1, j), row(i + 1, j + 1)])
            cells.append([row(i, j), row(i + 1, j + 1), row(i, j + 1)])
    cells = np.array(cells, dtype=np.int32)
    if clockwise:
        cells = cells[:, ::-1].copy()
    if lifted:
        V = lift(V)
    return PETSc.DMPlex().createFromCellList(2, cells, V, comm=PETSc.COMM_SELF)


def lift(xy):
    """The grid [0, 3]^2 put on the unit sphere, 0.1 rad per unit."""
    xy = np.atleast_2d(xy)
    lon, lat = 0.1 * (xy[:, 0] - 1.5), 0.1 * (xy[:, 1] - 1.5)
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


G = rng.uniform(0.0, 3.0, size=(4 * N, 2))
for clockwise in (False, True):
    for lifted in (False, True):
        dm = grid(clockwise=clockwise, lifted=lifted)
        tag = (f"18-triangle grid {'on the sphere' if lifted else 'flat'}, "
               f"{'clockwise / inward' if clockwise else 'anticlockwise / outward'}")
        if lifted:
            P_g = HEAD._coords(dm)[HEAD._cell_vertices(dm)]
            print(tag, "| vote", HEAD._global_flip(P_g))
        for t in G:
            compare(f"{tag}: pull, one target", "pull", dm, lift(t)[0] if lifted else t)
        for k in range(N):
            pair = G[2 * k:2 * k + 2]
            compare(f"{tag}: pull, two targets in one call", "pull", dm,
                    lift(pair) if lifted else pair)
        for t in G[:N]:
            compare(f"{tag}: pull, floor off", "pull", dm, lift(t)[0] if lifted else t,
                    min_quality=None)

# ---------------------------------------------------------------- report
width = max(len(k) for k in tally)
print(f"\n{'case'.ljust(width)}  calls  placed/cut  refused  equal to development")
all_equal = True
for name, row in tally.items():
    print(f"{name.ljust(width)}  {row['n']:5d}  {row['ok']:10d}  {row['refused']:7d}  "
          f"{row['equal']:5d}{'' if row['equal'] == row['n'] else '   <-- DIFFERS'}")
    all_equal &= row["equal"] == row["n"]
    for d in row["differ"][:3]:
        print("     ", d)
print("\nTOTAL calls", sum(r["n"] for r in tally.values()),
      "| equal", sum(r["equal"] for r in tally.values()),
      "| every case bit-identical to development:", all_equal)
sys.exit(0)
