# Review of #1126 (head 9f63111e): READY, two low recommendations

Reviewer: H4 (the adjoint and thin-sheet session), against the adversarial-review checklist. Runs were serial, plus np 2 and 3 where stated, on a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH). The development side is development 01dec8d2 plus the unrelated #1124, which leaves `line_cut`, `fault_split` and `surfaces` untouched. Not posted on GitHub: posting is not approved in this session.

## Claims checked

- **The new tests fail on development.** We see 8 failures across #1126's three new files; the two sequential #494 cases pass there and are guards, as the PR says. On the head, all 10 pass.
- **#494, two lines 0.7 h and 0.9 h apart, in one call and in two.** The test counts the edges between each line's collinear vertices (V − 1 for a complete chain), and an empty chain fails it. The one-call cases fail on development and pass on the head. In the two-call cases the second cut now also goes through #595's protection, because line A's label is an internal label for the second cut. They pass on both builds.
- **Callers passing nothing get the same cut.** This was our main attack, and it failed. The new guard protects every vertex on any labelled internal facet, so we tried meshes that already carry one, with `add_fault` and no snap options. The head's cut is identical to development's (vertex count, and a hash of the coordinates rounded to 1e-9) in all six cases:
  - one fault (572 vertices);
  - a second fault 0.8 h, 1.5 h and 3 h from the first (632, 632, 614);
  - `AnnulusInternalBoundary` with a fault crossing the internal boundary (880);
  - the same with a fault 0.03 inside the internal boundary (870).

  No #595 warning fired in any of them.

## Attacks that failed

- **Parallel.** On the band cut from `test_0595`, the guard spares 10 skin vertices at np 1, 2 and 3 alike. The region verdict is allgathered and the protected mask is OR-reduced over the SF. The count is reduced over owned vertices only, and the warning is printed on rank 0 only.
- **Cost.** `_internal_label_vertices` takes 0.001 s on a 23,264-cell box, against 3.8 s for the whole cut.
- **Crossing faults.** A second fault crossing the first is refused by `add_fault`'s existing check ("would change the fault(s) already split"), on both builds.

## Findings (low, not merge conditions)

1. **The guard is loud once per process.** It is a `warnings.warn` on rank 0. Under Python's default filter, two identical spared cuts in one process print one warning (measured: 1 of 2, at np 1, 2 and 3), so a driver that rebuilds in a loop sees it only the first time. The test sets `simplefilter("always")`, so it cannot see this. Suggestion: give it a `UserWarning` subclass that the package registers as `always`, or also report the count through the cut's returned `info`.
2. **State on a function object.** `_resolve_snapping.refused` carries the spared count from `_resolve_snapping` back to `cut_along_lines` as a function attribute: module-global state, and not reentrant. Returning it, or putting it in the returned `info`, is the plain form.
3. **Tier on the module.** `test_0494` and `test_0595` carry `tier_b` in the module's `pytestmark`. Charter §8 says the tier goes on each test.

## Not tested

- #540 beyond its own tests: they compare against analytic normals and distances for two traces, fail on development and pass on the head.
- #429's test half: it passes on both builds, as the PR says. We did not repeat H5's mutant.
- np above 3.
