"""#962: after every Stokes solve of a test run, compare the Jacobian and the
preconditioner's matrix that the solver's local routine assembles (one matrix to
a call) with the two that PETSc's DMPlexSNESComputeJacobianFEM assembles in one
pass, at the solution, on fresh matrices of the same pattern.

    MATEQUAL_OUT=<file.jsonl> pytest -p matequal_plugin tests/...

(with this file's directory on PYTHONPATH). One JSON line per solve, written by
rank 0. A solve on a mesh with a rank that holds no cells is recorded and not
compared: PETSc's one pass is the defect there.
"""
import ctypes
import inspect
import json
import os
import sys

import petsc4py

_records = []
_state = {"nodeid": None, "depth": 0}


def _petsc():
    config = petsc4py.get_config()
    name = "libpetsc.dylib" if sys.platform == "darwin" else "libpetsc.so"
    lib = ctypes.CDLL(os.path.join(config["PETSC_DIR"], config.get("PETSC_ARCH", ""), "lib", name))
    lib.DMPlexSNESComputeJacobianFEM.argtypes = [ctypes.c_void_p] * 5
    lib.DMPlexSNESComputeJacobianFEM.restype = ctypes.c_int
    lib.DMPlexSNESComputeBoundaryFEM.argtypes = [ctypes.c_void_p] * 3
    lib.DMPlexSNESComputeBoundaryFEM.restype = ctypes.c_int
    return lib


def _compare(stokes):
    from petsc4py import PETSc

    record = {"test": _state["nodeid"], "solver": type(stokes).__name__,
              "np": PETSc.COMM_WORLD.getSize()}
    snes, dm = getattr(stokes, "snes", None), getattr(stokes, "dm", None)
    if snes is None or dm is None:
        return dict(record, outcome="no snes")
    start, end = dm.getHeightStratum(0)
    counts = dm.comm.tompi4py().allgather(end - start)
    if min(counts) == 0:
        return dict(record, outcome="rank without cells", cells=counts)
    J, P, _ = snes.getJacobian()
    if J.handle == P.handle:
        return dict(record, outcome="one matrix")
    if not (J.getType().endswith("aij") and P.getType().endswith("aij")):
        return dict(record, outcome=f"matrix types {J.getType()}, {P.getType()}")
    x = snes.getSolution()
    if x.handle == 0 or x.getSize() != J.getSize()[0]:
        return dict(record, outcome="no solution vector")

    ours_J, ours_P = J.duplicate(copy=False), P.duplicate(copy=False)
    snes.computeJacobian(x, ours_J, ours_P)

    lib = _petsc()
    one_J, one_P = J.duplicate(copy=False), P.duplicate(copy=False)
    xl = dm.getLocalVec()
    xl.zeroEntries()
    assert lib.DMPlexSNESComputeBoundaryFEM(dm.handle, xl.handle, None) == 0
    dm.globalToLocal(x, xl)
    assert lib.DMPlexSNESComputeJacobianFEM(dm.handle, xl.handle, one_J.handle, one_P.handle, None) == 0
    dm.restoreLocalVec(xl)

    record.update(outcome="compared", rows=J.getSize()[0],
                  J_equal=bool(ours_J.equal(one_J)), P_equal=bool(ours_P.equal(one_P)),
                  J_norm=one_J.norm(), P_norm=one_P.norm(),
                  J_differs_from_P=not bool(one_J.equal(one_P)))
    for m in (ours_J, ours_P, one_J, one_P):
        m.destroy()
    return record


def _wrap(solve):
    def wrapped(self, *args, **kwargs):
        _state["depth"] += 1
        try:
            result = solve(self, *args, **kwargs)
        finally:
            _state["depth"] -= 1
        if _state["depth"] == 0:
            try:
                _records.append(_compare(self))
            except Exception as error:  # a probe: record, never change the test
                _records.append({"test": _state["nodeid"], "solver": type(self).__name__,
                                 "outcome": f"probe error: {type(error).__name__}: {error}"})
        return result
    return wrapped


def pytest_configure(config):
    import underworld3 as uw
    from underworld3.systems import solvers

    root = [c for c in uw.systems.Stokes.__mro__ if c.__name__ == "SNES_Stokes_SaddlePt"][0]
    seen = set()
    for module in (uw.systems, solvers):
        for cls in vars(module).values():
            if inspect.isclass(cls) and issubclass(cls, root) and "solve" in cls.__dict__ \
                    and cls not in seen:
                seen.add(cls)
                cls.solve = _wrap(cls.__dict__["solve"])
    root_solve = root.__dict__.get("solve")
    if root not in seen and root_solve is not None:
        root.solve = _wrap(root_solve)


def pytest_runtest_setup(item):
    _state["nodeid"] = item.nodeid


def pytest_sessionfinish(session):
    from petsc4py import PETSc

    if PETSc.COMM_WORLD.getRank() == 0 and os.environ.get("MATEQUAL_OUT"):
        with open(os.environ["MATEQUAL_OUT"], "a") as f:
            for record in _records:
                f.write(json.dumps(record) + "\n")
