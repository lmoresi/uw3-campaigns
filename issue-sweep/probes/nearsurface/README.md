# A fault ribbon refused when its top is a few cells below the surface

## The symptom

A slab model places a fault as a thin ribbon volume (`place_fault_ribbon_2d`, which calls
`place_thin_volume` in `src/underworld3/utilities/place_surface.py`) and splits the mesh
along it. On an annulus with 10 km cells near the trench, faults whose split top lay 13,
24, 67 and 400 km below the surface were placed, while tops at about 42 and 55 km
(3 to 6 cells down, at dips of 30 and 35 degrees) were refused with

    place_thin_volume failed on the surgery rank: RuntimeError: the ribbon's cavity
    reached the domain wall; the volume must be interior, with clearance to spare

A top within a cell or two of the surface reaches it and is placed as an outcrop; a
deep top is placed as an interior ribbon. Between the two there is a band of depths
where neither is possible. This probe reproduces the band on a small annulus, measures
where it starts and ends in cells, and shows that it scales with the cell size.

## The reproducer

`p_nearsurface_split.py` uses test_0865's fixture (an annulus of outer radius 1 built with
one refinement, a ladder ribbon placed with `place_fault_ribbon_2d`), with cellSize 0.05
(cells of h = 0.025 at the wall; measured wall edge 0.0249) and an inner radius of 0.4 so
the fault's lower end stays clear of the inner wall. Everything else is in cells: band
width 2 h, the trace sampled every h (7 points, so 6 h long), the default tip margin of
2 rings (the band runs 2 h past each end of the trace), the default clearance 0.3, and
`split=True`. The dip is measured from the local horizontal. Only k, the depth of the
trace's top below the outer wall in cells, varies; the dip and length are fixed.

For each k it prints the top depth (absolute and in cells), the depth of the band's
highest corner (the extended end raised by half the width; negative means the band
crosses the wall), and the outcome on every rank: placed as an outcrop (band cells touch
the outer wall), placed as interior, or refused, with the full message. Each log starts
with `underworld3.__file__`. A serial point takes 2 to 3 s at h = 0.025 and about 25 s
at h = 0.0125.

## How to run

`run.sh` holds the exact commands. It needs two environment variables:

- `ENV`: a script that, given `dev` or `u60`, activates the environment. Here `dev` is a
  clean install of development at fbef72fa, and `u60` is the same install with
  `place_surface.py` from the UNFILED 60 head (02f34664, patches 0001-0004; Python only)
  overlaid on a copy of it through `PYTHONPATH`.
- `UW`: an underworld3 checkout, for `scripts/mpi_supervisor.py`.

`bash run.sh serial` runs the four serial sweeps on both versions, `bash run.sh fine` the
0.1-cell sweeps at the band's two edges, and `bash run.sh mpi` six points at np 2 and 3
under `mpi_supervisor.py --silence 180` inside `timeout 900`, pinned to three cores. One
point by hand:

    python p_nearsurface_split.py --dip 30 --cellsize 0.05 --k 3

`python table.py <dip> <cellsize>` rebuilds a table below from `logs/`.

## The clearance mechanism

Read from `_place_thin_volume_2d` at fbef72fa; the refusal hit here is the one at
`place_surface.py` line 7871 (the gather path; the same text is at 7809 on the
seam-conforming path).

1. `place_fault_ribbon_2d` extends the trace by `margin_rings` spacings along its end
   tangents and builds a band of width w around it. The band is clipped to the domain:
   if its skin then has edges on the wall it is an outcrop, otherwise it is interior.
2. The carve's reach at a vertex is `R = max(clearance * h, 0.6 * w)` (here
   max(0.3 h, 1.2 h) = 1.2 h; the width term decides). Every vertex closer than R to the
   skin is deleted, except wall vertices, which are protected. Every cell with a deleted
   vertex, and every cell whose centre is within `max(clearance * h_min, 0.6 * w)` of the
   skin, is dropped; pinches and islands then grow the drop set.
3. The cavity's boundary is the ring of vertices around the dropped cells. For an
   interior band, any wall vertex on that ring is the refusal.
4. Because wall vertices are protected rather than deleted, one dropped cell that
   touches the wall is enough to put a wall vertex on the ring. The cavity therefore
   reaches one ring of cells past R: UNFILED 60 reports it as about 2.1 h from the skin
   when R is 1.2 h.
5. In UNFILED 60's message, "the cavity reaches" is the largest skin distance of a ring
   vertex, and "the nearest wall vertex" is the smallest skin distance of any wall vertex.

