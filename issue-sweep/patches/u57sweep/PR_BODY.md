## Tests: describe the review or the machine, not session codes or host names

**Why.** Comments and docstrings in 62 files under `tests/` named the review sessions that took a measurement, by their internal codes, or the machine it was taken on, by its host name. Neither tells a reader anything. Each one now says what matters:
- where the number came from: "the #1225 review", "review round 3";
- what kind of machine, when that matters: "a 96-thread Linux workstation", "a Linux cluster", "a workstation";
- nothing, when neither matters: the attribution is dropped.

There are 104 lines in all. This follows the docstring change made for UNFILED 57, and leaves the six files that change edits to it.

**Text only.**
- With docstrings dropped and every string constant replaced by a placeholder, each file's AST is identical before and after (`astdiff.txt`: 62 of 62; 19 are identical in full).
- The one string constant that changes is a dictionary key in `test_1134_fac_cover_gate_structure.py`, `"Linux x86_64 (kaiju), PETSc 3.25.0"`, now `"Linux x86_64 cluster, PETSc 3.25.0"`. The test reads only the dictionary's values.
- The same 411 tests are collected from the 62 files before and after, and test_1134 passes.
- No edited line is longer than 100 characters.

**Search used.** `\b(H[1-9]|W[1-9]|C1|K1)\b|hyperion|[Kk]aiju|wombat|\bdesks?\b` over `tests/`. Seven hits remain, all false positives:
- a matrix coefficient name in test_0023:80;
- MeshVariable names in ptest_001:16, test_0700:96-106 and test_0836:314;
- "desk" in its everyday sense in serial_reference.py:47.

**Base.** development fbef72fa. One commit, as a `git format-patch` file. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
