import sys, numpy as np, warnings, importlib.util
warnings.simplefilter("ignore")
spec = importlib.util.spec_from_file_location("t", "tests/test_1120_split_transfer_fault_copies.py"); t = importlib.util.module_from_spec(spec); sys.modules["t"] = t; spec.loader.exec_module(t)
fm = t.fault_mg
import underworld3.utilities.fault_split as fs
fs._pulled_samples = lambda dm, P: np.asarray(P, dtype=float)
for amp in (0.0, 0.002, 0.015):
    child = t._child()
    if amp: t._move_every_addon_level(child, amp)
    mesh = child.add_fault([("Flt", t.TRACE)], **({"snap_frac": float(sys.argv[1])} if len(sys.argv) > 1 else {}))
    keep = fm._WEAK_COPY; fm._WEAK_COPY = 0.0
    norms = t._copy_column_norms(mesh); fm._WEAK_COPY = keep
    r = np.sort(norms / np.median(norms))
    print(f"W1120 amp {amp}: smallest ratios {np.round(r[:5], 4).tolist()} threshold {keep}")
