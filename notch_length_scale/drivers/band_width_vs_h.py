"""PHASE 2, EXPERIMENT 1 — does xi give a MESH-OBJECTIVE shear-band width?

This is the experiment the whole campaign has been pointing at and never ran. Every xi
measurement made here was SOLVER-SIDE (residual vs xi). Nobody measured the only thing
that decides whether xi is a physical regularisation: the BAND WIDTH as h -> 0.

--------------------------------------------------------------------------------------
WHY THIS IS THE RIGHT FIRST EXPERIMENT — the algebra (2026-08-06)
--------------------------------------------------------------------------------------
The literature rule (Duretz / de Borst / Le Pourhiet 2019-2023, verified in
REGULARISATION_SURVEY_2026-07-31.md) is that the rate-limiting damper must sit in
PARALLEL with the plastic slider, with the overstress acting on the PLASTIC strain rate:

    tau = tau_y + 2 eta_vp edot_pl                     (Kelvin / consistency)

and NOT on the total strain rate (Perzyna-shaped), which is what our xi appears to do:

    tau_y_eff = tau_y + 2 xi eta_bg edot_II            (ours)

The prior reading of this file's own memory was that ours is Perzyna-shaped and
therefore explains the mesh-dependence. THAT READING IS WRONG, and the reason matters.

Our problem is INSTANTANEOUS: no elasticity, so the element in series with the plastic
branch is the linear viscous dashpot eta_bg. Then edot_pl is an EXACTLY LINEAR function
of the total rate and the stress,

    edot_pl = edot - tau/(2 eta_bg),

and substituting into the consistency law with eta_vp = xi*eta_bg:

    tau = tau_y + 2 xi eta_bg (edot - tau/(2 eta_bg))
    tau (1 + xi) = tau_y + 2 xi eta_bg edot
    tau = [tau_y + 2 xi eta_bg edot] / (1 + xi)

The bracket is EXACTLY our law. So in the absence of elasticity the plastic-rate and
total-rate forms differ ONLY by the constant factor (1 + xi) — i.e. ours is the
consistency model with (tau_y, eta_vp) rescaled by 1/(1+xi). At xi <= 0.3 that is at
most a 30% reparameterisation of two constants we choose anyway.

  ==> The Perzyna/Kelvin distinction, decisive in the papers, COLLAPSES here. It bites
      only when the series element is ELASTIC, because then edot_pl involves the stress
      HISTORY (tau - tau_old)/(2 G dt) rather than tau itself. Our xi already IS a
      consistency viscoplastic model. The "second arm" proposed in the handoff
      (plastic-rate vs total-rate) is provably null and is NOT run.

Dimensional consequence, which is what makes this experiment falsifiable. Scale lengths
by H, velocity by V, viscosity by eta_bg. Incompressible Stokes with eta(edot, p, x) then
contains NO length but H itself, and exactly two dimensionless groups: xi, and
tau_y* = tau_y H / (eta_bg V). Any band width the regularised problem admits must be

    W / H = f(xi, tau_y*),   and the literature's D_c ~ eta_vp V / C  ==>  W/H ~ xi / tau_y*

So the SHARP PREDICTIONS this driver tests are:
  (P1) at fixed xi > 0, W converges to a CONSTANT as h -> 0        [mesh objectivity]
  (P2) that constant is LINEAR IN xi                               [the length is xi's]
  (P3) at xi = 0, W tracks h and never converges                   [the negative control]
P3 is the control that stops (P1) from being true by construction — if the xi = 0 column
also converges, the measurement is resolving nothing and the driver is wrong.

--------------------------------------------------------------------------------------
METHOD NOTES THAT ARE NOT OPTIONAL
--------------------------------------------------------------------------------------
* DO NOT PROJECT edot BEFORE MEASURING A WIDTH. An L2 projection onto a continuous
  P1/P2 space carries its OWN smoothing length of order h, which is precisely the
  quantity under test: it would manufacture the h-dependence in the xi=0 control and
  smear it out of the xi>0 columns. Einv2 is sampled POINTWISE with
  uw.function.evaluate on a FIXED, resolution-independent set of sample points.
* THE EXISTING `loc` METRIC CANNOT DO THIS. It is the smallest fraction of CELLS
  carrying half the dissipation — cell-count weighted on a graded mesh, so it changes
  with h by construction (localisation_regime.py says so in its own docstring). It is
  reported here only as continuity with earlier rows, never as the width.
* The bands are INCLINED, so a horizontal cut overestimates the width by 1/sin(dip).
  The dip is measured from the peak's x-position across the sampling levels and the
  width is corrected to the band-perpendicular one. The correction is common to all
  rows, so it does not affect (P1)/(P3), but it makes the number physical.
* Widths are reported in km. A row whose solve did not converge is printed with its
  reason and must not be read as a measurement.

Usage (uw.Params is PETSc-style; `key=value` is SILENTLY IGNORED):
    python -u band_width_vs_h.py -uw_xis 0,0.05,0.1,0.2 -uw_refs 1,2,3
"""
import importlib.util
import json
import os
import time

