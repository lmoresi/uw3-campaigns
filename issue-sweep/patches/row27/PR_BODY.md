## Velocity sub-solve: the projected null modes are its transpose null space (register row 27)

On an annulus with rotated free-slip on both walls, or a shell with the exact radial normal, the
rotations the outer solve admits are null modes of the velocity block. `_NullModeProjectedPC`
projects them out of what the preconditioner is given and what it returns (#963). The velocity
sub-solve's right-hand side kept its component along them. Its residual cannot fall below that
component, so a target below it is reached only by a slow creep, or not at all.

On test_1157's low-viscosity annulus one sub-solve's right-hand side is 6e-5 along the mode. It
plateaus at 9e-6 against its target of 3.3e-8 (`0.033 x tol`) and runs to its 200-iteration cap.
This is also the source of that test's run-to-run 78/200 (UNFILED 64).

The admitted modes are now also the velocity block's transpose null space
(`A_vv.setTransposeNullSpace`), so `KSPSolve` removes them from every velocity sub-solve's
right-hand side. It is the same mode set the shell holds. The outer operator already carries its
null space this way. Where no mode is admitted (a no-slip wall, the mesh normal on a shell),
nothing is attached and the solve is development's, bit for bit. PETSc's mechanism gives what a
hand projection of the right-hand side gave: 57 velocity iterations and an error of 1.52e-10
against LU, both ways. No projection code is added. The modes are only near-null in the discrete
block (they are admitted below a threshold), and that is enough here: the removal is a projection
of the right-hand side and does not require exact nullity.

Serial, before and after. Rotated counts are outer/velocity/pressure, last application; "capped"
counts velocity sub-solves that hit their cap.

| fixture | modes | before | capped | wall | after | capped | wall | rel. change of v |
|---|---|---|---|---|---|---|---|---|
| warm 8-step loop, annulus, mu 1e-4 (each step) | 1 | 2/200/7 typical | 1-2 | ~6.7 s | 2/3/7 | 0 | 1.85 s | <= 5.6e-13 |
| TI annulus (radial director, eta_1 = 0.01 eta_0), mu 1e-4 | 1 | 2/11/11 | 1 | 7.30 s | 2/11/11 | 0 | 6.28 s | 5.9e-14 |
| TI annulus, mu 1 | 1 | 1/10/9 | 0 | 3.37 s | 1/10/9 | 0 | 3.63 s | 6.5e-14 |
| 3-D shell, exact normal, mu 1e-4 / 1 | 3 | 2/5/18, 1/6/18 | 0 | 14.4, 12.3 s | unchanged | 0 | 14.2, 12.3 s | 1.8e-15, 1.3e-12 |
| 3-D shell, mesh normal (no mode admitted) | 0 | 2/12/11, 1/12/10 | 0 | | unchanged | 0 | | 0 (bit-identical) |
| #893 fault ladder, refinement 3, unsplit / split, tol 1e-6 | 1 | 1/3/7, 1/21/14 | 0 | | unchanged | 0 | | 4.1e-14, 8.8e-14 |
| test_1157's case at cell 0.1, cold (probe) | 1 | 305 total velocity its | 1 | 5.54 s | 57 | 0 | 2.53 s | error vs LU 1.52e-10 both |

The 39 rotated free-slip test files (236 tests with solves) were recorded solve by solve on both
builds:
- 234 have identical counts. Their answers move at most 2.8e-9 (test_1131's analytic-normal
  shell, which admits 3 modes; tolerance 1e-6).
- test_1157's cold solve goes from 200 to 4 velocity iterations.
- test_0895 is new here, and fails on development.

The full tables are in the review record.

Test: `tests/test_0895_rotated_velocity_subsolve_null_mode_rhs.py` (level_2, tier_b). The annulus
at mu 1e-4, cell 0.1, asserts no capped velocity sub-solve (1 on development) and the answer within
1e-9 of LU (1.52e-10 measured). The guard has a no-slip inner wall: no mode is admitted, and the
answer is within 1e-7 of LU.

Tolerances: the solve tolerance is 1e-6; the answer against LU 1e-9 (1e-7 for the guard). No
iteration count is asserted exactly.

Not measured: parallel (np 2-4 is the review's), and the pressure sub-solve's own creep on
fault-network layouts (a different floor).

Underworld development team with AI support from Claude Code
