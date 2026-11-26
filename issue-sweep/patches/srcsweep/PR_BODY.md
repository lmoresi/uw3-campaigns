## src: describe the review or the machine, not session codes or host names

**Why.** Comments and docstrings in 11 source files named the review sessions that took a measurement, by their internal codes, or the machine it was taken on, by its host name. Each one now says what matters:
- where the number came from: "the #1218 review", "review round 3";
- what kind of machine, when that matters: "a Linux cluster", "a 96-thread workstation";
- nothing, when neither matters: the attribution is dropped.

There are 27 lines in all. The `tests/` sweep (separate) does the same for the test suite.

**Left alone, because they are code or mathematics:**
- the H0-H3 matrices of the adjoint assembly in `petsc_generic_snes_solvers.pyx`;
- `A1, B1, C1` in `meshing/extrude.py`;
- "C1-continuous" in `meshing/surfaces.py`.

**Text only.**
- **Tokens:** for every changed file, `.pyx` included, the token stream with comment and string contents blanked is identical before and after (`tokcmp.txt`: 11 of 11). The check reports DIFF for a planted one-token code change in the `.pyx`.
- **AST:** for the ten Python files, the AST with docstrings dropped and every string replaced by a placeholder is identical too (`astdiff.txt`; four are identical in full).
- **Compiled code:** the only Cython change is in comments, so the compiled module is unchanged in behaviour.

**Search used.** H1's joined-line search (`grep_joined.py`), which catches a reference split over a line break, plus `\b(H[1-9]|W[1-9]|C1|K1)\b|hyperion|[Kk]aiju|wombat`. What remains is the false positives above.

**Base.** development fbef72fa. One commit, as a `git format-patch` file. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