import numpy as np

import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, f"{_here}/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nm = _load("notch_model")

params = uw.Params(
    uw_mesh=uw.Param(1, description="notch mesh index"),
    uw_refs=uw.Param("1,2,3", description="refinement levels (h halves each step)"),
    uw_xis=uw.Param("0,0.05,0.1,0.2", description="xi values; 0 is the control"),
    uw_point=uw.Param("2.5e23", description="eta*V operating point"),
    uw_levels=uw.Param("-0.70,-0.60,-0.50,-0.40",
                       description="non-dim depths y at which to cut the bands"),
    uw_nsample=uw.Param(4001, description="sample points per cut (fixed across h)"),
    uw_xspan=uw.Param(1.85, description="cuts span x in [-xspan, xspan]"),
    uw_budget=uw.Param(40, description="nonlinear iteration cap"),
    uw_wall=uw.Param(400.0, description="wall seconds per nonlinear step"),
    uw_H=uw.Param(30.0, description="H in km — sets the km conversion"),
    uw_out=uw.Param("", description="results json (default: results/band_width_*.json)"),
    uw_pdeg=uw.Param(1, description="pressure degree: 1 = P1 (Taylor-Hood), 0 = P0"),
    uw_pcont=uw.Param(1, description="1 = continuous pressure, 0 = discontinuous. "
                                     "P2/P0 (-uw_pdeg 0 -uw_pcont 0) lets the pressure "
                                     "JUMP across the band; DP yield reads p, so a "
                                     "continuous pressure smears the yield strength."),
    uw_floor=uw.Param(0.0, description="shear_viscosity_min as a fraction of eta_bg, "
                                       "active in the STRONG layer only. 0 = off (the "
                                       "old default). Its job is to stop eta reaching "
                                       "ZERO where tau_y is clamped to zero in tension: "
                                       "that is a singular operator, and it is what ended "
                                       "the ref=3 rows of this experiment in "
                                       "DIVERGED_LINEAR_SOLVE (underworld3#759). ⚠️ It "
                                       "must be verified INACTIVE in the band before any "
                                       "width from a floored run is quoted — a binding "
                                       "floor IS a regularisation (it is xi in min-form) "
                                       "and would be measuring itself."),
    uw_hardmin=uw.Param(0, description="1 = force yield_mode='min' (the SHARP law). "
                                       "See the note below — this is a CONTROL, not a "
                                       "tuning knob."),
    # ---- 2026-10-06 recipe scan (PR #794): the shipped defaults and controls
    uw_law=uw.Param("", description="'' = legacy (uw_hardmin decides); 'min' = exact Min; "
                                    "'default' = the library default (softmin, sqrt, "
                                    "anchor onset, delta 0.1); 'powermean' = nm.build's"),
    uw_route=uw.Param("newton", description="newton = consistent tangent from the seed "
                                            "(legacy); blend = consistent_jacobian="
                                            "'continuation'; ladder = solve(homotopy="
                                            "'rate_strengthening') on the declared eta_reg"),
    uw_etareg=uw.Param(0, description="1 = xi enters as the library's "
                                      "Parameters.plastic_rate_strengthening = xi*eta_bg "
                                      "(notch xi field left at 0); 0 = the notch xi field"),
    uw_tag=uw.Param("", description="suffix for the profile files"),
    uw_monitor=uw.Param(0, description="1 = SNES monitor (one line per nonlinear iteration)"),
    uw_pcoupling=uw.Param(1, description="0 = partial Newton: the tangent's pressure "
                                        "column from the frozen-viscosity flux (J_vp = -B^T)"),
    uw_lsmon=uw.Param(0, description="1 = line-search monitor (step length per Newton step)"),
    uw_mf=uw.Param(0, description="1 = snes_mf_operator: the Newton operator is the "
                                "residual's finite-difference derivative, the assembled "
                                "tangent only its preconditioner"),
    uw_ew=uw.Param(1, description="0 = Eisenstat-Walker off: fixed linear tolerance "
                               "(the solver's ksp_rtol) every Newton step"),
    uw_fields=uw.Param("", description="directory: also save the mesh triangulation and the "
                                     "nodal strain-rate invariant (npz) for rendering"),
)

