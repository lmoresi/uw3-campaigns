# UNFILED 75: lowercase mpi4py reductions under MIN, MAX or a custom op

mpi4py's lowercase `allreduce`/`reduce` pickles its argument and combines with Python's own
operators. A NumPy array under MIN or MAX is compared as a whole, and that raises on the combining
rank while the others wait: the hang fixed in labels70-22 round 1. SUM on an array is safe (`+`
is element-wise), and so is a 0-d NumPy scalar or a tuple of scalars (compared element by
element).

## Method
`audit75.py` walks every lowercase `.allreduce(` / `.reduce(` call in `src/` at development
fbef72fa. It parses the full argument list (multi-line calls included), drops SUM and the logical
ops (LAND, LOR, BOR, LXOR, BAND), and lists the rest with the first argument (`sites_fbef72fa.txt`,
88 sites). Each site whose argument is not visibly scalar (`float(...)`, `int(...)`, `len(...)`,
`bool(...)`, a conditional scalar) was traced back to its definition.

## Verdict: no site reduces an array under MIN, MAX or a custom op; nothing to convert
- Most sites wrap the argument as a scalar at the call.
- Every other site, traced:
  - **Python floats:** adjoint 963; constitutive_models 2927, 2971, 2972; mesh 9096, 9118;
    level_set 511; the advection-diffusion, navier-stokes, ddt, free-surface and solvers sites;
    yield_continuation 349; _cylindrical_pressure 229; _pressure_split 286; place_surface 999;
    swarm 6133; snes 14166.
  - **Python ints:** snes 2104 and 4554; mesh 4449; swarm 3679; custom_mg 2800; rotated_bc 1224.
  - **A 0-d NumPy scalar:** solvers 3026 (`np.min`).
  - **A tuple of scalars under MIN:** line_cut 1395, a lexicographic minimum by design.
  - **A helper or wrapper fed only scalars:** mesh 2275 `_reduce(val, op)`, whose two callers pass
    floats; level_set 550 (a variable op on a float); agreed_build 114, whose 12 callers pass ints.
  - **NOT MPI (NumPy ufunc `.reduce`):** mesh 2367, 2371; materials 1033, 1036.
  - **Default SUM on an array (safe):** metrics 495; fault_mg 1192.
- **Our branches:** labels70-22 (fb02df80) and row 29 (5a7ccf63) add only two sites,
  `int(on_slit)` under MAX and the flat-cell guard's `worst` tuple under MIN, built from floats and
  unpacked NumPy scalars. UNFILED 80 (d8d843d2) adds none.
- **The array reductions this class was named for** were labels70-22's own (the per-point
  distances and the inside mask). They are already in-place `Allreduce` on buffers.
