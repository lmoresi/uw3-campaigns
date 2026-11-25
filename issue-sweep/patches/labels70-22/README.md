# UNFILED 70 and 22: the cut labels its edge across a kink inside a cell (with 68's refusal as the guard)

Base: development fbef72fa. Three commits, as `git format-patch` files. Not pushed.
- 0001 (d37db66e) is UNFILED 68: add_fault refuses a cut with no facet, or one that misses part
  of the trace. It is reviewed on its own.
- 0002 (44aa8c53) is the labelling fix, plus 68's refusal on add_conforming_surface.
- 0003 (911a7b16) is UNFILED 72: the cut refuses a flat cell (see the last section).

## Cause
`line_cut._label_cut_edges` labelled an edge only when both its ends AND its midpoint lay on the
trace. A sample of the trace inside a cell (no vertex on it) is a kink, and the cut's edge across it
is a chord with its midpoint off the trace, so it was dropped:
- add_conforming_surface, which puts no vertex on the samples, returned every curved surface
  partial, even sampled a cell apart;
- add_fault hid it by pulling a vertex onto every sample, and paid with snap failures and empty
  faults.

## The rule
An edge is the line's when:
- both its ends lie on the line;
- they are consecutive along it (no vertex on the line between their arc-length parameters);
- its chord is at least `_CHORD_TO_ARC = 0.5` of the line's length between them. That admits a
  kink of up to 120 degrees inside a cell and refuses a hairpin, or two stretches passing close.

Distances and parameters follow the cut's own segments: chords in the plane, great-circle arcs on a
sphere. A first version measured chords on the sphere too, and dropped 15 of 16 edges of test_1079's
arc; caught by the suite (`sphere_dbg.py`).

## Measured: old rule against new on one build (`measure_labels.py`, `grid.sh`; `grid_out.txt`)
Families, each run forward and reversed:
- lines_arcs: 10 lines and 10 gentle arcs. For add_conforming_surface they cross the box wall to
  wall; for add_fault they are 6 cells long.
- hairpin: arms half a cell apart.
- approach: an arc of 1.9 pi whose ends pass 0.47 cells apart.

Meshes: irregular and regular 1/12 boxes. Sample spacings: 1.0, 0.5 and 0.3 cells. Outcomes:
complete, partial or empty by 68's check; "spurious" means a labelled edge with more than twice
its chord of trace between its ends.

add_conforming_surface, lines_arcs, complete of 40:

| mesh | 1.0 | 0.5 | 0.3 |
|---|---|---|---|
| irregular, old | 22 (18 partial) | 20 (20 partial) | 20 (16 partial, 4 empty) |
| irregular, new | 40 | 40 | 40 |
| regular, old | 20 (20 partial) | 20 (18 partial, 2 empty) | 20 (14 partial, 6 empty) |
| regular, new | 40 | 40 | 40 |

add_fault (every sample pulled), lines_arcs:
- new against old, complete: irregular 40/40, 22/13, 18/6; regular 32/24, 26/12, 13/8;
- empty under old: 1, 8 (irregular), 2, 2 (regular); under new: 0 in every row;
- raised: unchanged (snap failures from pulling every sample).

Hairpins and the self-approach:
- no spurious edge under either rule, on either path;
- add_conforming_surface refuses them under both rules alike (19-20 of 20), so that path carries
  no information about them;
- add_fault: complete about equal or up under the new rule.

## Separate number: add_fault's pull rule under the new labelling (NOT changed here)
With only the tips and the turns above 45 degrees pulled, with or without samples about a cell
apart: 240/240 complete (lines_arcs, both meshes, three spacings), none raised. Pulling every
sample gives 8-19 refusals per row. UNFILED 22's snap failures disappear with correct labelling plus
the lighter pull. That is a register row for Louis, measured after this PR's review.

## Tests
- tests/test_0898_cut_labels_the_chord_across_a_kink.py (level_1, tier_b): an arc crossing the
  regular box is labelled along its whole length (fails under the midpoint rule: 0.682 from the
  trace); no labelled edge joins the arms of a hairpin. Both assert relations.
- test_0897: its "empty" fixture is partial under the new labelling, and still refused. The
  empty-label refusal is checked on a hand-labelled chain.
- The fault, conforming-surface and line-cut suites (40 files): 428 passed, 1 skipped.

## UNFILED 72: the cut refuses a flat cell (0003)
With the labelling fixed, add_fault places traces that development refused for other reasons, and
some came back with a flat cell: area 1e-17 to 6e-19 of the cell's own size, a 0-degree angle. They
sit at 90- and 120-degree turns where several samples lose their vertex to a later one. It happens
under the every-sample pull, not only a lighter one; `dev72.py` reproduces it, and add_fault
returned that mesh. The cut refused inverted cells but not flat ones.

The guard: a cell whose area is below 1e-9 of its own longest edge squared is refused. Every mesh
add_fault returned in the hunt was measured with the guard off (`pull22r.py`, `ratio_*.jsonl`;
about 1060 meshes). Minimum area / longest edge^2, per returned mesh:

| bin | development (329) | labelling, every sample (304) | labelling, light+sharp (428) |
|---|---|---|---|
| < 1e-14 | 0 | 17 | 5 |
| 1e-14 to 5.7e-5 | 0 | 0 | 0 |
| 5.7e-5 to 1e-2 | 3 (5.7e-5, 3.7e-3, 9.9e-3) | 0 | 0 |
| 1e-2 to 0.1 | 124 | 102 | 326 |
| > 0.1 | 202 | 185 | 97 |

The gap runs from 1e-14 to 5.7e-5. The threshold, 1e-9, is its log-middle, with a margin of about
5e4 on each side. It is a flatness guard, not a quality guard: development returns a poor but not
flat mesh at 5.7e-5, and it passes.

Every refusal by the guard in the guarded hunt (22 under the every-sample pull, 7 under light+sharp,
at either snap setting) is a trace that development also refuses (it raised on all 29). So the guard
never refuses a trace development places.

test_0899: the measured trace is refused under both pull rules; a trace that places normally is not;
the refusals fail with the guard disabled. Suites: 431 passed, 1 skipped (run at a threshold of 1e-6;
1e-9 refuses strictly less).