# ⚠️ THE SECOND REGULARISATION (found 2026-08-06)
# `notch_model.build` leaves the model on yield_mode="softmin" with the POWERMEAN
# family, and `_combine_yield`'s own docstring says that family is NOT exact Min at
# δ = 0: its sharpness saturates at s = 1/(δ+0.001) = 1000, approaching Min only to
# ~0.3%. The campaign's controller harness overrode this to yield_mode="min"; this
# driver did not, which is why its rows converge in 6 Newton iterations where the
# campaign stalled at 40 on the same point.
# That is a SECOND regularisation running beside xi, and the experiment asks whether
# xi sets a length — so it must be controlled, not assumed harmless. The claim on
# record that the difference is unobservable was measured on the RESIDUAL (6e-10,
# inside solver tolerance), never on a BAND WIDTH. Run -uw_hardmin 1 as the control
# and compare widths; only if they agree is the smooth law safe to measure on.

POINTS = {"2.5e23": (1.0e23, 2.5), "5e23": (1.0e23, 5.0), "1.25e24": (1.0e23, 12.5)}
DONE = ("CONVERGED_FNORM_ABS", "CONVERGED_FNORM_RELATIVE", "CONVERGED_SNORM_RELATIVE")


# ----------------------------------------------------------------------------------
# The width diagnostic
# ----------------------------------------------------------------------------------
def _peak_width(x, f, side):
    """Width of the dominant peak of f(x) on one side of the notch.

    Returns (x_peak, W_equiv, W_gauss_fwhm, amplitude) in the units of x, or None if
    there is no peak worth measuring. Two independent widths are returned because they
    fail differently: the equivalent width is fit-free but sensitive to the choice of
    support, the Gaussian FWHM matches Duretz's published protocol but assumes a shape.
    """
    m = (x < 0) if side == "L" else (x > 0)
    if m.sum() < 20:
        return None
    xs, fs = x[m], f[m]

    # Far-field baseline: the profile away from the bands. The median over the whole cut
    # is dominated by unyielded material, which is what "background" means here.
    base = float(np.median(f))
    amp = float(fs.max()) - base
    if amp <= 0 or not np.isfinite(amp):
        return None
    i = int(np.argmax(fs))

    # Support = walk out from the peak until the profile falls to 10% of the peak's
    # height above baseline, or turns back up (the start of the neighbouring structure).
    thr = base + 0.10 * amp
    lo = i
    while lo > 0 and fs[lo - 1] < fs[lo] and fs[lo - 1] > thr:
        lo -= 1
    hi = i
    while hi < len(fs) - 1 and fs[hi + 1] < fs[hi] and fs[hi + 1] > thr:
        hi += 1
    if hi - lo < 4:
        return None

    xw, fw = xs[lo:hi + 1], fs[lo:hi + 1] - base
    w_equiv = float(np.trapezoid(fw, xw) / amp)

    # Gaussian via a log-parabola on the upper part of the peak — no scipy, no
    # initial guess, and it degrades to nan rather than to a wrong number.
    sel = fw > 0.25 * amp
    w_gauss = float("nan")
    if sel.sum() >= 5:
        try:
            c = np.polyfit(xw[sel] - xs[i], np.log(fw[sel]), 2)
            if c[0] < 0:
                sigma = 1.0 / np.sqrt(-2.0 * c[0])
                w_gauss = float(2.0 * np.sqrt(2.0 * np.log(2.0)) * sigma)
        except (ValueError, np.linalg.LinAlgError):
            pass

    return float(xs[i]), w_equiv, w_gauss, amp


