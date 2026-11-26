# UNFILED 70 and 22: the cut labels its edge across a kink inside a cell (with 68's refusal as the guard)

Base: development fbef72fa. Nine commits, as `git format-patch` files. Not pushed.
- 0001 (d37db66e) is UNFILED 68: add_fault refuses a cut with no facet, or one that misses part
  of the trace. It is reviewed on its own.
- 0002 (44aa8c53) is the labelling fix, plus 68's refusal on add_conforming_surface.
- 0003 (911a7b16) is UNFILED 72: the cut refuses a flat cell (see the 72 section).
- 0004 is review round 1 (see its section).
- 0005 is review round 2 (see its section).
- 0006 keeps a vertex on each tip and requires the chain to end on them (see its section).
- 0007 keeps a vertex on each turn and requires the chain to pass through it, with review round 3 (see its section).

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

## Review round 1 (Linux server: changes requested), commit 0004
1. HIGH, parallel hang: every array reduction is in-place `comm.Allreduce` (the distances under
   MIN, the inside mask under MAX, the local-size reductions). The remaining lowercase reductions
   are on scalars and tuples. Not run in parallel here; np 2-4 is the review's.
2. Tolerance: half the LOCAL median edge length at each trace point. On the irregular box the local
   median is about 1.25 nominal cells. kink120_1's worst gap (0.541 nominal = 0.43 local cells)
   therefore passes the distance test. It is refused by the new topological check: one polyline
   must cut to ONE connected chain, counted globally (gathered edges joined at coordinate-keyed end
   points, so a chain across a seam counts once). It defers to the split's touching-junction refusal
   when an earlier slit cut it.
   - The defect it exposed on development: the split splits one fragment and leaves the other
     labelled but unsplit, and add_fault returns no error. In kink120_1 the Plus and Minus chains end
     2.2 cells short of the trace (`dbg_split2.py`). On development's build, 101 of 265 returned
     sharp-kink faults were in 2-3 pieces (`dev_pieces.jsonl`). Every trace the check refuses was in
     pieces on development.
3. Lows:
   - add_conforming_surface's refusal gives surface advice;
   - 72's message no longer asks for a sample at an existing one;
   - 72's loop is vectorised;
   - the 120-degree comment is corrected;
   - test_0897 gains a two-pieces hand-labelled case, which only the piece count refuses.
     (Corrected in round 2: the trace cases are NOT refused by the piece count. Both are one
     chain; the distance refuses them, at 0.9 cells (the empty case) and 0.6 cells (the short case).)
Suites: 431 passed, 1 skipped.

## Review round 2 (Linux server: changes requested), commit 0005
1. Medium, tolerance:
   - h is now the median length of the 6 BASE-mesh edges nearest each trace point (by midpoint).
     The base is the mesh before the pull and the cut, so neither the gap being judged nor the
     cut's own short edges (low 3) can move it.
   - Collective: each rank offers its 6 nearest OWNED edges (owned by `createPointNumbering`),
     and every rank takes the same 6 nearest, ties broken by global point number.
   - The fraction is the named constant `_COVERAGE_FRACTION`, kept at 0.5. The numbers below say
     why: no measured distribution has a gap.
2. The piece join is keyed by global vertex number, not coordinates, so an earlier slit's
   coincident vertices stay apart.
3. Low 3 follows from (1).
4. New parallel test `tests/parallel/test_0897_add_fault_refusal_agrees_across_ranks_parallel.py`:
   - refused and added traces give one outcome and one message on every rank;
   - a hand-labelled chain across the distributed box is one piece, and the same chain with one
     edge out is "2 pieces" on every rank.
   - Not run here (no MPI on the laptop).
5. The round 1 text on the short case is corrected above.

### The threshold measurement (`cover.py`, the 480-trace box grid)
For each fault, the refusal was patched to record instead of raise, keeping: the pieces, the worst
trace-to-chain distance (in base k=6 cells), and the frictionless-fault max slip against the same
curve sampled one cell apart (the reference counts only when it is one piece within 0.25 cells).

