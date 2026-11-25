# UNFILED 22: what breaks add_fault's cut on finely sampled traces (measurement, no change built)

Development fbef72fa, serial, macOS (12-core Apple M4). `add_fault` (2-D, and the sphere sheet)
pulls a mesh vertex onto EVERY control point (`pull_vertex_onto`) and then cuts along the whole
polyline (`cut_along_lines`). The row's diagnosis was that WHICH of two consecutive points keeps a
shared vertex decides the cut. The measurements say otherwise.

## The hunt (`hunt.py`, 60 random smooth traces per mesh, each forward and reversed, so 120 cuts per mesh)
The traces are 2-4 cells long, sampled every 0.3-0.7 cells (so the samples share vertices), on an
irregular box (1/12), a regular box (1/12) and an annulus (0.1).

| which samples get a pulled vertex | failed cuts, irregular / regular / annulus |
|---|---|
| every sample (development) | 14 / 32 / 10 (all "snapping inverted cells") |
| the two tips only | 0 / 0 / 0 |
| none | 116 / 116 / 106 (the tips need their vertex) |
| tips + turns above 45 deg | 0 / 0 / 0 |
| tips + 45 deg turns + samples >= 1.0 cell apart ("thin 1.0") | 0 / 2 / 0 |
| tips + 45 deg turns + samples >= 0.7 cell apart | 1 / 6 / 0 |

Under development's rule, failures occur with NO shared vertex (two traces of the first sweep),
and every failing trace fails both forward and reversed, although reversing it swaps which point
is "later". The owner of a shared vertex is not the cause; pulling many closely spaced samples is.

## Sharp turns (`kink.py`, two arms of 2.5 cells, 20 traces per angle, irregular box), ok/fail
| turn | tips | tips + corner | every sample (dev) | tips + 45 deg rule |
|---|---|---|---|---|
| 10 | 20/0 | 20/0 | 15/5 | 20/0 |
| 30 | 20/0 | 20/0 | 18/2 | 20/0 |
| 60 | 19/1 | 20/0 | 15/5 | 20/0 |
| 90 | 15/5 | 20/0 | 20/0 | 20/0 |
| 120 | 10/10 | 19/1 | 14/6 | 19/1 |
| 150 | 7/13 | 13/7 | 17/3 | 13/7 |

A sharp turn needs its own vertex, as add_fault's comment says. At a 150-degree hairpin,
development's every-sample rule does better than any thinned rule (17 against 13). That case
is hard for all of them.

## The suite (`corners_plugin.py` applied to add_fault's call only; 38 fault test files)
- Development: 417 passed.
- Tips + 45 deg turns: 4 failures.
  - test_0559's sphere fault, forward and reversed, and test_1092's membrane test fail with
    DMPlexComputeGeometryFVM error 77 (a degenerate cell after the cut on the sphere manifold).
  - test_0847's analytic-normal smoothing assumes every sample carries a vertex.
- Thin 1.0 and thin 0.7, on the sphere-sheet set (test_0559, test_1092, test_1079, test_0847):
  16 of 18 pass. The 2 failures are test_0559's two cases, which assert that the shared-point
  warning is raised, and with thinning nothing is shared. They are a premise of the test, not a
  broken cut.

## What a rule would change, and what it would not
The cut still follows the user's full polyline: only the choice of which samples become mesh
vertices changes. An unpulled sample lies on the cut but is not itself a vertex. Not yet measured:
how far an unpulled sample is from the nearest vertex of the cut chain (C1's stated-distance
condition), and the refusal of a feature sample a rule would drop. Thinning as written keeps every
turn above 45 degrees, so it drops no corner.

Proposal for C1 to rewrite the row: the defect is "add_fault pulls every control point, and pulled
samples closer than a cell distort the mesh until the snap inverts cells" (8-27 % of finely sampled
traces). It is not the owner of a shared vertex. Candidate rule: pull the tips, the turns above a
threshold, and samples at least about a cell apart. Acceptance: the hunt, the kink table, and the
sphere-sheet set. test_0559 needs its premise restated (the warning is for samples that share a
vertex, which a thinning rule removes).

## CORRECTION (2026-11-26, later): the first hunt measured the wrong thing
The tables above count cuts that did not raise. A cut that does not raise can still label almost
nothing: `_label_cut_edges` marks an edge only when both ends AND its midpoint lie on the polyline,
so a chord between two pulled vertices is not marked. End to end with `add_fault`, a fault can come
back with ZERO facets and no error. The "0 of 360" for the thinned rules is withdrawn.

End to end (`hunt3.py`): 20 smooth traces (lines and gentle arcs, 6 cells long, centred in a 1/12
irregular box), forward and reversed, so 40 add_fault calls per row. "complete" means the fault
chain lies within half a cell of every point of the trace; "partial" means it does not; "empty"
means add_fault returned a fault with no facet.

| sample spacing | development | thin (tips, turns > 45 deg, >= 1 cell) | tips + turns > 45 deg |
|---|---|---|---|
| 1.0 cell | 40 complete | 40 complete | 24 complete, 12 partial, 4 raised |
| 0.5 cell | 16 complete, 5 partial, 1 empty, 18 raised | 20 complete, 6 empty, 14 raised | 20 complete, 2 empty, 18 raised |
| 0.3 cell | 6 complete, 4 partial, 8 empty, 22 raised | 20 complete, 20 empty | 20 complete, 12 empty, 8 raised |

Straight-line control (`straight.py`): development is complete at spacings of 2 and 1 cell at both
angles tried, and refuses some orientations at 0.7, 0.5 and 0.3 cell (inverted snap, a
self-meeting label).

What this says:
1. A DEFECT on development, whatever rule is chosen: add_fault can return a fault with no facet
   and no error (1/40 at 0.5 cell, 8/40 at 0.3). It should refuse.
2. Sampling finer than about a cell degrades add_fault on development: 40, 16 and 6 of 40
   complete at 1.0, 0.5 and 0.3 cell.
3. No pull rule measured here fixes it. Thinning turns refusals into silent empty faults, and the
   exact 20s suggest the outcome depends on the trace's direction (the thinning measures spacing
   from the first sample). The cause of the empty and partial chains is in the cut's labelling of
   chords and in the snap, not in which samples are pulled.
The hairpin and before/after-solve measurements C1 asked for are moot until the rule question is
settled.
