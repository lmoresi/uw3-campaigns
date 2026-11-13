# How gthyagi's curved-wall work (#1033) meets the existing tools: a walkthrough

> **For the hub, 2026-11-13 (third update).** New: section 9 **A-bis, the wall contract by provenance**,
> replacing A's recommendation after Louis's objection to a tolerance test at every use. All from
> reading development 01dec8d2. In short: the registered surface is authoritative; every coordinate
> writer preserves it by construction or releases it; all live coordinate writes already pass through
> one primitive (`Mesh._deform_mesh`), so the inventory is short; four paths today do neither (listed
> there, 1 to 3 hours each); about 10 to 12 hours in all against 4 to 6, of which 1.5 hours (a read
> accessor that returns the registered surface or refuses) is all the lagged walls need. Five
> questions for Louis at its end, each with a recommendation. Also open: PR #1127 (W1); PR B building;
> reviews of #1124 and #1125 in progress.

H6 curved walls, 2026-11-12, for Louis. Version 6: sections from reading, with the measured
examples of sections 1, 3, 5b and 6, the opt-in measurement, the history of #857's recovery
methods (section 7), the generality of each method (section 8) and the pick-apart plan (section 9,
with the tangential-move runs in A2) filled in. Other measured examples are marked PENDING and will be filled as runs
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

**Measured example (run).** The slid-wall annulus of `test_1142` (factory annulus, two refinements,
custom FMG, default normal, wall vertices slid along their circles by `slide·sin 3θ`), serial.
"Residual of the returned fields" is computed the same way on both builds by the probe
`walk/probe_residual.py`: the SNES function at the fields the user gets back, rotated by `Q`, normal
rows removed; at slide 0 it reproduces the loop's own number. The reference residual is 1.995e-2.
The correct energy is 5.50595e-5 (development's four values agree to 9 digits; the slide moves no
wall).

| slide, tolerance | build | loop's reported residual | residual of the returned fields | energy ∫v·v | rotation rate |
|---|---|---|---|---|---|
| 0, 1e-9 | development | 6.7e-14 | 6.7e-14 | 5.505954e-5 | 2e-19 |
| 0, 1e-9 | #1033 | 7.5e-14 | 7.5e-14 | **9.717185e-5** | -5.3e-3 |
| 3e-5, 1e-9 | development | 4.7e-16 | **3.83e-8** (1.9e-6 relative, target 1e-9) | 5.505954e-5 | -1e-20 |
| 3e-5, 1e-9 | #1033 | 6.3e-16 | 6.3e-16 | **6.554309e-5** | 2.7e-3 |
| 3e-4, 1e-9 | development | 4.3e-16 | **3.85e-8** | 5.505954e-5 | -3e-20 |
| 3e-4, 1e-9 | #1033 | 8.2e-12 | 8.2e-12 | **5.516560e-5** | 2.7e-4 |
| 3e-4, 1e-5 | development | 1.9e-9 | **4.11e-7** (2.1e-5 relative, target 1e-5) | 5.505954e-5 | -2e-18 |
| 3e-4, 1e-5 | #1033 | 2.0e-9 | 2.0e-9 | **7.738944e-5** | -3.9e-3 |

Every solve on both builds reports converged. Two things are true at once:

- gthyagi's measurement reproduces exactly on development. When the rotation is near-null but not
  exact (slide 3e-5), development removes it after the loop has converged, and the fields it returns
  have a residual of 3.83e-8, eight orders above the number it reports and 2,000 times the
  tolerance asked for. That is a real gap in what our tool reports. The answer itself is unharmed:
  the energy matches the unslid mesh to 9 digits.
- #1033's returned fields do satisfy the equations to the reported residual, but its answer is wrong
  by 0.2% to 76% in energy, differently in each case, because the rotation it declines to remove is
  nearly free: a residual of 1e-14 does not control a mode the operator barely sees. Its residual
  check passes every time.

So the residual check is worth having as a report of what was returned; it cannot be the test of
whether the gauge is right.

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

**Measured example (run).** Probe `walk/probe_labels.py`: for every Internal facet, is there an Inner
cell on one side and an Outer cell on the other? On 12 unrefined or once-refined shells on hyperion,
development's labels are correct: his single-tetrahedron case did not reproduce here. With two
refinements it is systematic, because refinement leaves the new Internal vertices on the chords of
the coarse surface, so cells just outside it have centroids below `radiusInternal`. Shell
0.547 / 0.8 / 1.0, cell size 0.3, `refinement=2` (98,112 cells, 4,096 Internal facets):

| build | Inner cells | Internal facets with Inner cells on both sides |
|---|---|---|
| development | 37,267 | 1,363 |
| #1033 (flood fill) | 35,904 = 64 × 561, the unrefined count | 0 |

This is now PR #1100 (his commit alone on development, plus a test of those two exact properties
that fails on development); it passes at np 1 to 5.

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

**Measured example (run).** A scratch branch on development f8c60140 with every file #1033 adds and
its new solver methods, and development's `rotated_bc.py`, mesh, integral and multigrid code
untouched (hyperion `wt-h6-port`, logs in `port/logs/`). All 35 of #1033's new serial test files
were run against it:

