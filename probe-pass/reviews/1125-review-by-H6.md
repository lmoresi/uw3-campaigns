## Adversarial review of #1125

**Verdict: ready with listed changes.** The three library fixes are correct on every attack we ran. The changes asked for are in the tests and the commit text: the clamp tests do not exercise the one place the fix could be wrong, and their baseline holds only by the choice of three points.

Reviewed at head `60defae8`, base `development` `01dec8d2` (one commit, 4 files, +112/−3), by the reviewing desk for rotated boundary conditions and curved walls, standing in for the second review desk. Runs on a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH), PETSc int32, at most two cores.

### Findings

**Medium**

1. **The clamp tests cannot fail on the layout mapping, which is the substance of the fix for a MATRIX.** The fix maps the requested component to its stored column through `_data_layout`. For TENSOR and SYM_TENSOR the flat index already equals the stored column (0,1,2,3 and 0,1,2); only a MATRIX differs (a 2×3 stores entries 0..5 in columns 0,2,4,1,3,5). A mutant that uses the flat index instead (`stored_column = [_comp]`) passes all 6 tests. On a 2×3 MATRIX it returns values wrong by 1.7 at 399 of 400 points. #1000's own example names a MATRIX; no test here clamps one.
2. **The clamp tests' baseline is true only at the three points chosen.** The docstring says a linear field "lies inside its neighbour range at interior points, so the clamped value is the exact one". It does not: the bound is the range of the three nearest nodes, which need not enclose the point. On the test's own mesh and field, 3 of 400 random interior points are clipped, by up to 6.3e-2. A different gmsh triangulation can put one of the three fixed points among them.
   - A baseline that is exact on any mesh: `clamp(var.sym[i, j])` equals entry `(i, j)` of `clamp(var.sym)`. We measured the difference as exactly 0 for every entry of TENSOR, SYM_TENSOR (both orders of the off-diagonal), VECTOR and a 2×3 MATRIX, at two cell sizes. Asserting that for every entry kills the mutant of finding 1.

**Low**

