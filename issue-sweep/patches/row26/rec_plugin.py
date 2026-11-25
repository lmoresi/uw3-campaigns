"""pytest plugin: record every solver solve in every test (iterations, reason, solution) and every
barycentric orphan count, to compare two builds. REC_OUT names the output directory."""
import json, os, re
import numpy as np
import pytest

OUT = os.environ["REC_OUT"]
os.makedirs(OUT, exist_ok=True)
_state = {"test": None, "k": 0, "depth": 0}


def _wrap_solves():
    import underworld3 as uw
    from underworld3.cython import generic_solvers as g
    from underworld3.systems import solvers as s
    from underworld3.utilities import custom_mg
    seen = set()
    for mod in (g, s):
        for name in dir(mod):
            c = getattr(mod, name)
            if isinstance(c, type) and "solve" in c.__dict__ and c not in seen:
                seen.add(c)
                c.solve = _wrapper(c.__dict__["solve"])
    orig = custom_mg.barycentric_prolongation

    def bary(coarse_coords, fine_coords, repair_orphans=True, stats=None):
        st = {} if stats is None else stats
        P = orig(coarse_coords, fine_coords, repair_orphans=repair_orphans, stats=st)
        P0 = P if not repair_orphans else orig(coarse_coords, fine_coords, repair_orphans=False)
        n0 = int((np.asarray((P0 != 0).sum(axis=0)).ravel() == 0).sum())
        _log({"kind": "bary", "shape": list(P.shape), "orphans": n0, "repair": bool(repair_orphans)})
        return P
    custom_mg.barycentric_prolongation = bary
    for k, v in list(custom_mg._BUILDERS.items()):
        if v is orig:
            custom_mg._BUILDERS[k] = bary


def _log(rec):
    rec["test"] = _state["test"]
    with open(os.path.join(OUT, "log.jsonl"), "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def _wrapper(f):
    def solve(self, *a, **kw):
        _state["depth"] += 1
        try:
            return f(self, *a, **kw)
        finally:
            _state["depth"] -= 1
            if _state["depth"] == 0:
                _record(self)
    solve.__wrapped__ = f
    return solve


def _record(solver):
    rec = {"kind": "solve", "cls": type(solver).__name__}
    try:
        snes = solver.snes
        rec.update(snes=int(snes.getIterationNumber()), lin=int(snes.getLinearSolveIterations()),
                   reason=int(snes.getConvergedReason()))
    except Exception:
        pass
    try:
        subs = solver.snes.getKSP().getPC().getFieldSplitSubKSP()
        rec["sub_its"] = [int(k.getIterationNumber()) for k in subs]
    except Exception:
        pass
    info = getattr(solver, "_rotated_freeslip_info", None) or {}
    for k in ("ksp_its", "vel_its_last", "pres_its_last", "ksp_reason", "converged"):
        if k in info:
            v = info[k]
            rec[k] = v if isinstance(v, (int, float, bool, list, type(None))) else str(v)
    arrays = {}
    for nm in ("u", "p"):
        var = getattr(getattr(solver, "Unknowns", None), nm, None)
        try:
            arrays[nm] = np.array(var.array, dtype=float).ravel()
        except Exception:
            pass
    k = _state["k"]; _state["k"] += 1
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(_state["test"]))[-150:]
    if arrays:
        np.savez(os.path.join(OUT, f"{safe}__{k}.npz"), **arrays)
        rec["npz"] = f"{safe}__{k}.npz"
    _log(rec)


def pytest_configure(config):
    _wrap_solves()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    _state["test"], _state["k"] = item.nodeid, 0