def measure_bands_vertical(S, stations, nsample, yspan, H_km, profile_out=None):
    """Cut each limb of the conjugate pair on a VERTICAL line at fixed x.

    Louis, 2026-09-20: *"You would be better doing vertical cuts to catch those bands."*

    Why vertical. The limbs rise from the notch at roughly +-45 degrees, so a vertical and
    a horizontal cut are equally oblique to a band and need the same dip correction — but
    they differ in WHAT THEY CATCH. The horizontal cuts sat at y = -0.70 .. -0.40, low
    down where the two limbs are still close to their crossing point at the notch, so one
    cut crosses BOTH limbs and the estimator has to separate them (and, measured, could
    not: the two sides disagreed by 40% and the l=0 control never collapsed). A vertical
    line at fixed |x| away from the notch crosses exactly ONE limb, where it is well
    separated from its partner and from the corner field.

    `stations` are x positions (non-dimensional). Negative x samples the left limb,
    positive the right.
    """
    einv2 = S["stokes"].Unknowns.Einv2
    y = np.linspace(-yspan, -0.02, int(nsample))
    out_rows = {"L": [], "R": []}
    prof = []
    for xs in stations:
        coords = np.column_stack([np.full_like(y, xs), y])
        # global_evaluate: the cut crosses every rank's part of the mesh (evaluate is
        # rank-local and extrapolates points owned elsewhere)
        f = np.asarray(uw.function.global_evaluate(einv2, coords)).ravel()
        f = np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0)
        prof.append(f)
        side = "L" if xs < 0 else "R"
        # _peak_width takes (coordinate, field, side); on a vertical cut the coordinate
        # is y and there is a single peak, so the side argument only selects which half
        # of the profile to search — pass the whole line by asking for the dominant peak.
        # The whole cut lies at y < 0, so search it all ("L" selects y < 0). Passing the
        # station's side here searched y > 0 for the right limb, i.e. nothing, and the
        # right limb was never measured (found 2026-10-09).
        got = _peak_width(y, f, "L")
        if got is not None:
            out_rows[side].append((xs,) + got)

    if profile_out is not None and uw.mpi.rank == 0:
        os.makedirs(os.path.dirname(profile_out), exist_ok=True)
        np.savez_compressed(profile_out, y=y, stations=np.asarray(stations),
                            edot_II=np.asarray(prof), H_km=H_km, cut="vertical")

    res = {}
    for side, rows in out_rows.items():
        if len(rows) < 2:
            res[side] = None
            continue
        arr = np.array(rows)                       # x, y_peak, W_eq, W_g, amp
        # Dip from the peak track, now dy/dx along the limb.
        m = float(np.polyfit(arr[:, 0], arr[:, 1], 1)[0])
        # A band dipping at alpha to the horizontal is intersected over w/sin(alpha) by a
        # HORIZONTAL cut and w/cos(alpha) by a VERTICAL one. With m = dy/dx along the limb,
        # tan(alpha) = |m|, so the vertical cut's correction is cos(alpha) = 1/sqrt(1+m^2).
        # (The horizontal routine below uses m = dx/dy, where the same expression evaluates
        # to sin(alpha) — the two are not interchangeable and an earlier draft here had
        # them swapped.)
        #
        # ⚠️ THE MEASURED DIP IS A SANITY CHECK, NOT JUST BOOKKEEPING. For Drucker-Prager
        # in compression with phi = 30 deg, psi = 0, the predicted band orientations from
        # the maximum-compression (horizontal) direction are Coulomb 45 - phi/2 = 30 deg,
        # Arthur 45 - (phi+psi)/4 = 37.5 deg, Roscoe 45 - psi/2 = 45 deg. A fitted dip
        # outside roughly 25-50 deg means the peak track is not following a band and the
        # width taken from it means nothing.
        corr = 1.0 / np.sqrt(1.0 + m * m)
        res[side] = dict(
            n_cuts=len(rows),
            y_peak=float(np.median(arr[:, 1])),
            dip_deg=float(np.degrees(np.arctan2(abs(m), 1.0))),
            dip_ok=bool(25.0 <= float(np.degrees(np.arctan2(abs(m), 1.0))) <= 50.0),
            W_equiv_km=float(np.median(arr[:, 2]) * corr * H_km),
            W_fwhm_km=float(np.nanmedian(arr[:, 3]) * corr * H_km),
            W_equiv_spread_km=float(
                (np.max(arr[:, 2]) - np.min(arr[:, 2])) * corr * H_km),
            amp_max=float(np.max(arr[:, 4])),
        )
    return res


