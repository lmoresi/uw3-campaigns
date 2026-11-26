import sys, numpy as np, warnings, importlib.util
warnings.simplefilter("ignore")
spec = importlib.util.spec_from_file_location("t", "tests/test_1120_split_transfer_fault_copies.py"); t = importlib.util.module_from_spec(spec); sys.modules["t"] = t; spec.loader.exec_module(t)
fm = t.fault_mg
dys = [float(x) for x in sys.argv[1:]]
for dy in dys:
    tr = t.TRACE + np.array([0.0, dy])
    out = []
    for amp in (0.0, 0.002, 0.015):
        try:
            child = t._child()
            if amp: t._move_every_addon_level(child, amp)
            mesh = child.add_fault([("Flt", tr)])
            keep = fm._WEAK_COPY; fm._WEAK_COPY = 0.0
            norms = t._copy_column_norms(mesh); fm._WEAK_COPY = keep
            r = np.sort(norms / np.median(norms))
            weak = r[r < keep]; sound = r[r >= keep]
            out.append(f"amp {amp}: weak {len(weak)} (max {weak.max() if weak.size else float('nan'):.3f}) sound min {sound.min():.3f}")
        except Exception as e:
            out.append(f"amp {amp}: raised {str(e)[:50]}")
    print(f"SCAN dy {dy:+.3f} | " + " | ".join(out), flush=True)
