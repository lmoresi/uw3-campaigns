"""Shared machinery for the notch runs with a coupled length-scale field.

The micromorphic and the Cosserat drivers differ only in the field they couple to the
flow. Both build the same notch (mesh1, 5e23, softmin/sqrt/onset, delta 0.1), solve it
with exact Newton (MUMPS LU of the Jacobian itself, the trap described in
newton_exact_linear.py) warm from the viscous seed, and measure the bands with the
campaign's estimator (band_width_vs_h.measure_bands).
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import notch_model as nm   # noqa: E402

ETA_BG, U_MMYR, H_KM, PHI = 1.0e23, 5.0, 30.0, 30.0
MESH = os.path.join(_here, "..", "meshes", "notch_mesh1.msh")
DONE = ("CONVERGED_FNORM_ABS", "CONVERGED_FNORM_RELATIVE", "CONVERGED_SNORM_RELATIVE")
LEVELS = [-0.7, -0.6, -0.5, -0.4]


def build_notch(ref, xi, seed=True, msh=None, weak_ramp=None, snap_arcs=False,
                ramp_scope="weak"):
    """The notch at refinement ``ref`` with the shipped yield law and xi as
    plastic_rate_strengthening; returns notch_model.build's dict. ``seed=False``
    skips the viscous seed solve (for loading saved fields)."""
    S = nm.build(msh or MESH, ETA_BG, U_MMYR, PHI, ref, xi=0.0, seed=seed,
                 p_degree=1, p_continuous=True, weak_ramp=weak_ramp, snap_arcs=snap_arcs, ramp_scope=ramp_scope)
    cm = S["cm"]
    cm.yield_mode = "softmin"
    cm.yield_smoother = "sqrt"
    cm.yield_anchor = "onset"
    cm.yield_softness = 0.1
    if xi > 0.0:
        cm.Parameters.plastic_rate_strengthening = uw.quantity(xi * ETA_BG, "Pa*s")
    return S


def yield_stress_with_shift(S, shift):
    """The notch's Drucker-Prager yield stress plus ``shift``, with the positive
    residual-strength floor 0.02 C (a shift may lower the flank yield stress)."""
    m = S["mat"].sym[0]
    s_min = 0.02 * S["C"]
    sigma_y = uw.maths.smooth_max(
        S["C_eff"] + np.sin(np.deg2rad(PHI)) * S["p"].sym[0] + shift, s_min, s_min)
    S["cm"].Parameters.yield_stress = m * sigma_y + (1 - m) * S["yield_none"]
    return sigma_y


def solve_newton(S, name, out_dir, budget, monitor, linear="exact"):
    """Consistent Newton; returns the wall time of the solve. The solve runs inside a
    model step, so the model's transcript (``<out_dir>/transcripts/<name>.jsonl``)
    records it, with its solve report, as the run's account.

    ``linear="exact"``: every linear solve an LU factorisation of J.
    ``linear="production"``: the notch's own solver (Schur fieldsplit, FMG on the
    velocity block, Eisenstat-Walker), with the coupled fields grouped into the
    velocity split by the solver. ``linear="production_tight"``: the same
    preconditioner, every linear solve to rtol 1e-8."""
    stokes = S["stokes"]
    model = S["model"]
    os.makedirs(os.path.join(out_dir, "transcripts"), exist_ok=True)
    model.transcript_file = os.path.join(out_dir, "transcripts", name + ".jsonl")
    stokes.consistent_jacobian = True
    stokes.petsc_options["snes_max_it"] = int(budget)
    if monitor:
        stokes.petsc_options["snes_monitor_short"] = None
        stokes.petsc_options["snes_linesearch_monitor"] = None
        stokes.petsc_options["ksp_converged_reason"] = None
    if monitor > 1:
        # the outer Krylov residual every iteration: tells a slow linear solve
        # from a stuck one when a Newton step goes quiet
        stokes.petsc_options["ksp_monitor_short"] = None
    if linear.startswith("production"):
        # the multigrid coarse level's direct solver: native LU unless the driver set
        # nm.COARSE_FACTOR (-uw_coarse mumps, measurements only). Native LU of a 3-D P2
        # coarse problem took 6.5 min per Newton step at 37k coarse dofs (2026-10-12),
        # so the 3-D answer is a genuinely coarse base.
        nm.set_coarse_factor(stokes)
    if linear.startswith("production_rtol") or linear.startswith("production_ew"):
        # inexact Newton, for time to solution. production_rtol<X>: every linear solve
        # to a fixed rtol X, no Eisenstat-Walker. production_ew<X>: Eisenstat-Walker
        # with its forcing capped at X (rtol0 = rtolmax = X); the uncapped default
        # (0.1-0.3) gave 15 / 57 / > 40 Newton steps at refs 1 / 2 / 3 (REPORT).
        x = float(linear.split("_rtol" if "_rtol" in linear else "_ew")[1])
        if "_rtol" in linear:
            stokes.petsc_options.delValue("snes_ksp_ew")
            stokes.petsc_options.delValue("snes_ksp_ew_version")
            stokes.petsc_options["ksp_rtol"] = x
        else:
            stokes.petsc_options["snes_ksp_ew"] = None
            stokes.petsc_options["snes_ksp_ew_rtol0"] = x
            stokes.petsc_options["snes_ksp_ew_rtolmax"] = x
        t0 = time.time()
        with model.step(0, label=name):
            stokes.solve(zero_init_guess=False)
        return time.time() - t0
    if linear in ("production", "production_tight"):
        if linear == "production_tight":
            # every Newton direction solved to a fixed, tight tolerance (no
            # Eisenstat-Walker): isolates the preconditioner from the inexact-Newton
            # forcing, so the Krylov count per step measures the preconditioner alone
            stokes.petsc_options.delValue("snes_ksp_ew")
            stokes.petsc_options.delValue("snes_ksp_ew_version")
            stokes.petsc_options["ksp_rtol"] = 1.0e-8
        t0 = time.time()
        with model.step(0, label=name):
            stokes.solve(zero_init_guess=False)
        return time.time() - t0
    stokes.saddle_preconditioner = 0

    solve = uw.systems.Stokes._snes_solve_with_retries

    def exact_linear(self, gvec, divergence_retries=0, verbose=False):
        ksp = self.snes.getKSP()
        J, _ = ksp.getOperators()
        ksp.setOperators(J, J)            # factor the operator itself, not the Schur Pmat
        ksp.setType("preonly")
        pc = ksp.getPC()
        pc.setType("lu")
        pc.setFactorSolverType("mumps")
        return solve(self, gvec, divergence_retries=divergence_retries, verbose=verbose)

    uw.systems.Stokes._snes_solve_with_retries = exact_linear
    t0 = time.time()
    with model.step(0, label=name):
        stokes.solve(zero_init_guess=False)
    return time.time() - t0


def taylor_slopes(solver, steps=(1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)):
    """Remainder |F(x + s d) - F(x) - s J d| against s at the current iterate, for a
    random direction d scaled to x. Slope 2 means the assembled J is F's derivative."""
    solver._set_newton_alpha(1.0)
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


