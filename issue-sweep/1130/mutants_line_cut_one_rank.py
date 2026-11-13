"""Review of PR #1130: mutants of the winding vote, in memory, on one rank.

1. Mutants of the PR head's line_cut (its installed source, changed as text and
   executed into a module object of its own; nothing installed is edited) run
   against the PR head on surface meshes in three dimensions, where the vote
   exists. Bit-identical output means the mutated line decides nothing there.
2. The arithmetic of the PR's test (b) for 2, 3 and 4 ranks, the collective
   replaced by a sum over the ranks' contributions, against the head, against
   development (the rank's own vote) and against mutants of ``_global_flip``.

    OMP_NUM_THREADS=1 pixi run -e runtime python <this file>
"""
import inspect
import subprocess
import types

import numpy as np
from mpi4py import MPI
from petsc4py import PETSc

import underworld3 as uw
from underworld3.utilities import line_cut as HEAD

params = uw.Params(
    uw_n_targets=uw.Param(300, description="random targets per fixture"),
    uw_seed=uw.Param(1130, description="seed of the targets"),
    uw_dev_ref=uw.Param("origin/development", description="git ref of the comparison"),
)
print("uw:", uw.__file__)
HEAD_SRC = inspect.getsource(HEAD)


def module_from(src, name, replacements=()):
    for old, new, count in replacements:
        assert src.count(old) == count, (name, old, src.count(old))
        src = src.replace(old, new)
    mod = types.ModuleType(f"underworld3.utilities.{name}")
    exec(compile(src, f"{name}.py", "exec"), mod.__dict__)
    return mod


PULL_VOTE = ("    flip = _global_flip(X[np.asarray(cell_verts, dtype=np.int64).reshape(-1, 3)])\n"
             "    wound = ")
SNAP_VOTE = ("    flip = _global_flip(X[np.asarray(cell_verts, dtype=np.int64).reshape(-1, 3)])\n"
             "    floor = ")
MUTANTS = {
    "pull: the vote inverted": [(PULL_VOTE, PULL_VOTE.replace(
        "\n    wound", "\n    flip = None if flip is None else (not flip)\n    wound"), 1)],
    "pull: no vote, convention fixed (flip False)": [(PULL_VOTE, PULL_VOTE.replace(
        "\n    wound", "\n    flip = None if flip is None else False\n    wound"), 1)],
    "pull: each reading votes for itself (flip None)": [(PULL_VOTE, PULL_VOTE.replace(
        "\n    wound", "\n    flip = None\n    wound"), 1)],
    "snap: the vote inverted": [(SNAP_VOTE, SNAP_VOTE.replace(
        "\n    floor", "\n    flip = None if flip is None else (not flip)\n    floor"), 1)],
    "snap: each reading votes for itself (flip None)": [(SNAP_VOTE, SNAP_VOTE.replace(
        "\n    floor", "\n    flip = None\n    floor"), 1)],
    "cut: inversion count on the rank's own vote": [
        ("areas = cell_areas(cut, global_vote=True)", "areas = cell_areas(cut)", 1)],
    "cut: inversion count with the vote inverted": [
        ("return 0.5 * _signed_twice_areas(P, _global_flip(P) if global_vote else None)",
         "return 0.5 * _signed_twice_areas(P, (not _global_flip(P)) if global_vote else None)", 1)],
}


def outcome(module, kind, dm, *args, **kwargs):
    try:
        if kind == "pull":
            return ("ok", module._coords(module.pull_vertex_onto(dm, *args, **kwargs)).tobytes())
        out, info = module.cut_along_lines(dm, *args, **kwargs)
        return ("ok", module._coords(out).tobytes(), tuple(sorted(info.items())))
    except Exception as err:
        return ("raise", type(err).__name__, str(err))


def inside_out(dm):
    out = dm.clone()
    X = HEAD._coords(dm).copy()
    HEAD._set_coordinates(out, np.arange(len(X)), -X)
    return out


def equator_arc(half_angle, n=9, tilt=0.0):
    phi = np.linspace(-half_angle, half_angle, n)
    P = np.column_stack([np.cos(phi), np.sin(phi), tilt * phi])
    return P / np.linalg.norm(P, axis=1)[:, None]


def lift(xy):
    xy = np.atleast_2d(xy)
    lon, lat = 0.1 * (xy[:, 0] - 1.5), 0.1 * (xy[:, 1] - 1.5)
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def lifted_grid(clockwise):
    def row(i, j):
        return 4 * j + i
    V = np.array([[i, j] for j in range(4) for i in range(4)], dtype=float)
    cells = []
    for j in range(3):
        for i in range(3):
            cells.append([row(i, j), row(i + 1, j), row(i + 1, j + 1)])
            cells.append([row(i, j), row(i + 1, j + 1), row(i, j + 1)])
    cells = np.array(cells, dtype=np.int32)
    if clockwise:
        cells = cells[:, ::-1].copy()
    return PETSc.DMPlex().createFromCellList(2, cells, lift(V), comm=PETSc.COMM_SELF)


rng = np.random.default_rng(int(params.uw_seed))
N = int(params.uw_n_targets)
sphere = uw.meshing.SphericalManifold(radius=1.0, cellSize=0.2, degree=1, qdegree=2)
split = sphere.add_fault(("Flt", equator_arc(np.pi / 6)))
phi = rng.uniform(-np.pi / 6, np.pi / 6, size=N)
off = rng.uniform(-0.12, 0.12, size=N)
beside = np.column_stack([np.cos(phi) * np.cos(off), np.sin(phi) * np.cos(off), np.sin(off)])
G = rng.uniform(0.0, 3.0, size=(N, 2))

