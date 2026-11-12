# How gthyagi's curved-wall work (#1033) meets the existing tools: a walkthrough

H6 curved walls, 2026-11-12, for Louis. Version 1: sections from reading, with the first measured
example (section 1) filled in. Other measured examples are marked PENDING and will be filled as runs
finish.

Heads: development f8c60140 (measured build: 93e66eed, which differs only in the MMPDE mover);
#1033 1b740463; #857 23c11aa8. Every number is marked **run** (by H6 today on hyperion, serial unless
stated), **run by H1** (2026-11-06, old heads) or **read** (from code, docs or gthyagi's review
document). Detail and logs: hyperion `runs/2026-11-12-h6/` (`walk/`, `map-*.md`).

**The short version.** #1033 is two things in one PR. One is a set of new methods (pressure lifting,
lagged wall corrections, coupled gap solves, spherical loads) that a user must call to get. The other
is a rewrite of how the existing rotated free-slip solve decides what is a gauge, which every user
gets. From reading, the new methods do not need the rewrite. The rewrite starts from a correct
observation about our tool, but as shipped it brings back the rigid rotation that #906 removed: on
the test shell with the default normal the answer carries a rotation four times the size of the flow,
and the solve reports converged (run, section 1).

One idea runs through all four sections. On a wall made of straight facets there are two candidate
"free" modes: constant pressure and rigid rotation. Each is an exact null vector of the constrained
discrete operator under one choice of wall normal and only approximately under the other.

| wall normal | constant pressure | rigid rotation |
|---|---|---|
| default (facet normals, weighted by facet size) | exact: this is what #560 built it for | approximate, error of order h² on a shell |
| analytic `X/|X|` | approximate (1e-14 on even arcs, 3e-7 on uneven ones, from our subsystem doc) | exact: `(-y, x)·X = 0` at any point |

Development treats an approximate mode as a gauge anyway and bounds the consequence. #1033 treats a
mode as a gauge only when it is exact to rounding, and otherwise leaves it in the equations.

## 1. The rotated free-slip solve and its rotation gauge

