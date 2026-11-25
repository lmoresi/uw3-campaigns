# add_fault's pull rule under the labelling fix: measurement for a register row (nothing built)

Builds: development fbef72fa ("dev"), and the labelling fix 44aa8c53 (branch
bugfix/cut-labels-chords-across-kinks). Modes on the latter:
- new_all: every sample pulled (today's rule);
- new_light: the tips and the turns above 45 degrees pulled;
- new_light_sharp: new_light, plus every sample within 1.5 cells of a turn above 90 degrees.

The pull rule is changed from the probe (`corners_plugin.py`, applied to add_fault's call only).
Serial, macOS (12-core Apple M4), irregular and regular 1/12 boxes, sample spacings of 1.0, 0.5
and 0.3 cells. Families:
- lines+arcs: 20 traces, 6 cells long;
- kinks: two arms of 2.5 cells, with a turn of 10-150 degrees, 10 of each.

Full tables are in `pull_report.md`; the raw records are in `pull_*.jsonl`.

## Outcomes, complete of 120 (lines+arcs) and of 360 (kinks), summed over meshes and spacings
| family | dev | new_all | new_light | new_light_sharp |
|---|---|---|---|---|
| lines+arcs | 51 | 76 | 120 | 120 |
| kinks | 181 | 209 | 306 | 305 |

Kinks by turn, complete of 60:

| turn | dev | new_all | new_light | new_light_sharp |
|---|---|---|---|---|
| 10-90 | 25-37 | 31-46 | 60 | 60 |
| 120 | 28 | 32 | 45 | 45 |
| 150 | 21 | 21 | 21 | 20 |

So a 150-degree hairpin is no worse than development under either light rule (21 against 21, and
20 with the sharp keep).

## Traces that place on development (232): what changes
- new_all: 224 still complete; cells and moved vertices identical; slips identical (bit for bit,
  all 13 solves). The labelling fix alone changes nothing that worked.
- new_light: 209 still complete, 23 not, all at 120- and 150-degree turns ("an edge crossed more
  than once", or partial). Cells differ in 208 (by up to 24); base vertices moved per trace fall
  from 6.1 to 3.3.
- new_light_sharp: 227 still complete, 5 not. Cells differ in 190.

## The answer: max fault slip in a sheared box with a frictionless fault (13 traces)
Under the light rules the slip is the same whatever the sample spacing (la0: 0.141536 at 0.5 and
1.0 cell; la2: 0.110946 at both). Under development's rule it depends on the spacing (la0:
0.141337 and 0.142238; la2: 0.102970 and 0.111159). The differences from development, -1.5 % to
+7.7 % (la2 at 0.5 cell), are mostly development's own sampling dependence: pulling a vertex onto
every sample makes the mesh, and so the answer, follow how finely the user sampled the trace.
Neither result has been checked against a converged reference. A refinement study would say which
is closer.

Velocity iterations rise on the irregular box under the light rules (21-24 -> 26-32), and are mixed
on the regular box (one case 25 -> 46). They are bounded and converged.

## For the row
- The candidate is new_light_sharp: tips, turns above 45 degrees, and every sample within 1.5
  cells of a turn above 90 degrees.
- It fixes add_fault on finely sampled traces (lines+arcs 51 -> 120 of 120 complete), makes the
  answer independent of the user's sampling, and keeps 227 of 232 of today's working traces (the 5
  are 120-150-degree turns).
- It changes the mesh, and the slip by up to ~8 %, for traces that place today.
- Open before Louis decides: a refinement reference for the slip, and the 5 sharp-turn
  regressions.
