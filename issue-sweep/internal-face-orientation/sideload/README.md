# The side-load for #1188: boundary quadrature paired by face orientation

The remap in underworld3 `src/underworld3/cython/uw_face_orientation.h` (branch
`bugfix/boundary-quadrature-face-orientation-1188`), measured against `development`
(aee3fa65). One rank, conda-forge PETSc 3.25.3, macOS on a 12-core Apple M4 (serial runs
only), 2026-11-15.

- `bd_orientation_library.c`: the PETSc-only reproducer of `../petsc_only`, with
  `-uw_fix 1` installing the remap from the library header (copy the header beside it).
  Options `-dim -refine -uw_fix -wall_axis -wall_side -wall_pos -swap -shuffle`; serial.
  `all_walls_library.txt` is the 135-run sweep. 48 runs whose wall is not a whole plane
  (b.1 wrong either way) are left out of the table below.

  | walls (whole planes) | runs | development | side-load |
  |---|---|---|---|
  | exterior, orientations 0 to 2 | 45 | 5.21e-3 | 9.44e-16 |
  | interior, with negative orientations | 33 | 1.56e-2 | 7.77e-16 |
  | interior, positive orientations only | 6 | 6.51e-4 | 7.77e-16 |
  | interior, all at 0 | 3 | 3.3e-16 | 3.3e-16 |

- `kramer_delta_benchmark.py`: Kramer, Davies & Wilson (2021) delta-forced Stokes,
  l = 2, m = 0, free boundaries, on the shell 1.22 / 1.72 / 2.22. Output in
  `kramer_runs.txt`. The errors move by about 0.3 % of themselves; this benchmark's
  error is discretisation, and it does not show the defect.

- `boundary_assembly_timing.py`: residual and Jacobian assembly on the same shell, with
  and without a natural load on Upper, Lower and Internal, best of 5. Output in
  `timing_runs.txt`. Laptop wall times, which throttling moves; the boundary share
  differs between the two builds by less than the run-to-run spread of the load-free
  baseline.
