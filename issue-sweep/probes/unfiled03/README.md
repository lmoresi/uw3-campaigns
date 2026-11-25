# UNFILED 3: partition-dependent rows in the fault-MG cell-located transfer

The finding (H1, review of #1206): 15 located rows near a fault trace change with the partition,
on development too. Measured on development fbef72fa, serial, macOS (12-core Apple M4).
Fixture: the #893 K1 ladder (`issue-sweep/probes/p_893_k1.py`), refinement 3, chain 2.

## Cause
`cell_located_prolongation` and its parallel form give each fine node the row of the coarse cell
located from the CENTROID of one fine cell containing the node, then clamp the node into that
cell (`_clamp`). The fine cell is `_fine_cell_of_node`'s choice, the LAST cell listing the node,
and in parallel that is the last in the rank's local cell order, which the partition sets. A node
shared by several fine cells whose centroids fall in different coarse cells gets a different row
under a different choice: evaluated in a different coarse cell, clamped there if it lies outside
it, and with different columns where the cells are on different sides. It is neither a tie in
point location nor the order of rank-local candidates; it is the owner cell, a choice made before
location. This is the same centroid-then-clamp mechanism as #1120. #1206 handled the copies that
have no fine image; this is the rest of it.

Serial count, every candidate owner tried (`owner_choice.py`, P2 nodes):

| pair | coarse split | nodes whose owners locate in different coarse cells | rows that would differ | max abs weight difference | kinds | farthest from the trace |
|---|---|---|---|---|---|---|
| 0 -> 1 | no | 576 | 0 | 0 | | |
| 1 -> 2 | no (placed, not cell-located) | 2,480 | 113 | 0.56 | clamped, columns | 0.19 |
| 2 -> 3 | yes (cell-located) | 10,651 | 973 | 1.12 | clamped, columns | 0.21 |
| 3 -> 4 | yes (cell-located) | 17,736 | 1,849 | 1.11 | clamped, columns | 0.11 |

On nested pairs (0 -> 1) the choice cannot matter: a continuous Lagrange row is the same in either
cell. Where the levels are not nested, inside the placed band within about 0.2 of the trace, it
can. A partition changes the "last" cell only where a node's cells are split across ranks, which
fits H1's 15 rows.

## Effect: none beyond tolerance
Serial bound (`owner_effect.py`): the split ladder solved with the owner taken as the last cell
(development), the first, or a seeded random one. That changes thousands of rows, far more than
any partition changes.

| tol | owner | outer / vel / pres | capped | rel. change of v vs last |
|---|---|---|---|---|
| 1e-6 | last | 1 / 21 / 14 | 0 | - |
| 1e-6 | first | 1 / 21 / 14 | 0 | 1.15e-7 |
| 1e-6 | random, seeds 1-3 | 1 / 21-22 / 14 | 0 | 3.9e-8 - 4.3e-8 |
| 1e-9 | last | 1 / 26 / 19 | 0 | - |
| 1e-9 | first | 1 / 26 / 19 | 0 | 2.2e-10 |
| 1e-9 | random, seed 1 | 1 / 26 / 19 | 0 | 1.1e-10 |

The difference falls with the tolerance, so every choice converges to the same discrete answer.
The transfer changes the preconditioner's path, not the solution. Counts move by at most one
velocity iteration.

**Verdict, under Louis's 2026-11-14 rule: informational.** Bit patterns of the transfer move with
the partition; the answer (to tolerance) and the convergence do not, on this bound. It remains for
H1 to confirm across rank counts.

Not in scope here: whether a clamped row from a far coarse cell is a good row. It is a quality
question of the non-nested band, #1120's territory (H5). The serial bound says it costs at most
an iteration.

## For H1 (np 1-4, default and random layouts with your partition hook)
```bash
export OMP_NUM_THREADS=1
for np in 1 2 3 4; do
  mpirun -n $np python owner_effect.py last 3 1e-6 > u3_np${np}_t6.log 2>&1
  mpirun -n $np python owner_effect.py last 3 1e-9 > u3_np${np}_t9.log 2>&1
done
grep -h "^EFF" u3_np*.log
```
Compare across rank counts: the counts (outer/vel/pres), capped, and |v|. The probe prints |v| as
the L2 norm by integration, which is independent of the partition (np 1, tol 1e-6: 62.23669508874).
Informational if the counts stay within one iteration and |v| agrees to the tolerance at both
tolerances. (The serial table above compared full nodal vectors.)
