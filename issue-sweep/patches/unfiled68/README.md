# UNFILED 68: add_fault refuses an empty or partial cut

Base: development fbef72fa. One commit (`git format-patch`). Not pushed.

- Change: `fault_split._refuse_an_empty_or_partial_cut`, called after each segment's cut in
  add_fault's cut path.
- Refusal: no facet labelled; or some trace point (ten per segment) more than half a cell from the
  labelled chain. The cell is the mean edge length near the trace, a stated tolerance, not
  inferred.
- Message: the trace's median sample spacing against that cell size, and "resample the trace to
  about one cell apart".
- Collective: the facet count is an allreduce SUM, and each trace point's distance to the chain an
  allreduce MIN. The verdict comes from reduced values only, so it is identical on every rank.
- Unchanged: add_fault(cut=False), the label-only path, where an empty label is legitimate (the
  seam ligament).

C1's point (5): `place_fault_ribbon_2d` and `place_sheet` do NOT share `_label_cut_edges`. They
label through their own assembly edges, and place_surface imports other line_cut helpers but not
this one. Two other paths do share the chord rule: `add_fault(cut=False)` (`_label_embedded_edges`)
and `Mesh.add_conforming_surface` (through `cut_along_lines`). The second may have the same silent
empty or partial result; it is not measured here.

Tests: tests/test_0897_add_fault_refuses_an_empty_or_partial_cut.py (level_1, tier_b, 3 s).
- An empty case (trace k 3) and a short case (trace k 4) on the regular box, sampled 0.3 cells
  apart. Both fail on development.
- A guard (trace k 0, sampled 1 cell apart), which is added.
- The check on hand-labelled chains along y = 0.5 (empty, half, whole), which is independent of
  any mesher.
The fault suite (38 files): 417 passed, 1 skipped, unchanged from development.

For the server at np 2: test_0897, to confirm that the verdict and message are identical on
every rank.