STATIONS = [-0.7, -0.6, -0.5, -0.4, 0.4, 0.5, 0.6, 0.7]     # x / H, i.e. +-12..21 km


def _band_module():
    spec = importlib.util.spec_from_file_location(
        "bw", os.path.join(_here, "band_width_vs_h.py"))
    argv, sys.argv = sys.argv, [sys.argv[0]]
    # its uw.Params read the PETSc options database, not sys.argv: hide the
    # driver's -uw_mesh (a path) from its own -uw_mesh (an integer index)
    from petsc4py import PETSc
    opts = PETSc.Options()
    mesh_opt = opts.getString("uw_mesh", None)
    if mesh_opt is not None:
        opts.delValue("uw_mesh")
    bw = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(bw)
    finally:
        sys.argv = argv
        if mesh_opt is not None:
            opts.setValue("uw_mesh", mesh_opt)
    return bw


def measure(S, out_dir, name):
    """Band widths per side (km) from horizontal cuts (the campaign's older estimator)
    and from vertical cuts at |x| = 12..21 km (the settled one, one limb per cut), and
    the peak of edot_II over the far-field background on the vertical cuts (a ratio,
    free of the units edot_II comes back in). The raw profiles are saved."""
    bw = _band_module()
    os.makedirs(out_dir, exist_ok=True)
    horizontal = bw.measure_bands(S, LEVELS, 4001, 1.85, H_KM,
                                  profile_out=os.path.join(out_dir, f"profiles_{name}.npz"))
    vertical = bw.measure_bands_vertical(S, STATIONS, 4001, 0.68, H_KM,
                                         profile_out=os.path.join(out_dir, f"vprofiles_{name}.npz"))
    y = np.linspace(-0.68, -0.02, 4001)
    peaks = {}
    for side, stations in (("L", STATIONS[:4]), ("R", STATIONS[4:])):
        ratios = []
        for xs in stations:
            coords = np.column_stack([np.full_like(y, xs), y])
            f = np.asarray(uw.function.global_evaluate(S["stokes"].Unknowns.Einv2, coords)).ravel()
            base = np.median(f)
            ratios.append((f.max() - base) / base)
        peaks[side] = float(np.mean(ratios))
    width = lambda bands: {k: (None if v is None else v["W_equiv_km"]) for k, v in bands.items()}
    return dict(W_horizontal_km=width(horizontal), W_vertical_km=width(vertical),
                W_integral_km=integral_width(S), relative_peak=peaks,
                bands_horizontal=horizontal, bands_vertical=vertical)


