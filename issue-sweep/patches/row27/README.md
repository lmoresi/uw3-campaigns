# Register row 27 (proposed): velocity sub-solve transpose null space

Base: underworld3 development fbef72fa. One commit (89b36128), as a `git format-patch` file. Not
pushed. Merging is Louis's call; the parallel review (np 2-4) is the server's.

Files:
- `PR_BODY.md`: the draft, with the summary table.
- `FIXTURES.md`: the broader fixtures, step by step, from `fix27.py` and `cmp27.py`.
- `ITERATIONS_ALL.md` and `ITERATIONS_CHANGED.md`: the 39 rotated free-slip test files, solve by
  solve, before (fbef72fa) and after, from `rec_plugin.py`, `rot_suite.txt` and `compare27.py`.
- `floor_any.py`: the probe that found the floor (UNFILED 64, STAGNATION.md).

The fault fixture is `run_k1.py` (issue-sweep/patches/row26) with arguments `<tag> 3 2 1e-6
<split>`.

For the server at np 2-4: test_0895, test_1157 and the fixtures. The velocity sub-block's
transpose null space is set per rank on the distributed sub-matrix, from the same modes the shell
holds.