**Today.** `add_rotated_freeslip_bc` rotates each wall node into a normal/tangent frame `Q` and
removes the normal rows. The mesh declares its rigid rotations (`mesh.nullspace_rotations`: one on an
annulus, three on a shell, #906). `_mode_satisfies_constraints` admits a mode `m` if it is tangential
on the constrained rows and `|J m|` is below 1e-8 of the velocity diagonal scale, where `J` is the
operator *before* the normal rows are removed. A declared mode skips the tangency test, because on a
faceted sphere it fails it by 0.004 to 0.016 (#906); its normal rows are zeroed to make it compatible.
Admitted modes go into the Krylov null space, are projected out of the residual the loop converges
on, and are subtracted from the answer in `_finalize_rotated_solution`. A given-normal wall is tested
against its own normal (#968). A guard warns when the projected-out part is large (net torque).

**With #1033.** The test is applied to the mode the solve actually uses: `c = Qᵀ·zero_normal_rows(Q m)`.
It must satisfy `|Â c|` and `|Âᵀ c|` ≤ 256 ε (5.7e-14) of the scale, with `Â` the operator after the
normal rows are removed. Declaring a mode no longer waives anything. The #968 given-wall test is
absent. Result, per the PR's edits to `test_1131`: default normal, shell 3 modes removed becomes 0,
annulus 1 becomes 0; analytic normal, the modes are still admitted.

**Why he did it.** His commit says independent 3-DOF examples "reproduce false rotation admission
after normal elimination". The mathematics is right. `J m = 0` because a rotation has no strain. But
`c = m − (normal part of m)`, and the normal part is a wall-only field of size s (the faceting
error) with real strain, so `Â c ≠ 0`. Subtracting `a·c` from a converged answer therefore adds a
residual `a·Â c`. He measured it on our slid-wall fixture: residual after gauge removal 3.8e-8
against a target of 2.0e-11. Our doc concedes the same thing from the other side (a declared mode
"is near-null, and leaves `‖Â v‖` of the order of its slack"; about s²/3 of the forcing is
discarded). So this is a known approximation in our tool, which he has turned into a refusal. Two
caveats. On the as-built annulus our doc records the rotation as exact to 4e-11 under the default
normal: that passes our 1e-8 and fails his 5.7e-14, so there the difference is a tolerance, not a
defect. And refusing the mode has its own cost, which his document does not measure and the example below
does: the answer keeps whatever rotation the Krylov solve leaves.

**Measured example (run).** P2/P1, isoviscous, radial buoyancy with no net torque, rotated free slip
on both walls, `petsc_use_pressure_nullspace = True`, tolerance 1e-6. Annulus 0.5 to 1, cell size 0.1,
GAMG. Shell 0.5 to 1, cell size 0.3, one refinement, custom FMG (the `test_1131` shell). Probe:
`walk/probe_gauge.py`. "Rotation rate" is the least-squares rigid rotation of the nodal velocity.

| case | build | rotation removed | v_rms | rotation rate | energy ∫v·v | converged | velocity / pressure its |
|---|---|---|---|---|---|---|---|
| annulus, default normal | development | yes | 4.91302e-3 | 9e-21 | 5.52982e-5 | yes | 25 / 7 |
| annulus, default normal | #1033 | **no** | 4.91328e-3 | **-6.3e-5** | 5.53040e-5 | yes | 25 / 7 |
| annulus, analytic normal | development | yes | 4.91302e-3 | -6e-20 | 5.52982e-5 | yes | 25 / 7 |
| annulus, analytic normal | #1033 | yes | 4.91302e-3 | 6e-20 | 5.52982e-5 | yes | 25 / 7 |
| shell, default normal | development | yes (3) | 1.795 | 2e-15 | 12.10 | yes | 12 / 9 |
| shell, default normal | #1033 | **no (0)** | **5.151** | **7.04** | **91.11** | yes | 10 / 9 |
| shell, analytic normal | development | yes (3) | 1.794 | 7e-17 | 12.0817 | yes | 5 / 17 |
| shell, analytic normal | #1033 | yes (3) | 1.794 | 1e-16 | 12.0817 | yes | 5 / 17 |
| annulus, default normal, direct LU | development | yes | 4.91302e-3 | -5e-19 | 5.52982e-5 | yes | direct |
| annulus, default normal, direct LU | #1033 | **no** | **5.41262e-3** | **-2.8e-3** | **6.70664e-5** | yes | direct |
| annulus, analytic normal, direct LU | development | yes | 4.91302e-3 | -6e-19 | 5.52982e-5 | yes | direct |
| annulus, analytic normal, direct LU | #1033 | raises `NotImplementedError` (constant pressure not verified; section 2) | | | | | |

What this shows. With the analytic normal the two builds agree to the digits printed (on the shell
#1033 does not verify the constant pressure there, declines the user's nullspace and installs its
pressure-coarse preconditioner; the answer and the iteration counts are the same). With the
default normal, which is what `add_rotated_freeslip_bc(0, wall)` gives, #1033 removes no rotation.
On the annulus the answer then carries a small spin with the iterative solve (about 1% of v_rms at
the outer wall) and a larger one with direct LU (energy 21% too large). On the
shell it carries a rigid rotation of rate 7.0 on a flow whose v_rms is 1.8: the energy is 7.5 times
too large. Nothing warns, `converged` is True, and #1033's own fresh-residual check passes
(6.6e-7 of 13.7), because the rotation is nearly free and so nearly invisible to the residual. This
is the state the `test_1131` docstring describes from before #906 ("rate 4.66 in a v_rms of 3.93").
So gthyagi's criticism of our gauge is fair as mathematics, but his replacement trades a residual of
order 1e-8 for an order-one error in the velocity on the default path. PENDING: the per-mode
violations on each side, and the slid-wall case where his residual argument bites.

**What the choice is.** (a) Keep development: approximate modes are gauges, with the s² bound and the
warning. (b) Take #1033: only exact modes; users on a shell must pass the analytic normal to have
rotation removed. (c) Keep development's admission but measure and report the residual it leaves.

## 2. The pressure nullspace and the LU pin

**Today.** With `petsc_use_pressure_nullspace = True` the constant pressure is attached to the
operator and the Schur complement, and its mean is projected out of every residual, unconditionally.
The direct-LU route has no null space; `_global_pressure_pin` pins the lowest global pressure row,
one row at any rank count (#1054), none under a pressure Dirichlet condition, and the pinned row is
zeroed after the mean projection (#899). Its docstring already says the pin "is a correct gauge only
where constant pressure is an exact null mode of the constrained operator".

**With #1033.** `_pressure_nullspace_checks` applies `Â` and `Âᵀ` to the constant pressure and
compares with the pressure column and row norms. Above 256 ε the request is not applied: no null
space, no projection, the mode stays in the equations (and section 4's preconditioner may switch on).
On the LU route the same failure raises `NotImplementedError`. His pin (`_naive_pressure_pin`) is
also one global row but has no Dirichlet check and zeroes the row before the projection.

**Why he did it.** `Â·(0,1) = Bᵀ1`, the integral of each wall basis function times the facet normal.
It lies wholly in the removed normal rows only if the nodal normal is the facet-size-weighted one,
which is exactly the #560 argument. Under an analytic normal, or with a prescribed normal velocity
whose data carry net flux, it is not null, and projecting or pinning then discards a real mass
equation. He reports a radial-datum case going from a pressure offset near -7.7e8, unconverged, to a
residual of 3.0e-10. Our own comment records the opposite hazard: unprojected, the outer norm
"floors at rel ~2e-3" on a deformed wall. The check itself is sound and cheap. What is debatable is
the threshold (our doc's analytic-normal annulus sits at 1.1e-14, just inside) and silently ignoring
a user's setting. On the pin, development's version is the more careful one.

**Measured example: PENDING.** Planned: Same annulus, default and analytic normal, even and uneven arcs,
iterative and LU. Print `right_relative`, `left_relative`, whether the gauge was applied, mean
pressure, `solver._rotated_pressure_gauge_residual`, iterations, and for LU whether it solved or raised.

**What the choice is.** Keep unconditional; adopt the check as a report and warning only; or adopt it
as a gate. Separately, whether LU should refuse or pin-and-warn as #1053 does now.

## 3. How a solve reports convergence

**Today.** The rotated loop is the nonlinear solve. It converges on the residual in the rotated
frame, normal rows removed, gauges projected out, against `rtol·ref + atol`. `ref` follows #1014
(`_resolved_reference_rule`): a stationary equation uses max(initial, rest-state residual); one with
memory uses its own initial residual. `ref` is fixed once. The gauge is removed from the answer
after the loop has given its verdict, and that verdict is what the SNES reports.

**With #1033.** After `_finalize_rotated_solution` the residual is evaluated once more on the fields
as returned. If it exceeds the same target, `converged` becomes False, the SNES reason is set to 0
and a warning is printed. The reported `rnorm` becomes this fresh value. `ref` is also recomputed
each iteration under the current gauge verdict, and the Picard-to-Newton switch is moved.

**Why he did it.** "Finalized-field residuals are recomputed against the original equations." It
closes the gap in section 1: the loop can pass and the gauge removal then break the answer. With
exact gauges the check passes trivially; it only bites when an approximate mode was removed, which
is the case development allows by design. The extra residual costs one evaluation per solve. The
`ref` and switch changes are not explained in his document and are stale against #1014's comment.

**Measured example: PENDING.** Planned: The slid-wall annulus from `test_1142` (slide 3e-5, tol 1e-9) on
both builds: loop `rnorm`, residual of the finalized fields, `ref`, `converged`, SNES reason. Then a
nonlinear case for iteration counts and switch iteration.

**What the choice is.** The post-solve check can be taken alone, as a report or as a verdict; it does
not need the rest. If section 1 stays as it is, a verdict would fail shell solves that pass today.

## 4. Preconditioning

**Today.** The outer KSP is FGMRES on a Schur fieldsplit; the velocity block takes FMG, custom MG or
FAC; the pressure block a mass-matrix Schur preconditioner. Exact rotations are projected inside the
velocity solve (`_NullModeProjectedPC`, #963); near-null ones are left to the multigrid.

**With #1033.** If the pressure gauge was requested, failed verification, and its relative response
exceeds `max(256 ε, solver.tolerance)`, the KSP's preconditioner is replaced by a Python one,
`_RotatedBalancedPressureCoarse`, that wraps the existing fieldsplit `M₀`. With `z` the constant
pressure and `w ≈ A_uu⁻¹ (A z)_u`, `V = [z, w]`, it applies `E + (I − E A) M₀⁻¹ (I − A E)`,
`E = V (VᵀAV)⁻¹ Vᵀ`: a two-vector deflation of the nearly free pressure mode. Nothing selects it; it
installs from the measurement, and removes itself when the condition stops holding. It can raise
from inside a default solve ("Rotation modes are not true null vectors").

**Why he did it.** Once section 2 leaves a weakly determined pressure mode in the system, the plain
fieldsplit converges slowly on it; the deflation fixes that without touching the equations. The later
threshold on `solver.tolerance` is there because inverting a tiny response exactly "can amplify a
harmless defect into a huge pressure offset". It is a consequence of section 2, not an independent
improvement: if the gauge stays unconditional it never installs.

**Measured example: PENDING.** Planned: Analytic-normal annulus with uneven arcs: on #1033 print
`pressure_coarse_correction_active`, outer `ksp_its`, and the same solve on development.

**What the choice is.** It follows section 2. If the check becomes a gate, this (or something like
it) is needed, and should then be an option a user can see and turn off.

## 5. Mesh-side changes every mesh sees

### 5a. Where the nodes of a field are (`Mesh._get_coords_for_basis`)

**Today.** Every mesh variable asks the mesh for the coordinates of its nodes. Development builds an interpolation matrix from the P1 coordinate field to the variable's space and multiplies the vertex coordinates by it. Since #902 (31 October) that matrix comes from our own copy of PETSc's nested interpolator, because PETSc's version failed on a rank that holds cells but owns none of their nodes.

**With #1033.** The matrix is gone. PETSc projects the identity function x -> x onto the variable's space cell by cell, on local vectors, and the owner's value is then copied to the halo so shared nodes agree to the last bit. Two additions follow: any node that lands outside the mesh bounding box by round-off is clipped back onto it, and an excursion larger than 64 eps raises `ArithmeticError`.

**Why he did it.** He hit the same defect #902 fixed: PETSc error 63 at 16 ranks, reproduced on development 7222caf3 (23 October, a week before #902 landed), and fixed it four days later his own way. The clip came later, from PETSc point location failing on boundary nodes a few ulps outside the box. So this is a second fix for a defect development has already fixed. It does not expose anything still wrong in our tool, unless the point-location failure reproduces on development; that is worth one probe.

**What differs numerically.** Node coordinates change at round-off (his own `test_0005` needed a 16 eps allowance), and boundary nodes are pinned inside the bounding box. Any code comparing coordinates exactly sees a difference; nothing else should.

**Measured example: PENDING.** Planned: Annulus and box at np 1, 4, 16: max |x_dev - x_1033| over P2 nodes; number of nodes clipped; whether shared nodes agree bitwise across ranks on each; whether point location of every boundary node succeeds on development.

**The choice.** Keep #902 (my recommendation: none of the new methods needs the replacement, see section 6), or adopt his projection as a simplification, on evidence that it is equal or better at high rank counts. Not both.

### 5b. Which side of the internal sphere a cell is on (`SphericalShellInternalBoundary`)

**Today.** The shell is one gmsh volume with the internal sphere embedded, so gmsh gives no Inner/Outer cell groups. We label each cell by whether its centroid radius is below `radiusInternal`.

**With #1033.** Labels come from connectivity: start from the cells touching the Lower and Upper walls and flood outward, never crossing an Internal facet.

**Why he did it. This is a real defect in our tool.** The internal surface is made of flat triangles whose vertices are on the sphere. A tetrahedron just outside it can have all four vertices on r = R, and then its centroid is inside R. He found one on Gadi: four vertices at r = 2, centroid at r = 1.99706, labelled Inner by us and Outer by gmsh's own facet tags. `extract_region` then puts that cell on the wrong side.

**Measured example: PENDING.** Planned: One shell mesh on both builds: cells labelled Inner and Outer; number of cells whose label differs; whether every Internal facet separates an Inner cell from an Outer cell.

**The choice.** Take the fix. It is small (153 lines plus the constructor call), self-contained, and worth landing on its own as a bug fix with his test, rather than waiting for the spherical methods.

## 6. How the new opt-in methods sit on the existing tools

The short answer for D1: **the coupled gap methods do not use the rotated free-slip solve at all, and the lagged walls use it only through its public call.** Nothing in the new methods needs #1033's changes to the rotated solve.

**Pressure lifting** (`cylindrical_pressure_lifting`, `pressure_split`). A density interface with a known pressure jump is written p = q + p_J, with p_J prescribed and discontinuous. The sheet force cancels, leaving a smooth body force -grad p_J and a correction to the outer natural condition. It creates mesh variables and hands the user a force and a datum; the ordinary Stokes solve then solves for q. *Runs on development unchanged.*

**Lagged walls** (`add_cylindrical_wall_transfer`, zero-slip transfer, `solve_cylindrical_wall_updates`). The mesh wall is a polygon inside (or outside) the true circle. After a solve, the P2 velocity in each wall cell is continued radially to the circle, the defect there is measured, and the wall condition on the polygon is corrected for the next solve: a few solves, each an ordinary one. Free slip registers `add_rotated_freeslip_bc` with a non-zero normal datum plus a natural condition; zero slip refreshes an essential condition. *Runs on development's rotated solve.* One adaptation: the history record reads two report keys (`velocity_ksp_type`, `pressure_ksp_type`) that only #1033's solve writes; two lines.

**Cylindrical coupled gap** (`solve_cylindrical_gap`, zero-slip variant). Instead of correcting the polygon, integrate over the true domain: add the caps between chord and arc outside, remove them inside, and enforce the wall condition on the true circle with a Lagrange multiplier, which is -sigma_nn. It assembles its own matrix and solves with its own KSP, pinning one pressure and one rotation row. It refuses a Stokes object that has any essential, natural or rotated condition registered. *Independent of the rotated solve, the nullspace code and our multigrid.*

**Spherical coupled gap.** The same idea on tetrahedra, with cut cells at the inner sphere, "curtain" terms between neighbouring caps, and its own preconditioner (GAMG on a norm matrix). Same refusal, same independence.

**Spherical pressure lift and sheet loads.** The lift is the 3-D form of pressure lifting on the true sphere; it labels Inner/Outer cells by calling the flood fill itself, so it does not need the mesh constructor change. The sheet loads assemble a right-hand side and use the solver's own Jacobian; they add a small hook in the base solver that frees that vector on rebuild.

**What each unit needs from the held solver-core unit**

| Unit | Needs from the held unit |
|---|---|
| 1 Analytic references | nothing |
| 2 Pressure split, lagged walls | nothing; drop two report keys from the wall history |
| 3 Cylindrical coupled gap | nothing (the shared observer and field-layout helpers are new files) |
| 4 Spherical coupled gap | nothing |
| 5 Spherical lift, sheet loads | the flood-fill module (new file) and the RHS-release hook (additive); not the rotated solve |
| 6 Diagnostics | `rotated_stokes_diagnostics` reads `pressure_nullspace_verified`; drop that field or hold that one function |
| every unit | `_get_coords_for_basis(1, True)`, which exists on development with the same meaning |

Not needed by any unit: the two-sided rotation test, verify-before-gauge, the self-installing preconditioner, the post-solve residual guard, the loop reordering, the LU pin, the coordinate projection, the integral JIT offsets.

```
ordinary Stokes solve ──< pressure lifting (force + datum in)
rotated free-slip solve (development's) ──< lagged free-slip wall
essential BC ──< lagged zero-slip wall
own matrix + own KSP ── cylindrical gap ── spherical gap (own PC)
flood-fill labels ──< spherical pressure lift ; solver Jacobian ──< sheet loads
all of the above ──< diagnostics (read-only)
```

**Measured example: PENDING.** Planned: Each unit's tests run against development with only that unit's files added: pass counts, and the first failure if any.

**The choice (D1).** Port the methods onto development's solve and hold the solver-core changes. From reading, the port costs almost nothing in the methods themselves. The solver-core changes can then be judged on their own evidence, separately.

## 7. #857's recovery methods against what we already have

**Today.** After a rotated free-slip solve, the constraint's reaction is the wall normal traction. `boundary_normal_traction(boundary)` returns sigma_nn at the wall nodes, `dynamic_topography(boundary, field)` writes h = -(sigma_nn - mean)/(drho g), and `boundary_normal_traction_integral(boundary, fn)` gives harmonic coefficients without nodal recovery. For a wall with prescribed velocity, `boundary_flux(boundary, normal=...)` recovers the traction from the essential-condition reaction (consistent boundary flux). Our own docstrings carry the known weakness: on a curved wall the P2 vertex values converge slowly; midpoints and integrals are good.

**What #857 adds.**
- *Topography recovery:* takes the same reaction and moves its moments from the polygon to the circle with a Taylor shift, giving sigma_nn as a P2 field on the true circle.
- *Trace reconstruction:* smooths that trace with a compact polynomial-reproducing kernel, keeping its mean and resultant.
- *Boundary coefficient:* the cosine coefficient of a wall field, weighted on the circle. Our integral method already gives this from the reaction directly.
- *Zero-slip traction recovery:* the full traction vector at a prescribed-velocity circle, split into sigma_nn and sigma_rtheta, with the same polygon-to-circle correction. `boundary_flux` gives the polygon version today; the circle correction and the shear component as a field are new.

**Numbers (run by H1 on 2026-11-06 at the old head, not by us).** Smooth free-slip case: the transferred topography was 9 to 22% *worse* in rms than raw `boundary_normal_traction` at every resolution; on the sheet case 23 to 51% better. The large gains came from the wall updates and from the reconstruction: at h = 1/32, wall updates took the Lower traction rms from 1.32e-2 to 4.90e-4; zero-slip shear went from 6.1e-2 to 3.07e-3 with updates and to 5.9e-5 after reconstruction, converging at second order.

**With #1033.** These four methods are gone. The coupled gap methods return the multiplier, which is the wall reaction on the true circle or sphere, normal and tangential separately. The lagged walls in #1033 have no recovery step of their own; a user would call our existing reaction methods after them.

**Measured example: PENDING.** Planned: One analytic annulus, free slip and zero slip, three resolutions: rms error in sigma_nn (and sigma_rtheta) from (a) our reaction alone, (b) our reaction after wall updates, (c) #857's transfer and reconstruction, (d) the gap multiplier.

**The choice (D2).** If the gap multiplier measures as well as (c), #857's recovery is superseded and can close. If the publication uses the lagged walls, then the reconstruction, and the zero-slip shear recovery, are the parts with something our tools lack, and they need the mathematical review gthyagi asked for. The boundary coefficient and the plain topography transfer add little over what we have.

## D1 and D2 in the light of the tour

**D1. What happens to #1033's changes to the rotated solve.**
The new methods do not need them (section 6, read; to be confirmed by running each unit's tests on
development). The changes themselves are a mixed bag:
- The rotation test (section 1) must not land as it is: it reintroduces the #906 rotation on the
  default path (run). His underlying point, that removing an approximate mode leaves a residual, is
  right and deserves an answer of its own: option (c) in section 1, measure and report it.
- The pressure check (section 2) is sound as a diagnostic; as a gate it silently overrides a user's
  setting. The LU pin is development's.
- The post-solve residual (section 3) is cheap and independent; worth taking as a report.
- The preconditioner (section 4) follows the pressure gate and is not needed without it.
- The flood-fill shell labels (section 5b) fix a real defect of ours and should land on their own.
- The coordinate projection (section 5a) duplicates #902; keep #902.

Recommendation: port the methods onto development's solve, hold the rotated-solve rewrite, and take
three small things out of it on their own merits: the flood-fill labels, the post-solve residual as a
report, and the pressure check as a report. Cost: the port is mechanical, about a day for the
cylindrical units including reruns of their tests at np 1 to 5; the convergence studies are the real
time, two to three days for cylindrical, longer for spherical because the first analytic comparison
does not exist yet. The three small items are each a short PR for W1's review, since they are in its
code. Considering the gauge rewrite on its merits instead would add W1's time and a benchmark
campaign, and from the shell result above I do not think it can land without a different design.

**D2. Whether #857's recovery methods are needed.**
We already have the reaction as wall normal traction, topography from it, harmonic coefficients by
integral, and consistent boundary flux at prescribed-velocity walls. Of #857's four methods, the
boundary coefficient and the plain topography transfer add little (run by H1: the transfer was 9 to
22% worse than our raw reaction on the smooth case). The trace reconstruction and the zero-slip shear
recovery on the true circle are new, and H1 measured second-order convergence for the latter. #1033
replaces all four with the gap multiplier.

Recommendation: decide by one measurement, the four-way comparison planned in section 7. If the gap
multiplier matches the reconstructed trace, close #857 after the lagged-wall unit lands. If the
publication relies on the lagged walls, keep the reconstruction and the zero-slip recovery as a
further unit, with the mathematical review gthyagi asked for. Cost of the measurement: about a day,
reusing H1's manufactured cases.

Underworld development team with AI support from Claude Code
