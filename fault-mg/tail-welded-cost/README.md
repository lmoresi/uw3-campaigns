# What a welded add-on level costs the velocity multigrid

A first look, prompted by a campaign replay in which 19 of 60 mesh rebuilds left one
add-on level welded under a split finest mesh (the cut could not be replayed onto that
level; the library warns and carries on). The question: what does that cost the solve?

**Fixture.** `tests/parallel/fault_fixtures.py` in underworld3: a unit box, an add-on of
`k` levels toward a straight interior trace, the trace cut and split, a frictionless
fault, simple shear on the walls, constant viscosity, tolerance 1e-6. The hierarchy under
the finest mesh is 2 background levels and `k - 1` add-on levels.

**Method.** `welded_tail_cost.py` wraps `fault_split.add_fault` in memory so that the
replay onto the add-on levels (`fault_mg.split_tail_levels`, which runs from the finest
add-on level down) is refused after a set number of levels. The library's own fallback
and warning then run. No library file is edited.

**Build.** underworld3 at the head of PR #1180 (0993858e); `fault_mg.py`,
`fault_split.py` and `custom_mg.py` are identical there to development b0ea8118.
One rank, macOS, 12-core Apple M4 (serial runs only).

**Result.** Velocity iterations of the one outer iteration (the outer count is 1 in every
row). Every row converged on the custom geometric multigrid.

| k | add-on levels under the finest | all split | finest 2 split | finest 1 split | none split |
|---|---|---|---|---|---|
| 2 | 1 | 5 | - | - | 4 |
| 3 | 2 | 5 | - | 9 | 5 |
| 4 | 3 | 4 | 7 | 11 | 6 |

The peak slip is the same to six digits within each `k` (0.159581, 0.158986, 0.159264):
a welded level changes the cost and not the answer.

- With every add-on level welded the cost is 0 to 2 iterations here.
- A hierarchy split at the top and welded below is worse than either all split or all
  welded (11 against 4 and 6 at `k = 4`). Why is not measured.

**Limits.** One fixture, one rank, an easy problem (constant viscosity, an interior
fault). The stiff cases of `docs/developer/design/FAULT_MULTIGRID_HIERARCHIES.md`, where
welded levels cost 9 to 32 iterations, are not reproduced by this fixture. The rows
labelled `kept=k-1` in the output repeat the unforced row. In the output, "of k" counts
the finest mesh as a level; the hierarchy holds `k - 1` add-on levels.

Underworld development team with AI support from Claude Code