def measure_bands(S, levels, nsample, xspan, H_km, profile_out=None):
    """Cut the conjugate bands at several depths and return per-side widths in km.

    edot_II is sampled POINTWISE (see the module docstring — projecting first would
    impose the very length scale being measured).

    THE RAW PROFILES ARE ALWAYS SAVED (`profile_out`). A width is an ESTIMATOR applied
    to a profile, and the estimator is the cheap part: the solves behind a full scan are
    hours, so every alternative estimator must be re-runnable offline without re-solving.
    This was not optional — the first control row returned an equivalent width of 1.29 km
    with a Gaussian FWHM of 4.95 km, i.e. the two estimators disagreed by 4x on the same
    profile, and settling that from summary numbers alone is impossible.
    """
    einv2 = S["stokes"].Unknowns.Einv2
    x = np.linspace(-xspan, xspan, int(nsample))
    per_side = {"L": [], "R": []}
    prof = []
    for y in levels:
        coords = np.column_stack([x, np.full_like(x, y)])
        # global_evaluate: the cut crosses every rank's part of the mesh (evaluate is
        # rank-local and extrapolates points owned elsewhere)
        f = np.asarray(uw.function.global_evaluate(einv2, coords)).ravel()
        f = np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0)
        prof.append(f)
        for side in ("L", "R"):
            got = _peak_width(x, f, side)
            if got is not None:
                per_side[side].append((y,) + got)

    if profile_out is not None and uw.mpi.rank == 0:
        os.makedirs(os.path.dirname(profile_out), exist_ok=True)
        np.savez_compressed(profile_out, x=x, levels=np.asarray(levels),
                            edot_II=np.asarray(prof), H_km=H_km)

    out = {}
    for side, rows in per_side.items():
        if len(rows) < 2:
            out[side] = None
            continue
        arr = np.array(rows)                       # y, x_peak, W_eq, W_g, amp
        # Band dip from the peak track: a horizontal cut of a band inclined at angle
        # alpha to the horizontal is wider than the true perpendicular width by
        # 1/sin(alpha); with m = dx/dy along the track, sin(alpha) = 1/sqrt(1+m^2).
        m = float(np.polyfit(arr[:, 0], arr[:, 1], 1)[0])
        corr = 1.0 / np.sqrt(1.0 + m * m)
        out[side] = dict(
            n_cuts=len(rows),
            x_peak=float(np.median(arr[:, 1])),
            dip_deg=float(np.degrees(np.arctan2(1.0, abs(m)))) if m != 0 else 90.0,
            W_equiv_km=float(np.median(arr[:, 2]) * corr * H_km),
            W_fwhm_km=float(np.nanmedian(arr[:, 3]) * corr * H_km),
            W_equiv_spread_km=float(
                (np.max(arr[:, 2]) - np.min(arr[:, 2])) * corr * H_km),
            amp_max=float(np.max(arr[:, 4])),
        )
    return out


