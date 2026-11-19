# D2: is #857's wall-traction recovery worth bringing back?

2026-11-19, H6 (the curved-walls review session) for Louis, through the dev hub. Measured on a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH), serial, with a two-rank spot check.

## Verdict

Bring back the trace reconstruction (`reconstruct_cylindrical_trace` and the reconstruction half of `recover_cylindrical_zero_slip_traction`), for both normal and shear traction. It gives the largest gain by far: 30 to 100 times smaller errors at h = 1/32, at order 2.4 to 3.3. It is cheap.

The circular CBF transfer alone is not worth carrying. On the same lagged-wall solve, development's own CBF reaction is within a factor of about 2 of it, and both converge at second order. Most of the gain over development comes from two things:

- #857's lagged wall solve, which turns development's order-1 reaction into order 2. That solve is #1110's lagged walls, already under review.
- The reconstruction.

Two cautions before trusting the reconstruction:

- **Smooth test case.** The Kramer case here is a single smooth n = 2 harmonic, which favours a polynomial-reproducing smoother. #857's own guide gives the kernel a bandwidth limit (about 0.82 response at the eighth harmonic on a 32-edge circle).
- **Untried combination.** The reconstruction has not been tried on development's own reaction from development's own solve. That measurement would say whether the lagged walls are needed for the reconstruction's gain.

## Configuration

- **Model:** Kramer, Davies & Wilson (2021) smooth case, rho = (r/R_O)^3 cos(2 theta), viscosity 1, annulus R_I = 0.5, R_O = 1.0. Built with `uw.meshing.Annulus` at cell size h = 1/8, 1/16, 1/32, P2/P1, pressure null space on.
- **Free-slip case:** free slip on both walls.
  - Development (4ab522a4): rotated free slip on both walls.
  - #857 (head 23c11aa8, built as is): its lagged circular wall transfer, four updates and five solves.
- **Zero-slip case:** zero slip on both walls.
  - Development: essential zero velocity on the polygonal walls.
  - #857: its zero-slip wall transfer, four updates.
- **Exact traction:** sigma_rr = tau_rr - p and sigma_r_theta from `assess`, evaluated at each wall node's radial projection onto the true circle.
- **Error:** taken at the P2 velocity-trace nodes of each wall, selected by label. Every route is read from the same solve at the same nodes.
- **Normal-traction gauge:** each sigma_rr trace has its own best constant removed per wall, because of the pressure constant and topography's mean. Shear is compared as it is.
- **Normalisation:** L2 is the nodal RMS of the error over the largest absolute exact value on that wall (after the mean, for sigma_rr). The maximum error uses the same scale.
- **Sign:** each route's sign is fitted, since a reaction is minus sigma_rr. Every fitted sign was the physically expected one.
- **Order:** the least-squares slope of log L2 against log h over the three cell sizes.
- **Cost:** wall time of the recovery call over the solve's wall time at h = 1/32. For #857 the solve is all five lagged solves. Times are small (2 to 9 s per solve), so they are indicative only. The raw-stress cost includes a first-call compile.

Routes:

- **(a) Rotated reaction:** `boundary_normal_traction(wall, mass=lumped | consistent)` (free slip), or `boundary_flux(wall, mass=...)` resolved on the true radial frame (zero slip). Read from each build's solve, labelled by solve.
- **(b) #857's recovery:**
  - circular CBF: `recover_cylindrical_topography` with buoyancy scale -1 (free slip), or the circular fields of `recover_cylindrical_zero_slip_traction` (zero slip);
  - CBF + reconstruction: `reconstruct_cylindrical_trace`, degree 6, half-width 5 edges (free slip), or the reconstructed fields (zero slip).
- **(c) Raw FE stress:** the solved stress, n.sigma.n and n.sigma.t on the true radial frame, evaluated at the wall nodes.
- **(d) Development's consistent boundary flux:** this is (a) for zero slip. For free slip, `boundary_normal_traction` is development's CBF on the rotated solve.

