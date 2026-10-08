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
H, not with the viscosity contrast.

Exact linear solves (MUMPS LU of the Jacobian itself, see newton_exact_linear.py),
consistent Newton, warm from the viscous seed with chi = 0. Band widths with the
campaign's estimator (band_width_vs_h.measure_bands).

Usage: python -u micromorphic_notch.py -uw_ref 1 -uw_xi 0.01 -uw_beta 0.01 -uw_l_km 1
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np
import sympy
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import notch_model as nm   # noqa: E402

params = uw.Params(
    uw_ref=uw.Param(1, description="refinement"),
    uw_xi=uw.Param(0.01, description="xi (eta_reg = xi * eta_bg)"),
    uw_beta=uw.Param(0.01, description="H / eta_bg"),
    uw_l_km=uw.Param(1.0, description="micromorphic length l in km"),
    uw_budget=uw.Param(60, description="Newton iteration cap"),
    uw_tag=uw.Param("", description="suffix for the output files"),
    uw_monitor=uw.Param(1, description="1 = SNES and line-search monitors"),
    uw_taylor=uw.Param(0, description="1 = Taylor test of the coupled Jacobian at the "
                                      "final iterate (slope 2 = exact tangent)"),
)
ETA_BG, U_MMYR, H_KM, PHI = 1.0e23, 5.0, 30.0, 30.0
MESH = os.path.join(_here, "..", "meshes", "notch_mesh1.msh")
OUT = os.path.join(_here, "..", "results", "micromorphic")
DONE = ("CONVERGED_FNORM_ABS", "CONVERGED_FNORM_RELATIVE", "CONVERGED_SNORM_RELATIVE")

ref, xi = int(params.uw_ref), float(params.uw_xi)
beta, l_km = float(params.uw_beta), float(params.uw_l_km)
name = f"micro_ref{ref}_xi{xi:g}_beta{beta:g}_l{l_km:g}" + \
    (f"_{params.uw_tag}" if str(params.uw_tag) else "")

S = nm.build(MESH, ETA_BG, U_MMYR, PHI, ref, xi=0.0, seed=True,
             p_degree=1, p_continuous=True)
mesh, stokes, cm = S["mesh"], S["stokes"], S["cm"]
cm.yield_mode = "softmin"
cm.yield_smoother = "sqrt"
cm.yield_anchor = "onset"
cm.yield_softness = 0.1
if xi > 0.0:
    cm.Parameters.plastic_rate_strengthening = uw.quantity(xi * ETA_BG, "Pa*s")

# ---- the micromorphic field and its coupling ---------------------------------------
m = S["mat"].sym[0]
e = stokes.Unknowns.Einv2
chi = uw.discretisation.MeshVariable("chi", mesh, 1, degree=1, units="1/s")
H = uw.expression(r"H_{\chi}", uw.quantity(beta * ETA_BG, "Pa*s"), "micromorphic modulus")
ell = uw.expression(r"\ell", uw.quantity(l_km, "km"), "micromorphic length")
stokes.add_coupled_field(
    chi,
    F0=H * (chi.sym[0] - m * e),
    F1=H * ell ** 2 * chi.sym.jacobian(mesh.CoordinateSystem.N),
)

s_min = 0.02 * S["C"]
shift = m * H * (e - chi.sym[0])
sigma_y = uw.maths.smooth_max(S["C_eff"] + np.sin(np.deg2rad(PHI)) * S["p"].sym[0] + shift,
                              s_min, s_min)
cm.Parameters.yield_stress = m * sigma_y + (1 - m) * S["yield_none"]

# ---- exact Newton --------------------------------------------------------------------
stokes.consistent_jacobian = True
stokes.saddle_preconditioner = 0
stokes.petsc_options["snes_max_it"] = int(params.uw_budget)
if int(params.uw_monitor):
    stokes.petsc_options["snes_monitor_short"] = None
    stokes.petsc_options["snes_linesearch_monitor"] = None

_solve = uw.systems.Stokes._snes_solve_with_retries


def _exact_linear(self, gvec, divergence_retries=0, verbose=False):
    ksp = self.snes.getKSP()
    J, _ = ksp.getOperators()
    ksp.setOperators(J, J)            # factor the operator itself, not the Schur Pmat
    ksp.setType("preonly")
    pc = ksp.getPC()
    pc.setType("lu")
    pc.setFactorSolverType("mumps")
    return _solve(self, gvec, divergence_retries=divergence_retries, verbose=verbose)


