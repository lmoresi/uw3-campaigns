# UNFILED 70: Mesh.add_conforming_surface's cut can be empty or partial, and it says nothing

Development fbef72fa + UNFILED 68's check (as a classifier), serial, macOS (12-core Apple M4).
`conf70.py` runs 10 straight lines and 10 gentle arcs (turn up to 1 rad over 1.6, crossing a unit
box wall to wall), forward and reversed, through `add_conforming_surface`, and classifies the
child's label with 68's check. Only the part of the trace inside the box counts. No arc leaves and
re-enters.

| mesh | spacing | complete | partial | empty |
|---|---|---|---|---|
| irregular 1/12 | 1.0 cell | 22 | 18 | 0 |
| irregular | 0.5 | 20 | 20 | 0 |
| irregular | 0.3 | 20 | 16 | 4 |
| regular 1/12 | 1.0 | 20 | 20 | 0 |
| regular | 0.5 | 20 | 18 | 2 |
| regular | 0.3 | 20 | 10 | 10 |

The straight lines are complete at every spacing. The arcs are partial, or empty, at every spacing,
even at one cell.

Traces that end inside the mesh are refused by design ("N triangle(s) are entered but not left"),
but at 0.3 cells 2 of 40 such traces came back empty instead.

## Root cause (shared with UNFILED 22)
`look70.py`, an arc of turn -0.08 rad on the regular box at 1-cell spacing: the cut split 14 edges
but labelled 5, and the last 8 cells of the trace have no labelled edge. add_conforming_surface does
not put vertices on the samples, so every sample inside a cell is a kink in the polyline. The cut
edge across that kink joins two crossing points on different segments: a chord, whose midpoint is
off the polyline. `_label_cut_edges` labels an edge only when both ends AND its midpoint lie on the
line, so it drops every such chord. The rule was meant to keep out edges joining non-consecutive
points across a turn; it also drops the legitimate edge across a kink within a cell. add_fault
hides most of this by pulling a vertex onto every sample (the kinks become vertices), at the cost
of the snap problems of UNFILED 22.

A rule to measure for the root cause: label an edge when both ends are on the line and they are
CONSECUTIVE along it, by arc-length parameter, rather than requiring its midpoint on the line.

## Recommendation on order
Adding 68's refusal to add_conforming_surface now would make every curved conforming surface raise
(the arcs above are partial even at one cell). Six test files and three docs pages use the method.
Fixing the labelling first (UNFILED 22's root cause), and then adding the refusal as a guard,
changes no correct result and refuses only what remains wrong.