So an interior band needs a gap g between its skin and the wall larger than the cavity's
reach, about R plus one cell. An outcrop needs the band to cross the wall. For
0 < g < R + about one cell, neither path applies, and there is no third one.

## Sweeps

Outcomes on development and on UNFILED 60 are identical at every point. The UNFILED 60
column adds the two numbers from its message, in absolute units and in cells. "band top
below wall" is g measured at the band's highest corner, in cells.

### Dip 30 degrees, h = 0.025 (full sweep)

| k (cells) | top depth | band top below wall (cells) | development | UNFILED 60 (reach / nearest wall, in h) | np 2-3 agree with serial? |
|---|---|---|---|---|---|
| 0.0 | 0 | -1.88 | split refused: tip on wall | split refused: tip on wall | - |
| 0.5 | 0.0125 | -1.38 | outcrop | outcrop | - |
| 1.0 | 0.025 | -0.88 | outcrop | outcrop | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 1.5 | 0.0375 | -0.38 | outcrop | outcrop | - |
| 2.0 | 0.05 | +0.11 | wall refusal | wall refusal (0.0532 / 0.00557; 2.13 h / 0.22 h) | - |
| 2.5 | 0.0625 | +0.61 | wall refusal | wall refusal (0.053 / 0.0166; 2.12 h / 0.66 h) | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 3.0 | 0.075 | +1.11 | wall refusal | wall refusal (0.0529 / 0.0286; 2.12 h / 1.14 h) | - |
| 3.5 | 0.0875 | +1.61 | wall refusal | wall refusal (0.0521 / 0.041; 2.08 h / 1.64 h) | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 4.0 | 0.1 | +2.11 | interior | interior | - |
| 4.5 | 0.1125 | +2.61 | interior | interior | - |
| 5.0 | 0.125 | +3.11 | interior | interior | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 5.5 | 0.1375 | +3.61 | interior | interior | - |
| 6.0 | 0.15 | +4.11 | interior | interior | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 6.5 | 0.1625 | +4.61 | interior | interior | - |
| 7.0 | 0.175 | +5.11 | interior | interior | - |
| 7.5 | 0.1875 | +5.61 | interior | interior | - |
| 8.0 | 0.2 | +6.11 | interior | interior | dev np2 yes, dev np3 yes, u60 np2 yes, u60 np3 yes |
| 8.5 | 0.2125 | +6.61 | interior | interior | - |
| 9.0 | 0.225 | +7.11 | interior | interior | - |
| 9.5 | 0.2375 | +7.61 | interior | interior | - |
| 10.0 | 0.25 | +8.11 | interior | interior | - |

At 0.1-cell steps (logs `fine-*`): placed as an outcrop at k = 1.8 (g = -0.08 h),
refused from k = 1.9 (g = +0.01 h) to k = 3.8 (g = 1.91 h), placed as interior at
k = 3.9 (g = 2.01 h). On UNFILED 60 the cavity reach at k = 1.9 to 3.8 is
0.0529 to 0.0573 (2.1 to 2.3 h), against a nearest wall vertex of 0.0034 to 0.0484.

### Dip 45 degrees, h = 0.025 (k = 0 to 5.5; every k from 4.5 to 10 is interior)

| k (cells) | top depth | band top below wall (cells) | development | UNFILED 60 (reach / nearest wall, in h) | np 2-3 agree with serial? |
|---|---|---|---|---|---|
| 0.0 | 0 | -2.13 | split refused: tip on wall | split refused: tip on wall | - |
| 0.5 | 0.0125 | -1.63 | outcrop | outcrop | - |
| 1.0 | 0.025 | -1.13 | outcrop | outcrop | - |
| 1.5 | 0.0375 | -0.63 | outcrop | outcrop | - |
| 2.0 | 0.05 | -0.13 | outcrop | outcrop | - |
| 2.5 | 0.0625 | +0.37 | wall refusal | wall refusal (0.0536 / 0.0117; 2.14 h / 0.47 h) | - |
| 3.0 | 0.075 | +0.87 | wall refusal | wall refusal (0.0531 / 0.0228; 2.12 h / 0.91 h) | - |
| 3.5 | 0.0875 | +1.37 | wall refusal | wall refusal (0.0543 / 0.0349; 2.17 h / 1.40 h) | - |
| 4.0 | 0.1 | +1.87 | wall refusal | wall refusal (0.0562 / 0.0472; 2.25 h / 1.89 h) | - |
| 4.5 | 0.1125 | +2.37 | interior | interior | - |
| 5.0 | 0.125 | +2.87 | interior | interior | - |
| 5.5 | 0.1375 | +3.37 | interior | interior | - |

