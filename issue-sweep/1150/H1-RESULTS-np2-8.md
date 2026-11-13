# #1150 probe at np 2 and np 8 (H1, Linux workstation), development c766bea5, cell size 0.2

Relayed to the dev hub by H1 on 2026-11-14. The probe is at campaigns 57524f3, with D corrected.

## Result

- **A to D are zero** at np 2 and at np 8, for every field and for each field separately. Corrected D works.
- **E (residual moments).** np 2 and np 4 are identical to np 1 in every digit. At np 8, pressure and both multipliers are exact, but the **velocity load** differs from np 1:

| velocity moment | np 1 | np 8 | np 8 - np 1 |
|---|---|---|---|
| every field zero, w1 | 2.736318375214e-01 | 2.736372332814e-01 | +5.40e-06 (2.0e-5 rel.) |
| every field zero, w2 | 1.036275407586e+00 | 1.036278169001e+00 | +2.76e-06 |
| every field zero, w3 | -5.306037538154e-01 | -5.306038781979e-01 | -1.24e-07 |
| every field zero, w4 | 5.197470510535e-01 | 5.197477669221e-01 | +7.16e-07 |
| smooth state, w1 | 4.557968503179e+04 | 4.557968503719e+04 | +5.40e-06 |
| smooth state, w2 | 2.955670337325e+04 | 2.955670337601e+04 | +2.76e-06 |
| smooth state, w3 | 1.709689732705e+04 | 1.709689732693e+04 | -1.2e-07 |
| smooth state, w4 | 1.181573242194e+03 | 1.181573242910e+03 | +7.16e-07 |

- **The absolute shift is identical in both states.** So it is the load term alone, not the stiffness or the constraints. This is consistent with W1's guess that the `Internal` surface load is integrated differently at np 8.
- **The shift is far smaller than one whole face**, counted twice or missed: there are 810 Upper faces. So it is a partial contribution, not yet localised.

## Wall counts (A to C), summarised

- **Upper (label 13, solver field 2):** 407 vertices, 1215 edges, 810 faces; 1622 multiplier unknowns at both rank counts.
- **Lower (label 11, solver field 3):** 135 vertices, 399 edges, 266 faces; 534 multiplier unknowns.
- At both np 2 and np 8:
  - the per-rank closures equal the labels;
  - label completion equals the union;
  - no shared wall point has ranks that disagree;
  - no wall point is left unkept.

H1 keeps the full logs: at np 8, the forty all-zero D lines are compressed in the relay.