# ----------------------------------------------------------------------------------
def run_one(mesh_file, eta_bg, u, ref, xi, H_km, budget, wall, hardmin=False,
            p_degree=1, p_continuous=True):
    t0 = time.time()
    etareg = bool(int(params.uw_etareg))
    S = nm.build(mesh_file, eta_bg, u, 30.0, ref, xi=(0.0 if etareg else xi), seed=True,
                 p_degree=p_degree, p_continuous=p_continuous)
    st = S["stokes"]
    law = str(params.uw_law)
    if law == "min":
        hardmin = True
    elif law == "default":
        cm = S["cm"]
        cm.yield_mode = "softmin"; cm.yield_smoother = "sqrt"; cm.yield_anchor = "onset"
        cm.yield_softness = 0.1
    if etareg and xi > 0.0:
        S["cm"].Parameters.plastic_rate_strengthening = uw.quantity(xi * eta_bg, "Pa*s")
    # THE VISCOSITY FLOOR, off by default. `floor_var` is a live P0 field so this is a
    # data write, not a JIT recompile.
    if float(params.uw_floor) > 0.0:
        nm.set_floor(S, float(params.uw_floor))
    if hardmin:
        S["cm"].yield_mode = "min"      # the SHARP law — see the note at the top
    st.guard(wall_per_step=float(wall))
    st.petsc_options["snes_max_it"] = int(budget)
    # Consistent Newton with the shipped auto warm-start (one Picard step from a cold
    # state, because the consistent tangent is NaN at edot = 0). This is the tangent the
    # `nonlinear-solver` skill prescribes for non-elastic Drucker-Prager.
    route = str(params.uw_route)
    if int(params.uw_monitor):
        st.petsc_options["snes_monitor_short"] = None
    if not int(params.uw_pcoupling):
        st.newton_pressure_coupling = False
    if int(params.uw_mf):
        st.petsc_options["snes_mf_operator"] = None
    if int(params.uw_lsmon):
        st.petsc_options["snes_linesearch_monitor"] = None
        st.petsc_options["ksp_converged_reason"] = None
    if not int(params.uw_ew):
        st.petsc_options.delValue("snes_ksp_ew")
        st.petsc_options.delValue("snes_ksp_ew_version")
    st.consistent_jacobian = "continuation" if route == "blend" else True
    n_hist = len(st._solve_history)
    ladder = None
    if route == "ladder" and xi > 0.0:
        ladder = st.solve(homotopy="rate_strengthening",
                          homotopy_options=dict(verbose=True, step_maxit=int(budget)))
    else:
        st.solve(zero_init_guess=False)
    rep = st.solve_report
    reps = list(st._solve_history)[n_hist:]
    return S, dict(
        ref=ref, xi=xi, law=(law or ("min" if hardmin else "powermean")), route=route,
        etareg=etareg,
        ncells=int(S["ncells"]),
        h_min_km=float(S["mesh"].get_min_radius()) * H_km,
        nl_its=int(getattr(rep, "nl_its", -1)),
        nl_total=int(sum(r.nl_its for r in reps)),
        ksp_total=int(sum(r.ksp_its for r in reps)),
        reduction=float(getattr(rep, "reduction", float("nan")) or float("nan")),
        ladder=(None if ladder is None else dict(
            reached_one=ladder["reached_one"], converged=ladder["converged"],
            rungs=[(float(m), int(r), int(i)) for m, r, i in ladder["rungs"]])),
        reason=str(getattr(rep, "reason_str", "?")),
        converged=(str(getattr(rep, "reason_str", "?")) in DONE
                   and (ladder is None or bool(ladder["converged"]))),
        seconds=time.time() - t0,
    )


