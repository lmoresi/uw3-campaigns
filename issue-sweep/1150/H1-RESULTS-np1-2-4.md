# #1150 probe results, np 1, 2, 4 (H1)

*Run by H1 (the parallel review desk) on a 96-thread Linux workstation (Intel Xeon Gold 6240R; MPICH),
development c766bea5 built from source, `multiplier_unknowns_by_rank.py -uw_cell_size 0.2` (08a0dba);
3,241 cells. Placed here by the dev hub from H1's message. np 8 follows.*

## H1's summary

- **A, B, C:** zero everywhere. Global counts equal np 1 (Upper 1622 multiplier unknowns, Lower 534).
- **E:** every residual moment equals np 1 to all 13 printed digits at np 2 and 4.
- **D is non-zero, but it is the probe's arithmetic, not the section.** For a ghost point the script compares
  the local free count (dof - cdof) with -(globalSection.getDof+1); for a ghost, PETSc stores minus one minus
  the LOCAL total dof there, constraints included, not the owner's free count. Checked with a point-SF
  broadcast of the owner's own dof - cdof: np 2, rank 0 has 324 D mismatches, all carrying local
  constraints, and on all 324 the global value equals the local total dof; the owner's free count differs
  from the ghost's at 0 points on every rank. np 4: D mismatches 286, 180, 129 and 0; the owner's count
  differs at 0 points everywhere. (The last rank owns all of its shared points, hence its 0.)
  Fix for the script: compare against the owner's dof - cdof fetched over the point SF
  (`dm.getPointSF().bcastBegin/End` on an int64 per-point array of dof - cdof).
- So nothing in A to E distinguishes np 2 or 4 from np 1.

## Residual moments (E), identical at np 1, 2 and 4

```
E. every field zero | pressure: +0.000000000000e+00 +0.000000000000e+00 +0.000000000000e+00
E. every field zero | velocity: +2.736318375214e-01 +1.036275407586e+00 -5.306037538154e-01 +5.197470510535e-01
E. every field zero | multiplier_0: +0.000000000000e+00 +0.000000000000e+00 +0.000000000000e+00
E. every field zero | multiplier_1: +0.000000000000e+00 +0.000000000000e+00 +0.000000000000e+00
E. smooth state | pressure: +2.088689063756e+00 +9.118154150582e-01 -3.602284875658e-01
E. smooth state | velocity: +4.557968503179e+04 +2.955670337325e+04 +1.709689732705e+04 +1.181573242194e+03
E. smooth state | multiplier_0: +1.016530358400e+00 +7.704656539772e-01 +2.130944625100e+00
E. smooth state | multiplier_1: -3.116646384312e-01 -1.865663546729e-02 -8.012248088702e-01
```

## Per-rank wall counts (A and C)

| np | wall | rank: labelled vertices / edges / faces (closure identical; held-without 0; pinned 0; disagree 0) |
|---|---|---|
| 1 | Upper | 0: 407 / 1215 / 810 |
| 1 | Lower | 0: 135 / 399 / 266 |
| 2 | Upper | 0: 224 / 627 / 404; 1: 225 / 630 / 406 |
| 2 | Lower | 0: 81 / 218 / 138; 1: 76 / 203 / 128 |
| 4 | Upper | 0: 117 / 310 / 194; 1: 124 / 330 / 207; 2: 121 / 325 / 205; 3: 122 / 325 / 204 |
| 4 | Lower | 0: 45 / 112 / 68; 1: 46 / 114 / 69; 2: 41 / 101 / 61; 3: 45 / 112 / 68 |

B (label completion against the union): no differences at any np. The full raw outputs are in the hub's
copy of H1's message.
