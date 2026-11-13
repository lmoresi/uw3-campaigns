# Review of the Stokes constructor change (#844) on `units/evaluate-gateway` at 4cd075be

*By W1 (owns the solver code). Copied by the dev hub from W1's message of 2026-11-13; no PR existed yet.
Scope: the hunk in `petsc_generic_snes_solvers.pyx` only (commit 0e01991c: `_stokes_default_units` and
the field creation in `SNES_Stokes_SaddlePt.__init__`) and the five Stokes tests in
`tests/test_0760_evaluate_units_contract.py`. macOS (12-core Apple M4), serial only. "Before" = PR
#1127's head 07647295 (development 01dec8d2 plus two docstrings in this file, nothing in the
constructor). "After" = 4cd075be.*

Probe: unit box, simplex cells of size 0.125, viscosity 1, body force (0, cos(pi x) sin(pi z)), no slip
on Bottom, `(0, None)` on Left and Right, open Top, tolerance 1e-8. Every case ends with SNES reason 2
after one step and one linear iteration. Stored values compared by the SHA-1 of `u.data` and `p.data`.

**Result.** The change does what #844 asks for the first half (keep the field that was passed) and stored
solutions are bitwise unchanged wherever the old code already used the fields it was given. Finding 1 is
the second half of #844's "Expected" and is not done: fix before merge. Finding 2 belongs in the PR body.

## Findings

**1 (fix before merge). A passed field whose degree does not match the `degree` argument is paired with a
field that does not fit it, silently.** The created field's degree still comes from `degree` (default 2).
#844: "If the pair cannot be built consistently, for example a degree mismatch, raise instead of
replacing a field the user supplied."

| Call | Before (both replaced) | After | max abs p after |
|---|---|---|---|
| `Stokes(mesh)` | P2 / P1 | P2 / P1 | 0.416528 |
| `velocityField=` P1 | P2 / P1 on hidden fields | P1 / P1 | 1.236435 |
| `pressureField=` P2 | P2 / P1 on hidden fields | P2 / P2 | 0.507668 |
| `velocityField=` P3 | P2 / P1 on hidden fields | P3 / P1 | 0.416614 |
| `pressureField=` P0 discontinuous | P2 / P1 on hidden fields | P2 / P0 | 0.381856 |

P1/P1 and P2/P2 with continuous pressure are not stable pairs; both report convergence, and the P1/P1
pressure is three times the P2/P1 one. Either take the missing field's degree from the kept one
(velocity degree minus one; pressure degree plus one) and raise when `degree` was given and disagrees,
or raise on any mismatch. Add a test beside the two identity tests.

**2 (PR body). In a model with reference quantities, `.array` of the default fields changes from
non-dimensional to dimensional.** Stored values bitwise the same; what a script reads is not.
(Reference quantities: length 30 km, viscosity 1e24 Pa s, velocity 2.5 mm/year; force 3300 kg/m3 x 10 m/s2.)

| Call | max abs `u.array` before | after | max abs `p.array` before | after |
|---|---|---|---|---|
| `Stokes(mesh)` | 1.660248e-02 | 1.315252e-12 (m/s) | 1.561581e-01 | 4.123626e+08 (Pa) |
| `Stokes(mesh, v m/s, p Pa)` | 1.315252e-12 | same | 4.123626e+08 | same |

The ruling's intent; the body should say that a script building `Stokes(mesh)` in a units model and
reading `.array` gets different numbers, `.data` unchanged, for every class inheriting the constructor
(`SNES_Stokes`, `SNES_VE_Stokes`, `SNES_Stokes_Constrained`, `SNES_NavierStokes`, `SNES_NavierStokes_Composed`).

**3. One field passed without units in a units model gives a mixed pair.**

| Call | u units | p units | `evaluate(stress[0,1])` | `evaluate(stress[0,0] - p)` |
|---|---|---|---|---|
| `Stokes(mesh)` | m/s | Pa | 2.640674e+09 Pa | Pa |
| `velocityField=` v without units | none | Pa | refused | refused |
| `pressureField=` p without units | m/s | none | 2.640674e+09 Pa | refused |

The refusal is the gateway contract working; nothing silently wrong. The body should say so, or the
constructor should warn.

**4. With length and time scales only, velocity has units and pressure has none** (m/s needs length and
time; Pa needs mass too). Is a model with no mass scale meant to be supported, and if so should the
velocity stay unitless too?

**5. m/s and Pa are written into the generic saddle-point class** `SNES_Stokes_SaddlePt`. A class
attribute for the two unit strings would keep the assumption with the classes that make it. Does not block.

**6. Tests.** The five Stokes tests: 5 passed at 4cd075be; on development 4 fail and 1 passes (true on
both). Missing: a solve in the identity tests showing the solve writes into `v`; a baseline that stored
values are unchanged without reference quantities (max abs u 4.428457322774e-02, max abs p
4.165279087610e-01 on the probe above, macOS); tier per test, not on the module (Charter section 8).

**7. Style.** `model = uw.get_default_model()` (line 9234 and the test fixture line 33): never name a
variable `model`; use `orchestration_model`. The comment at line 9432 cites "Louis's units ruling,
2026-11-13": belongs in the commit message or design note. Commit 0e01991c and the five after it are
authored as "Claude", carry a Co-Authored-By trailer naming a model, and lack the project's attribution
line: a squash merge with a corrected message is enough.

**8. Solver register row (suggested):** "Stokes constructor keeps a passed field and creates only the
missing one; created fields carry m/s and Pa in a units model; stored solutions bitwise unchanged for the
default and for both fields passed; no solver setting touched" (plus "a degree mismatch is refused" if
finding 1 is fixed that way).

## What holds
- No change to stored solutions where the old code used the given fields (default and both passed, with
  and without reference quantities, and `velocityField=` P2 with `p_continuous=False`): same SHA-1, same counts.
- The passed field is kept (`st.Unknowns.u is v`, `st.Unknowns.p is p`).
- A one-field call with matching degrees gives the default's solution.
- No units appear without reference quantities.
- No tolerance and no coordinate comparison in the hunk.

## Not checked
More than one rank; the rest of the branch; `SNES_NavierStokes` and the constrained solver end to end
with one field passed; `pixi run docs-build`.

## Issue verdict
#844: fixed by this branch for "keep the passed field"; the degree-mismatch half still live (finding 1).
