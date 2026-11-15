# Probe sweep, 2026-11-15 (W1: the serial list)

Every probe ran on `development` 176958a9 (the #1195 merge), built clean in a fresh
worktree, serial, on macOS (12-core Apple M4), conda-forge PETSc 3.25.3, pyvista 0.46.4.
W1 is the integration session on that laptop. Each `pNNNN_*.py` is the probe for issue
#NNNN; the matching `.txt` holds its output. `tests_0844_1056.txt` is the run of the two
test files named below. Run a probe from the repository root with
`pixi run -e runtime python <probe>`.

| Issue | Verdict | Evidence |
|---|---|---|
| #410 | FIXED (the defect in the title) | A Dirichlet value `[mesh.t]`, clock 1.0, `solve(time=3.0)`: SNES reason 2, every bottom value 1.000000. No `PETSC_MIN_REAL`, no NaN. The `time=` docstrings now say `mesh.t` follows the model clock (#1127). Left open: what `solve(time=)` should do, a design question for the roadmap, not a defect. |
| #559 | LIVE | `test_0844_line_cut.py::test_two_targets_that_choose_one_vertex_leave_the_earlier_without_one` passes, so the overwrite is still the behaviour. |
| #587 | LIVE | `_KNOWN_COLLECTION_TIME_WORK` in `tests/conftest.py` still holds 18 entries, `test_0601_mesh_vector_calc.py` among them. |
| #608 | FIXED | Top rotated against `(None, 0)`, with the other walls held by component Dirichlet. Relative velocity difference 6.1e-11 at eta_B 10 and 2.6e-10 at 1e6, against 9.1e-03 reported. Top-corner pressure difference 2.6e-12 and 1.3e-12. sigma_nn at the corners is +0.284 and -0.368, against 0.357 for the largest value away from the corners, so there is no corner spike (0.497 reported). |
| #742 | LIVE | After 5 ETD-1 solves, `psi_star[0]_xy` = 0.393469 = exact(5) under Stokes, and 0.329681 = exact(4) under NavierStokesSLCN. |
| #824 | LIVE | `uw.unwrap(outer)` and `uw.unwrap(outer, keep_constants=False)` both return `3*a_{in}`; `expressions.unwrap(outer)` returns `6*x`. |
| #864 | LIVE | CI on development (run 43569043145 at f3568c6c) skips `test_0019_mcp_server.py` ("could not import 'mcp': No module named 'mcp.server'") and `test_1105`'s polygon test (shapely). Neither package is in `pixi.toml` or `pixi.lock`. The probe pass of 2026-11-13 recorded mcp as fixed, which held only on that machine's environment. `check_test_coverage.py` still does not see a skip for a missing import. |
| #870 | LIVE, changed | No segfault now. `read_timestep` on a `SphericalManifold` raises `ValueError` in `add_particles_with_global_coordinates` ("must have shape (n, cdim)"), called from `discretisation_mesh_variables.py:1553`. |
| #872 | FIXED | 8a3fc3dd sizes the NavierStokes fields by `cdim`. `tests/test_1056_navier_stokes_surface_mesh_sizing.py` passes (4 tests). The saddle-point base sites listed in the comment are out of this issue's scope. |
| #944 | LIVE, in part | The parse half was fixed by #1035. Runtime: `uw.function.evalf` does not exist, and 28 example files still call it (4 under `WIP/`); 2 files index `stats()[5]`. #1171 and #1187 are both still open. They cover 3 and 4 utility examples; of the files named here, only `Ex_BCs_from_meshVariables.py` (the bare-sympy BC value) is among them. |
| #957 | LIVE | `plot_scalar(mesh, T.sym[0])` raises `ValueError: Invalid colormap ''`; with `cmap="viridis"` it works. |
| #966 | LIVE | Annulus, spring smoothing, largest node move 1.95e-2. After the move and a rewrite, the proxy's error is 1.94e-2 against the moved nodes and 4.4e-16 against the pre-move nodes. `_mesh_version` stays 0 and `_move_version` goes 0 to 1; the proxy cache reads `_mesh_version`. |
| #969 | LIVE | Annulus moved by (1e-3, 0), rotated free slip on both walls, default velocity block (GAMG): converged (reason 2), with a rigid rotation about the moved centre of 3.2e-2 x R / v_rms. The "not a sphere about [0, 0]" warning fires. The ruled warning (re-declare the modes after a translation) has not landed. |
| #1029 | LIVE | Diffusion, one step of a sin(pi x) mode: the ratio is 0.66958 for theta 0, 0.5 and 1. Backward Euler predicts 0.66958 and Crank-Nicolson 0.60418. The default DFDt is `Symbolic`. |
| #1069 | LIVE | A Robin coefficient changed through two narrow rewires: `boundary_residual_f0` on Top lists 1, then 2, then 3 kernels. |
| #1083 | LIVE | Exactly affine cells: P4 at aspect 100, P5 at 10, P8 at 1, Q3 at 100 and Q4 at 10 are refused (None), with no warning on the fallback. The controls, P3 and Q2 at aspect 1, render natively. |
| #1118 | LIVE | A re-declaration asking for 2 components, degree 1 and `\bar{f}` prints "already exists ... Skipping." and returns 1 component, degree 2 and `{f}`. |
| #1138 | LIVE | Bare DMPlex: `mesh.boundaries` lists `All_Boundaries`, `hasLabel` is False, and `solve()` ends in SEGV (exit 59). |

Three are fixed (#410, #608, #872) and fifteen are live.

Underworld development team with AI support from Claude Code
