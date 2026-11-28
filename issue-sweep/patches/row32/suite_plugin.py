"""Log every rotated solve in a pytest run: iterations, convergence, |U|, hash (UNFILED 94)."""
import json, os, hashlib
import numpy as np
import pytest
from underworld3.utilities import rotated_bc as rb
LOG = os.environ.get("SUITE94_LOG", "/dev/null")
cur = {"t": None, "k": 0}
orig = rb.solve_rotated_freeslip
def wrapped(*a, **k):
    info = orig(*a, **k)
    cur["k"] += 1
    try:
        Uv = info.get("U")
        arr = np.asarray(Uv.getArray(readonly=True)) if Uv is not None else np.zeros(0)
        ctx = (getattr(a[0], "_rotated_linear_cache", None) or {}).get("ctx") or {}
        t = ctx.get("schur_roundoff")
        rec = {"t": cur["t"], "k": cur["k"],
               "p": [i for i in (info.get("pres_its_last") or []) if i is not None],
               "v": [i for i in (info.get("vel_its_last") or []) if i is not None],
               "outer": info.get("ksp_its"), "nl": info.get("nonlinear_iterations"),
               "conv": bool(info.get("converged")), "capped": info.get("sub_capped"),
               "floored": getattr(t, "floored", None), "fired": getattr(t, "fired", None), "mismatch": getattr(t, "scale_mismatch", None),
               "unorm": float(np.linalg.norm(arr)), "umax": float(np.abs(arr).max(initial=0.0)),
               "hash": hashlib.sha1(arr.tobytes()).hexdigest()[:8]}
    except Exception as e:
        rec = {"t": cur["t"], "k": cur["k"], "err": str(e)[:100]}
    with open(LOG + f".{os.getpid()}", "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return info
rb.solve_rotated_freeslip = wrapped
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    cur["t"] = item.nodeid; cur["k"] = 0
    yield