- **Today's pull rule** (every sample pulled; `cover_box_*.jsonl`): 164 one-piece faults have a
  reference, 109 of them within 10 % and 55 off by more. There is no gap.
  - The sound faults' worst distance reaches 0.94 cells (quantiles 50/90/99 %: 0.13/0.52/0.65).
  - The bad faults' starts at 0.000 (quantiles 50/90 %: 0.50/0.94).
  - Three bad faults lie exactly on their trace and are still 10-18 % off: the pull's cell
    distortion moves slip without any coverage fault (register row 29).
- **Row 29's rule, emulated in the probe** (`ROW29=1`, `cover29_box_*.jsonl`):
  - sound faults reach at most 0.313 cells (99 %: 0.146);
  - eight bad faults lie at 0 (kinks of 90 and 150 degrees, off for another reason), and the
    rest run from 0.271 to 0.624;
  - 0.35-0.43 would separate them here, but 38 of today's 109 sound faults lie above 0.4. It is
    not a threshold for today's rule.
- **Geometry, which depends on no pull rule** (`GEOM=1`, `coverg_box_*.jsonl`): each chain edge's
  ends are projected onto the trace's arc length, the intervals are joined, and the gaps are
  measured in base cells.
  - No fault has an interior gap; every uncovered stretch is at a tip. Corner cuts project as
    covered and are left to the distance.
  - The tip shortfalls fall at whole sample spacings: 0.31 and 0.625 cells at sampling 0.3, 0.5
    at sampling 0.5. So the empty band at 0.40-0.45 belongs to the sampling grid, not to the faults.
  - Slip does not split at it either: the 0.45-0.60 band holds 26 faults within 10 % and 15
    outside.
