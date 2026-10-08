"""2-D Cosserat continuum on the Spiegelman notch.

The micro-rotation rate omega (a scalar in 2-D) is solved in the same Newton system as
the flow (``stokes.add_coupled_field``). With the continuum spin
W = (du_y/dx - du_x/dy)/2 and E = [[0, -1], [1, 0]]:

    momentum flux   sigma + 2 eta_c (W - omega) E            (skew stress)
    moment balance  -div(m) + 4 eta_c (omega - W) = 0,   m = 2 eta_eff l^2 grad omega

The plasticity sees the generalised strain-rate invariant

    e_gen^2 = edot_II^2 + (1/2) l^2 |grad omega|^2,

so eta_eff = tau_y / (2 e_gen) (soft-min with the background) and it scales both the
deviatoric and the couple stress. The Cosserat viscosity eta_c = c * visc_lin stays
unyielded. A band narrower than l pays for its rotation gradient, which is the length
scale. Solver and measurements: coupled_notch.py.

Usage: python -u cosserat_notch.py -uw_ref 1 -uw_xi 0.01 -uw_c 1 -uw_l_km 1
"""
import os
import sys

import numpy as np
import sympy
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_ref=uw.Param(1, description="refinement"),
    uw_xi=uw.Param(0.01, description="xi (eta_reg = xi * eta_bg)"),
    uw_c=uw.Param(1.0, description="eta_c / visc_lin"),
    uw_l_km=uw.Param(1.0, description="Cosserat length l in km"),
    uw_degree=uw.Param(1, description="degree of the omega field"),
    uw_budget=uw.Param(60, description="Newton iteration cap"),
    uw_tag=uw.Param("", description="suffix for the output files"),
    uw_linear=uw.Param("exact", description="exact (LU of J) | production (Schur "
                                            "fieldsplit with FMG velocity block)"),
    uw_monitor=uw.Param(1, description="1 = SNES and line-search monitors"),
    uw_taylor=uw.Param(0, description="1 = Taylor test of the coupled Jacobian at the "
                                      "final iterate (slope 2 = exact tangent)"),
)
OUT = os.path.join(_here, "..", "results", "cosserat")

ref, xi = int(params.uw_ref), float(params.uw_xi)
c, l_km, degree = float(params.uw_c), float(params.uw_l_km), int(params.uw_degree)
name = f"cosserat_ref{ref}_xi{xi:g}_c{c:g}_l{l_km:g}_P{degree}" + \
    ("" if str(params.uw_linear) == "exact" else f"_{params.uw_linear}") + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

S = cn.build_notch(ref, xi)
mesh, stokes, cm = S["mesh"], S["stokes"], S["cm"]
m = S["mat"].sym[0]

omega = uw.discretisation.MeshVariable("omega", mesh, 1, degree=degree, units="1/s")
ell = uw.expression(r"\ell", uw.quantity(l_km, "km"), "Cosserat length")
eta_c = c * (m * S["eta_bg"] + (1 - m) * S["eta_b"])
spin = stokes.Unknowns.W[1, 0]
grad_omega = omega.sym.jacobian(mesh.CoordinateSystem.N)

# The generalised invariant replaces the model's strain-rate invariant, so the yield
# viscosity (and everything built on it) sees the rotation gradient. Built from the
# raw symbolic form: assigning the expression to itself would nest it (#447).
edot_II = cm._strainrate_inv_II.sym
cm._strainrate_inv_II.sym = sympy.sqrt(
    edot_II ** 2 + ell ** 2 * (grad_omega * grad_omega.T)[0, 0] / 2)
cn.yield_stress_with_shift(S, 0)

stokes.add_coupled_field(
    omega,
    F0=4 * eta_c * (omega.sym[0] - spin),
    F1=2 * cm.viscosity * ell ** 2 * grad_omega,
    momentum_flux=2 * eta_c * (spin - omega.sym[0]) * sympy.Matrix([[0, -1], [1, 0]]),
)

seconds = cn.solve_newton(stokes, params.uw_budget, int(params.uw_monitor),
                          str(params.uw_linear))
report = stokes.solve_report
taylor = cn.taylor_slopes(stokes) if int(params.uw_taylor) else None
if taylor:
    uw.pprint(f"[taylor] remainders {taylor[0]}  slopes {taylor[1]}")

bands = cn.measure(S, OUT, name)
W = {k: (None if v is None else v.get("W_equiv_km")) for k, v in bands.items()}
omega_values = np.asarray(omega.array).ravel()
record = dict(
    ref=ref, xi=xi, c=c, l_km=l_km, omega_degree=degree, init="seed",
    reason=report.reason_str, converged=report.reason_str in cn.DONE,
    nl_its=report.nl_its, ksp_its=report.ksp_its, linear=str(params.uw_linear),
    seconds=seconds,
    h_min_km=float(mesh.get_min_radius()) * cn.H_KM,
    bands=bands, W_equiv_km=W,
    omega_range=[float(omega_values.min()), float(omega_values.max())],
    relative_rotation_range_strong=cn.strong_layer_range(S, spin - omega.sym[0]),
    viscosity_range_strong_Pas=cn.strong_layer_range(S, cm.viscosity),
    taylor=taylor,
)
uw.pprint(f"[cosserat] ref {ref} xi {xi} c {c} l {l_km} km P{degree}: {report.reason_str} "
          f"its {report.nl_its} ({seconds:.0f} s)  W_L/W_R {W}  omega {record['omega_range']}  "
          f"eta_eff strong {record['viscosity_range_strong_Pas']}")
cn.write(OUT, name, record, dict(v=S["v"], p=S["p"], omega=omega))
