# UNFILED 111: measurements behind the proposal

Fixture: H1's (probes/nearsurface), with checks added to p_nearsurface_split.py. For every placement:
- the outer-wall boundary edges not carrying `Upper` ("wall-unlabelled");
- the smallest cell angle, over all cells and over cells touching the outer wall within 0.3 of the top;
- whether `FaultPlus` exists.

- l70-dip{15,30,45}.log: the labels70-22 build (0011), k 0-6. Outcomes are identical to H1's
  development logs at every point.
- exp_ring_on_wall.diff: the experiment, on development fbef72fa. The gather path's "cavity
  reached the domain wall" refusal is skipped for an interior band when UW_EXP_RING_ON_WALL is set.
- exp-fine.log: the experiment, dips 30/45/15, k 1.0-4.6 in 0.1-cell steps, h 0.025. Each line
  shows g, the band corner's gap below the wall in h.
- exp-h0125.log: k 2.0-3.5 and 6 at h 0.0125, with and without the experiment.

Findings:
- With the refusal removed, every g > 0 places as interior, at all three dips and both h.
  wall-unlabelled is 0 in all 111 placements of exp-fine.log, and in exp-h0125.log, and the
  Plus side is present.
- Smallest angle against g (dip 30, h 0.025): 1.0 deg at 0.01 h, 8.5 at 0.11, 15.7 at 0.21,
  22.5 at 0.31, 28.9 at 0.41, 34.6 at 0.51. From g of about 0.5 h on, 32-39 deg, the same as a
  deep interior placement (38.3). At 45 and 15 deg it is the same shape: 5.6 / 6.6 deg at
  g = 0.07 / 0.08 h. At h 0.0125, g = 0.12 h gives 9.2 deg.
- Development's outcrop path, for comparison (g < 0): smallest angles of 3.3-8.6 deg at several
  g, e.g. 3.7 at -0.68 h, 3.3 at -0.48 h, 8.3 at -0.08 h (dip 30), and 4.9 at -0.63 h (dip 45).
- Dip 15, g from -0.52 to -0.02 h (all but -0.32): "the fill ring crosses itself". This is on
  the outcrop path, untouched by the experiment.