- **Choice (hub's rule when no gap exists):** keep 0.5, keep the piece check for the split chains,
  and state the residual risk. (Superseded by 0006, which removes the tip shortfalls; the numbers
  below are 0005's.) At 0.5, 252 of the 321 one-piece faults are added. Of those, 36
  stop short of a tip, by at most 0.50 cells:
  - shortfalls up to 0.4 cells: slip error median 10 %, 12 of 21 above 10 %;
  - shortfalls of 0.4-0.5 cells: slip error median 5 %, 1 of 13 above 10 %;
  - no shortfall: median 1.4 %, 13 of 77 above 10 % (the distortion).
  This is stated in add_fault's docstring (Raises) and in the PR body.

## 0006: the tips keep their vertices (hub, after round 2's geometry)
Every one of the 36 tip-short faults was short at the START of the trace, by one sample spacing.
`tip_dbg.py` on box_reg, sampling 0.5, la3 shows the mechanism:
- sample 0 (the tip) and sample 1 chose the same vertex, and `pull_vertex_onto` gives it to the
  later target;
- the tip ended 0.5 cells from any vertex, and the cut's first segment began at sample 1.
At the end of a trace the tip is the later target of its pair, so it always won there.
test_0897's "empty" and "short" traces of UNFILED 68 were this defect too.

The fix, in add_fault:
- the tips are pulled after the other samples;
- their vertices are labelled `UW_FaultTip` (the pull writes the tip's own coordinates, matched
  exactly; the cut carries the label);
- the chain's ends, joined globally by vertex number, must be those vertices, or the cut is refused.
  This is exact, by mesh point, with no tolerance.

On the grid (`cover6_box_*.jsonl`):

| | 0005 | 0006 |
|---|---|---|
| one-piece faults refused by distance | 69 | 20 |
| median slip error (judged) | 5.0 % | 2.0 % |
| sound faults' worst distance (99 % / max) | 0.645 / 0.94 cells | 0.447 / 0.52 cells |
| added faults short of a tip | 36 | 0 |

- The 12 faults still short of a tip are 150-degree hairpins that lose a whole arm (2-4 cells).
  The distance (1.25-1.56 cells) and the end check refuse them.
- The distance keeps 0.5 for the corners. Bad faults still start at 0 there, from the pull's cell
  distortion (row 29).
- Suites: 432 passed, 1 skipped.

### The size of 0006's change on faults development places today (`order0006.py`)
The pull is the same function on development and 0006, and the cut is deterministic once the pull
is done. So a mesh changes exactly when the two target orders pull a different vertex set.
- **Whole grid:** 167 of 480 meshes change (sampling 0.3: 101, 0.5: 64, 1.0: 2). Each differs by
  ONE vertex: the tip's vertex in place of the neighbouring sample's.
- **Development-placed faults** (complete on development, `pull_dev.jsonl`): 29 of 232 change
  (24 kinks, 5 lines/arcs; sampling 0.5: 16, 0.3: 13). All 29 are still added.
- **Slip, 0005 to 0006** (same labelling; only the order differs):
  - median change +5.5 %; 90 % of changes within 17 %; the largest 26 %; 20 up, 9 down;
  - against the one-cell reference (25 with one): |error| median 9.5 % to 2.3 %; faults off by more
    than 10 %: 12 to 3. Better in 16, worse in 9.
  - Worse by more than 2 points: six faults. Five are kink30s, which move from 0.2-5 % to 3-9 %
    error. The sixth is kink150_3 at sampling 0.3, off already (68 % to 75 %).

## 0007: the turns keep their vertices; review round 3
**The corner gap was 0006's defect one level up** (`turns-last-measurement/k1202.py`). kink120_2's
turn sample lost its vertex to its later neighbour, so the chain cut the corner by up to half a
cell and the slip was 33 % low. A check that the chain passes through every pulled vertex could
not see this, because the turn was never marked (`thru*_box_*.jsonl`: it refused nothing on
either rule).

**The fix:**
- add_fault pulls plain samples first, then turns over `_TURN_DEG` = 45 degrees, then the tips;
- the turns' vertices are labelled `UW_FaultTurn` by exact identity;
- the chain must pass through them (global, by vertex number).

**Measured** (`ord6_*`, `ord29_*`, `order7_*` in `turns-last-measurement/`):

| | today's rule (0006 → 0007) | row 29 (current → turns last) |
|---|---|---|
| kink120_2 | 0.5 → 0 cells, slip −33 % → −3.2 % | the same |
| bad faults among those added | 22 → 13 | 21 → 9 |
| median slip error | 1.69 % → 1.50 % | 0.23 % → 0.20 % |
| outcomes changing class | none | 4 now refused: 3 wrong before, caught by the cell guards; the 4th unusable before too, now refused for a single facet |
| added faults with a turn off the chain | 30 → 0 | 20 → 0 |

- **The coverage distance now has a gap.** Every one-piece fault lies within 0.172 cells of its
  trace, or at 1.25 cells or more (150-degree hairpins that lose an arm). Half a cell sits in the
  gap: 2.9 times above the largest added, 2.5 times below the smallest refused. The two verdicts
  that were round-off (kink120_2 and kink120_3 at 0.4999999999997) are both gone.
- **Development-placed faults whose mesh changes:** 13 of 232, each by one vertex (all kinks;
  sampling 0.5: 5, 0.3: 8). All 13 are still added.
  - Slip change: median +10 %, 90 % within 44 %.
  - The largest change is box_reg kink150_6 at 0.5. On development it is a half-split fault (two
    pieces, slip 0.0036 against a reference of 0.101). 0006 refuses it; 0007 splits it whole at
    0.0999.
  - Against the one-cell reference (9 with one), the median error falls from 14 % to 3.8 %, and
    faults off by more than 10 % from 5 to 2.
  - Worse by more than 2 points: box_irr kink90_1 at 0.5 (2.7 → 5.0 %), box_irr kink90_9 at 0.3
    (2.2 → 17.8 %), box_reg kink60_2 at 0.3 (1.2 → 4.0 %).
- **Caveat (UNFILED 84, not this patch):** 150-degree hairpins at sampling 0.3 give wrong slip
  whatever the order (box_reg kink150_3: +74 % under both). On the irregular box 0007 adds one
  that 0006 refused by distance (+83 %).

**Review round 3 (Linux workstation, changes requested):**
1. The end check was partition-dependent. The edges are now gathered and counted ONCE
   (`{tuple(sorted(e)) ...}`), for the pieces, the ends and the turns. The parallel test adds a
   stray end on a seam; it fails at np 2 without the fix (the reviewer's run).
2. Round-off at 0.5: removed by the turn fix, as measured above.
3. Lows:
   - the tip and turn labels are removed after use;
   - slits are matched to the exact side labels of the faults already split into the mesh
     (`_fault_point_pairs`), and a test shows a 'UserPlus' label no longer disables the checks;
   - a failing check beside a slit is returned and raised after the record check and the split,
     so a 3-piece chain across a slit is refused, with test_1174's junction messages kept;
   - the parallel test also runs add_fault distributed (`partition=False, across_seams=True`) and
     catches every exception before its gather;
   - "half" replaces "0.5 of".

Suites: 433 passed, 1 skipped. On one rank, all 12 cases of the parallel test pass, called
directly; np 2-4 is for the reviewer.

### The three faults 0007 made "worse": the yardstick, and discretisation (hub's question)
The one-cell reference is the same trace sampled a cell apart on the same 1/12 mesh. For these
faults it is not converged, so each was also solved on finer meshes (12, 24 and 48 cells per side,
the same trace; `kref.py`, `k909ref.py`). Cells were compared under both orders (`k909.py`,
`k901.py`).

| Fault | 0006 slip | 0007 slip (0.5 / 0.3) | one-cell ref | converged | Smallest angle near the turn (0006 → 0007) |
|---|---|---|---|---|---|
| box_irr kink90_9, 0.3 | 0.0589 (corner cut 0.28 cells) | 0.04748 / 0.04736 | 0.0576 | 0.0456 (12/24/48: 0.04736, 0.04583, 0.04561) | 24.3 → 25.8 deg |
| box_irr kink90_1, 0.5 | 0.0903 (corner cut 0.35 cells) | 0.0975 / 0.0977 | 0.0928 | about 0.087 (12/24/48: 0.0975, 0.0866, 0.0874) | 28.2 → 23.9 deg |
| box_reg kink60_2, 0.3 | 0.0987 | 0.0936 | 0.0975 | not converged (0.0936, 0.1028, 0.0958) | — |

- **kink90_9 is not worse; it is much better.** 0006 was 29 % above the converged slip and 0007
  is 3.8 % above it. The one-cell reference is itself 26 % high, which is what made 0007 look 18
  points worse.
- **kink90_1 is worse against the converged slip** (3.8 % to 12 %), but not from distortion:
  - no cell near the turn is under 15 degrees, and the snap moves nothing more;
  - under 0007, samplings 0.5 and 0.3 agree to 0.2 %, both exactly on the trace;
  - the 12 % is the 1/12 mesh's discretisation error at a 90-degree corner. 0006's fault cut the
    corner by 0.35 cells, which shortens it and partly cancelled that error.
- **kink60_2** does not converge cleanly over 12/24/48. Both orders lie inside that spread, so
  there is no verdict.
- **None is a defect.** "Worse against the one-cell reference" is an unreliable verdict wherever
  that reference cuts or rounds a corner itself.

## 0008: docstring caveat (text only)
add_fault's Notes say the slip reported at a sharp turn's apex can be spurious (one constraint normal there; UNFILED 84 mechanism, register row 30 proposed), and to read slip more than about a cell from a sharp turn.

## 0009: review round 4 (Linux workstation; library clean, the test changed)
1. The parallel test's distributed cases now accept the split's refusal of a chain running ALONG
   a seam ("a fault facet lies ON the partition seam"), asserting agreement across the ranks.
2. The stray end sits on an edge that the ACTUAL partition gives to two ranks (from the point
   star-forest; the test skips at np 1). The kink case asserts, reduced over the ranks, that the
   turn is a vertex of the chain. Both are meant to fail on 0006 at np 2; that is the reviewer's
   run.
3. `marked_vertices` reduces `hasLabel` over the ranks before its gather (a hang when a label was
   on one rank only).
4. A chain cut beside both side labels of a fault the mesh does not record as split (a reloaded
   mesh) is refused as a crossing of that fault (`test_a_crossing_of_an_unrecorded_fault_is_named`).
   test_1174's JUNCTION pattern is now the split's own message.

Suites: 435 passed, 1 skipped. On one rank the parallel test's functions pass, called directly
(the seam case skips).
