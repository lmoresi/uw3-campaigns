# Graded annulus base for the slab workbench (geometry only)

Louis, 2026-11-14: MMPDE resolves the thermal boundary layer and tightens around the slab
(about a factor of four); the fault cut-in handles the fault's own resolution. The missing
piece is a base that is coarse in the lower mantle and coarse around the annulus, with enough
resolution that MMPDE's factor of four reaches what is needed.

`graded_base.py` builds the annulus (r_o = 1/0.45, r_i = 0.55/0.45 layer depths, 1 = 2,900 km)
with gmsh and a size callback. Sizes are FINEST-level targets in km:

| region | base | after MMPDE x4 |
|---|---|---|
| top 200 km (thermal boundary layer) | 40 | ~10 |
| 200-660 km | 80 | ~20 |
| lower mantle | grading to 200 (optional 80 km layer at the CMB) | |
| optional trench window, +-750 km arc to 700 km depth | 16 | ~4 |

    python3 graded_base.py H_LM H_CMB out.npz HALF_ARC   # HALF_ARC 0: no trench window
    python3 plot_base.py out.npz "title" out.png

Results (cells): window, LM 200: 37,396 (a); window, LM 200 + 80 km CMB layer: 39,747 (b);
radial only, no window: 27,913 (c). For comparison, the present uniform mesh is ~120,000
cells (~42 km everywhere) and the workbench's 4 km box is 304,064.

Not done: no underworld3 here (no PETSc), so no solve, no MMPDE, no multigrid hierarchy.
Underworld3 builds its multigrid levels by refining a COARSE gmsh mesh; this grading has to
survive at the coarse level (sizes x 2^refinement), which a 200 km band at 40 km does not
at refinement 3 (coarse cells 320 km). That is the first thing to test in the library.

Underworld development team with AI support from Claude Code
