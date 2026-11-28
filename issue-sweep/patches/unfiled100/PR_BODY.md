The pressure sub-solve's iteration cap is the user's on both Stokes paths

## What was wrong
- **The standard path.** Setting `strategy` wrote `fieldsplit_pressure_ksp_max_it` and
  `fieldsplit_velocity_ksp_max_it` back to 200, over a value the user had set.
- **The rotated free-slip path.** This path builds its own Krylov solver under a per-solve
  prefix, and fixed the pressure sub-solve's cap at 200. No option reached it, so on P2/dP1
  triangle meshes, where the Schur complement is poorly conditioned, the cap could not be raised.

## What changes
- Both caps are written by `_push_default_option`, which leaves alone a value it did not write
  (one set on `petsc_options` or on the command line). It keeps its own record, so the multigrid
  bundle's test of which keys are the user's (`_managed_pc_options`) is unchanged. Every writer of
  these keys writes 200, so a user value of exactly 200 cannot be told apart from the default;
  that is harmless while that holds.
- The rotated path reads the solver's own `fieldsplit_pressure_ksp_max_it` (default 200) from the
  options database under the solver's prefix. The same option, from `petsc_options` or the command
  line, reaches both paths. The rotated solver is cached; the cap is read again before every solve (the
  solve's context holds the option's key), so a value set after the first solve takes effect.

## Left open
Strategy still rewrites the sub-solves' `rtol` and `ksp_type`.

## Default unchanged (solver code: measured)
- A probe of a standard solve, a standard solve with `strategy`, and a rotated P2/dP1 annulus
  solve gives identical solution bytes (SHA-256 of the velocity and pressure arrays) and
  iteration counts before and after.
- Every SNES and KSP solve in test_1111, test_1087 and test_1018 (221 solves; iterations, reason,
  final residual norm to full precision) matches a development run exactly. Two rotated solves
  differ between runs: their last residual takes one of two values from session to session, on
  development as well (three development runs and two runs of this branch are attached).
- **The record decides behaviour.** A first version recorded the caps in `_managed_pc_options`,
  the record the multigrid bundle uses to tell the user's keys from UW3's. That changed the bundle's
  user-override test and one rotated solve's residual, so it was replaced.

## Tolerances
None. No coordinate matches.

## Tests
**test_0908** (tier B):
- a user's caps survive a later `strategy`;
- `strategy` alone keeps 200;
- the rotated pressure sub-solver carries the user's cap;
- a cap set between two solves (the load changed through a constant, so nothing is rebuilt)
  reaches the cached rotated solver.
The first, third and fourth fail before the change.

Underworld development team with AI support from Claude Code
