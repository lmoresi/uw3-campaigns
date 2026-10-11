"""Micromorphic (gradient-plasticity) coupling on the Spiegelman notch.

The yield law gets a length scale through an extra field chi, solved in the same
Newton system as the flow (``stokes.add_coupled_field``). The free energy gains

    (H/2) (e - chi)^2 + (A/2) |grad chi|^2,      A = H l^2,  e = edot_II(u),

so chi is the strain-rate invariant smoothed over l,

    H (chi - m e) - div(A grad chi) = 0          (m = strong-layer mask),

and the yield stress is shifted by s = H (e - chi) = -A lap chi:

    sigma_y = smooth_max(C_eff + sin(phi) p + m H (e - chi), s_min, s_min).

Eliminating chi adds no stiffness to modes longer than l and about H to modes
shorter than l, which is the band's collapsing soft mode. The cross blocks scale with
H, not with the viscosity contrast. Solver and measurements: coupled_notch.py.

Usage: python -u micromorphic_notch.py -uw_ref 1 -uw_xi 0.01 -uw_beta 0.05 -uw_l_km 1
"""
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_ref=uw.Param(1, description="refinement"),
    uw_xi=uw.Param(0.01, description="xi (eta_reg = xi * eta_bg)"),
    uw_beta=uw.Param(0.01, description="H / eta_bg"),
    uw_l_km=uw.Param(1.0, description="micromorphic length l in km"),
    uw_budget=uw.Param(60, description="Newton iteration cap"),
    uw_tag=uw.Param("", description="suffix for the output files"),
    uw_linear=uw.Param("exact", description="exact (LU of J) | production (Schur "
                                            "fieldsplit with FMG velocity block, "
                                            "Eisenstat-Walker) | production_tight "
                                            "(the same, every linear solve to 1e-8)"),
    uw_init=uw.Param("", description="checkpoint of the ref - 1 run to start from, "
                                     "results/micromorphic/checkpoints/<run> (empty = the "
                                     "viscous seed with chi = 0)"),
    uw_monitor=uw.Param(1, description="1 = SNES and line-search monitors, 2 = and the outer Krylov residual"),
    uw_seed=uw.Param(1, description="1 = start from the viscous seed (warm: no Picard "
                                     "warm-up); 0 = cold from rest (the automatic warm-up "
                                     "step arms)"),
    uw_ksp_max_it=uw.Param(0, description="cap on Krylov iterations per linear solve "
                                          "(0 = PETSc's default); a capped solve that misses "
                                          "rtol ends the Newton solve, reported as such"),
    uw_taylor=uw.Param(0, description="1 = Taylor test of the coupled Jacobian at the "
                                      "final iterate (slope 2 = exact tangent)"),
)
OUT = os.path.join(_here, "..", "results", "micromorphic")

ref, xi = int(params.uw_ref), float(params.uw_xi)
beta, l_km = float(params.uw_beta), float(params.uw_l_km)
name = f"micro_ref{ref}_xi{xi:g}_beta{beta:g}_l{l_km:g}" + \
    ("" if str(params.uw_linear) == "exact" else f"_{params.uw_linear}") + \
    ("" if uw.mpi.size == 1 else f"_np{uw.mpi.size}") + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

coarse = (cn.load_coarse(str(params.uw_init), ref - 1, xi,
                         dict(chi=(1, 1, True, "1/s")))
          if str(params.uw_init) else None)
S = cn.build_notch(ref, xi, seed=bool(int(params.uw_seed)))
mesh, stokes = S["mesh"], S["stokes"]

m = S["mat"].sym[0]
e = stokes.Unknowns.Einv2
chi = uw.discretisation.MeshVariable("chi", mesh, 1, degree=1, units="1/s")
H = uw.expression(r"H_{\chi}", uw.quantity(beta * cn.ETA_BG, "Pa*s"), "micromorphic modulus")
ell = uw.expression(r"\ell", uw.quantity(l_km, "km"), "micromorphic length")
stokes.add_coupled_field(
    chi,
    F0=H * (chi.sym[0] - m * e),
    F1=H * ell ** 2 * chi.sym.jacobian(mesh.CoordinateSystem.N),
)
shift = m * H * (e - chi.sym[0])
sigma_y = cn.yield_stress_with_shift(S, shift)
if coarse is not None:
    cn.prolong(coarse, dict(v=S["v"], p=S["p"], chi=chi))

if int(params.uw_ksp_max_it):
    stokes.petsc_options["ksp_max_it"] = int(params.uw_ksp_max_it)
seconds = cn.solve_newton(S, name, OUT, params.uw_budget, int(params.uw_monitor),
                          str(params.uw_linear))
report = stokes.solve_report
taylor = cn.taylor_slopes(stokes) if int(params.uw_taylor) else None
if taylor:
    uw.pprint(f"[taylor] remainders {taylor[0]}  slopes {taylor[1]}")

measured = cn.measure(S, OUT, name)
record = dict(
    ref=ref, xi=xi, beta=beta, l_km=l_km,
    init=os.path.basename(str(params.uw_init)) or "seed",
    reason=report.reason_str, converged=report.reason_str in cn.DONE,
    nl_its=report.nl_its, ksp_its=report.ksp_its, linear=str(params.uw_linear),
    seed=bool(int(params.uw_seed)),
    # the solve report folds a Picard warm-up into nl_its and records its steps here
    warmup_its=int((getattr(report, "config", None) or {}).get("tangent", {})
                   .get("picard_warmup_its", 0)),
    nprocs=uw.mpi.size, seconds=seconds,
    h_min_km=float(mesh.get_min_radius()) * cn.H_KM,
    W_horizontal_km=measured["W_horizontal_km"], W_vertical_km=measured["W_vertical_km"],
    W_integral_km=measured["W_integral_km"], relative_peak=measured["relative_peak"],
    bands_horizontal=measured["bands_horizontal"], bands_vertical=measured["bands_vertical"],
    floor_bound_over_floor=cn.floor_bound_over_floor(S, chi, beta),
    chi_max=float(np.asarray(chi.max())),
    taylor=taylor,
)
width9 = cn.integral_width(S, 9.0, "outside")      # the current estimator
record.update(W_outside9_km=width9["median"], W_outside9_spread_km=width9["spread"],
              peak_outside9=width9["peak_over_background"])
uw.pprint(f"[micromorphic] current estimator: W {width9['median']:.3f} km  peak "
          f"{width9['peak_over_background']:.3f}")
uw.pprint(f"[micromorphic] ref {ref} xi {xi} beta {beta} l {l_km} km np {uw.mpi.size}: "
          f"{report.reason_str} its {report.nl_its} ({seconds:.0f} s)  "
          f"W_int {record['W_integral_km']['median']:.2f}  W_v {record['W_vertical_km']}  "
          f"peak {record['relative_peak']}  floor bound {record['floor_bound_over_floor']:.1f}")
cn.write(OUT, name, record, dict(v=S["v"], p=S["p"], chi=chi), mesh)
