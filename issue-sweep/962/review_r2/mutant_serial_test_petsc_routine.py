"""Review r2 in-memory mutant (serial): a solver that leaves PETSc's own local
Jacobian routine on its DM. The serial test_0786 must fail. Nothing on disk changes:
the built solver's solve() is wrapped so that PETSc's routine is back on the DM
when it returns, which is the state a solver that did not register its own leaves."""
import importlib.util
import sys
from pathlib import Path

worktree = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "t0786", worktree / "tests/test_0786_stokes_jacobian_and_preconditioner_one_call_each.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def mutant(build):
    def built():
        stokes = build()
        solve = stokes.solve

        def solve_then_petsc_routine(*args, **kwargs):
            result = solve(*args, **kwargs)
            t._use_the_one_pass_assembly_of_petsc(stokes.dm)
            return result

        stokes.solve = solve_then_petsc_routine
        return stokes
    return built


test = t.test_each_matrix_is_the_one_petsc_assembles_in_one_pass
test = getattr(test, "__wrapped__", test)
for build in (t._plain, t._nitsche, t._constrained):
    try:
        test(mutant(build))
        print(f"{build.__name__}: MUTANT SURVIVED (test passed)")
    except AssertionError as error:
        import traceback
        line = traceback.extract_tb(error.__traceback__)[-1]
        print(f"{build.__name__}: mutant killed at test line {line.lineno}: {line.line}")
