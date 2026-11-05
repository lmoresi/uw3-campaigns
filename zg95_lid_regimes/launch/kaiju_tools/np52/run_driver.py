# kaiju_tools: runs the campaign driver with the coarse-log hook (and optional workarounds); used by every packed/scaling/crust job 3959-4107
"""kaiju-launch/scaling/run_driver.py with the #935 workaround (2026-11-04, the np 52 throughput test): runs a driver
with the coarse-log hook; UW_WANN=1 first installs the integration session's workaround_analytic_normal_nodes on the
walls Upper and Lower (lmoresi/uw3-campaigns addon-matrix-2026-11, see workaround_SOURCE.txt), so the label check (if
UW_LABEL_CHECK is set) wraps the patched node list, and prints the nodes it added per rank at exit.
    python3 run_driver.py <driver.py> <args...>"""
import atexit, os, runpy, sys
drv = os.path.abspath(sys.argv[1])
sys.argv = [drv] + sys.argv[2:]
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), os.path.dirname(drv)]
import petsc4py  # noqa: E402
petsc4py.init(sys.argv)
if os.environ.get("UW_WANN"):
    import workaround_analytic_normal_nodes as wann  # noqa: E402
    wann.install(("Upper", "Lower"))
    from mpi4py import MPI  # noqa: E402

    def _report():
        allc = MPI.COMM_WORLD.gather(dict(wann.ADDED), root=0)
        if MPI.COMM_WORLD.rank == 0:
            tot = {b: sum(c.get(b, 0) for c in allc) for b in ("Upper", "Lower")}
            print(f"WANN added wall nodes (all ranks, last build): {tot}; ranks adding: "
                  f"{[r for r, c in enumerate(allc) if any(c.values())]}", flush=True)
    atexit.register(_report)
import coarse_log_hook  # noqa: E402,F401
if os.environ.get("UW_LABEL_CHECK"):
    import label_check_hook  # noqa: E402,F401
runpy.run_path(drv, run_name="__main__")
