## Serial custom-FMG: drop orphan coarse DOFs, do not repair them (register row 26)

**Serial and parallel runs built different transfers.** Since #890, the parallel custom-FMG
route builds its node transfers without the barycentric orphan repair and drops unreached
coarse columns at install. The serial route still ran the repair first. The same hierarchy
therefore got a different multigrid on one rank than on several, and its iteration counts
could depend on the rank count for no reason. `_reduced_transfer` now uses the parallel
builds' `_node_transfer_no_repair`, so both routes build their node transfers the same way.

**The repair did not help, and with many orphans it hurt.** It gives each orphan coarse DOF
its nearest fine DOF by overwriting that fine row. That can take away the only fine image of
the row's old coarse DOFs, so it emptied more columns than it filled. Install dropped those
columns anyway.

Serial, Stokes P2/P1, tolerance 1e-8. Rotated counts are outer/velocity/pressure; the 3-D box
gives fieldsplit velocity/pressure:

| fixture | orphans | empty after the repair | its before | its after | rel. diff of v |
|---|---|---|---|---|---|
| graded finest annulus, 0.006 to 0.06, under a uniform tail | 3,245 | 8,631 | 1/13/9 | 1/3/9 (macOS), 1/4/9 (Linux server, matching its np 2-4) | 3.2e-10 |
| graded finest annulus, 0.01 to 0.04 | 185 | 338 | 1/3/9 | 1/3/9 | 1.5e-12 |
| #893 placed-ladder hierarchy, refinement 4, chain 2, unsplit | 10, 38 | 1, 34 | 1/4/9 | 1/4/9 | 2.4e-9 |
| the same, split ladder | 0 (split levels use the cell-located transfer) | 0 | 1/25/17 | 1/25/17 | 0 |
| 3-D box, uniform tail (0.25, refinement 2), independent finest 0.07 | 1,255 | 1,749 | 2 / 31 | 2 / 31 | 5.0e-11 |
| the same, finest 0.05 | 29 | 12 | 3 / 30 | 3 / 30 | 3.2e-14 |
| unnested uniform finest annulus, 0.02 and 0.012 | 0 | 0 | 1/3/9 and 1/4/8 | unchanged | 0 |

Every custom-MG and placed-ribbon test (51 files, 229 tests with solves) was recorded on both
builds, solve by solve:
- 227 have identical iteration counts, with solutions within 1e-14.
- test_0894, new here, goes from 13 to 3 velocity iterations.
- test_1157's first warm solve takes 78 or 200 velocity iterations from run to run on the
  same build (three runs gave 78, 200, 200). Its transfers have no orphans, so they are
  identical on both builds.

The full table is in the review record.

Not changed: the public `barycentric_prolongation(..., repair_orphans=True)` default and legacy
`set_custom_mg`. Their callers have no install-time drop, so without the repair a zero column
would remain (#424).

Test: `tests/test_0894_serial_custom_fmg_drops_orphans.py` (level_2, tier_b, 25 s). The graded
fixture asserts at most 4 velocity iterations (13 on development) and |v| = 787.24535978 to
rtol 1e-7. A no-orphan guard bounds its counts (outer <= 2, velocity <= 4, pressure <= 10; 1/3/9 measured),
because counts are reproducible only to round-off (UNFILED 64). It also asserts |v| = 816.99052405 to
rtol 1e-7.

Tolerances: solver 1e-8; the norm baselines rtol 1e-7; the iteration bounds as above.

Depends on the bounded orphan-repair query (UNFILED 62), which this branch carries as its first
three commits. UNFILED 62 is in turn stacked on UNFILED 65 (the uw ckdtree stale-buffer fix),
which must merge first.

Underworld development team with AI support from Claude Code
