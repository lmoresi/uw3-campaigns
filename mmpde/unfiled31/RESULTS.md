# UNFILED 31: node_redistribution's partition dependence with an analytic density

For the hub, 2026-11-26: **fixed on development already, by #1258** (`global_evaluate` exact ownership). A regression test is added locally (not pushed: GitHub paused).

## Case
The #1166 measurement's: `UnstructuredSimplexBox`, cell 0.07 (303 vertices); density 1 + 0.15 |grad T|^2 of the front T = (1 - tanh((y - 0.5 - 0.1 cos 6x)/0.05))/2, read exactly (no projection); `node_redistribution` with its defaults (`metric_eval="frozen"`). Moved vertices gathered by original position and compared with serial (`probe.py`, `compare.py`, `compare_pre.py`; layouts via `hook/sitecustomize.py`, LAYOUT=rand3 / emptyband).

## Result

| build | layout | interp L2 error | exit (stol) at outer | max moved-vertex difference from serial |
|---|---|---|---|---|
| any | np 1 | 8.0075468683e-3 | 30 | — |
| before #1258 (9a38b360) | np 2 | 8.0075658824e-3 | 30 | 2.1e-6 |
| before #1258 | np 3 | 8.0334380153e-3 | 29 | 1.3e-3 |
| before #1258 | np 4 | 8.0075473491e-3 | 30 | 6.3e-8 |
| before #1258 | np 4, cells at random | 8.1088850373e-3 | 31 | 7.9e-3 |
| before #1258 | np 4, last rank empty | 7.9990880563e-3 | 30 | 1.3e-3 |
| #1258's merge (233d3c44) | np 3 / random / empty | 8.00754754e-3 / 8.00754747e-3 / 8.00754736e-3 | 30 | — (bit-identical to development) |
| development (fbef72fa) | np 2, 3, 4, random, empty | 8.0075472-8.0075475e-3 | 30 in every case | 5.0e-8 to 8.4e-8 |

The largest serial move is 6.9e-2 (about one cell). The pre-#1258 numbers reproduce H4's 2026-11-20 matrix to every digit.

## Stages
- (i) **metric read at moved points** — the cause. The default read evaluates the metric through `global_evaluate` in parallel; before #1258 a point on a partition seam was answered from a neighbouring cell (#1178). Bisected: the build just before #1258 differs by up to 7.9e-3; the build at #1258's merge is bit-identical to development.
- (ii) MMPDE update: an explicit descent, no linear solve; (iv) reductions: energy and step predicates are allreduced; (v) stopping: every layout now exits at the same outer iteration (30). The residue left by (ii)-(v) on development is 5e-8 to 8.4e-8, accumulated rounding from reductions summed in a different order (no layout-dependent decision).
- (iii) boundary sliding: not exercised here (walls pinned by default). The slip path's own small dependence is bounded in test_1086 (1e-6 to 7.7e-6, unexplained, recorded there); facet slip is #1103.

## Note
H1's np 3 figure of -2.6 % (#1282 review) was with #1282's projected density, not this analytic one; that residue belongs to the projection, not the mover, and is not measured here.
