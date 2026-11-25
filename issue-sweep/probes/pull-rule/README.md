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

## Row 29 follow-up (2026-11-26): refinement reference, guard check, cost

### (1) Refinement: max slip, sheared box, frictionless fault, trace sampled at one cell
The four traces have fixed geometry (6/12 long), on irregular boxes of 12, 24, 48 and 96 cells a
side (`refine29.py`, `ref_dev.jsonl` and `ref_sharp.jsonl`).

| trace | N | development | light + sharp |
|---|---|---|---|
| 0 (line) | 12 / 24 / 48 / 96 | 0.142238 / 0.141118 / 0.140109 / 0.140014 | 0.141536 / 0.141207 / 0.139955 / 0.140052 |
| 1 (arc) | 12 / 24 / 48 / 96 | 0.121347 / 0.121105 / **0.074992** / 0.120290 | 0.121390 / 0.121105 / 0.120359 / 0.120335 |
| 2 (line) | 12 / 24 / 48 / 96 | 0.111159 / 0.109895 / 0.109820 / 0.109328 | 0.110946 / 0.110000 / 0.109991 / 0.109323 |
| 3 (arc) | 12 / 24 / 48 / 96 | 0.167323 / 0.167023 / 0.165926 / 0.165642 | 0.164868 / 0.167095 / refused / 0.165631 |

- **Same limit.** At N = 96 the two rules agree to about 1e-4 relative on all four traces.
- **Accuracy at the working resolution (N = 12):** both are within 0.5-1.7 % of the N = 96 value.
  The light rule is closer on three of the four traces, and on trace 3 it is 0.5 % low against
  development's 1.0 % high.
- **Development gave a wrong answer silently:** trace 1 at N = 48 has slip 0.0750 against about
  0.120 (38 % low), with no error. That is a silent partial fault, the defect UNFILED 68 refuses
  and the labelling fix removes.
- **One new refusal under the light rule:** trace 3 at N = 48, "the cut did not converge in 12
  passes". It is refused, not wrong.

### (2) The 5 sharp-turn regressions are refused, with a message
All five are `add_fault: the cut along 'F' misses part of the trace: ...` (four at 150 degrees,
one at 120). None comes back silently. A scan of every labelling-build record found 22 results
that came back from add_fault while my probe's check called them partial: their trace-to-chain
distance is 0.500-0.568 of the NOMINAL cell (1/12). The guard's own tolerance is half the mean
edge length near the trace, which includes the diagonals and comes to about 0.59 nominal cells
here, so they pass it as specified. This is not a gap, but the guard's "half a cell" is looser
than the nominal cell; tightening it (the median, or the shortest side) is a question for the
row.

### (3) Cost: the iteration rise is the mesh quality
- **Smallest angle in the faulted mesh** (`min_angles`): development 12-39 degrees; light + sharp
  4-7 degrees. Without a vertex on every sample, the cut's crossing points sit close to existing
  vertices and leave slivers.
- **Velocity iterations at N = 12 / 96:** development 26-29 / 78-82; light + sharp 33-42 /
  148-191.
- **A remedy, measured** (`ref_snap.jsonl`, traces 0 and 2, N = 12-48): the cut's own snap,
  `snap_frac`, raised from 0.1 to 0.3, restores the angles to 15-24 degrees and the iterations to
  29-63 (development 26-50). The slip moves by under 0.3 %.

| snap_frac | min angle (deg) | velocity its N = 12 / 24 / 48 |
|---|---|---|
| 0.1 | 5.3-11.3 | 34-36 / 61-64 / 89-108 |
| 0.2 | 8.1-24.2 | 28-36 / 52-55 / 74-83 |
| 0.3 | 15.7-24.2 | 28-29 / 36-38 / 46-63 |

The row's candidate is therefore the light + sharp pull WITH snap_frac 0.3 for add_fault. The
effect of snap_frac 0.3 on development's rule, on add_conforming_surface, and on the 360 kink
and 120 line traces is not yet measured.

## Row 29, the snap_frac measurements (2026-11-26)

### (2) add_conforming_surface
It has its own `snap_frac` argument with its own default (0.10). A change to add_fault's default does
not touch it, so that path is unchanged by the row.

### (1) and (3) The hunt: 120 lines+arcs and 360 kinks, both meshes, spacings 1.0 / 0.5 / 0.3 cell
"refused" counts add_fault raising; "returned partial/empty" counts a result that came back from
add_fault but misses part of the trace by the probe's nominal-cell check (on development there is no
guard).

| family | dev (snap 0.1) | dev + snap 0.3 | light+sharp (snap 0.1) | light+sharp + snap 0.3 |
|---|---|---|---|---|
| lines+arcs | 51 complete / 50 refused / 19 returned partial or empty | 51 / 50 / 19 | 120 / 0 / 0 | 120 / 0 / 0 |
| kinks | 181 / 95 / 84 | 179 / 96 / 85 | 305 / 52 / 3 | 304 / 53 / 3 |

The 3 "returned" under light+sharp are the guard-tolerance borderline cases (0.50-0.57 nominal
cells).

- Kinks complete by turn, of 60: at 10-90 degrees, dev 25-37 and light+sharp 60, with or without
  snap. At 120, 28 / 27 / 45 / 44. At 150, 21 / 20 / 20 / 20.
- Traces that place on development (232), still complete: dev + snap 0.3 230; light+sharp 227;
  light+sharp + snap 0.3 226.
- **So snap 0.3 alone changes little in the hunt; the pull rule is what changes the outcomes.**

### Refinement at snap 0.3 (four traces, N = 12-96): max slip, velocity iterations, smallest angle
- **dev + snap 0.3 is identical to dev at snap 0.1** on traces 0, 1 and 3 up to N = 48 (the snap
  never fires there). Small changes elsewhere (trace 2 N = 24: 0.109876 against 0.109895). It still
  gives the silent 0.0750 at trace 1, N = 48.
- **light+sharp + snap 0.3:**
  - iterations at N = 12 / 96 are 27-33 / 73-112, against development's 26-29 / 69-82 and
    light+sharp at snap 0.1's 33-42 / 148-191;
  - smallest angles in the solved meshes are 14-37 degrees;
  - slips agree with the other modes' limit to about 1e-4 at N = 96;
  - trace 3 at N = 48, refused at snap 0.1, places at snap 0.3 (0.166138).

### A blocker found: the light+sharp rule leaves ZERO-AREA cells at sharp turns
In the kink hunt, 5 results that add_fault returned as complete hold a cell of area 1e-17 to 3e-16
cell^2, with a smallest angle of 0 degrees. All are at 90- and 120-degree turns, and they are the
same 5 at snap 0.1 and at 0.3 (`flat.jsonl`). Development's every-sample rule produces none at
either snap setting (0 of about 330 results, `flat_dev.jsonl`). The cut refuses an INVERTED cell
but not a flat one, so these come back silently. A flat cell gives the finite-element map a zero
Jacobian, so a solve on such a mesh cannot be trusted. None of the refinement study's solved meshes
has one; the smallest angle there is 4 degrees or more.

So, as measured, the row is not ready. Either the cut refuses a degenerate cell (area below a
stated fraction of h^2, alongside its inverted-cell check), which would turn these 5 into
refusals, or the sharp-turn keep is changed so that it does not produce them. The first is a
guard the cut needs anyway: any pull rule could reach it.
