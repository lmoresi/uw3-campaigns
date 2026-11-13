# UWTN 2026-016: evidence for the version 1.1 correction

> **For the hub, 2026-11-13.** The cause of the note's unreproducible annulus Nitsche numbers is
> confirmed by a bracket of two adjacent commits. Nothing else in the annulus tables needs correcting
> on this evidence. The rewrite itself waits for #1145 to merge.

All runs: the note's own `examples/stress.py both`, unmodified (note repository at 39335ce), serial, on
a 96-thread Linux workstation (single system image, Intel Xeon Gold 6240R, MPICH, PETSc int32).
Entries are leak / stress error for the Nitsche column at gamma = 10.

| cell size | published | 8b7c8b9e (18 Aug, the note's stated revision) | 9da04b72 (5 Sep) | 4b4f341c (5 Sep, #694) | development 01dec8d2 |
|---|---|---|---|---|---|
| 0.150 | 1.0e-2 / 5.8e-2 | 1.0e-2 / 5.8e-2 | 1.0e-2 / 5.8e-2 | (stress 7.80e-2) | 1.6e-2 / 7.8e-2 |
| 0.100 | 2.4e-3 / 2.4e-2 | 2.6e-3 / 2.4e-2 | 2.6e-3 / 2.4e-2 | (stress 3.33e-2) | 4.2e-3 / 3.3e-2 |
| 0.075 | 1.2e-3 / 1.5e-2 | 1.3e-3 / 1.5e-2 | 1.3e-3 / 1.5e-2 | (stress 1.98e-2) | 2.2e-3 / 2.0e-2 |
| 0.050 | 2.7e-4 / 6.3e-3 | 2.7e-4 / 6.3e-3 | 2.7e-4 / 6.3e-3 | (stress 8.58e-3) | 4.9e-4 / 8.6e-3 |

- 9da04b72 is the parent of 4b4f341c, "Take the cell radius from PETSc again, so it cannot depend on
  the partition (#694)". The numbers change at that commit and nowhere else in the bracket. The
  commit after it, c0948ac2, only rescales the DEFAULT gamma to 12.5; the note's scripts pass
  gamma = 10 explicitly, so after #694 the same number is a weaker penalty.
- At 4b4f341c only the `sweep` form was run (stress column); it equals development's.
- Every other entry of the `both` table (penalty with the node normal, multiplier, rotated, and the
  three reaction columns) is identical to the published table at every revision above, including
  development.
- Two published leak entries (2.4e-3, 1.2e-3) differ in the second digit from every run (2.6e-3,
  1.3e-3). Not explained.
- `examples/leak.py sweep` is a different experiment (free slip on both radii) and is not the source
  of the note's combined table; an earlier message of mine compared against it by mistake.
- From the review desk that ran the note's scripts on development and on #1145's branch: #1145 moves
  the annulus Nitsche entries by 1 to 4 %, and no gamma from 1 to 1e4 diverges on either build.
  From the session that owns the solver: with #1145 the SolCx case converges (it did not before).

So the correction note has three things to say: the published annulus Nitsche numbers belong to the
code before #694 at gamma = 10; #1145 changes them slightly; #1145 changes SolCx materially.
