# UNFILED 84: 150-degree hairpins at fine sampling give wrong slip

Measured on labels70-22 0007 (today's pull rule with the tips and turns kept), `hp84.py`. For each
kink trace: max slip at 12 cells per side against the same trace at 48 (the converged value), and
the geometry at the apex:
- cells with a vertex on each arm;
- cells with all three vertices on the chain;
- the smallest angle among the cells at the apex.

## What happens to the 150-degree hairpins (40 traces: both boxes, samplings 0.5 and 0.3)
- **32 are refused:** in two pieces, ending off a tip, or with an inverted cell.
- **8 are added.** Three have a converged reference: box_irr kink150_3 at 0.3 is +60 %, box_reg
  kink150_3 at 0.3 is +57 %, and box_irr kink150_5 at 0.5 is +11 %.
- **The 48-cell mesh refuses most of them too,** so few have a reference.

## What separates them so far
Cells with all three vertices on the chain are wedge cells between the two arms near the apex,
every node a split node:

| Kink | Faults added | Such cells per added fault | Error against refinement (12 cells) |
|---|---|---|---|
| 150 degrees | 8 | 3-4 (all of them) | +60 %, +57 %, +11 % |
| 120 degrees | 14 | 0-2 (one fault with 3, no reference) | −11 % to +14 % |
| 90 degrees | 11 | 0-1 | −5 % to +15 % |

The 90- and 120-degree errors are the 12-cell mesh's discretisation at a corner. Hypothesis: a
run of three or more wedge cells, each made entirely of split nodes, leaves the apex region
kinematically loose, and the slip there is too large.

**The evidence is thin:** only three judged hairpins, and one of them only 11 % off. Before any
guard:
- solve more hairpins against refinement, at 140, 150 and 160 degrees, on finer bases so that the
  48-cell reference is not refused;
- test the mechanism directly: does one wedge cell made entirely of split nodes move as a rigid
  block between the two slit faces?
A count threshold ("three wedge cells") would be a special case, so it is not proposed.

## The mechanism (hub's test (b); `wedge84.py`, `apex84.py`)
- **The wedge cells are NOT the cause.** In box_reg kink150_3 at 0.3 the three wedge cells strain
  at 0.41-0.53, against 0.69 for the other cells near the apex. That is somewhat stiffer, but not
  a rigid block. In the sound 120-degree contrast (box_irr kink120_9) the wedge cells strain MORE
  than their neighbours.
- **The error sits at ONE point, the apex pair.** At 12 cells per side the largest slip is at the
  apex itself, 0.134; at 48 the largest is 0.086, 1.07 cells away, and the apex slips nearly
  zero (the 12/48 ratio there reaches 19). Beyond a cell from the apex the profiles agree (median
  ratio 0.97 at 1-2 cells, 0.80 at 2-3).
- **The cause is the apex's single constraint normal.**

  | Pair near box_reg kink150_3's apex | Jump along its own normal | Along arm-in normal | Along arm-out normal |
  |---|---|---|---|
  | the apex (normal 77 / 47 degrees from the arms' normals) | −1.35e-17 | **−0.131** | **+0.098** |
  | 0.47 cells away (normal on one arm) | −2.6e-18 | 0.000 | −0.018 |

  The strong constraint holds the jump to zero along that ONE normal. The arms' normals are 150
  degrees apart, so the apex opens against each arm, and that opening becomes the fault's largest
  "slip". In the 120-degree kink the apex opens too (0.056 along one arm's normal), but its
  largest slip falls elsewhere.
- **A principled fix:** at a turn vertex, hold the jump to zero along BOTH arms' normals. In 2-D
  that pins the apex pair (zero jump), which is what refinement shows. This is a change to the
  rotated fault constraint (`utilities/rotated_bc.py`), so a solver decision for Louis, not part
  of the labelling patches.
