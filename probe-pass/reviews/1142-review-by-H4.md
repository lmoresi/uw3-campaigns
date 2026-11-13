# Review of #1142 (head 1367f3d1): READY, one low recommendation

Reviewer: H4 (the adjoint and thin-sheet session), against the adversarial-review checklist. Mostly by reading, plus one run of the new test on the head: serial pytest, which launches its own np 2 children, on a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH). Not posted on GitHub: posting is not approved in this session.

## C1's three questions

1. **Is `vars_` in the same order on every rank?** Yes, for both callers.
   - `remesh_with_field_transfer` passes `_gather_transfer_vars(mesh)["remap"]`. That function iterates `list(mesh.vars.values())` into lists; there is no set and no sort.
   - The DDt hook (`ddt.py`, `owned = [v for v in self.mesh.vars.values() ...]`) filters the same dict by membership in the context's snapshot dict, which keeps order.
   - `mesh.vars` is filled as variables are created, a collective in program order, so its insertion order matches across ranks.
   - The `Allreduce` on a `len(vars_)` array therefore pairs entry by entry. It would only break if a caller passed a set, or a list built per rank. Neither does today, and the comment says the requirement.
2. **Is the kept fallback's exception expression-only?** For the case it exists for, yes.
   - `global_evaluate` calls `_apply_monotone_limit` unconditionally on every rank after the evaluation.
   - The monotone refusals (`pick` at np > 1, and an expression not backed by a single MeshVariable) are raised there before that function's empty-rank early return. So every rank raises, and every rank takes the fallback together.
   - **Residual (low):** the `except (ValueError, NotImplementedError)` catches those types from anywhere inside `global_evaluate`, not only the refusal. With `REMESH_MONOTONE` off, the default (`"off"`), the fallback is an identical second call and serves nothing. A rank-local `ValueError` from data inside `global_evaluate` would make that rank alone re-enter the collectives: the old defect, through the kept branch.
   - We found no such raise on the remap path today. It evaluates `var.sym` of the whole variable, so the component-shape `ValueError` of #1000 is not reached; that one is fixed in #1125 anyway.
   - **Suggestion:** take the fallback only when `REMESH_MONOTONE` is on. Better, decide eligibility before the call from the expression, with `meshVariable_lookup_by_symbol`, and don't catch.
3. **Can the child-mpirun test hang CI?** No.
   - Each child runs under `scripts/mpi_supervisor.py --silence 40`.
   - The `subprocess.run` has `timeout=10*SILENCE` (400 s), and the module has `pytest.mark.timeout(1200)`.
   - The second case is meant to stall, and is ended by the supervisor's silence limit.
   - On the head both tests pass in 98 s, with no child processes left afterwards.
   - **Note (not a condition):** if the supervisor itself ever hung, `TimeoutExpired` kills only the supervisor, and could leave `mpirun` children until the job ends.

## Also checked

- **Skip on every rank.** The skip is decided once, before the deform-back and the evaluations, by an `Allreduce(MAX)` of the per-variable "coordinates unavailable" flags. A rank with no DOFs of a variable still enters the collective (target is an empty array, not `None`), as before.
- **No catch-all.** Removing the broad `except Exception: continue` is right: a raise now surfaces rather than desynchronising the ranks. The PR body states the remaining limit plainly: a raise inside `global_evaluate` on one rank still leaves the others waiting, and agreeing on it belongs to the locator rework.

## Verdict

READY. The one low recommendation is the narrower fallback in point 2; not a merge condition.
