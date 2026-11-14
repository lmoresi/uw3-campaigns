# Boundary terms on faces not at orientation 0 (underworld3 #1188)

One-rank probes for underworld3 issue #1188. Run each with plain `python` in an
underworld3 environment; none starts another process.

- `exterior_load_against_exact.py`: a linear load on the Top wall of a unit cube, PETSc's
  nodal values against closed-form integrals, at refinement 0, 1, 2.
- `swap_control_2d_3d.py`: the load on an interior surface with and without the support
  order of its faces swapped in memory, in 2-D and 3-D.
- `orientation_census.py`: the orientation of every labelled face in its first support
  cell, for several meshes.
- `support_order_one_rank.py`: the #1150 setup (constrained Stokes on the shell) with the
  same swap; writes files that `../1150/compare_internal_load.py` reads.

The tables are in the issue. Built at underworld3 d3f7ced5, conda-forge PETSc 3.25.3,
macOS, 12-core Apple M4 (serial runs only).

Underworld development team with AI support from Claude Code
