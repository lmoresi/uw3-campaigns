"""#917 pytest plugin: dump every JIT source by its key, log each xdist worker's test
order with the keys it builds and which call built them, record the global state when
test_0023's sharpness test starts, and optionally seed SymPy's assumption shuffle.

CI runs each serial batch as ``pytest --dist loadfile -n 4``: a file runs whole on
one worker, and which files share test_0023's worker depends on the scheduling. This
logs, per worker, every test as it starts and every key built, with the solver and the
call chain that built it, so a failing run names the files that ran before test_0023 in
its process and which build changed.

SymPy's assumption system shuffles the order in which it deduces facts, with a
``random.Random`` seeded from the OS in each process (``sympy.core.random``). An
inference left incomplete in one order and complete in another changes how SymPy
rewrites an expression. SYMPY_ASSUME_SEED=<int> seeds that shuffle at start-up.

    PYTHONPATH=<dir of this file>:$PYTHONPATH JITDUMP_DIR=<out> \\
        python -m pytest --dist loadfile -n 4 tests/test_00[0-4]*py -p jitdump917

Outputs in JITDUMP_DIR: <key>.c per distinct source; order_<worker>.txt with
"test <nodeid>" and "key <nodeid> <key> <solver> <calls>" lines in the order they
happened; state_<worker>.txt for the worker that ran the sharpness test.
"""
import inspect
import os

OUT = os.environ.get("JITDUMP_DIR", "jitdump917")
os.makedirs(OUT, exist_ok=True)
WORKER = os.environ.get("PYTEST_XDIST_WORKER", "main")


def _log(line):
    with open(os.path.join(OUT, f"order_{WORKER}.txt"), "a") as f:
        f.write(line + "\n")


def _caller():
    """The solver that asked for this build, and the underworld3 calls above it."""
    solver, calls = "?", []
    for frame in inspect.stack()[2:40]:
        if "underworld3" not in frame.filename and "test_" not in frame.filename:
            continue
        calls.append(frame.function)
        owner = frame.frame.f_locals.get("self")
        if solver == "?" and owner is not None and hasattr(owner, "snes"):
            solver = f"{type(owner).__name__}#{getattr(owner, 'instance_number', '?')}"
    return solver, ">".join(reversed(calls[:8]))


def pytest_configure(config):
    seed = os.environ.get("SYMPY_ASSUME_SEED")
    if seed is not None:
        import sympy.core.random as sr
        rng = getattr(sr, "_assumptions_rng", None)
        if rng is None:
            _log("seed: sympy.core.random has no _assumptions_rng")
        else:
            rng.seed(int(seed))
            _log(f"seed {seed}")
    import sympy
    _log(f"sympy {sympy.__version__}")

    from underworld3.utilities import _jitextension as jx
    agree = jx._agree_source_across_ranks

    def dump(codeguys, source, key):
        path = os.path.join(OUT, f"{key}.c")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(source)
        current = os.environ.get("PYTEST_CURRENT_TEST", "?").split(" ")[0]
        solver, calls = _caller()
        _log(f"key {current} {key} {solver} {calls}")
        return agree(codeguys, source, key)

    jx._agree_source_across_ranks = dump


def pytest_runtest_logstart(nodeid, location):
    _log(f"test {nodeid}")


def pytest_runtest_setup(item):
    if "power_mean_sharpness" in item.name:
        import underworld3 as uw
        from underworld3.function.expressions import UWexpression
        from underworld3.utilities import _jit_graph
        from underworld3.utilities._api_tools import uw_object
        with open(os.path.join(OUT, f"state_{WORKER}.txt"), "w") as f:
            f.write(f"route={uw.jit_route()} nodes_made={_jit_graph._nodes_made} "
                    f"serial={next(_jit_graph._serial)} expr_count={UWexpression._expr_count} "
                    f"obj_count={uw_object._obj_count} persistent={len(UWexpression._expr_names)} "
                    f"ephemeral={len(UWexpression._ephemeral_expr_names)}\n")