uw.systems.Stokes._snes_solve_with_retries = _exact_linear
t0 = time.time()
stokes.solve(zero_init_guess=False)
seconds = time.time() - t0
report = stokes.solve_report


def taylor_slopes(solver, steps=(1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)):
    """Remainder |F(x + s d) - F(x) - s J d| against s at the current iterate, for a
    random direction d scaled to x. Slope 2 means the assembled J is F's derivative."""
    snes = solver.snes
    x = solver.dm.getGlobalVec()
    solver._gather_fields_to_global(x)
    rng = np.random.default_rng(0)
    d = x.duplicate()
    d.array[:] = rng.standard_normal(x.getLocalSize()) * (np.abs(x.array).max() or 1.0)
    J, P, _ = snes.getJacobian()
    snes.computeJacobian(x, J, P)
    Jd = x.duplicate()
    J.mult(d, Jd)
    F0 = x.duplicate()
    snes.computeFunction(x, F0)
    remainders = []
    for step in steps:
        xs = x.duplicate()
        xs.waxpy(step, d, x)
        Fs = x.duplicate()
        snes.computeFunction(xs, Fs)
        remainders.append(float(np.linalg.norm(Fs.array - F0.array - step * Jd.array)))
    return remainders, list(np.diff(np.log(remainders)) / np.diff(np.log(steps)))


taylor = None
if int(params.uw_taylor):
    stokes._set_newton_alpha(1.0)
    taylor = taylor_slopes(stokes)
    uw.pprint(f"[taylor] remainders {taylor[0]}  slopes {taylor[1]}")

# ---- measurements --------------------------------------------------------------------
spec = importlib.util.spec_from_file_location("bw", os.path.join(_here, "band_width_vs_h.py"))
sys.argv = [sys.argv[0]]
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
os.makedirs(OUT, exist_ok=True)
bands = bw.measure_bands(S, [-0.7, -0.6, -0.5, -0.4], 4001, 1.85, H_KM,
                         profile_out=os.path.join(OUT, f"profiles_{name}.npz"))
W = {k: (None if v is None else v.get("W_equiv_km")) for k, v in bands.items()}

nodes = mesh.X.coords
strong = np.asarray(uw.function.evaluate(m, nodes)).ravel() > 0.5
yield_nodes = np.asarray(uw.function.evaluate(sigma_y, nodes)).ravel()
shift_nodes = np.asarray(uw.function.evaluate(shift, nodes)).ravel()
chi_values = np.asarray(chi.array).ravel()
stress_scale = float(nm._stress_scale(ETA_BG, U_MMYR, H_KM))

out = dict(
    ref=ref, xi=xi, beta=beta, l_km=l_km, init="seed",
    reason=report.reason_str, converged=report.reason_str in DONE,
    nl_its=report.nl_its, seconds=seconds,
    h_min_km=float(mesh.get_min_radius()) * H_KM,
    bands=bands, W_equiv_km=W,
    chi_range=[float(chi_values.min()), float(chi_values.max())],
    min_yield_stress_strong=float(np.nanmin(yield_nodes[strong])),
    shift_range_strong=[float(np.nanmin(shift_nodes[strong])),
                        float(np.nanmax(shift_nodes[strong]))],
    stress_scale_Pa=stress_scale,
    taylor=taylor,
)
uw.pprint(f"[micromorphic] ref {ref} xi {xi} beta {beta} l {l_km} km: {report.reason_str} "
          f"its {report.nl_its} ({seconds:.0f} s)  W_L/W_R {W}  chi {out['chi_range']}  "
          f"min sigma_y {out['min_yield_stress_strong']:.3g}")
if uw.mpi.rank == 0:
    with open(os.path.join(OUT, name + ".json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    np.savez_compressed(
        os.path.join(OUT, f"fields_{name}.npz"),
        v=np.asarray(S["v"].array), v_coords=np.asarray(S["v"].coords),
        p=np.asarray(S["p"].array), p_coords=np.asarray(S["p"].coords),
        chi=np.asarray(chi.array), chi_coords=np.asarray(chi.coords))
