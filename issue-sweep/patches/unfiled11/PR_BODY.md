## DDt: the source snapshot substitution reaches inside named expressions (UNFILED 11)

**What was wrong.** With the source snapshot enabled (`enable_source_snapshot`), the commit projection of a flux history should read a frozen copy of `psi_star[0]`. `_DDtBase._build_projection_source` made the swap with `.subs`, which treats a `UWexpression` as an atom. An occurrence of `psi_star[0]` held inside a named expression (at yield, the viscosity reads `E_eff_inv_II`, whose contents hold it) kept reading the history live. No result was wrong: `commit_flux_to_history` checks that the copy equals the history at the commit (test_1109). But the projection's source was not what `enable_source_snapshot` describes, and the check was all that kept it right.

**The change.** `_substitute_through_expressions` (about 25 lines in `systems/ddt.py`):
- A named expression whose contents, at any depth, hold a substituted symbol gives way to those contents with the substitution made.
- Every other named expression is kept as an atom, so a parameter still reads its current value.
- Contents that are a number or a quantity with units are not descended into.

The commit's check stays, as a safeguard. Its docstring and the comment in `_build_projection_source` now describe the new behaviour.

UNFILED 11's part (b), the record-projection fallback reading a snapshot refreshed after the trace-back, was already closed by 22ca45a2 (2026-11-20): the fallback refreshes the snapshot before it projects.

**Tests.** `tests/test_1322_source_snapshot_reaches_named_expressions.py` (level 1, tier A), three cases:

| case | development | the first version of this fix | this branch |
|---|---|---|---|
| the projection reads the snapshot through a named expression (the copy and the history set 1 apart; projection solved directly, at tolerance 1e-10) | fails: the diagonal is 1.0 off | passes | passes |
| no `psi_star[0]` symbol is left in the compiled source | fails | passes | passes |
| a named quantity with units (2 Pa s) is left as an atom | passes | fails: SympifyError | passes |

**What was run** (serial, on a 96-thread Linux workstation, Intel Xeon Gold 6240R):

| what | result |
|---|---|
| test_1322 | 3 passed |
| the 73 test files that touch DDt histories, viscoelastic or Navier-Stokes models (`-m "not tier_c"`, 4 workers) | 609 passed, 2 skipped, 1 xfailed, 1 failed |
| the failure, test_1092 `test_maxwell_transfer_function_under_a_tide` (level 3, 192 steps) | the run's own `--timeout=1200` fired inside a solve (PETSc error 101, pytest-timeout's stack dump). The file alone, without the timeout, gives 19 passed with the other eight below. |
| the 9 cases a first version broke (units-model histories: test_1053, 1054, 1064, 1092), plus test_1322 and test_1092 | 19 passed; development passes the same 14 |

The first version sympified a named expression's contents and so raised on a quantity with units. The batch caught it before review, and the third test pins it.

**Not run:** np > 1 (the change is symbolic and rank-independent); macOS; the full suite.

Underworld development team with AI support from Claude Code