| group | files | result |
|---|---|---|
| analytic references, pressure split, cylindrical and spherical gap, spherical lift and sheet loads, fitted regions, diagnostics, observers | 30 | all pass (231 tests) |
| lagged walls (`test_1098_cylindrical_wall`) | 1 | 8 pass, 1 fails: the free-slip history reads the report key `velocity_ksp_type`, which only #1033's solve writes (the two-line change predicted above) |
| tests of the rotated-solve rewrite itself (`test_1018_rotated_pressure_coarse`, `_pressure_nullspace`, `_solver_options`) | 3 | fail, as they must: they test the held changes |
| integral field offsets (`test_1115_integral_primary_layout`) | 1 | fails: it tests the held integral change |

So the reading holds: no new method needs the rewrite. Not yet run: #1033's parallel tests on this
branch, and np above 1.

**The choice (D1).** Port the methods onto development's solve and hold the solver-core changes. From reading, the port costs almost nothing in the methods themselves. The solver-core changes can then be judged on their own evidence, separately.

## 7. #857's recovery methods against what we already have

### Why #1033 does not carry them: the history (stage 1, from reading)

**Short answer.** They were neither lost nor declared unnecessary. gthyagi left them out on purpose
when he rebuilt the work on a clean base, and he says so in the commits; he does not say they are
superseded. Our reviews did not cause it: the rebuild started two days before our first review. What
we did fail to do is the mathematical review he asked for, so #857 has sat with the recovery half
unjudged since 29 October.

**When and where they left.** They never left #1033, because they were never on it.
- #857's algorithm commits are dated 23 to 25 October (recovery: `6649a609` "Add conservative spatial
  annulus trace reconstruction and gauge consistency", `1e2d0a5e` "Recover full zero-slip annulus
  traction on physical circles", both 25 October). *Read from git.*
- #1033's lineage starts the next day from development, not from #857: `eb304238`, 26 October,
  "Isolate cylindrical prescribed pressure-jump extraction on development". Its message: *"Port only
  the Stokes pressure-lifting entry point, bounded circular-cut source helper and mathematical tests.
  No wall transfer, traction recovery, gravity or analytical-module changes."* *Quoted.*
- `908079a5`, 27 October: *"Add lagged rotated free-slip and full-vector zero-slip circle conditions
  without topography or gravity APIs."* *Quoted.*
- None of `_cylindrical_reactions.py`, `_cylindrical_reconstruction.py`,
  `_cylindrical_dirichlet_traction.py`, nor any of the four methods, appears in any commit of #1033's
  history. *Read from git (`git log -S`, path history).*

**What he says about them.**
- #1033 body: *"Numerical gravity/topography integration is outside scope."* Its review document:
  *"Numerical topography/gravity integration is outside this change."* Its guide text on the lagged
  walls: *"No topography or gravity calculation is needed."* *Quoted.*
- Nowhere in #1033 (body, review document, guide, commit messages) are #857 or the four methods
  named, and nowhere does he say the gap reactions replace them. *Read; searched for recover,
  reconstruct, topograph, CBF, 857.*
- On #857 itself, 29 October: *"Your separate mathematical-review requirement remains open; this PR
  stays in draft, and I am not claiming that the structural checks validate the recovery
  mathematics."* He has not commented on #857 since; the last entry is our review of 6 November.
  *Quoted; read.*
- So: deliberately out of scope for #1033, status of #857 unstated. Whether he still wants the
  recovery methods in the library, or keeps them in his benchmark repository, he does not say.
  **That question goes to gthyagi.** *Inferred from the above:* the rebuild looks like a move to
  small, separately checkable pieces (pressure lift, then walls, then gap), with recovery and
  gravity left in the benchmark drivers.

**What replaced them, if anything.** *Read from code.*

| #857 method | In #1033 | In development already |
|---|---|---|
| topography recovery (σ_nn moved from the polygon to the circle) | nothing for the lagged walls; the coupled gap solves return `normal_reaction`, the multiplier λ = −σ_nn on the true circle | `boundary_normal_traction`, `dynamic_topography` on a rotated free-slip wall (polygon, annulus and shell) |
| boundary coefficient (cosine coefficient of a wall field) | nothing | `boundary_normal_traction_integral` gives harmonic coefficients from the reaction |
| trace reconstruction (smoothing kernel keeping mean and resultant) | nothing | nothing |
| zero-slip traction recovery (σ_nn and σ_rθ on the circle) | nothing for the lagged zero-slip wall; `solve_cylindrical_gap_zero_slip` returns `normal_reaction` and `tangential_reaction` | `boundary_flux(boundary)` at a prescribed-velocity wall returns the full traction vector (polygon; no circle correction) |

So a user of #1033's lagged walls who wants topography has only our existing reaction on the polygon.
The two things #857 has that exist nowhere else are the trace reconstruction and the zero-slip shear
on the true circle.

**Against the technical note (UWTN 2026-016, "Free-Slip boundary conditions on curved boundaries").**
The note's finding is that the wall traction should be carried, as the constraint reaction (the
consistent boundary flux, σ_nn = −M_Γ⁻¹(Au − b)|_Γ) or as a multiplier, and not recovered by
projecting a differentiated velocity; the two carried forms are the same computation. Against that
frame, *read from the code at 23c11aa8*:

- **None of #857's four methods is a projection recovery.** All four are post-processors applied to
  the reaction development already returns. The zero-slip traction recovery calls
  `stokes.boundary_flux(wall, mass="consistent")` itself; the topography recovery takes the rotated
  constraint's reaction (`_cylindrical_reactions.py`: "The consistent boundary flux (CBF) principle
  recovers surface stress from the discrete momentum balance"). So #857 does not replace the note's
  method; it sits on top of it.