DIP_DEG = 37.5      # the limbs' measured dip; perpendicular width = cut width * cos(dip)
WINDOW_KM = 6.0


def canonical_run(ref, l_km, beta=0.1, xi=0, model="micromorphic"):
    """The checkpoint name of the run that stands for (ref, l) in the tables: exact
    Newton at refs 1-3, tight FMG grid-sequenced at ref 4 (micromorphic: serial, and
    inexact Newton at l = 0.25 km; Cosserat: np 8) and at ref 5 (np 16). Cosserat is
    c = 1, omega in P1 (``beta`` is ignored)."""
    if model == "cosserat":
        base = f"cosserat_ref{ref}_xi{xi:g}_c1_l{l_km:g}_P1"
        suffix = {1: "", 2: "", 3: "", 4: "_production_tight_np8",
                  5: "_production_tight_np16"}[ref]
        return base + suffix
    base = f"micro_ref{ref}_xi{xi:g}_beta{beta:g}_l{l_km:g}"
    suffix = {1: "", 2: "", 3: "", 4: "_production_tight", 5: "_production_tight_np16"}[ref]
    if ref == 4 and l_km == 0.25:
        suffix = "_production_np2"
    return base + suffix


def integral_width(S, window_km=WINDOW_KM, background="cut", z_km=None):
    """The band width with no support cut-off: on each vertical cut, the area of
    edot_II above the far-field background within +-``window_km`` of the peak, over the
    peak height, times cos(dip) for the band-normal width; the median over the cuts.
    ``background="cut"``: the median over the whole cut; ``"outside"``: the median over
    the part of the cut outside the window (falls back to the whole cut where the
    window covers it). The cut spans y = -20.4 .. -0.6 km, so a window much wider than
    +-6 km reaches the cut's ends. On the extruded (3-D) notch the cuts lie in the
    plane z = ``z_km``.
    The equivalent width stops its support at 10% of the peak, and on these profiles
    (a long tail on the upper side) that cut-off moves by +-0.5 km between limbs and
    refinements; this measure does not. The spread between cuts is real: the limb
    widens toward the surface."""
    y = np.linspace(-0.68, -0.02, 4001)
    y_km = y * H_KM
    widths, peaks = [], []
    for xs in STATIONS:
        coords = np.column_stack([np.full_like(y, xs), y])
        if z_km is not None:
            coords = np.column_stack([coords, np.full_like(y, z_km / H_KM)])
        f = np.asarray(uw.function.global_evaluate(S["stokes"].Unknowns.Einv2, coords)).ravel()
        i = int(np.argmax(f - np.median(f)))
        window = np.abs(y_km - y_km[i]) < window_km
        outside = f[~window] if (background == "outside" and (~window).sum() > 20) else f
        g = f - np.median(outside)
        widths.append(np.trapezoid(np.clip(g[window], 0, None), y_km[window]) / g[i])
        peaks.append(g[i] / (f[i] - g[i]))           # (max - background) / background
    widths = np.asarray(widths) * np.cos(np.deg2rad(DIP_DEG))
    return dict(median=float(np.median(widths)), spread=float(widths.max() - widths.min()),
                peak_over_background=float(np.median(peaks)))


