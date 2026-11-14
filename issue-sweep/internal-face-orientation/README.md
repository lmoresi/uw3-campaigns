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

## Follow-up, 2026-11-14: the mechanism, the reach into Nitsche terms, a PETSc-only reproducer

All on one process, macOS, 12-core Apple M4, conda-forge PETSc 3.25.3.

### The wrong loads are predicted exactly (`mispairing_prediction.py`)

Case A again (unit cube, load (0, 0, x) on Top, P2). If the load is read at the
physical quadrature point and the basis at the point a rotation of the triangle
away, the computed nodal load is the exact integral of the load with its three
vertex values rotated. Of the 36 choices (one permutation for orientation 1, one
for orientation 2) exactly one reproduces PETSc at every node:

| refinement | Top faces by orientation | nodes differing from exact | nodes differing from the prediction | largest difference |
|---|---|---|---|---|
| 1 | 0: 132, 1: 15, 2: 21 | 163 of 369 | 0 | 1.3e-17 |
| 2 | 0: 435, 1: 96, 2: 141 | 864 of 1409 | 0 | 6.8e-18 |

The permutation is (2, 0, 1) at orientation 1 and (1, 2, 0) at orientation 2: the
two rotations. The next best choices leave 42 and 216 nodes wrong. So on a face
with a positive orientation the basis is tabulated at the un-rotated point. This
is what the line `qp = ornt < 0 ? (Nq - 1 - q) : q` does for a positive
orientation (nothing), measured rather than read. It is not a patched build.

### Nitsche free slip with a radial normal (`nitsche_normal_rigid_rotation.py`)

Spherical shell (inner 0.55, outer 1, cell 0.5), `add_nitsche_bc(0, "Upper")`,
velocity set to a rigid rotation about z. A rigid rotation has no strain rate
and no component along the radial unit vector at any point, and P2 holds it
exactly, so with the normal written as the radial unit vector the residual is
zero to round-off on any mesh if velocity and normal are read at the same point.
The scale is the residual of the radial velocity u = x through the same terms.

| refinement | Upper faces by orientation | normal | largest residual, rigid rotation | scale | ratio |
|---|---|---|---|---|---|
| 0 | 0: 324 | radial unit vector | 5.2e-16 | 2.10 | 2.5e-16 |
| 0 | | PETSc face normal | 4.1e-2 | 2.02 | 2.0e-2 |
| 0 | | solver default | 2.1e-2 | 2.04 | 1.0e-2 |
| 1 | 0: 1052, 1: 175, 2: 69 | radial unit vector | 1.8e-2 | 1.19 | 1.5e-2 |
| 1 | | PETSc face normal | 1.0e-2 | 1.19 | 8.7e-3 |
| 1 | | solver default | 8.5e-3 | 1.17 | 7.3e-3 |
| 2 | 0: 3465, 1: 1130, 2: 589 | radial unit vector | 5.6e-3 | 0.606 | 9.2e-3 |
| 2 | | PETSc face normal | 2.6e-3 | 0.606 | 4.4e-3 |
| 2 | | solver default | 3.2e-3 | 0.605 | 5.3e-3 |

On the unrefined mesh the radial normal is exact and the two face-based normals
carry the faceting error of about 1 to 2 %. On the refined meshes the radial
normal carries an error of the same size as the faceting error it was meant to
remove, and larger than either face-based form. The face-based rows are not a
measure of the defect: a flat-face normal against a rigid rotation is not zero
by construction, and the solver default reads a mesh variable. Not measured: the
effect on a solved flow, the penalty form, internal surfaces, hexahedra.

### Reproducer with nothing of ours in it (`petsc_only/bd_residual_orientation.c`)

The unit cube cut into six tetrahedra by hand (conda-forge PETSc has no 3-D mesh
generator), refined regularly, a P2 scalar field, the natural term f0 = x on the
wall z = 1, residual at zero state. b.1 must be 1/2 and b.x must be 1/3.

    mpicc bd_residual_orientation.c -I$PETSC_DIR/include -L$PETSC_DIR/lib -lpetsc -o bd_residual_orientation
    ./bd_residual_orientation -dim 3 -refine 1

| case | wall faces by orientation | b.1 − 1/2 | b.x − 1/3 |
|---|---|---|---|
| 3-D, refine 0 | 0: 2 | -1.1e-16 | -5.6e-17 |
| 3-D, refine 1 | 0: 6, 1: 2 | -1.7e-16 | -5.2e-3 |
| 3-D, refine 2 | 0: 18, 1: 12, 2: 2 | 0 | -2.3e-3 |
| 3-D, refine 3 | 0: 56, 1: 54, 2: 18 | 1.1e-16 | -7.3e-4 |
| 2-D, refine 0 | 0: 1 | -2.2e-16 | -1.1e-16 |
| 2-D, refine 2 | 0: 4 | -1.7e-16 | -5.6e-17 |

The error in b.x falls by 0.44 and then 0.32 per refinement.
