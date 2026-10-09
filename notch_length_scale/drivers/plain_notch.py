"""The control for the FMG comparison: the plain notch law, NO micromorphic field,
regularised only by rate strengthening xi (tau_y + 2 xi eta_bg edot_II), solved with
the same consistent Newton and the same linear solvers as micromorphic_notch.py.
Without a length scale its band shrinks with h (W ~ sqrt(xi h)), so the Krylov
count per Newton step is the reference for what an unresolved band does to FMG.

Usage: python -u plain_notch.py -uw_ref 3 -uw_xi 0.03 -uw_linear production_tight
Writes results/plain/<name>.json (and the transcript, checkpoint).
"""
import os
import sys

import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_ref=uw.Param(1, description="refinement"),
    uw_xi=uw.Param(0.03, description="xi (eta_reg = xi * eta_bg)"),
    uw_budget=uw.Param(40, description="Newton iteration cap"),
    uw_linear=uw.Param("production_tight", description="exact | production | production_tight"),
    uw_ksp_max_it=uw.Param(0, description="cap on Krylov iterations per linear solve (0 = "
                                          "PETSc's default)"),
    uw_monitor=uw.Param(1, description="1 = SNES, line-search and KSP-reason monitors, "
                                       "2 = and the outer Krylov residual"),
    uw_tag=uw.Param("", description="suffix for the output files"),
)
OUT = os.path.join(_here, "..", "results", "plain")
ref, xi = int(params.uw_ref), float(params.uw_xi)
name = f"plain_ref{ref}_xi{xi:g}_{params.uw_linear}" + \
    ("" if uw.mpi.size == 1 else f"_np{uw.mpi.size}") + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

S = cn.build_notch(ref, xi)
cn.yield_stress_with_shift(S, 0)              # the same yield law, no micromorphic shift
if int(params.uw_ksp_max_it):
    S["stokes"].petsc_options["ksp_max_it"] = int(params.uw_ksp_max_it)
seconds = cn.solve_newton(S, name, OUT, params.uw_budget, int(params.uw_monitor),
                          str(params.uw_linear))
report = S["stokes"].solve_report
measured = cn.measure(S, OUT, name)
width = cn.integral_width(S, 9.0, "outside")
record = dict(ref=ref, xi=xi, reason=report.reason_str, converged=report.reason_str in cn.DONE,
              nl_its=report.nl_its, ksp_its=report.ksp_its, linear=str(params.uw_linear),
              nprocs=uw.mpi.size, seconds=seconds,
              h_min_km=float(S["mesh"].get_min_radius()) * cn.H_KM,
              W_integral_km=measured["W_integral_km"], relative_peak=measured["relative_peak"],
              W_outside9_km=width["median"], peak_outside9=width["peak_over_background"])
uw.pprint(f"[plain] ref {ref} xi {xi} np {uw.mpi.size}: {report.reason_str} its "
          f"{report.nl_its} ksp {report.ksp_its} ({seconds:.0f} s)  "
          f"W_int {record['W_integral_km']['median']:.2f}  W_out9 {width['median']:.2f}")
cn.write(OUT, name, record, dict(v=S["v"], p=S["p"]), S["mesh"])