3. **The file fails under MPI.** At np 2, five of the six tests fail on one rank and two on the other. Two are the test's own doing (`tmp_path` is a different directory on each rank, so the swarm file is not found). Three are the clamp tests, which meet a defect that is already on `development` (see "Outside this PR"). The file lives in `tests/`, which CI runs serially, so CI is unaffected; the docstring should say it is a serial file.
4. **The MATRIX history test stops at `initialise_history`.** An update step is not asserted. We measured it: over two steps in a rotating flow, a (2,2) MATRIX history equals a TENSOR history of the same field entry for entry (difference exactly 0), and its (0,1) entry equals a scalar history of that entry (0), with and without `monotone_mode="clamp"`. That comparison would make a good second assertion.
5. **`read_timestep` now also works in a units model, and nothing says or tests it.** On `development`, `read_timestep` raises for every swarm variable when reference quantities are set ("Cannot assign plain array to '….array' when units are active"), scalars and vectors included. On this head all four types round-trip exactly there. It is a real fix beyond the three issues: say so in the body and add the one-line units case to the round-trip test.
6. **Commit and PR text.** The commit carries `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; the project's rule is no `Co-Authored-By` line and no model name. The PR body ends with an emoji line ("Generated with Claude Code"); PR descriptions carry no emoji.

### Attacks that failed

- **New tests:** all 6 fail on `development` for the stated reasons (`'NoneType' object is not subscriptable`; "could not broadcast (252,3)/(252,4) into (252,2)"; "cannot reshape array of size 3 into shape (3,4)/(3,2)") and pass on the head.
- **Swarm round trip, exact (difference 0.0):** scalar, vector, tensor and symmetric tensor, in 2-D and 3-D (stored widths 1/2/4/3 and 1/3/9/6), at np 1 and np 2, with values set as a function of position. An `int` variable keeps its dtype and values. The proxy mesh variable is current after the read (evaluates to 2.8 and 4.3 at two points, as before the write) on both builds.
- **Clamp, single component:** the clamped value never leaves its own component's neighbour range (largest excursion 0.0, bounds computed independently) on a step field where the clamp acts (4 to 102 of 200 points), for TENSOR, SYM_TENSOR, VECTOR, MATRIX and scalar at P1 and P2.
- **Nothing else moved:** whole-variable clamp fingerprints (sum and absolute sum to 13 digits) are identical on `development` and the head for TENSOR, SYM_TENSOR, VECTOR, MATRIX and scalar at P1 and P2. Scalar and vector semi-Lagrangian histories over three steps, with and without the clamp, are identical to 15 digits. TENSOR and SYM_TENSOR histories with `monotone_mode="clamp"` already ran on `development` and give the same numbers here.
- **#988 and #982 are not undone:** the whole-variable branch is untouched; the new branch is entered only for a single component.
- **Mutants:** 4 of 6 killed. Killed: clamp bounded by the transposed entry (2 tests), clamp bounded by column 0 (3), swarm columns reversed (2), MATRIX history shape transposed (1). Survived: the flat-index mutant of finding 1; and ordering the MATRIX history's entries by column, which is equivalent (the order is internal and used consistently).
- **Surrounding suites:** 56 history, swarm, evaluate, remap and transport files (tier C excluded), serial: 399 passed, 2 skipped, 0 failed. We did not rerun the author's full set of 70 files (583 passed).
- **Gates:** every test file is reachable from `scripts/test.sh` (the `test_116*` decade); the style gate passes; markers are level 1 on the module and tier B on each test; the PR body names the machine by what it is and has no local paths.

### Issues

- **#995:** fixed by this branch. A MATRIX history builds, initialises and updates, and matches the TENSOR path exactly.
- **#1000:** fixed by this branch for the failure in its title, for every type including a MATRIX. Its "from reading" note, that a tensor history with `monotone_mode` set reaches the failure, does not reproduce: those histories ran on `development` already.
- **#984:** both halves are now fixed. `mesh.deform` with a SYM_TENSOR variable runs on `development` 01dec8d2 (the half fixed earlier), and the swarm half is fixed here. Nothing of #984 remains.

### Merge conditions

- Clamp a 2×3 MATRIX in the test, and assert each component's clamp against the same entry of the whole-variable clamp for every entry, in place of the three-point "exact value" baseline.
- Say in the test file that it is serial, or make it rank-safe (one output directory for all ranks; the clamp cases compared as above).
- Add the units round trip to the swarm test, and say in the body that `read_timestep` in a units model is fixed as well.
- Drop the `Co-Authored-By` line from the commit and the emoji line from the body.
- Finding 4 is a suggestion, not a condition.

### Outside this PR (one line each, for the hub)

- **`global_evaluate(..., monotone="clamp")` returns wrong values at np 2 on `development`.** A P1 scalar linear in x and y, 400 interior points: unclamped, exact to 9e-16; clamped, 48 of 400 wrong on one rank and 74 on the other, by up to 0.61 (serial: 5 of 400, by up to 1.7e-2). The whole-variable clamp of a vector does the same. The bound is taken from the rank's own nodes for points the rank does not own. The code calls the clamp "rank-local-only and parallel-safe". No open issue names this (#989 and #990 are the units cases).
- `ddt.py` has a docstring with an invalid escape (`\k`, a SyntaxWarning at import of that module from source); it is on `development` too.

### Not tested

Above np 2; 3-D clamps and 3-D histories; a `read_timestep` into a swarm other than the one that wrote the file; the other five history classes the PR lists as still lacking the MATRIX shape; the author's full 70-file run.

Underworld development team with AI support from Claude Code

### Probe for the clamp defect on `development` (outside this PR)

Run on `development` 01dec8d2, serially and with `mpirun -n 2`. Unclamped evaluation of a P1 field
that is linear in x and y is exact; the clamp must not change it at interior points.

```python
"""Whole-variable clamp of a P1 linear scalar and vector at interior points, any rank count:
how many of the returned values differ from the exact linear value (serial: the 3-nearest-node bound)."""
import numpy as np, underworld3 as uw
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.125)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1); V = uw.discretisation.MeshVariable("V", mesh, 2, degree=1)
X = np.asarray(T.coords); T.array[:, 0, 0] = 3 * X[:, 0] + 2 * X[:, 1]
XV = np.asarray(V.coords); V.array[:, 0, 0] = 3 * XV[:, 0] + 2 * XV[:, 1]; V.array[:, 0, 1] = XV[:, 0] - XV[:, 1]
pts = np.random.default_rng(5).uniform(0.15, 0.85, size=(400, 2))
exact = 3 * pts[:, 0] + 2 * pts[:, 1]
plain = np.asarray(uw.function.global_evaluate(T.sym, pts)).ravel()
c = np.asarray(uw.function.global_evaluate(T.sym, pts, monotone="clamp")).ravel()
cv = np.asarray(uw.function.global_evaluate(V.sym, pts, monotone="clamp")).reshape(len(pts), -1)[:, 0]
print(f"RESULT np {uw.mpi.size} rank {uw.mpi.rank}: unclamped max error {np.abs(plain - exact).max():.1e}; clamped scalar: {int(np.count_nonzero(np.abs(c - exact) > 1e-10))} of 400 differ, largest {np.abs(c - exact).max():.2e}; clamped vector entry 0: {int(np.count_nonzero(np.abs(cv - exact) > 1e-10))} differ, largest {np.abs(cv - exact).max():.2e}", flush=True)
```

Measured in this review: at one rank the unclamped maximum error is 9e-16 and the clamped scalar
differs from the exact value at 5 of 400 points, by up to 1.7e-2 (the bound taken from the three
nearest nodes does not always enclose the point). At two ranks, 48 of 400 points are wrong on one
rank and 74 on the other, by up to 0.61; the whole-variable clamp of the vector does the same. The
bound is taken from the evaluating rank's own nodes for points that rank does not own.
