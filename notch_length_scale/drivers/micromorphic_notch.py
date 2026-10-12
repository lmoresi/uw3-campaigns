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
    uw_mesh=uw.Param("", description="gmsh file of the notch (empty = the 2-D mesh1); a 3-D "
                                     "extruded notch from make_notch_mesh_3d.py"),
    uw_weak_ramp=uw.Param("", description="3-D only: 'z0,w' in km, the weak inclusion's "
                                          "viscosity ramped along strike, log10 eta_b = 22 - "
                                          "tanh((z0 - z)/w) (empty = uniform)"),
    uw_snap=uw.Param(0, description="1 = snap refined vertices of the notch's fillet arcs "
                                     "back onto the arcs (for a coarse base mesh, refined "
                                     "several times: a deeper FMG hierarchy)"),
    uw_seed=uw.Param(1, description="1 = start from the viscous seed (warm: no Picard "
                                     "warm-up); 0 = cold from rest (the automatic warm-up "
                                     "step arms)"),
    uw_ksp_max_it=uw.Param(0, description="cap on Krylov iterations per linear solve "
                                          "(0 = PETSc's default); a capped solve that misses "
                                          "rtol ends the Newton solve, reported as such"),
    uw_taylor=uw.Param(0, description="1 = Taylor test of the coupled Jacobian at the "
                                      "final iterate (slope 2 = exact tangent)"),
    uw_ramp_scope=uw.Param("weak", description="what the along-strike ramp stiffens: weak "
                                                "(the whole Weak region, lower layer too) | "
                                                "notch (the bump above y = -3/4 H only)"),
    uw_coarse=uw.Param("native", description="direct solver of the multigrid coarse level: "
                                             "native (PETSc LU, production) | mumps "
                                             "(measurements only)"),
)
OUT = os.path.join(_here, "..", "results", "micromorphic")

ref, xi = int(params.uw_ref), float(params.uw_xi)
cn.nm.COARSE_FACTOR = None if str(params.uw_coarse) == "native" else str(params.uw_coarse)
weak_ramp = (tuple(float(v) for v in str(params.uw_weak_ramp).split(","))
             if str(params.uw_weak_ramp) else None)
beta, l_km = float(params.uw_beta), float(params.uw_l_km)
name = f"micro_ref{ref}_xi{xi:g}_beta{beta:g}_l{l_km:g}" + \
    ("" if str(params.uw_linear) == "exact" else f"_{params.uw_linear}") + \
    ("" if uw.mpi.size == 1 else f"_np{uw.mpi.size}") + \
    (f"_{os.path.splitext(os.path.basename(str(params.uw_mesh)))[0]}" if str(params.uw_mesh)
     else "") + \
    (f"_ramp{weak_ramp[0]:g}w{weak_ramp[1]:g}" if weak_ramp else "") + \
    ("_notchonly" if weak_ramp and str(params.uw_ramp_scope) == "notch" else "") + \
    ("_snap" if int(params.uw_snap) else "") + \
    ("" if str(params.uw_coarse) == "native" else f"_{params.uw_coarse}") + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

coarse = (cn.load_coarse(str(params.uw_init), ref - 1, xi,
                         dict(chi=(1, 1, True, "1/s")), msh=str(params.uw_mesh) or None,
                         weak_ramp=weak_ramp, snap_arcs=bool(int(params.uw_snap)),
                   ramp_scope=str(params.uw_ramp_scope))
          if str(params.uw_init) else None)
S = cn.build_notch(ref, xi, seed=bool(int(params.uw_seed)), msh=str(params.uw_mesh) or None,
                   weak_ramp=weak_ramp, snap_arcs=bool(int(params.uw_snap)),
                   ramp_scope=str(params.uw_ramp_scope))
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

base_record = dict(
    ref=ref, xi=xi, beta=beta, l_km=l_km, dim=mesh.dim,
    init=os.path.basename(str(params.uw_init)) or "seed",
    reason=report.reason_str, converged=report.reason_str in cn.DONE,
    nl_its=report.nl_its, ksp_its=report.ksp_its, linear=str(params.uw_linear),
    seed=bool(int(params.uw_seed)),
    # the solve report folds a Picard warm-up into nl_its and records its steps here
    warmup_its=int((getattr(report, "config", None) or {}).get("tangent", {})
                   .get("picard_warmup_its", 0)),
    nprocs=uw.mpi.size, seconds=seconds,
    h_min_km=float(mesh.get_min_radius()) * cn.H_KM,
    floor_bound_over_floor=cn.floor_bound_over_floor(S, chi, beta),
    chi_max=float(np.asarray(chi.max())),
    taylor=taylor,
)
if mesh.dim == 2:
    measured = cn.measure(S, OUT, name)
    record = dict(
        base_record,
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
else:
    # The extruded notch: the current estimator on cut planes along strike. The
    # 2-D horizontal / vertical-equivalent measures are not carried over.
    # the global extent, collectively (PETSc), in the mesh's non-dimensional units
    Lz_km = float(S["mesh"].dm.getBoundingBox()[2][1]) * cn.H_KM
    along = {}
    for fz in (0.02, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98):
        w = cn.integral_width(S, 9.0, "outside", z_km=fz * Lz_km)
        along[f"{fz * Lz_km:.2f}"] = dict(W_km=w["median"], spread_km=w["spread"],
                                          peak=w["peak_over_background"])
    mid = along[f"{0.5 * Lz_km:.2f}"]
    record = dict(base_record, Lz_km=Lz_km, along_strike=along, weak_ramp=weak_ramp,
                  W_outside9_km=mid["W_km"], peak_outside9=mid["peak"])
    uw.pprint(f"[micromorphic 3-D] ref {ref} beta {beta} l {l_km} km np {uw.mpi.size}: "
              f"{report.reason_str} its {report.nl_its} ({seconds:.0f} s)  mid-strike W "
              f"{mid['W_km']:.3f} km, peak {mid['peak']:.3f}; W(z) " +
              " ".join(f"{v['W_km']:.2f}" for v in along.values()))
cn.write(OUT, name, record, dict(v=S["v"], p=S["p"], chi=chi), mesh)
