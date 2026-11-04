"""#917 pytest plugin: dump every JIT source by its key, log each xdist worker's test
order with the keys it builds, and the global state when test_0023's sharpness test
starts.

CI runs each serial batch as ``pytest --dist loadfile -n 4``: a file runs whole on
one worker, and which files share test_0023's worker depends on the scheduling. This
logs, per worker, every test as it starts and every key built, so a failing run
names the files that ran before test_0023 in its process.

    PYTHONPATH=<dir of this file>:$PYTHONPATH JITDUMP_DIR=<out> \\
        python -m pytest --dist loadfile -n 4 tests/test_00[0-4]*py -p jitdump917

Outputs in JITDUMP_DIR: <key>.c per distinct source; order_<worker>.txt with
"test <nodeid>" and "key <nodeid> <key>" lines in the order they happened;
state_<worker>.txt for the worker that ran the sharpness test.
"""
import os

OUT = os.environ.get("JITDUMP_DIR", "jitdump917")
os.makedirs(OUT, exist_ok=True)
WORKER = os.environ.get("PYTEST_XDIST_WORKER", "main")


def _log(line):
    with open(os.path.join(OUT, f"order_{WORKER}.txt"), "a") as f:
        f.write(line + "\n")


def pytest_configure(config):
    from underworld3.utilities import _jitextension as jx
    agree = jx._agree_source_across_ranks

    def dump(codeguys, source, key):
        path = os.path.join(OUT, f"{key}.c")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(source)
        current = os.environ.get("PYTEST_CURRENT_TEST", "?").split(" ")[0]
        _log(f"key {current} {key}")
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
