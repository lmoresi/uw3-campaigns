add_fault and add_conforming_surface refuse a cut that does not follow the trace; the cut labels its edge across a kink; add_fault keeps a vertex on each tip

## What was wrong
`add_fault` could return a fault that did not follow its trace, and say nothing:

- **No facet at all.** A trace sampled finer than the mesh left samples without a vertex, and the
  cut labelled nothing.
- **Split along part of its length.** At a sharp kink the cut labelled only the edges whose
  midpoint lay on the trace, so it dropped the chord across a kink inside a cell. The chain came
  back in pieces. The split then split one piece and left the other labelled but unsplit, or on
  a sphere split both into separate slits with an unsplit bridge. On development, 101 of 265
  returned sharp-kink faults on a 1/12 box grid were in two or three pieces.
- **Short of its first tip.** `add_fault` pulled the samples in trace order, and when two choose
  one vertex the later keeps it. A first tip within reach of the next sample lost its vertex, and
  the fault ended one sample spacing short. All 36 tip-short faults of a 480-trace grid were
  short at the start.
- **Flat cells.** Pulling every sample of a finely sampled trace could leave cells with near-zero
  area, which the cut returned.

## What changes
- **Labelling.** The cut labels an edge whose two ends lie on the trace at consecutive
  arc-length parameters, with chord at least 0.5 of the arc between them. Arc length is measured
  along great circles on a sphere. This labels the chord across an in-cell kink up to about 120
  degrees when the kink is midway; an off-centre kink is refused sooner.
- **Tips.** `add_fault` pulls the tips after the other samples, so each keeps its vertex, and
  labels those vertices.
- **Refusals.** A cut is refused, with the same message on every rank, when:
  - it labels no facet;
  - (`add_fault`) its chain is not one connected piece. Pieces are counted globally, joined at
    global vertex numbers, so a chain across a partition seam counts once. A chain cut by an
    earlier fault's slit is left to the split's own touching-junction refusal.
  - (`add_fault`) the chain's ends are not the tips' vertices (exact, by mesh point);
  - a point of the trace is farther from the chain than half the local cell side;
  - it leaves a cell whose area is below 1e-9 of its longest edge squared.

## Tolerances and coordinate matches
- **Half a cell.** The coverage test asks the chain to come within half the local cell side of
  each of ten points per trace segment. The cell side is the median length of the 6 base-mesh
  edges nearest the point, measured before the pull and the cut. No measured distribution had a
  gap to put this threshold in: on the 480-trace box grid, sound faults (slip within 10 % of the
  trace sampled a cell apart) reach 0.52 cells, and wrong ones start at 0 because the pull
  distorts the cells. It is left with the corners: a chain that cuts a corner by less than half a
  cell is added.
- **Chord ratio 0.5.** The chord across an in-cell kink must be at least 0.5 of the arc it spans.
- **Flat-cell ratio 1e-9.** Measured on the same grids, sound cells sit above 5.7e-5 and the flat
  cells produced fall between 1e-14 and 1e-9.
- **Tip vertices.** These are found by exact equality with the coordinates the pull has just
  written (the stored value itself, not a tolerance).
- **On the trace.** A vertex is on the trace when it lies within 1e-9 of the mesh's global extent
  of it. The same 1e-9 also separates arc-length parameters.

## Measured behaviour change
On the 480-trace box grid (two 1/12 boxes, regular and irregular; lines, arcs and kinks of 10 to
150 degrees; samplings 1.0, 0.5 and 0.3 cells):
- **Coverage refusals.** Faults refused by the distance test fell from 69 to 20 of the one-piece
  faults once the tips kept their vertices.
- **Slip error.** Against the trace sampled a cell apart, the median error fell from 5.0 % to
  2.0 %.
- **Tip shortfalls.** No added fault stops short of a tip.
- **Faults that development returns and these patches refuse.** These are the two-piece faults,
  and every one was in pieces on development.
- **Faults development places today.** 29 of 232 change mesh, each by one vertex: the tip's in
  place of the neighbouring sample's. All 29 are still added. Their slip changes by a median
  +5.5 % (largest 26 %). Against the one-cell reference, their median error falls from 9.5 % to
  2.3 %, and those off by more than 10 % from 12 to 3. Six get worse by more than 2 points: five
  kink30 traces move from 0.2-5 % to 3-9 % error, and one 150-degree hairpin moves from 68 % to
  75 %.

## Tests
- **test_0897** (tier B): cases labelled by hand for each refusal (no facet, short chain, two
  pieces, chain ending off a tip). The two traces of the original report are now split whole,
  and a trace sampled half a cell apart keeps both tips. That tip case fails before the fix, 0.5
  cells short.
- **test_0898**: the chord across a kink is labelled whole, and no hairpin edge is labelled.
- **test_0899**: the flat-cell refusal fails with the guard disabled.
- **tests/parallel/test_0897 (parallel)**: one outcome and one message on every rank; a chain
  across the partition is one piece.

Fault, conforming-surface and line-cut suites: 432 passed, 1 skipped, serial. The round-1 code ran
at 2-4 ranks on a Linux workstation (180 runs, identical messages on every rank). The parallel test
and the later commits are still to be run there.

Underworld development team with AI support from Claude Code
