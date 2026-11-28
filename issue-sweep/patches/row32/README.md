# Register row 32 (proposed): a floor on the rotated Schur pressure sub-solve (UNFILED 94)

H4, 2026-11-28. **Not a branch yet:** C1 ruled not to build it until Louis rules, so this is the measurement scaffold that row 32's evidence was taken with.

**Base:** UNFILED 89, applied first (issue-sweep/patches/unfiled89/, three commits ending at 3cb23ef3, on development fbef72fa). Then `0004-row32-floor-measurement-scaffold.diff`, uncommitted on top of 3cb23ef3, applied with `git apply`. In H4's worktree the branch name local/schur-pressure-floor-u94 is only a pointer at 3cb23ef3: row 32 has no commit of its own. **Row 32 needs Louis's ruling; 89 does not.**

**The floor (env-gated, off by default):**
- `UW94_FLOOR=1` switches it on.
- `UW94_C` is the factor c (default 1). **Row 32 proposes c = 1e-6.**
- Inside `_SchurRoundoffTest`: at iteration 0 it records |b_u| (the velocity sub-KSP's right-hand side). At every later iteration the pressure sub-KSP stops once rnorm <= c x rtol_p x |b_u|.
- It also counts `scale_mismatch`, set when |b_u| differs between ranks (it was 0 in 789 parallel solves).

**Probes:**
- `fire94.py <cell>` is the warm re-solve fixture (annulus, viscosity 1 + T). Env `OLD=1` patches the pre-89 NORM_1 scale back in.
- `suite_plugin.py` logs every rotated solve (iterations, convergence, floor firings, |U|, hash) under pytest: `-p suite_plugin` with `SUITE94_LOG=<path>`.

**Evidence:** hyperion runs/2026-11-10-h4/u94/; mail/H1 2026-11-27-H4-u94-measured and 2026-11-27-H4-row32-checks.
- Fixture at np 3: 200 -> 7 pressure iterations, same answer.
- Rotated suite: 374 passed; the floor fires in 24 solves; no convergence change; largest answer change 4.9e-8.
- Parallel: 789 solves with |b_u| identical on every rank.
- Fault and add-on suites: 359 passed both ways; largest answer change 2.3e-9.
