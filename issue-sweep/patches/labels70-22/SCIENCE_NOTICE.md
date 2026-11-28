# Notice to the science hub: add_fault places some faults one vertex differently

When this PR merges to development, `add_fault` changes the mesh of some faults it already
placed, by one vertex each:

- **Tips.** A trace's first tip now always keeps its vertex. Before, a tip within reach of the
  next sample lost it, and the fault ended one sample spacing short. On a 480-trace box grid,
  29 of the 232 faults development placed change mesh this way. Their slip changes by a median
  of +5.5 % (largest 26 %), and against a reference trace sampled a cell apart their median
  error falls from 9.5 % to 2.3 %.
- **Turns.** A turn of more than 45 degrees now keeps its vertex. Before, the chain could cut the
  corner by up to half a cell. 13 of 232 change, with median error 14 % to 3.8 %. One 90-degree
  corner gets worse on the coarse mesh (3.8 % to 12 % against the converged slip), because the
  old corner cut partly cancelled the coarse mesh's own error there.
- **Refusals.** Faults that come back in pieces, miss a tip or turn, or lie more than half a cell
  from their trace are now refused, with a message naming why. Every refused fault in the grid
  was in pieces on development.

What a campaign sees: a run with a kinked or finely sampled trace can place its fault one vertex
apart from before, and so give a slip a few percent different near the tip or turn. A run that
placed a fault in pieces now raises. Rerun the baseline of any comparison that crosses the
merge, on the same fixture.
