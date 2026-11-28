"""Compare gemv_timing.py's two runs: the default GEMV path against both options off.

    python gemv_timing_compare.py default.json off.json

Per case: the median wall time of each run and their ratio (off / default), and
whether the iteration counts are the same in every repeat of both runs.
"""
import json
import statistics
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
print(f"default: PETSC_OPTIONS={a['PETSC_OPTIONS']!r}  off: PETSC_OPTIONS={b['PETSC_OPTIONS']!r}  "
      f"np {a['np']}/{b['np']}  repeats {a['repeats']}")
print(f"{'case':22s} {'median default s':>16s} {'median off s':>13s} {'off/default':>11s}  iterations")
for name in a["cases"]:
    ra, rb = a["cases"][name], b["cases"].get(name)
    if isinstance(ra, dict) or isinstance(rb, dict) or rb is None:
        print(f"{name:22s} error: {ra if isinstance(ra, dict) else rb}")
        continue
    ma = statistics.median(r["wall"] for r in ra)
    mb = statistics.median(r["wall"] for r in rb)
    keys = ("snes_its", "linear_its", "rotated_ksp_its", "rotated_newton_its", "reason")
    its = {tuple(str(r[k]) for k in keys) for r in ra + rb}
    same = "equal" if len(its) == 1 else f"DIFFER: {sorted(its, key=str)}"
    print(f"{name:22s} {ma:16.3f} {mb:13.3f} {mb / ma:11.3f}  {same}")
