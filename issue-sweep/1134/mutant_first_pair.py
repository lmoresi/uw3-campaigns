"""Run PR #1134's tests with the one-coarse-cell condition taken out, in memory."""
import inspect, sys, textwrap
import pytest
import underworld3 as uw
from underworld3.utilities import nvb

params = uw.Params(root=".")
source = textwrap.dedent(inspect.getsource(nvb._nested_prolongation_local))
old = " and in_one_cell(p_, q_)"
assert source.count(old) == 1, source.count(old)
exec(compile(source.replace(old, ""), "<mutant>", "exec"), nvb.__dict__)

class Tally:
    def __init__(self): self.failed, self.passed = [], 0
    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.failed: self.failed.append(report.nodeid.split("::")[-1])
            else: self.passed += 1
tally = Tally()
pytest.main([f"{params.root}/tests/test_0449_nested_transfer_3d_rows.py",
             f"{params.root}/tests/test_0753_nested_mg_prolongation.py",
             "-q", "--no-header", "-p", "no:cacheprovider", "-o", "addopts="], plugins=[tally])
print(f"MUTANT first matching pair: passed {tally.passed}, failed {len(tally.failed)} {tally.failed}", flush=True)
