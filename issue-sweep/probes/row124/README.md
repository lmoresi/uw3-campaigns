# Row 124: partition_addon can empty a rank (np >= 3) or refuse (np 2)

Mechanism (addon_partition.py on development, _partition_addon_body and _peel_balance):
- Every unit (base cell, weighted by its finest descendants) of a fault region goes to the
  region's owner, argmax of the region's weight per rank. Other units stay (`assign = comm.rank`).
- _peel_balance offers free units only across faces a rank shares with a lighter neighbour, judged
  by the current assignment. A rank whose units all lie in a region it does not own is assigned
  nothing and touches nothing, so nothing is offered to it.
- Result: np 2 -> "the whole add-on would sit on one rank"; np >= 3 -> an empty rank. test_0912's
  first fixture (row 122) hit it by construction.

The question: can a real partition produce it? The base partition balances base cells, not weight,
and the region is a band of about 3 units (star + 1 layer). So it needs a rank's whole share inside
that band: coarse bases at higher np, or a later partition in which ranks near an earlier fault hold
few heavy units.

Probe: empty_rank_probe.py wraps _peel_balance and prints the per-rank load before and after it,
the ranks left at 0, and any refusal. Proposed sweep for H1 (under the supervisor, threads 1):
  cases: adapt k=1,2,3; second k=2; base;  cellsize 0.1 and 0.2;  np 2..8.
Serial smoke run on the laptop: all stages complete (no peel at np 1).
