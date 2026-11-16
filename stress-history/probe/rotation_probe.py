"""H7 probe: does each stress_transport move a stored stress with a rigid rotation?
Uses _carried_error from the port branch's test_1102 (bugfix/stress-snapshot-order-735)
unchanged, on whatever underworld3 is importable. Prints rotated / unmoved relative errors."""
import sys, time, importlib.util
spec = importlib.util.spec_from_file_location("t1102", sys.argv[1])
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
import underworld3 as uw
for tr in sys.argv[2:]:
    uw.reset_default_model()
    t0 = time.time()
    try:
        rot, unm = t._carried_error(tr)
        print(f"{tr:18s} rotated {rot:.3e}  unmoved {unm:.3e}  ({time.time()-t0:.0f}s)", flush=True)
    except Exception as e:
        print(f"{tr:18s} FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
