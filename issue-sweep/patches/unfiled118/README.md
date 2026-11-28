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