- **What they add to the reaction** is two things the note does not have. A geometric correction:
  the reaction lives on the polygonal wall, and #857 moves its moments to the true circle with a
  Taylor shift ("UW3 geometry adaptations, not a scheme or stability result established in that
  paper", his words). And a smoother: the trace reconstruction, a polynomial-reproducing convolution
  of the reaction trace that keeps its mean and resultant, aimed at the slow convergence of P2
  vertex values on curved walls that our own docstrings warn about (#414).
- **Zero slip, the case to check hardest.** Development does give the wall traction on a Dirichlet
  wall by the same consistent boundary flux: `boundary_flux(boundary)` on a Stokes solver returns the
  full traction vector σ·n̂ from the essential-condition reaction, or its normal component with
  `normal=`. So #857's zero-slip recovery is not the only route to a no-slip wall traction, and its
  absence from #1033 is not a gap in kind. (My table above said "no shear field"; the vector is
  returned at the wall nodes, so the shear is available, on the polygon.) What #857 adds there is
  the split into σ_nn and σ_rθ on the true circle, with the same correction and smoothing. The note's
  benchmark has free slip on the outer wall only, so it has no number for a no-slip wall; H1's
  6 November runs are the only measurements (shear rms 6.1e-2 raw, 3.07e-3 with wall updates,
  5.9e-5 after reconstruction).
- **The boundary coefficient** is the amplitude of one harmonic of the reaction on the circle; the
  note measures exactly this quantity, and `boundary_normal_traction_integral` returns it.
- **#1033's coupled gap follows the note's finding.** It carries the traction as an unknown: the
  multiplier on the true circle, returned as `normal_reaction` (λ = −σ_nn) and, for zero slip,
  `tangential_reaction`. This is the note's multiplier route moved from the polygon to the physical
  wall, so there is nothing to recover and no geometric correction to apply afterwards. gthyagi's
  docstring says the multiplier keeps "the returned reaction equal to physical normal stress"; he
  does not cite the note or state the comparison himself. *Read; quoted phrase from
  `solve_cylindrical_gap`.*

**What this means for decision 2.** In the note's terms nothing essential was dropped: the carried
traction is in development (reaction, on the polygon) and in #1033 (multiplier, on the true circle).
What exists only in #857 is the correction of a polygon reaction to the circle and the smoothing of
its trace (570 lines in three modules). Those matter only if the publication uses the lagged walls, or plain rotated free slip,
rather than the coupled gap, and wants pointwise wall stress rather than harmonic amplitudes.
Whether they are worth carrying is what stage 2 measures, against the note's own table.

**Our side of it.** *Read from the PR; H1's numbers were run on 2026-11-06 at 23c11aa8.*
- 28 October: our first review covered structure only and said the algorithm and recovery
  mathematics *"wants a reviewer with the annulus benchmark in hand"*. That review was never done.
- 6 November: "not ready", for three blocking reasons, none about the mathematics: a merge that
  dropped a datum (now fixed by #1097), a merge conflict with a shadowing trap, and tests that could
  not fail on the core (14 of 18 mutants survived). The same review found the numerics held against
  analytic cases: zero-slip σ_nn converging at second order, shear rms 6.1e-2 to 3.07e-3 with wall
  updates and 5.9e-5 after reconstruction; and that the plain topography transfer was 9 to 22% worse
  than our raw reaction on the smooth case, 23 to 51% better on the sheet case.
- Nothing in either review asked for the methods to be dropped, and #1033's design predates both. He
  has not replied to the 6 November review.

**Stage 2 (measured, to come after the first unit PRs):** the note's Kramer annulus case and its
table (cell sizes 0.15 to 0.05, error in the cos 2θ amplitude of σ_rr), with columns added for
#857's recovery, #1033's gap reaction and a no-slip wall, with convergence order. That decides whether #857 is finished or closed.

### Stage 2 baseline: the note's Kramer table reproduced on development (run)

The note's own script (`examples/stress.py sweep`, unmodified) on development 93e66eed, serial, on a
96-thread Linux workstation (Intel Xeon Gold 6240R, MPICH, PETSc int32). Kramer smooth case n = 2,
k = 3, annulus 0.5 to 1, free slip on the outer wall, exact velocity on the inner; relative error in
the cos 2θ amplitude of σ_rr on the outer wall, exact value 0.1506696429.

| cell size | recovered by projection (rotated solve) | rotated, reaction | multiplier, traction | note: rotated reaction / multiplier |
|---|---|---|---|---|
| 0.150 | 2.44e-2 | 6.82e-3 | 8.57e-3 | 6.8e-3 / 8.6e-3 |
| 0.100 | 9.87e-3 | 3.27e-3 | 8.46e-4 | 3.3e-3 / 8.5e-4 |
| 0.075 | 6.30e-3 | 2.08e-3 | 1.70e-3 | 2.1e-3 / 1.7e-3 |
| 0.050 | 2.68e-3 | 1.08e-3 | 1.41e-3 | 1.1e-3 / 1.4e-3 |

The reaction and multiplier columns reproduce the note to the digits it prints, as does the
projection column (note: 2.4e-2, 1.0e-2, 6.3e-3, 2.7e-3). One column has moved since the note was
written: Nitsche's recovered stress error is now 7.8e-2, 3.3e-2, 2.0e-2, 8.6e-3 against the note's
5.8e-2, 2.4e-2, 1.5e-2, 6.3e-3, about a third larger at every resolution. That is outside this
work; it is reported here for whoever owns the Nitsche condition.

The rotated reaction's error in this amplitude falls from 6.8e-3 to 1.1e-3 over a factor of 3 in
cell size: an observed order of about 1.7 between the ends, uneven between steps. This is the
number the lagged walls, the gap multiplier on the true circle and #857's recovery have to beat. Those
columns need the circle pieces to run on current development, so they follow the contract decision.

### What each method does

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

## 8. Are the new methods general, or tools for an exact circle and sphere?

*All from reading the code at 1b740463; quotes are gthyagi's. Detail with file and line: hyperion
`runs/2026-11-12-h6/generality.md`.*

**Short answer.** Two pieces are general: the fitted pressure split and the region labels. Every wall
method, and the spherical lift and sheet loads, takes a radius, assumes the centre is the origin, and
checks that the mesh's wall vertices lie on that circle or sphere. None accepts a surface the user
supplies, and none runs on a deformed wall, a wall with topography or a moved mesh: they refuse.

| Method | What it needs to know about the wall | Verdict |
|---|---|---|
| `pressure_split` | named fitted interior facets, the user's jump and normal | general (2-D and 3-D, straight facets) |
| `cylindrical_pressure_lifting` | one origin-centred circle and one cos nθ harmonic | circle only; `pressure_split` is its general form |
| lagged walls | a boundary label and a radius ("The labelled boundary must lie on the requested centered circle"); both walls together; fixed mesh; free slip needs constant viscosity | circle only. General with work: the wall geometry (about 680 lines) would be rewritten against a surface the user can evaluate; roughly two weeks plus validation |
| cylindrical coupled gap | two labels and two radii; a closed-form circular-cap rule; a multiplier that is P2 in angle; isoviscous | annulus only. General with substantial work; in practice a new method |
| spherical coupled gap | concentric origin-centred spheres; radial projection; cells cut against a concentric ball; linear, isoviscous | sphere only; generalising it is research |
| spherical pressure lift | a sphere radius (the interface area must equal 4πR²); the jump is any coordinate expression | sphere only, general jump |
| spherical sheet loads | a sphere and one spherical harmonic | sphere and harmonic only: a benchmark load |
| fitted regions (merged, #1100) | three labels and connectivity | general |

**Is the circle or sphere essential?** Not for the lagged walls or the cylindrical gap: the ideas he
cites (shifted boundary, Gap-SBM) are posed for general smooth boundaries, and the circle is how he
implemented them. For the spherical gap the sphere is used throughout its roughly 2,000 lines.

**What he says.** #1033 body: *"for cylindrical and spherical P2/P1 benchmarks"*. #857 body: *"The
supported scope is a nondimensional, origin-centred, isoviscous 2-D annulus"*. Guide: the gap solve is
*"an explicitly selected research alternative for the same constant-viscosity P2/P1 annulus"*;
`cylindrical_pressure_lifting` *"remains the specialised exact-circle method"* while *"The general API
instead uses the fitted polygon/polyhedron geometry"*. He uses "general" only for the pressure split.
He nowhere says the wall methods extend to general or deformed boundaries, and nowhere says they
cannot.

So these are benchmark tools for the annulus and the shell, plus one general piece (the pressure
split). They are not boundary conditions for a convecting model with a deforming or irregular wall.

## 9. Pick-apart plan: which chunks of #1033 and #857 fit the library, and in what form

Frame (Louis, 2026-11-12): take the chunks that fit our design; an analytic shortcut is legitimate
where the geometry is known, the mesh is what declares it, and a mover must be able to invalidate
that declaration.

### A. The contract as the library has it today

*Read from development 613ed1e0; nothing run. Detail with file and line: hyperion
`runs/2026-11-12-h6/contract.md`.*

**The declaration already exists, and #1033 does not read it.** Every annulus and shell constructor
(`Annulus`, `AnnulusInternalBoundary`, `SphericalShell`, `SphericalShellInternalBoundary`,
`CubedSphere`) registers each curved wall on `mesh.bounding_surfaces[label]` as a `BoundingSurface` of
kind `radial`, with its centre and radius (`register_radial_surfaces`, `meshing/bounding_surface.py`).
Internal surfaces are registered too, marked interior. The radii are stored nowhere else on the mesh.
gthyagi's methods instead take `radius=` from the caller, assume the origin, and check the wall
vertices against that number themselves.

Two neighbours of that declaration:
- `mesh.nullspace_rotations` (#906) is declared by the mesh and then verified at each solve: the
  rotated solve trusts a declared rotation only while the wall vertices are equidistant from the
  centre to 1e-9, checked collectively. This is the working precedent for "declared, then checked
  against the actual wall".
- `mesh.boundary_normals` / `canonical_normal` are stamped with the geometry version and raise once
  the coordinates change.

**What a move does to it today.**

| move | bounding surfaces | rotation modes | declared normals |
|---|---|---|---|
| `mesh.deform` (the free surface uses it) | every `radial`/`plane` surface released to `free` | re-tested at the next solve | stale, raise |
| MMPDE and smoothing movers (wall nodes slide on the surface) | kept | kept (the wall test passes) | stale, raise, although the wall has not moved |
| `adapt`, fault-split children | not inherited (inferred: nothing copies them) | inherited | rebuilt |
| checkpoint reload | absent (inferred) | from the constructor metadata | rebuilt |

**One declaration that is present and false.** The constructor's `refinement=` path does not put new
Internal-surface vertices back on the sphere (there is a `TODO(BUG)` in the source). That is the mesh
behind the 1,363 mislabelled cells of section 5b: still registered `radial`, vertices on chords.

**What is missing for these methods.** No single question a method can ask ("is this wall still the
circle the mesh says it is, and what are its centre and radius?"), and nothing that checks wall
vertices against the declared radius.

*Superseded: Louis (2026-11-13) does not accept a tolerance test at every use; see A-bis below, which replaces this recommendation. The alternatives are kept for the record.*

**Proposal, with alternatives (a design decision for Louis).**
- **(a) A query that verifies at use (recommended).** One method, for example
  `mesh.analytic_surface(label)`, returns the registered surface only if it has not been released and
  the label's vertices lie on it to a tolerance, checked collectively; otherwise it refuses and says
  why. The wall methods call it in place of their `radius=` argument and their own checks, when they
  are registered and again at each solve. It reuses `BoundingSurface`, the release already done by
  `deform`, and the pattern of the rotated solve's wall test. No mover changes: whatever moved the
  mesh, the method asks whether the wall is still where the mesh says it is. Children should also
  inherit bounding surfaces as they inherit rotation modes. Small: one method, one collective check
  over boundary vertices.
- **(b) Version-stamped declarations** that movers re-validate. Cheaper per call, but every mover
  must opt in, and today's stamp already goes stale under a move that preserves the wall.
- **(c) Keep `radius=` and verify at each solve.** Least work; leaves the geometry with the caller,
  which the frame rules out.

Open questions. For H5: should `adapt` and fault-split children inherit bounding surfaces; is
`release()` final; should constructor refinement snap the Internal surface. For W1: should the
rotated wall test and this query be one implementation; should `canonical_normal` use the vertex
check so a wall-preserving move does not stale it. For Louis: the tolerance (1e-9 relative in the
rotation test, 1e-10 absolute in gthyagi's checks), and whether a method that finds the declaration
invalid refuses or falls back to its chordal form.

### A-bis. The wall contract by provenance (replaces the recommendation in A)

*Read from development 01dec8d2 unless marked; nothing was run for this page. "Measured" refers to
the runs of A2 (serial, development 93e66eed).*

**The contract.** The `BoundingSurface` registered in `mesh.bounding_surfaces[label]` is the
declaration, and it is authoritative while it is registered as `radial` or `plane` and not released.
A method that uses an analytic shortcut reads the centre and radius from it and uses them; it
measures nothing. Every operation that writes mesh coordinates either keeps the wall on the declared
surface by construction, or releases the declaration. A method that finds no registered analytic
surface for its wall refuses and says so. No tolerance appears at run time.

**What exists.** *Read.* Kinds are `radial`, `plane`, `facet` and `free`; only the first two are
analytic. `restore()` on a radial surface rescales each point to the radius about the centre, which
is exact to round-off; on a plane it projects orthogonally; on a free surface it does nothing.
`release()` turns a radial or plane surface into `free` and remembers the old kind; there is no
un-release, but `register_tangent_slip_provider(label, surface)` replaces a surface, so a caller can
declare again. All coordinate writes on a live mesh already pass through one guarded primitive,
`Mesh._deform_mesh`, which refuses outside a sanctioned scope once the mesh carries variables. So
the inventory is short and closed.

**Every path that writes coordinates.**

| Path (file, function) | Today | How, or the smallest change |
|---|---|---|
| `Mesh.deform` (`discretisation_mesh.py`) | releases | releases every radial and plane surface, then moves |
| Free-surface update (`free_surface.py`, calls `deform`) | releases | as `deform`; all labels, including walls it did not move |
| MMPDE mover (`smoothing/mmpde.py`) with slip, through `Mesh.boundary_slip` | preserves | slides the node in the tangent, then `restore()` onto the registered surface (measured: 2.2e-16 after a slide of 2.0e-2); junction and interior-surface nodes are pinned |
| Smoothing movers (`smoothing/api.py`, `_smooth_mesh_interior_bare`) | preserves | boundary nodes pinned, or slip as above |
| Slip on a label passed as free (`boundary_slip`, dict value `False`) | **neither** | slides without restore while the surface stays registered. Release that label's surface in `boundary_slip`. About 1 hour with a test |
| `Mesh.ephemeral_coords`; old-frame sampling (`ddt.py`); `remap_var_set` (`remesh.py`) | preserves | trial coordinates are put back before the scope ends |
| `adapt` (`_adapt_nested`) | preserves, child undeclared | each generation is snapped with `restore()` onto the parent's surfaces, interior ones included; the child mesh carries no surfaces (inferred) |
| Constructor `refinement=`: `Annulus`, `AnnulusInternalBoundary`, `SphericalShell` | preserves | the callback rescales wall (and, in 2-D, Internal) vertices to their radii |
| Constructor `refinement=`: `SphericalShellInternalBoundary` | **neither** | walls are snapped, the Internal surface is not (`TODO(BUG)` in the source; measured 2.9e-2 off after one refinement; #949 item 3). Snap `Internal` in the callback: about 5 lines, 2 to 3 hours with the anchors that move |
| `_apply_refinement_callback`, vertices put back to avoid an inverted cell (`CubedSphere` creases, #949 item 1) | **neither** | it returns the count of wall vertices not where the callback meant; the surface stays registered. Release that label when the count is not zero: about 1.5 hours |
| A write to `mesh.X.coords` on a mesh with no variables yet (`_mesh_coords_update_callback`) | **neither** | the guard lets it through and nothing is released. Release all surfaces there, as `deform` does: about 1 hour |
| Reload with a moved-mesh stamp (`Mesh.__init__`, the hierarchy stamp) | **neither** | a constructor-built mesh keeps its surfaces while saved, deformed coordinates are written. Release when the stamp moves a vertex: about 1 hour |
| `apply_snapshot_payload` | conservative | coordinates return; a surface released since the snapshot stays released |
| Fault split, `line_cut`, `place_surface`, `extract_region`, checkpoint reload from file | undeclared | new meshes that carry no surfaces (inferred: nothing copies them, nothing in `checkpoint/` names them) |
| Generators that never register (`QuarterAnnulus`, `SegmentofAnnulus`, `AnnulusWithSpokes`, `DiscInternalBoundaries`, `SegmentofSphere`, the segmented and geographic meshes) | undeclared | methods refuse on them |

Four defects under this contract, each small, and one of them (the refined Internal surface) already
known. "Undeclared" is the safe failure: the method refuses on a mesh that would have qualified.

**`deform`.** It releases unconditionally (measured: even when no coordinate changes), and by
provenance that is right: a caller who wants to keep the declaration moves nodes through a path that
restores onto the surface, and a raw `deform` makes no such promise. For the uses we know: MMPDE
along the wall keeps the declaration (it restores); free-surface topography releases, correctly; a
rigid translation releases, correctly, and is out of scope. The only caller of `deform` in the
library is the free-surface update. Its cost is that it also releases the walls it did not move, so
an annulus with a free upper surface loses its analytic lower wall.

**What survives of the measurement.** Only tests, and an optional debug helper (say
`mesh.check_bounding_surfaces()`), asserting that each preserving operation kept its promise: the
largest distance of a label's vertices from its registered surface, with the tolerance stated as a
small multiple of machine epsilon times the radius (measured: at most 6e-16 relative for every true
declaration). One test per preserving row of the table. Never a gate in a solve.

**Units.** *Read.* The surface holds its centre and radius as plain floats in model coordinates, the
frame the DM holds. The annulus constructors non-dimensionalise their radii on entry;
`BoundingSurface` non-dimensionalises a radius that arrives as a quantity; `restore()` acts on the
model coordinates the movers pass. In a units model the shell test builds with plain radii, which
are model coordinates. Not checked by a run: a spherical constructor given radii with units.
gthyagi's methods refuse dimensional data, so they read the same frame.

**Cost, against 4 to 6 hours for the verified query.**
- Needed before the lagged walls can read the declaration: a read accessor that returns the
  registered, unreleased radial surface or refuses (1.5 hours, in `discretisation_mesh.py`, the mesh
  desk's file).
- Needed before a pressure lift on a refined shell: the Internal snap (2 to 3 hours, the generator
  file; it moves recorded anchors).
- The other three defects: about 3.5 hours, in `discretisation_mesh.py`.
- Tests and the debug helper for every preserving row: about 3 hours.
- Optional: children of `adapt` inherit (they are snapped already), 2 to 3 hours; surfaces persisted
  in a checkpoint, about 3 hours.

About 10 to 12 hours in all, of which 1.5 gate the annulus work.

**Questions for Louis.**
1. Refuse when the wall is undeclared, with no chordal fallback? *Recommend: refuse.*
2. Should `deform` take the labels it leaves alone (`keep=`), so a free surface does not release the
   lower wall? *Recommend: not now; add it when a model needs it.*
3. Snap the refined Internal surface (#949 item 3) now? *Recommend: yes; it is the one declaration
   that is false today in an ordinary mesh.*
4. Should `adapt` children inherit the surfaces they were snapped to? *Recommend: yes, later.*
5. `canonical_normal` keeps its own geometry-version stamp, which goes stale after a move that
   preserved the wall. Should it follow the surface's registration instead? *Recommend: yes, as a
   separate change for the desk that owns the rotated solve.*

### A2. Tangential moves: telling "slid along the surface" from "left the surface"

Louis's subtlety: MMPDE with boundary slip moves wall nodes along the circle or sphere, and the
special case is still true afterwards, so "a mover touched the boundary" is the wrong trigger. The
candidate rule is to verify the declaration rather than infer it: ask whether the wall's nodes are
still on the declared surface.

**Run** (serial, development 93e66eed, probe and logs in hyperion `runs/2026-11-12-h6/contract/`).
The check is the largest |‖x − c‖ − R| / R over the vertices of a labelled boundary, against the
surface registered in `mesh.bounding_surfaces`.

| case | largest relative distance from the declared surface | the check |
|---|---|---|
| annulus and shell as built | ≤ 2.2e-16 | passes |
| MMPDE slip on the registered surfaces (wall nodes moved by 2.0e-2) | 2.2e-16; surfaces still registered `radial` | passes: the special case survives |
| the same move with the surfaces unregistered (slip along facets) | 4.4e-3 at h = 0.1, 6.3e-4 at h = 0.05 | fails, correctly (O(h²)) |
| `deform` with topography of 1e-3 on the outer wall | 1.0e-3; both walls released | fails |
| rigid translation by 0.01 with `deform` | 2.0e-2 and 1.0e-2 against the declared centre; 1.1e-16 against the moved centre | fails |
| internal surfaces as built, 2-D and 3-D | ≤ 2.8e-16 | passes |
| `SphericalShellInternalBoundary`, one or two refinements | walls ≤ 6.1e-16; Internal 2.9e-2 | walls pass, Internal fails |

So the check separates the cases by ten orders of magnitude: every true declaration is at round-off,
every false one at 2e-4 or worse. Three things the runs showed that reading had not:
- the refined shell's Internal surface is off its declared sphere by 2.9% after one refinement
  already; walls are snapped on refinement, the Internal surface is not;
- `deform` releases every surface even when no coordinate changed: today's release is "who moved",
  not "what moved";
- the movers do not bump `_mesh_version` (still 0 after the MMPDE move) but do bump
  `_geometry_version` (11), so only the latter could serve as a stamp.

**Assessment of the candidate.** It is right, and it is alternative (a) above with a stamp added.
- Tolerance: 1e-9 relative to the radius, the value the rotated solve's wall test already uses;
  anything from 1e-12 to 1e-6 gives the same verdicts on these cases.
- Cost: one pass over the boundary's vertices and one collective reduction (254 vertices on the
  coarse shell, 4,004 at two refinements). Mesh coordinates are degree 1, so vertices suffice.
- Lazy, at use. I would go one step further than the candidate and check at every use, without a
  stamp: the check is cheap, and then no coordinate writer can get behind it. If a stamp is wanted
  for cost, it must be `_geometry_version`.
- Already there: `BoundingSurface.restore` (why the slip case passes) and the rotated solve's
  declared-rotation wall test, which is the same check; the two should become one.

**The proposal in one paragraph.** Registration is the declaration, and the distance check is its
verification. A curved wall is declared analytic by its entry in `mesh.bounding_surfaces` (centre and
radius, put there by the constructor). A mover that slides nodes restores them to that registered
surface (`BoundingSurface.restore`; run: 2.2e-16 after an MMPDE slip of 2.0e-2), so the special case
survives. A method that uses the shortcut asks the mesh for the surface, and the mesh answers only if
the wall's vertices lie on it to 1e-9 of the radius; otherwise the method refuses with a message
saying the wall no longer lies on the declared surface. A rigid translation of the whole mesh is out
of scope (Louis, 2026-11-12): the wall then fails the check against the declared centre and the
method refuses; there is no re-fitting of the centre and no special case.

**Where it still needs a decision.**
- With the check in place, should `deform` still release every surface unconditionally? (H5.)
- The refined Internal surface is declared and false from construction; snapping it is the open
  `TODO(BUG)`. Until then a method relying on it refuses, which is the right answer. (H5.)
- Child meshes and checkpoint reloads appear to carry no surfaces (inferred), so a method refuses
  there until they inherit.

**The other half: what each chunk builds from node positions, and when.** *Read.* None of gthyagi's
modules reads a geometry version or `bounding_surfaces`, and none refuses a moved mesh.

| chunk | built | after a tangential slide |
|---|---|---|
| `pressure_split` | once, when called | stale, silently (the guide says "Reconstruct the split after changing mesh geometry"; nothing enforces it) |
| `cylindrical_pressure_lifting` | once | stale, silently |
| lagged walls | once, in the handle at registration; updates reuse it | stale, silently |
| cylindrical and spherical gap | at every call | right, provided the walls still verify |
| spherical pressure lift | once | stale, silently |
| sheet loads | once | not established |
| fitted regions | at construction, connectivity only | right |
| #857 recovery | per call, on the wall handle | stale with the handle (inferred) |

Work to make the once-built chunks honest: lagged walls about 3 hours (rebuild the handle's geometry
at each update when the geometry version has changed); `pressure_split` and each lift about 2 hours
each (refuse a split built at an older geometry version). This moves `pressure_split` from "fits as
it is" to "fits with a 2-hour guard": it needs no wall geometry, but it must not silently outlive a
mesh move.

### B. The chunks

Fit: (i) fits as it is; (ii) fits once it reads the mesh's declaration and refuses when that is
invalid; (iii) duplicates what we have; (iv) does not fit. Hours are mine to a PR that meets the merge
conditions, plus one review round; "author's part" is the share of that which is his unfinished work.

| # | Chunk | What it does | Wall assumption, and where it comes from | Fit | Value | Hours (author's part) |
|---|---|---|---|---|---|---|
| 1 | Rotated datum collectives (#855) | fixes a hang when FE data prescribe wall-normal velocity | none | (i) | a bug fix | done: #1097, waiting on CI |
| 2 | Shell region labels | Inner/Outer cells by connectivity | none; labels only | (i) | fixes mislabelled cells on refined shells | done: #1100 merged; 2 h for H3's two test gaps |
| 3 | Spherical Kramer references, gravity kernels, harmonics | exact fields and kernels as formulae | none: data and formulae on a shell the user describes | (i) | the reference every spherical study needs; high | done: #1108 in review |
| 4 | `pressure_split` | writes a prescribed interface pressure jump as p = q + p_J on fitted facets | none: named fitted facets, user's jump and normal | (i), with a guard: built once, so it must refuse after a mesh move (A2) | general; removes the jump from the pressure space on any fitted interface; high | 3 h: cut out of #1110, add the guard and its test (the guard: his) |
| 5 | `cylindrical_pressure_lifting` | the same for one harmonic on an exact circle, cut cells integrated exactly | origin-centred circle; `interface_radius=`, `outer_radius=` arguments | (ii), or (iii): `pressure_split` on a fitted mesh is its general form | benchmark only; low unless the paper uses unfitted interfaces | 3 h after the contract (refuse an unfitted mesh: his) |
| 6 | Lagged circular walls, free slip and zero slip | corrects the polygon wall condition to the true circle over a few ordinary solves, on our rotated solve and essential conditions | origin-centred circle; `radius=` and `sign=` arguments, vertices re-checked | (ii) | the cheapest route to accurate walls on an annulus with our own solver. Run by H3 (2026-11-12, #1110 at 14627f57, manufactured azimuthal flow, zero slip): velocity error 1.1e-3 to 1.4e-4 from h = 1/8 to 1/16, third order, against 1.1e-2 to 2.8e-3, second order, for plain zero slip on the polygon; the same at np 2. High for the cylindrical benchmark and the publication | 6 to 8 h after the contract (analytic non-zero-flow test, transcript record: his) |
| 7 | Cylindrical coupled gap, free slip and zero slip | integrates over the true annulus (caps added and removed) with a wall multiplier; own matrix and solver | two radii as arguments; closed-form cap rule; isoviscous, linear | (ii) for the geometry; but it is a separate solver beside `Stokes` that refuses any registered condition, so it does not use our solve, multigrid or transcript: closer to (iv) as library code | carries the wall traction as an unknown on the true circle (the note's multiplier route); a benchmark reference rather than a tool; medium | 8 to 10 h (free-slip convergence test, np above 2: his) |
| 8 | Spherical coupled gap | the same on tetrahedra with cut cells, curtains and its own preconditioner | concentric origin-centred spheres, hard-wired through about 2,000 lines; viscosity 1 for the preconditioner | (ii) in geometry; (iv) as a second solver | the only spherical route to wall traction on the true sphere; unproven (no analytic-flow test); high if it works | 2 to 3 days (any parallel test, any convergence test: his); recommend it goes back to him with the list |
| 9 | Spherical pressure lift and sheet loads | 3-D lift on the true sphere; harmonic sheet loads as a right-hand side | sphere radius and one harmonic | (ii) for the lift; the sheet load is a benchmark forcing, better placed with the analytic references | medium for the spherical benchmark | 1 day (MPI, rank-0 gather: his) |
| 10 | Diagnostics package | observers, norms, spherical reactions | reads the gap solves' state | follows 7 and 8; its plain Stokes observer is (i) | low on its own | half a day, H4, after 7 and 8 are decided |
| 11 | #857 recovery (reaction moved to the circle, trace reconstruction, zero-slip shear on the circle) | post-processes the reaction we already return | circle, by argument | (ii) on top of (iii): the reaction itself is ours (`boundary_normal_traction`, `boundary_flux`; UWTN 2026-016) | only if pointwise wall stress from the lagged walls is wanted; decided by the stage 2 measurement | 1 day plus the mathematical review he asked for |
| 12 | Rotated-solve rewrite (gauge verification, self-installing preconditioner, residual guard, loop reorder, second LU pin) | changes what the default rotated solve treats as a gauge | none | (iv): changes defaults; measured to return a rigid rotation (sections 1 and 3) | his observation that we under-report the residual is right and is with W1 | not landed |
| 13 | Coordinate projection, integral field offsets, surface-mesh reaction normal | internal changes every mesh or integral sees | none | (iv) as bundled: not needed by any chunk (section 6, run); the first duplicates #902 | none shown | not landed |

**Recommended order** (fit and value first, cost second):
1. Chunks 1 to 3: in hand.
2. Chunk 4, `pressure_split`: general; fits once it refuses a split older than the mesh geometry.
   Cut #1110 down to it and add that guard.
3. The contract of part A, as one small PR of its own once Louis has chosen (my estimate 4 to 6 hours
   with tests at np 1 to 5, in H5's and W1's territory, so through the hub).
4. Chunk 6, the lagged walls, reading the declaration: the piece with the most value per hour for the
   annulus benchmark, and it runs on our solver. Chunk 5 with it or dropped.
5. Stage 2 of section 7 (the note's Kramer table with the lagged walls, the gap reaction and #857's
   recovery side by side). That measurement decides chunks 7 and 11.
6. Chunks 8 and 9 (spherical): return to gthyagi with the list of what is missing, unless the
   publication needs them from us; they are the bulk of the unfinished work.

## The opt-in claim, measured

**Run.** The 147 serial test files of #1033's own base commit (abe5e0ca) that use a Stokes solve or
the rotated path, unmodified, against a build of that commit and a build of #1033 (hyperion
`optin/`):

| build | passed | failed |
|---|---|---|
| base commit abe5e0ca | 1261 | 0 (3 source-scan tests cannot run from a copied test directory; they pass in the #1033 worktree) |
| #1033 | 1236 | 25, in 5 files |

The 25 are all in the rotated free-slip solve: `test_1131` 9 (rotation not removed on the shell,
annulus, moved and add_fault meshes, units shell), `test_1142` 10 (which rotations count as exact,
and what is projected at tight tolerance), `test_1018_rotated_nodal_normal` 3, `test_1111` 2,
`test_0022_rotated_adjoint` 1. These are the files #1033 edits. The other 142 files, including every
Stokes test that does not use rotated free slip, give the same pass counts on both builds. Iteration
counts are compared only where the tests assert them.

**Run, np 2 and np 4.** The base commit's 35 parallel test files that use a Stokes solve or the
rotated path, unmodified. On the base-commit build all 35 pass at both rank counts. On #1033, 3 of 35
fail at both: `test_1112_rotated_fmg_coarse_shifted_lu_parallel`, `test_1114_mg_coarse_gamg_parallel`
and `test_1131_rotated_nullspace_from_mesh_parallel`, the parallel counterparts of the serial
failures; the other 32 match.

## D1 and D2 in the light of the tour

**D1. What happens to #1033's changes to the rotated solve.**
The new methods do not need them (section 6, run: their tests pass on development's solver core). The changes themselves are a mixed bag:
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
