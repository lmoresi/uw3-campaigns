# #1168: the separated fix, as an experiment

From H6 (the curved-walls session), 2026-11-21, for the dev hub. An experiment, not a PR:
a local branch off development (06b9dec1), nothing pushed to underworld3. The change is
`separated-gauge.patch` (rotated_bc.py only, behind the private switch
`solver._rotated_separated_gauge`; with the switch off the default path is unchanged in the
same build). A 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R,
MPICH), one rank, P2/P1, manufactured annulus solutions of `../circles/`, errors modulo the
least-squares rigid rotation.

## The fix

Constrain u.n along the default, measure-weighted facet normal W_i (unchanged), and gauge the
constrained operator's own near-null mode instead of the declared rigid rotation.

- **Candidate A is what development already does.** For a declared rotation (#906) the gauge
  vector is `Q·rotation` with its constrained normal rows zeroed, normalised
  (`_rotated_compatible`, used both for the Krylov null space and the final projection). The
  "default" column below is A. It is first order on the graded circle with cos 3θ slip.
- **Candidate B: the constrained velocity block's near-null mode**, by inverse iteration (MUMPS
  LU, 12 iterations) from A, with the constrained rows given a unit-scale diagonal in a copy
  and re-zeroed in each iterate (without that, the iteration settles on the eliminated rows:
  the first attempt did, and was wrong). Still first order.
- **Candidate B2: the near-null mode of the whole constrained saddle-point operator**
  (velocity and pressure), the same inverse iteration on the full rotated operator with the
  constrained rows fixed and one pressure unknown pinned (as the direct-LU route does). The
  mode keeps its small pressure part (velocity fraction of its norm 0.99999 to 1). **Second
  order everywhere measured.** B2 differs from A by only 1e-6 to 1e-5 in cosine; the pressure
  part is what matters: the exact discrete solution carries a component of order 1/λ along the
  near-null mode, so removing a vector that differs from it by little still leaves a
  first-order remainder unless it is the operator's own mode.

How the comparison is made: default (A), B and B2 all use the direct-LU route (one exact
discrete solve, the gauge acting only on the final answer), so the columns differ only in the
mode projected out. `X/|X|` is the iterative route of round 2 (`../mmpde-and-graded/logs/conv_*`,
development plus the #1277 warning, same meshes); the LU route's pressure pin would drop the row
that carries #1168's constraint and hide it.

## Velocity error, 0.05 then 0.025 (rate)

| mesh, slip | default (A) | separated B | separated B2 | `X/|X|` |
|---|---|---|---|---|
| as built, sin 2θ | 2.48e-3, 3.82e-4 (2.70) | same | 2.48e-3, 3.82e-4 (2.70) | 2.48e-3, 3.82e-4 (2.70) |
| as built, cos 3θ | 3.00e-3, 5.20e-4 (2.53) | same | 3.00e-3, 5.20e-4 (2.53) | 3.00e-3, 5.20e-4 (2.53) |
| graded, sin 2θ | 2.58e-3, 4.19e-4 (2.62) | same | 2.58e-3, 4.19e-4 (2.62) | 2.60e-3, 4.26e-4 (2.61) |
| graded, cos 3θ | **8.82e-2, 4.39e-2 (1.01)** | **2.78e-2, 1.41e-2 (0.98)** | 3.24e-3, 5.95e-4 (2.45) | 3.20e-3, 5.82e-4 (2.46) |
| MMPDE trench, sin 2θ | 2.65e-3, 3.99e-4 (2.73) | same | 2.65e-3, 3.99e-4 (2.73) | **1.43e-2, 7.20e-3 (0.99)** |
| MMPDE trench, cos 3θ | 3.32e-3, 5.51e-4 (2.59) | same | 3.32e-3, 5.51e-4 (2.59) | **5.49e-2, 2.75e-2 (1.00)** |

Rotation carried in the answer (omega_h; the exact solution's omega_e is at most 1.6e-3): graded
cos 3θ -3.7e-2 / -4.0e-2 (A), -4.0e-2 / -4.1e-2 (B), -3.7e-2 / -3.9e-2 (B2); elsewhere 1e-3 to
6e-3 for every gauge. (The error is taken modulo rotation; the gauge sets the rotation, not the
error.) Mean pressure offset at most 1.1e-2 for every LU entry (A, B, B2); for `X/|X|` it grows
to -1.4e4 and +5.0e4 on the MMPDE meshes (round 2).

Convergence, from each rotated solve's own record: every LU solve converged True with a final
residual of 5e-11 to 7e-14 against an initial 3 to 6, except the as-built meshes at s2 0.05,
s2 0.025 and c3 0.05 (converged False at 7.5e-10, 3.0e-9, 4.6e-8, i.e. relative 1e-10 to 1e-8;
the same for A, B and B2, which differ only after the solve). `X/|X|`: converged True, round 2.

## The modes

Near-null-ness, ||A·mode|| over the operator's diagonal scale:

| mesh, cell | A | B2 | cosine distance B2 to A |
|---|---|---|---|
| as built 0.05 / 0.025 | 3.4e-12 / 1.0e-12 | 1.9e-16 / 1.9e-16 | 4.4e-16 / 2.2e-16 |
| graded 0.05 / 0.025 | 7.1e-5 / 1.2e-5 | 1.2e-8 / 3.9e-10 | 1.0e-6 / 5.6e-8 |
| MMPDE trench 0.05 / 0.025 | 2.5e-5 / 4.5e-6 | 1.3e-9 / 4.9e-11 | 1.1e-5 / 1.5e-6 |

On as-built (equal-chord) meshes A is the rigid rotation with nothing to zero (its residual is
round-off) and B2 equals it to round-off. On unequal chords A is not null (O(h^2)), and B2 is
the operator's own near-null mode (its residual is the small eigenvalue, about h^4 to h^6).

## Cost

The gauge's set-up (one extra MUMPS factorisation of the rotated operator and 12 back-solves):
B2 0.12 s at 0.05 and 0.55 to 0.61 s at 0.025, against whole solves of 7 to 21 s, so 2 to 6 %
here, once per solve (computed at the first Newton iteration). B (velocity block only) 0.09 and
0.38 to 0.41 s. Solve wall time otherwise unchanged (A 7.2 to 20.7 s, B2 7.1 to 21.4 s, the same
iteration counts: one Newton step, one LU solve). On the iterative route with multigrid, an
extra direct factorisation would be the dominant cost at production sizes; a few iterations of
the solver's own preconditioned operator, warm-started from A, would be the production form (not
built).

## Verdict

The separated fix with B2 (constrain along W_i; gauge the constrained saddle operator's own
near-null mode) converges at second order on every mesh and slip measured, including the graded
cos 3θ case where development's gauge is first order and the MMPDE-moved meshes where `X/|X|` is
first order; on equal-chord meshes it is development's gauge to round-off. B (velocity block
only) is not enough.

Not run: np > 1 (the experiment's inverse iteration is serial-minded: a direct factorisation of
the global operator and a global pressure pin); the iterative route with B2 as the Krylov null
space (the patch wires it there too, unmeasured); 3-D (the shell's three rotations); the driver.

## Files

`separated-gauge.patch`, `measure_sep.py`, `run_sep.sh`, `manufactured_annulus.py` and
`slide.py` (copies), `logs/` (`sep_<mesh>_<slip>_<cell>_<method>.log`; `smoke_*` are the first
attempts, including the wrong B that settled on the eliminated rows).
