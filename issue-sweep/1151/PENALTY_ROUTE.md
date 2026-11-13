# #1151: preonly + lu with a large penalty (Louis's question, 2026-11-14)

One rank, macOS, conda-forge PETSc 3.25.3, development bc3d5362 + PR #1170.
Box, Q2/Q1 on quads, viscosity 1, body force (0, cos(pi x)), Top open.
Scripts: penalty_route.py (log penalty_route.log), mass_route.py (log mass_route.log).

ref0 = default solve, tolerance 1e-10, no penalty.
refL = the same penalised system solved to 1e-12 (FGMRES on A, LU of P, adaptive tolerance off).
test = ksp_type=preonly, pc_type=lu.

## `stokes.penalty = lambda`, snes ksponly, velocity differences in L2 relative to ref0

| case | lambda | reported | residual | test - refL | refL - ref0 | speed vs ref0 | div |
|---|---|---|---|---|---|---|---|
| plain 4x4 | 0 | converged | 3.4e-2 | 3.7e-1 | 2e-12 | +11.3 % | 2.0e-2 |
| plain 4x4 | 1e2 | converged | 1.5e-3 | 1.7e-2 | 8.4e-2 | -4.7 % | 1.9e-3 |
| plain 4x4 | 1e4 | converged | 1.6e-5 | 2.1e-4 | 2.6e-1 | -3.9 % | 7.4e-5 |
| plain 4x4 | 1e6 | converged | 1.6e-7 | 2.1e-6 | 2.7e-1 | -3.9 % | 7.7e-7 |
| plain 4x4 | 1e8 | converged | 5.1e-8 | 2.1e-8 | 2.7e-1 | -3.9 % | 7.7e-9 |
| constrained 4x4 | 0 | converged | 1.2e-1 | 5.3e-1 | 6e-12 | +40.9 % | 6.1e-2 |
| constrained 4x4 | 1e2 | converged | 3.6e-3 | 1.7e-2 | 3.7e-2 | +0.1 % | 2.7e-3 |
| constrained 4x4 | 1e4 | converged | 3.7e-5 | 1.8e-4 | 8.7e-2 | -0.9 % | 6.0e-5 |
| constrained 4x4 | 1e6 | converged | 3.7e-7 | 1.8e-6 | 8.9e-2 | -0.9 % | 6.2e-7 |
| constrained 4x4 | 1e8 | converged | 1.8e-7 | 2.2e-8 | 8.9e-2 | -0.9 % | 6.2e-9 |
| plain 16x16 | 1e6 | converged | 2.0e-7 | 1.8e-6 | 2.5e-2 | -2.0 % | 7.7e-7 |
| constrained 16x16 | 1e6 | converged | 4.7e-7 | 1.7e-6 | 5.8e-3 | -0.05 % | 6.2e-7 |
| plain 32x32 | 1e6 | converged | 2.1e-7 | 1.8e-6 | 8.4e-3 | -0.4 % | 7.6e-7 |

"converged" = SNES CONVERGED_ITS, KSP CONVERGED_ITS, in every row including lambda 0.
Returned pressure: norm = (1.0 to 1.25)/lambda of ref0's.

## pressure block of P scaled by 1/lambda (`saddle_preconditioner = 1/lambda`), penalty 0, plain only

| case | lambda | residual | velocity vs ref0 | pressure vs ref0 | speed vs ref0 |
|---|---|---|---|---|---|
| 4x4 | 1e2 | 1.5e-3 | 1.7e-2 | 4.4e-2 | +0.29 % |
| 4x4 | 1e4 | 1.5e-5 | 1.8e-4 | 4.6e-4 | +0.003 % |
| 4x4 | 1e6 | 1.5e-7 | 1.8e-6 | 4.6e-6 | 0 to 7 digits |
| 4x4 | 1e8 | 1.6e-9 | 1.8e-8 | 4.6e-8 | 0 to 7 digits |
| 16x16 | 1e6 | 2.0e-7 | 1.8e-6 | 4.5e-6 | 0 to 7 digits |
| 16x16 | 1e8 | 2.0e-9 | 1.8e-8 | 4.5e-8 | 0 to 7 digits |

## snes newtonls, `stokes.penalty = lambda`, 4x4

Reported DIVERGED_MAX_IT (50 iterations) for lambda 0 to 1e6 (plain to 1e7), DIVERGED_LINE_SEARCH
at the largest, CONVERGED once (constrained, 1e8). test - refL after it stops: 5e-5 (lambda 0),
1.1e-2 (1e2), 1.8e-3 (1e3), then the one-application value.