### Dip 15 degrees, h = 0.025 (k = 0 to 5.5; every k from 3.5 to 10 is interior)

| k (cells) | top depth | band top below wall (cells) | development | UNFILED 60 (reach / nearest wall, in h) | np 2-3 agree with serial? |
|---|---|---|---|---|---|
| 0.0 | 0 | -1.52 | assembly area check | assembly area check | - |
| 0.5 | 0.0125 | -1.02 | outcrop | outcrop | - |
| 1.0 | 0.025 | -0.52 | fill ring crosses itself | fill ring crosses itself | - |
| 1.5 | 0.0375 | -0.02 | fill ring crosses itself | fill ring crosses itself | - |
| 2.0 | 0.05 | +0.48 | wall refusal | wall refusal (0.0524 / 0.0142; 2.10 h / 0.57 h) | - |
| 2.5 | 0.0625 | +0.98 | wall refusal | wall refusal (0.053 / 0.0255; 2.12 h / 1.02 h) | - |
| 3.0 | 0.075 | +1.48 | wall refusal | wall refusal (0.0536 / 0.0375; 2.14 h / 1.50 h) | - |
| 3.5 | 0.0875 | +1.98 | interior | interior | - |
| 4.0 | 0.1 | +2.48 | interior | interior | - |
| 4.5 | 0.1125 | +2.98 | interior | interior | - |
| 5.0 | 0.125 | +3.48 | interior | interior | - |
| 5.5 | 0.1375 | +3.98 | interior | interior | - |

At this shallow dip the outcrop side has other failures. At k = 1.0 and 1.5 (band
corner 0.5 h and 0.02 h above the wall) the outcrop fill fails with "the fill ring
crosses itself 1 time(s)". At k = 0 the assembly fails its area check ("the ribbon
assembly meshed to area 8.608879262612e-03 against CAD 8.608879092678e-03"; the
relative difference is 2e-8). These are separate from the wall refusal and are
recorded here only.

### Dip 30 degrees, h = 0.0125 (cellSize 0.025; k = 0 to 5.5; every k from 4 to 10 is interior)

| k (cells) | top depth | band top below wall (cells) | development | UNFILED 60 (reach / nearest wall, in h) | np 2-3 agree with serial? |
|---|---|---|---|---|---|
| 0.0 | 0 | -1.88 | split refused: tip on wall | split refused: tip on wall | - |
| 0.5 | 0.0063 | -1.38 | outcrop | outcrop | - |
| 1.0 | 0.0125 | -0.88 | outcrop | outcrop | - |
| 1.5 | 0.0188 | -0.38 | outcrop | outcrop | - |
| 2.0 | 0.025 | +0.12 | wall refusal | wall refusal (0.0281 / 0.00285; 2.25 h / 0.23 h) | - |
| 2.5 | 0.0312 | +0.62 | wall refusal | wall refusal (0.0268 / 0.00838; 2.14 h / 0.67 h) | - |
| 3.0 | 0.0375 | +1.12 | wall refusal | wall refusal (0.0271 / 0.0144; 2.17 h / 1.15 h) | - |
| 3.5 | 0.0438 | +1.62 | wall refusal | wall refusal (0.0249 / 0.0206; 1.99 h / 1.65 h) | - |
| 4.0 | 0.05 | +2.12 | interior | interior | - |
| 4.5 | 0.0563 | +2.62 | interior | interior | - |
| 5.0 | 0.0625 | +3.12 | interior | interior | - |
| 5.5 | 0.0688 | +3.62 | interior | interior | - |

At every dip, k = 0 is refused by the split ("the fault touches the domain boundary"),
because the trace's top lies on the wall. That is a different, expected refusal.

### np 2 and 3

At dip 30 and h = 0.025, the points k = 1, 2.5, 3.5, 5, 6 and 8 were run at np 2 and np 3
on both versions (logs `mpi-*`). Every rank gives the same outcome, the same as serial;
UNFILED 60's message is the same text on every rank and the same as serial, numbers
included. All four runs exited 0 under the supervisor.

## Where the band starts and ends

