add_fault and add_conforming_surface refuse a cut that does not follow the trace; the cut labels its edge across a kink; add_fault keeps a vertex on each tip and each turn

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
- **Across a corner.** A turn sample lost its vertex the same way, and the chain cut the corner
  by up to half a cell (one 120-degree kink: slip 33 % low).
- **Flat cells.** Pulling every sample of a finely sampled trace could leave cells with near-zero
  area, which the cut returned.

## What changes
- **Labelling.** The cut labels an edge whose two ends lie on the trace at consecutive
  arc-length parameters, with chord at least 0.5 of the arc between them. Arc length is measured
  along great circles on a sphere. This labels the chord across an in-cell kink up to about 120
  degrees when the kink is midway; an off-centre kink is refused sooner.
- **Tips and turns.** `add_fault` pulls the samples where the trace turns by more than 45 degrees
  after the plain samples, and the tips last of all. Each keeps its vertex, and those vertices
  are labelled (and the labels removed after use).
- **Refusals.** A cut is refused, with the same message on every rank, when:
  - it labels no facet;
  - (`add_fault`) its chain is not one connected piece. Pieces are counted globally, joined at
    global vertex numbers, so a chain across a partition seam counts once. A chain cut by an
    earlier fault's slit is left to the split's own touching-junction refusal.
  - (`add_fault`) the chain's ends are not the tips' vertices, or it misses a turn's vertex
    (exact, by mesh point, every edge counted once). Beside the slit of a fault already split into
    the mesh, this refusal is raised after the record check and the split;
  - a point of the trace is farther from the chain than half the local cell side;
  - it leaves a cell whose area is below 1e-9 of its longest edge squared.

## Tolerances and coordinate matches
- **Half a cell.** The coverage test asks the chain to come within half the local cell side of
  each of ten points per trace segment. The cell side is the median length of the 6 base-mesh
  edges nearest the point, measured before the pull and the cut. With the tips and turns kept, on
  the 480-trace box grid every one-piece fault lies within 0.172 cells of its trace, or at 1.25 or
  more (150-degree hairpins that lose an arm), so half a cell sits in a gap.
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
  faults once the tips kept their vertices. With the turns kept too, faults more than 10 % off
  among those added fell from 22 to 13.
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
- **Faults development places today, from keeping the turns.** 13 of 232 change, each by one
  vertex. Their median error against the one-cell reference falls from 14 % to 3.8 %. Three look
  worse against that reference. Solved on meshes 2 and 4 times finer:
  - one is in fact much better (29 % to 3.8 % above the converged slip; the reference itself is
    26 % high);
  - one is worse, 3.8 % to 12 %. This is the coarse mesh's error at a 90-degree corner, which the
    old corner cut of 0.35 cells partly cancelled. The cells near the turn are sound (smallest
    angle 23.9 degrees).
  - one does not converge cleanly, and both orders lie inside its spread.
- **Known, not fixed here:** a 150-degree hairpin sampled finer than a third of a cell gives wrong
  slip whatever the pull order (+74 % on the regular box). On the irregular box one is now added
  at +83 % that was refused by distance before. It is tracked separately.

## Tests
- **test_0897** (tier B): cases labelled by hand for each refusal (no facet, short chain, two
  pieces, chain ending off a tip, a turn off the chain, a label merely named like a slit). The two traces of the original report are now split whole,
  a trace sampled half a cell apart keeps both tips, and a 120-degree kink keeps its turn. The tip
  and turn cases fail before their fixes, 0.5 cells off.
- **test_0898**: the chord across a kink is labelled whole, and no hairpin edge is labelled.
- **test_0899**: the flat-cell refusal fails with the guard disabled.
- **tests/parallel/test_0897 (parallel)**: one outcome and one message on every rank, with
  add_fault both gathered onto one rank and distributed; a chain across the partition is one
  piece; a stray end on a seam is refused.

Fault, conforming-surface and line-cut suites: 433 passed, 1 skipped, serial. The round-1 code ran
at 2-4 ranks on a Linux workstation (180 runs, identical messages on every rank). The parallel test
and the later commits are still to be run there.

Underworld development team with AI support from Claude Code
