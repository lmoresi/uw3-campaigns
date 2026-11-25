# Register row 29: DRAFT build (not for review until Louis rules)

Branch feature/add-fault-pulls-tips-and-turns on labels70-22's 911a7b16 (UNFILED 68 + the labelling
fix + 72's flat-cell guard). One WIP commit: `fault_split._pulled_samples` (the tips, turns over 45
degrees, samples within 1.5 cells of a turn over 90 degrees; the cell size is reduced, so it is the
same on every rank), and add_fault's `snap_frac` default of 0.3 (`_ADD_FAULT_SNAP_FRAC`).

Test, first: tests/test_0900_add_fault_slip_independent_of_sampling.py. The arc la1 on the regular
box, sampled 1.0, 0.5 and 0.3 cells apart, places every time, and the slips agree:
- the draft: 0.1230493 / 0.1230582 / 0.1230498, a spread of 7.3e-5 (bound 1e-3);
- on the base (every sample pulled) it is refused: "snapping inverted 2 cell(s)".

## The suite (40 files): 18 failed, 414 passed (`suite29.log`)
1. **A real failure, on the sphere manifold:** test_0559 (both directions) and test_1092 give
   DMPlexComputeGeometryFVM error 77. Their arcs are sampled coarser than the mesh (9 samples, about
   1.5 cells apart). The rule pulls only the tips of a gentle arc, which leaves long great-circle
   stretches with no vertex. The earlier "thin" variant (also keep samples about a cell apart)
   passed this set (16/18, the 2 being test_0559's warning premise). So the likely fix is to add
   that spacing rule, which changes the measured rule, so row 29 would need remeasuring.
2. **Baselines pinned to the old meshes** (they change because the mesh changes):
   - test_1173: vertex counts 760 against 769-5; 20 against 16;
   - test_1174: facet counts {Flt: 23} against 31; 47 against 63; answers to 2e-5 (0.016551 against
     0.01691; 0.160355 against 0.160387);
   - test_1176: velocity iterations [5,5,5,5] against [6,6,6,6], an improvement pinned exactly;
   - test_1120: the weak-copy gap measured on the old meshes (0.140 and 0.343 against 0.255 and
     0.221);
   - test_0595: the default against an explicit snap_frac = 0.1 (the default is now 0.3, by
     intent).
3. **test_0897's add_fault fixtures now place** (the rule fixes them); the refusal stays checked on
   hand-labelled chains. The fixtures need replacing on this branch.

Each of (2) needs its baseline re-derived from the new mesh, and checked as a relation where it is a
mesh-bound number (this week's rule). That is 15 tests' worth of work, which should wait for Louis's
ruling and for the spacing decision in (1).
