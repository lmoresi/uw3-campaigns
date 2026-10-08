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
    uw_init=uw.Param("", description="fields npz of a coarser run to start from "
                                     "(empty = the viscous seed with chi = 0)"),
    uw_monitor=uw.Param(1, description="1 = SNES and line-search monitors"),
    uw_taylor=uw.Param(0, description="1 = Taylor test of the coupled Jacobian at the "
                                      "final iterate (slope 2 = exact tangent)"),
)
OUT = os.path.join(_here, "..", "results", "micromorphic")

ref, xi = int(params.uw_ref), float(params.uw_xi)
beta, l_km = float(params.uw_beta), float(params.uw_l_km)
name = f"micro_ref{ref}_xi{xi:g}_beta{beta:g}_l{l_km:g}" + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

S = cn.build_notch(ref, xi)
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
if str(params.uw_init):
    cn.prolong(str(params.uw_init), dict(v=S["v"], p=S["p"], chi=chi))

seconds = cn.solve_exact_newton(stokes, params.uw_budget, int(params.uw_monitor))
report = stokes.solve_report
taylor = cn.taylor_slopes(stokes) if int(params.uw_taylor) else None
if taylor:
    uw.pprint(f"[taylor] remainders {taylor[0]}  slopes {taylor[1]}")

bands = cn.measure(S, OUT, name)
W = {k: (None if v is None else v.get("W_equiv_km")) for k, v in bands.items()}
chi_values = np.asarray(chi.array).ravel()
record = dict(
    ref=ref, xi=xi, beta=beta, l_km=l_km,
    init=os.path.basename(str(params.uw_init)) or "seed",
    reason=report.reason_str, converged=report.reason_str in cn.DONE,
    nl_its=report.nl_its, seconds=seconds,
    h_min_km=float(mesh.get_min_radius()) * cn.H_KM,
    bands=bands, W_equiv_km=W,
    chi_range=[float(chi_values.min()), float(chi_values.max())],
    min_yield_stress_strong=cn.strong_layer_range(S, sigma_y)[0],
    shift_range_strong=cn.strong_layer_range(S, shift),
    viscosity_range_strong_Pas=cn.strong_layer_range(S, S["cm"].viscosity),
    taylor=taylor,
)
uw.pprint(f"[micromorphic] ref {ref} xi {xi} beta {beta} l {l_km} km: {report.reason_str} "
          f"its {report.nl_its} ({seconds:.0f} s)  W_L/W_R {W}  chi {record['chi_range']}  "
          f"min sigma_y {record['min_yield_stress_strong']:.3g}")
cn.write(OUT, name, record, dict(v=S["v"], p=S["p"], chi=chi))