cases = []      # (fixture, kind, dm, args, kwargs)
for label, dm, sign in (("split sphere", split.dm, 1.0), ("split sphere inside out", inside_out(split.dm), -1.0)):
    for t in sign * beside:
        cases.append((f"{label}: pull beside the fault", "pull", dm, (t,), {}))
for clockwise in (False, True):
    dm = lifted_grid(clockwise)
    for t in G:
        cases.append((f"grid on the sphere, {'inward' if clockwise else 'outward'}: pull", "pull",
                      dm, (lift(t)[0],), {}))
for label, dm, sign in (("sphere", sphere.dm, 1.0), ("sphere inside out", inside_out(sphere.dm), -1.0)):
    for half, tilt in ((np.pi / 6, 0.0), (0.25, 0.3), (0.6, -0.2)):
        arc = sign * equator_arc(half, tilt=tilt)
        pulled = HEAD.pull_vertex_onto(dm, arc)
        for frac in (0.0, 0.1, 0.3, 0.45):
            cases.append((f"{label}: cut along an arc", "cut", pulled, ([arc],), dict(snap_frac=frac)))

reference = [outcome(HEAD, kind, dm, *a, **k) for _f, kind, dm, a, k in cases]
fixtures = list(dict.fromkeys(c[0] for c in cases))
print("\nfixtures:", {f: sum(1 for c in cases if c[0] == f) for f in fixtures})
print("head: refused", {f: sum(1 for c, r in zip(cases, reference) if c[0] == f and r[0] == "raise")
                        for f in fixtures})
for name, repl in MUTANTS.items():
    mutant = module_from(HEAD_SRC, "line_cut_mutant", repl)
    differ = {f: 0 for f in fixtures}
    sample = None
    for (f, kind, dm, a, k), ref in zip(cases, reference):
        got = outcome(mutant, kind, dm, *a, **k)
        if got != ref:
            differ[f] += 1
            if sample is None and got[0] == "raise":
                sample = got[2][:110]
    total = sum(differ.values())
    print(f"mutant [{name}]: {total} of {len(cases)} calls differ from the head"
          + ("" if not total else f" {dict((f, n) for f, n in differ.items() if n)}"
             + (f" | e.g. {sample}" if sample else "")))

# ------------------------------------------------------------------ test (b), ranks emulated
def cap_triangle(centre_angle, inverted):
    th = [centre_angle, centre_angle + 0.05, centre_angle]
    ph = [0.0, 0.0, 0.05]
    P = np.array([[np.cos(p) * np.cos(t), np.cos(p) * np.sin(t), np.sin(p)] for t, p in zip(th, ph)])
    return P[[0, 2, 1]] if inverted else P


class SummingComm:
    """allreduce over emulated ranks: first pass records, second pass returns the sum."""
    def __init__(self):
        self.parts, self.total = [], None

    def allreduce(self, value, op=MPI.SUM):
        if self.total is None:
            self.parts.append(np.asarray(value))
            return np.asarray(value)
        return self.total


def test_b(module, size, majority_inward=False):
    """(counted, truth) of the PR's test (b) for ``size`` ranks."""
    fake = SummingComm()
    real = module.uw
    module.uw = types.SimpleNamespace(mpi=types.SimpleNamespace(comm=fake))
    try:
        def per_rank():
            counted = truth = 0
            for rank in range(size):
                inverted = [False] * (3 * size) if rank == 0 else [False, True, True]
                if majority_inward:
                    inverted = [not i for i in inverted]
                P = np.array([cap_triangle(0.1 * k + rank, inv) for k, inv in enumerate(inverted)])
                vote = getattr(module, "_global_flip", None)
                areas = (module._signed_twice_areas(P, vote(P)) if vote is not None
                         else module._signed_twice_areas(P))
                counted += int((areas <= 0).sum())
                # majority inward: the convention follows the majority, so the
                # inverted cells are the minority (the outward ones)
                truth += int(len(inverted) - sum(inverted)) if majority_inward else int(sum(inverted))
            return counted, truth
        per_rank()                                   # pass 1: record the contributions
        fake.total = np.sum(fake.parts, axis=0) if fake.parts else None
        return per_rank()                            # pass 2: every rank sees the sum
    finally:
        module.uw = real


dev_src = subprocess.run(
    ["git", "show", f"{params.uw_dev_ref}:src/underworld3/utilities/line_cut.py"],
    check=True, capture_output=True, text=True).stdout
variants = {
    "PR head": module_from(HEAD_SRC, "line_cut_head_copy"),
    "development (rank's own vote)": module_from(dev_src, "line_cut_development"),
    "mutant: _global_flip returns False": module_from(HEAD_SRC, "m1", [
        ("    return bool(neg > 0.5 * total)", "    return False", 1)]),
    "mutant: _global_flip votes on the rank alone": module_from(HEAD_SRC, "m2", [
        ("    return bool(neg > 0.5 * total)",
         "    return bool((signed < 0.0).sum() > 0.5 * len(signed))", 1)]),
    "mutant: _global_flip inverted": module_from(HEAD_SRC, "m3", [
        ("    return bool(neg > 0.5 * total)", "    return not bool(neg > 0.5 * total)", 1)]),
}
print("\ntest (b), (counted, truth) per emulated rank count; the test asserts counted == truth")
for name, module in variants.items():
    row = {size: test_b(module, size) for size in (2, 3, 4)}
    verdict = "passes" if all(c == t for c, t in row.values()) else "FAILS"
    inward = {size: test_b(module, size, majority_inward=True) for size in (2, 3, 4)}
    verdict_in = "passes" if all(c == t for c, t in inward.values()) else "FAILS"
    print(f"  {name:<46} as written {row} {verdict} | majority inward {inward} {verdict_in}")