def save_fields(S, outdir, name, info):
    """The mesh's own triangulation and the strain-rate invariant evaluated at its
    vertices (nodal, so a renderer interpolates within elements and nothing is
    resampled across element boundaries)."""
    import underworld3.visualisation as vis
    pvm = vis.mesh_to_pv_mesh(S["mesh"])
    pts = np.asarray(pvm.points)                      # metres
    # evaluate takes model coordinates (length unit H), as measure_bands' cuts do
    nd = pts[:, :2] / (float(params.uw_H) * 1.0e3)
    uw.pprint(f"fields: model-coordinate extent x [{nd[:, 0].min():.3f}, {nd[:, 0].max():.3f}] "
              f"y [{nd[:, 1].min():.3f}, {nd[:, 1].max():.3f}]")
    edot = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, nd)).ravel()
    eta = np.asarray(uw.function.evaluate(S["cm"].viscosity, nd)).ravel()
    uw.pprint(f"fields: edot_II range [{np.nanmin(edot):.3e}, {np.nanmax(edot):.3e}]")
    if uw.mpi.rank == 0:
        os.makedirs(outdir, exist_ok=True)
        np.savez_compressed(os.path.join(outdir, name + ".npz"), points=pts,
                            cells=np.asarray(pvm.cells), celltypes=np.asarray(pvm.celltypes),
                            edot_II=edot, viscosity=eta,
                            info=json.dumps({k: v for k, v in info.items() if k != "bands"}))