| dip, h | outcrop up to k | refused for k | interior from k | refused for g (band corner below wall) |
|---|---|---|---|---|
| 30, 0.025 | 1.8 | 1.9 to 3.8 | 3.9 | +0.01 h to +1.91 h (0.1-cell steps) |
| 30, 0.0125 | 1.5 | 2.0 to 3.5 | 4.0 | +0.12 h to +1.62 h (0.5-cell steps) |
| 45, 0.025 | 2.0 | 2.5 to 4.0 | 4.5 | +0.37 h to +1.87 h |
| 15, 0.025 | 0.5 (fill fails at 1.0 to 1.5) | 2.0 to 3.0 | 3.5 | +0.48 h to +1.48 h |

Measured from the band's skin, the band runs from g = 0, where the band stops crossing
the wall, to g ≈ 2.0 h. All the evidence agrees: placed at 1.98 h and 2.01 h, refused at
1.87 h and 1.91 h. In terms of the carve's reach R = 1.2 h, the band ends at about
1.7 R. This is R plus one ring of cells (0.8 h), which matches the cavity reach of 2.1 h
that UNFILED 60 reports. In terms of k it is the same in cells at h = 0.025 and
h = 0.0125, so it scales with h.

Where it sits in k depends on how far the band's top corner rises above the trace's top.
In cells that rise is `(margin_rings * spacing * sin(dip) + (w/2) * cos(dip)) / h`: 1.9 at
30 degrees and 2.1 at 45 here. The band in k is that offset plus 0 to 2. For the
campaign, a larger spacing or width, or a different margin, moves the same 2-cell band
down to the 4 to 6 cells it saw. At steeper dips the margin can carry the band through
the surface, which would explain why tops at the same depth were placed there. This
probe does not test that mapping.

## What a fix would need

The placement has an interior cavity with a closed ring, and an outcrop where the band
itself crosses the wall. It has nothing for a band that stays interior while its
cavity's ring reaches the wall. A fix would need one of these:

- **An interior cut that may open onto the wall.** When the ring meets wall vertices but
  the skin does not, let the cavity's ring run along the wall between them, keeping the
  wall vertices and their labels. The fill polygon is then the cavity bounded partly by
  the wall, with the band's skin as an interior hole. This is the outcrop splice without
  a band on the wall. With it, every g > 0 is placeable.
- **Or a carve that stops short of the wall.** Near the wall, drop no cell that touches
  a wall vertex. The local reach becomes `min(R, g - one cell)`, so the fill there is
  graded, not refused. The cost is a tighter fill near the top.
- **Or, at least, a stated minimum clearance.** Check before carving: if the band's skin
  is within R plus the wall cells' size of a wall it does not cross (about 2 h here), say
  so in those terms, with g, R and the needed distance. Name both remedies: move the top
  deeper by the difference, or extend the band to outcrop (for example a larger margin
  at that end). UNFILED 60's message already carries g and the reach. Its "move it at
  least about" guide is right in direction and size here: at k = 3, the guide of 0.0243
  plus g of 0.0286 is 0.0529, about 2.1 h.

One observation on UNFILED 60's text. At k = 1.9 and 2.0 (dip 30) and k = 2.0 and 2.5
(dip 15), it says that moving the band away "would bring the cavity onto the wall at"
a point that is on the same outer wall, about 0.2 further along the band, not on the
other wall. Moving the band deeper moves it away from that point too, so the warning is
spurious there. The heuristic treats a far stretch of the same curved wall as "the other
wall".

## Files

- `p_nearsurface_split.py`: the reproducer.
- `run.sh`: the exact commands.
- `table.py`: the tables above, from the logs.
- `logs/sweep-{dev,u60}-dip{30,45,15}-cs0.05-np1.log`,
  `logs/sweep-{dev,u60}-dip30-cs0.025-np1.log`: serial sweeps, k = 0 to 10 at 0.5.
- `logs/fine-{dev,u60}-dip30-cs0.05-np1.log`: the band's edges at 0.1 cell.
- `logs/mpi-{dev,u60}-dip30-cs0.05-np{2,3}.log`: the rank checks.
- `logs/prelim-rin0.5-*`: a first sweep on test_0865's annulus itself (inner radius 0.5,
  h = 0.05). From k = 5 there, the fault's lower end reaches the inner wall, so those
  refusals are not the near-surface band. They are kept for the record.
- `logs/superseded/`: the first np 2 and 3 runs. The probe compared each rank's own
  cell count, so it reported ranks "disagreeing" while the outcomes agreed. The probe
  now compares outcomes only, and the runs were repeated. The serial logs come from the
  probe before that change, which affected only how the cell count is printed.

Underworld development team with AI support from Claude Code