Scripts: `traction.py` (one solve per case, cell size and build) and `table.py`. Logs are in `logs/`; the full table, with maximum and midpoint errors, is in `table.md`.

## Summary at h = 1/32 (L2, relative; order in brackets)

| quantity | wall | dev reaction / CBF, lumped (dev solve) | same, on #857's lagged solve | #857 circular CBF | #857 CBF + reconstruction | raw FE stress (dev solve) |
|---|---|---|---|---|---|---|
| free slip sigma_rr | inner | 2.99e-3 (1.14) | 3.18e-4 (1.94) | 1.58e-4 (2.17) | 5.52e-6 (3.33) | 6.97e-4 (1.98) |
| free slip sigma_rr | outer | 5.00e-4 (1.15) | 3.95e-4 (1.92) | 2.10e-4 (1.92) | 1.12e-5 (2.36) | 1.37e-3 (1.48) |
| zero slip sigma_rr | inner | 5.04e-4 (1.87) | 3.77e-4 (1.95) | 6.58e-4 (1.80) | 4.32e-5 (2.47) | 1.57e-3 (1.91) |
| zero slip sigma_rr | outer | 2.73e-4 (1.89) | 3.77e-4 (1.95) | 1.87e-4 (1.89) | 1.56e-5 (2.78) | 1.26e-3 (1.50) |
| zero slip sigma_r_theta | inner | 2.59e-2 (0.48) | 4.92e-3 (1.83) | 1.31e-2 (1.81) | 2.93e-4 (2.63) | 8.47e-3 (1.66) |
| zero slip sigma_r_theta | outer | 1.66e-2 (1.05) | 1.72e-3 (1.84) | 4.17e-3 (1.82) | 9.16e-5 (2.45) | 3.54e-3 (1.61) |

Consistent-mass recovery is never better than lumped here; development's consistent free-slip reaction converges at order 0.6 to 0.8. Both are in `table.md`.

Cost of #857's recovery relative to the solve at h = 1/32:

| | circular CBF | CBF + reconstruction |
|---|---|---|
| free slip | 0.004 to 0.006 | 0.028 to 0.034 |
| zero slip (one call does both) | 0.21 to 0.36 | 0.21 to 0.36 |

Development's reactions cost 0.003 to 0.05 of their solve.

## Observations

1. **The lagged wall solve gives development's reaction its second order.** On development's solve on polygonal walls, the free-slip reaction converges at order 1.1. The zero-slip shear CBF converges at order 0.5 to 1.0. This is the O(h) facet-geometry error of #414. Development's own reaction read from #857's lagged solve converges at order 1.8 to 1.95.
2. **The circular CBF transfer adds little.** Against development's lumped CBF on the same lagged solve it is about 2 times better on free-slip normal traction. It is worse on zero-slip shear (2.7 and 2.4 times) and on the inner normal traction (1.7 times).
3. **The reconstruction carries the gain.** Its order is 2.4 to 3.3. Its accuracy rests on the kernel reproducing polynomials, and a single n = 2 harmonic is the easiest case for it.
4. **Raw FE stress at the wall nodes converges at order 1.5 to 2.** It beats development's free-slip reaction on the inner wall at every cell size.
5. **The free-slip velocity error does not fall with h** (about 3e-3) on either build, because the free-slip solves carry a rigid rotation that neither build removes here. A rigid rotation carries no stress, so the tractions are unaffected.
6. **The two-rank check (free slip, h = 1/16) agrees with serial.** Each rank's error on its own wall nodes is within 20 % of the serial value for every route, on both builds. No route behaves differently in parallel.

## Not run

- The reconstruction applied to development's reaction on development's solve.
- A broad-band or delta-load trace: the delta case, which #857's pressure lift targets.
- Anything above np 2.
- macOS.
- #857 rebased onto current development: it was run at its own head, whose base is 1d2297b8.

Underworld development team with AI support from Claude Code