def main():
    refs = [int(v) for v in str(params.uw_refs).split(",") if v.strip()]
    xis = [float(v) for v in str(params.uw_xis).split(",") if v.strip()]
    levels = [float(v) for v in str(params.uw_levels).split(",") if v.strip()]
    H_km = float(params.uw_H)
    eta_bg, u = POINTS[str(params.uw_point)]
    mesh_file = f"{_here}/../meshes/notch_mesh{int(params.uw_mesh)}.msh"

    uw.pprint(f"band width vs h — eta*V = {eta_bg * u:.2e}, mesh {params.uw_mesh}, "
              f"refs {refs}, xis {xis}")
    uw.pprint(f"cuts at y = {levels} ({int(params.uw_nsample)} points, "
              f"x in +-{float(params.uw_xspan)})")

    # RESOLUTION IS THE OUTER LOOP so a complete xi column lands at each h before any
    # time is spent on the next h: P2 (linearity in xi) is then testable from the
    # cheapest rows, and a run stopped early still holds whole columns rather than
    # whole xi blocks with a hole in the h axis.
    rows = []
    for ref in refs:
        for xi in xis:
            hardmin = bool(int(params.uw_hardmin))
            pdeg, pcont = int(params.uw_pdeg), bool(int(params.uw_pcont))
            S, info = run_one(mesh_file, eta_bg, u, ref, xi, H_km,
                              int(params.uw_budget), float(params.uw_wall),
                              hardmin=hardmin, p_degree=pdeg, p_continuous=pcont)
            info["yield_mode"] = info.get("law", "min" if hardmin else "softmin/powermean")
            info["pressure"] = f"P{pdeg}{'' if pcont else 'disc'}"
            tag = ("_min" if hardmin else "") + ("" if (pdeg == 1 and pcont) else f"_P{pdeg}d") \
                + (f"_{params.uw_tag}" if str(params.uw_tag) else "")
            pout = (f"{_here}/../results/profiles_m{int(params.uw_mesh)}_"
                    f"{str(params.uw_point)}_xi{xi:g}_ref{ref}{tag}.npz")
            bands = measure_bands(S, levels, int(params.uw_nsample),
                                  float(params.uw_xspan), H_km, profile_out=pout)
            info["bands"] = bands
            info["profiles"] = os.path.basename(pout)
            if str(params.uw_fields):
                save_fields(S, str(params.uw_fields),
                            f"m{int(params.uw_mesh)}_{params.uw_point}_xi{xi:g}_ref{ref}{tag}", info)
            rows.append(info)
            wl = bands.get("L") or {}
            wr = bands.get("R") or {}
            uw.pprint(
                f"xi={xi:<5g} ref={ref}  cells={info['ncells']:>7d} "
                f"h_min={info['h_min_km']:.3f} km  nl={info['nl_its']:>3d} "
                f"[{info.get('law')}/{info.get('route')}] nl_tot={info.get('nl_total')} ksp={info.get('ksp_total')} "
                f"{'OK ' if info['converged'] else 'XX '}{info['reason']:<28s} "
                f"W_L={wl.get('W_equiv_km', float('nan')):.3f} "
                f"W_R={wr.get('W_equiv_km', float('nan')):.3f} km  "
                f"(fwhm {wl.get('W_fwhm_km', float('nan')):.3f}/"
                f"{wr.get('W_fwhm_km', float('nan')):.3f})  "
                f"{info['seconds']:.0f}s")
            del S

    out = str(params.uw_out) or (
        f"{_here}/../results/band_width_m{int(params.uw_mesh)}_"
        f"{str(params.uw_point)}{'_min' if int(params.uw_hardmin) else ''}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if uw.mpi.rank == 0:
        with open(out, "w") as fh:
            json.dump(dict(point=str(params.uw_point), mesh=int(params.uw_mesh),
                           levels=levels, rows=rows), fh, indent=2)
    uw.pprint(f"\nwrote {out}")

    # The verdict, stated the way the predictions were stated.
    #
    # h is quoted as the mesh MINIMUM radius, which on this graded mesh sits at the
    # notch tip and not in the band — so W/h is not meaningful in absolute terms. What
    # IS exact is that `refinement` halves h EVERYWHERE, so the successive ratio
    # W(ref)/W(ref+1) is the whole test:
    #     P1 (mesh objectivity, xi > 0):  ratio -> 1
    #     P3 (the control,      xi = 0):  ratio -> 2   (the band is h wide, whatever h is)
    uw.pprint("\n--- (P1)/(P3) width vs h ---")
    widths = {}
    for xi in xis:
        sel = sorted((r for r in rows if r["xi"] == xi and r["converged"]),
                     key=lambda r: r["ref"])
        ws = [float(np.nanmean([(r["bands"].get("L") or {}).get("W_equiv_km", np.nan),
                                (r["bands"].get("R") or {}).get("W_equiv_km", np.nan)]))
              for r in sel]
        widths[xi] = (sel, ws)
        txt = "  ".join(f"ref{r['ref']}:{w:.3f}km" for r, w in zip(sel, ws))
        rat = "  ratios " + ", ".join(f"{a / b:.2f}" for a, b in zip(ws, ws[1:])) \
            if len(ws) > 1 else ""
        uw.pprint(f"xi={xi:<6g} {txt}{rat}")

    # P2: at the finest resolution reached, is the converged width linear in xi?
    fine = {}
    for xi, (sel, ws) in widths.items():
        if sel:
            fine[xi] = ws[-1]
    nz = sorted(k for k in fine if k > 0)
    if len(nz) > 1:
        uw.pprint("\n--- (P2) is the width linear in xi? (finest resolution) ---")
        for xi in nz:
            uw.pprint(f"xi={xi:<6g} W={fine[xi]:.3f} km   W/xi={fine[xi] / xi:.2f} km")
        uw.pprint("P2 holds if W/xi is constant across the xi column.")


if __name__ == "__main__":
    main()