def floor_bound_over_floor(S, chi, beta):
    """Lower bound of the micromorphic yield argument over the residual-strength floor,
    min over the strong layer of (C + sin(phi) p - H chi) / (0.02 C), non-dimensional
    (stress by eta_bg V/H, rate by V/H). The argument C_eff + sin(phi) p + H (e - chi)
    is at least this, since e >= 0 and C_eff >= C. Collective: the minimum is a P1
    variable's global min. A value above 1 means the floor cannot engage anywhere."""
    rate = U_MMYR * 1.0e-3 / (365.25 * 24 * 3600) / (H_KM * 1.0e3)
    stress = ETA_BG * rate
    mesh = S["mesh"]
    bound = uw.discretisation.MeshVariable("floor_bound", mesh, 1, degree=1)
    p = np.asarray(S["p"].array).ravel()
    chi_nd = np.asarray(chi.array).ravel() / rate
    strong = np.asarray(bound.coords)[:, 1] > -0.7 * H_KM * 1.0e3
    values = (1.0e8 / stress + np.sin(np.deg2rad(PHI)) * p - beta * chi_nd) / (0.02 * 1.0e8 / stress)
    bound.array[:, 0, 0] = np.where(strong, values, np.inf)
    return float(bound.min())


def strong_layer_range(S, expression):
    """Min and max of ``expression`` over the strong layer, at the P1 nodes. Each rank
    evaluates at its own nodes (exact there, so the rank-local evaluate is right), and
    the extremes are the collective min / max of a scratch P1 variable."""
    scratch = uw.discretisation.MeshVariable("range_scratch", S["mesh"], 1, degree=1)
    nodes = scratch.coords
    strong = np.asarray(uw.function.evaluate(S["mat"].sym[0], nodes)).ravel() > 0.5
    values = np.asarray(uw.function.evaluate(expression, nodes)).ravel()
    scratch.array[:, 0, 0] = np.where(strong, values, np.inf)
    lowest = float(scratch.min())
    scratch.array[:, 0, 0] = np.where(strong, values, -np.inf)
    return [lowest, float(scratch.max())]


def load_coarse(path, coarse_ref, xi, extra=None, msh=None, weak_ramp=None, snap_arcs=False,
                ramp_scope="weak"):
    """A coarser run's checkpoint (``write``'s ``write_timestep`` output, path without
    the ``.mesh...`` suffix) on a rebuilt coarse notch, for ``prolong``. The checkpoint
    is remapped by coordinates, so any decomposition, serial or parallel, reads it.
    ``extra`` maps the names of coupled fields to (components, degree, continuous, units).

    Call this BEFORE building the fine notch: named expressions are shared between
    builds in one process (#767), so a coarse build made after the fine one rebinds
    the fine solver's strain-rate invariant to the coarse velocity."""
    coarse = build_notch(coarse_ref, xi, seed=False, msh=msh, weak_ramp=weak_ramp,
                         snap_arcs=snap_arcs, ramp_scope=ramp_scope)
    fields = dict(v=coarse["v"], p=coarse["p"])
    for key, (components, degree, continuous, units) in (extra or {}).items():
        fields[key] = uw.discretisation.MeshVariable(
            f"{key}_coarse", coarse["mesh"], components, degree=degree,
            continuous=continuous, units=units)
    directory, name = os.path.split(path)
    names = dict(v=coarse["v"].name, p=coarse["p"].name)
    for key, var in fields.items():
        var.read_timestep(name, names.get(key, key), 0, outputPath=directory)
    return fields


def prolong(coarse_fields, fine_fields):
    """Set each fine field from its coarse counterpart. The notch meshes are nested
    (each refinement splits the previous one), so the coarse P2 velocity and P1
    pressure / coupled fields are exactly representable on the fine mesh: evaluating
    the coarse finite-element interpolant at the fine nodes is an exact transfer."""
    for key, fine in fine_fields.items():
        # fine.coords is unit-aware (metres); evaluate converts it to model units.
        # A plain np.asarray would be read as model coordinates and miss the domain.
        values = uw.function.global_evaluate(coarse_fields[key].sym, fine.coords)
        fine.array[...] = values.reshape(fine.array.shape)


def write(out_dir, name, record, fields, mesh):
    """The run's record as json and its fields as a checkpoint
    (``<out_dir>/checkpoints/<name>``, ``write_timestep``): collective, and readable on
    any decomposition by ``load_coarse`` and the measuring and rendering scripts."""
    os.makedirs(os.path.join(out_dir, "checkpoints"), exist_ok=True)
    mesh.write_timestep(name, 0, outputPath=os.path.join(out_dir, "checkpoints"),
                        meshVars=list(fields.values()), create_xdmf=False)
    with uw.selective_ranks(0) as rank0:  # the body runs on every rank: test the flag
        if rank0:
            with open(os.path.join(out_dir, name + ".json"), "w") as fh:
                json.dump(record, fh, indent=1, default=float)
