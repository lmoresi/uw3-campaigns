# Row 118: a fill ring crossing the band's skin (the seam-conforming hang)

One commit (0001), (1) + (2a) of the design C1 approved.

Apply order: UNFILED 60 (0001-0004) on development fbef72fa, then 111 (0001-0007), 113 (0001-0002),
114 (0001-0004), 115 (0001-0003), then this. Locally: branch bugfix/fill-ring-against-the-band,
which is 111's head with 113, 114 and 115 cherry-picked in that order (no conflicts), plus this.

- Guard: `_refuse_a_ring_crossing_the_band` before every 2-D placement fill (gather and conform).
  It finds proper crossings between ring and hole edges with 113's tolerant orientation test, and
  holes outside the ring (a vertex on the ring counts as inside). It raises inside the failure
  gather.
- Connector: `_conform_fill_loops_2d` refuses a non-crossing span's straight connector that meets
  the band, naming seams='gather'.
- test_0909: 7 passed. The dumped ring gives (2 crossings, 1 hole outside); the passing cases are
  inside, vertex-touching and edge-touching holes. Placement suite on the stack: 114 passed.
- Owed (H1, np 3): conform cases AWAY from the wall with a band tip near a seam (the connector
  path), and the guard on the gather path over a theta sweep at np 3 with no false refusals.
- Not in this patch (row 118, separate): the connector's re-routing round the band (2b);
  _outcrop_ring_splice's unfiltered _boundary_edges; the ligament path's distributed ring.

## 0002 (2026-11-29): touch guard + review lows (H7 0001 lows, H1 np 3)
Separate commit on 0001; delta review of 0002 alone. Base for 0002: 0001 (3ea3b14d), head 18afb07c.
- the touch guard (`_refuse_a_ring_touching_itself`, 1e-9 of the local edge) at the three 2-D fills,
  inside their gathered tries; evidence probes/gmsh-spin (1e-15 hanging, >= 1.8e-2 completing).
  Deviation from C1's list: the 1e-12-inside variant is REFUSED (it is within the guard's 1e-9;
  gmsh meshes it, but only with a 1e-12 sliver); 1e-6 and 1e-2 inside pass.
- `seam-conforming path:` prefix on every gathered refusal of _place_thin_volume_2d when seams='conform'
  (fixes tests/parallel/test_0904 at np 3: the connector refusal fires first there);
- vectorised _loop_self_crossings and the ring/hole inside test; n = 1000: 0.033 s self-crossings,
  0.038 s touch, 0.083 s band with a 1000-vertex hole (0.15 s total; was about 4.4 s);
- _inside_polygon: on-edge band 1e-12 x diameter (all 8 callers; vs the old absolute 1e-14 it differs
  only at points within 6e-17 of the diameter from an edge, 34 of 24k random tests, all at scale 1000);
- the connector's touch test (_segments_cross, used only by _edge_meets_band) relative;
- the band guard's message names seams='gather'.
Tests: test_0909 19 passed; serial placement suite 445 passed, 1 skipped. Mutants shown failing:
threshold 0 / 2e-2, each guard call site removed (spy test), old on-edge band, old connector tolerance.
NOT run here (no MPI on the laptop): tests/parallel/test_0904 at np 3 with the prefix.
