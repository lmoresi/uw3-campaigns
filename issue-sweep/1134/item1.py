"""PR #1134 at 01e5842d, item 1: test_0753's 3-D every-pass case with the
one-cell condition of nvb._nested_prolongation_local, and with it removed in
memory.  No source file is edited.  Serial."""
import inspect, sys, time
import pytest
from underworld3.utilities import nvb

name = sys.argv[1]
src = inspect.getsource(nvb)
MUTANTS = {
    "head": [],
    "no_one_cell_condition": [("if avg.tobytes() == target and in_one_cell(p_, q_):", "if avg.tobytes() == target:")],
}
for old, new in MUTANTS[name]:
    assert src.count(old) == 1, (name, src.count(old))
    src = src.replace(old, new)
exec(compile(src, nvb.__file__, "exec"), nvb.__dict__)
t0 = time.time()
rc = pytest.main(["tests/test_0753_nested_mg_prolongation.py", "-q", "-p", "no:cacheprovider", "-k", "3d-every-pass",
                  "-W", "ignore", "--no-header", "-rf", "--tb=short", "--durations=8"])
print(f"CASE {name}: pytest exit {int(rc)} in {time.time() - t0:.0f} s", flush=True)
