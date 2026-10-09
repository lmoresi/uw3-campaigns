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


def build_notch(ref, xi, seed=True):
    """The notch at refinement ``ref`` with the shipped yield law and xi as
    plastic_rate_strengthening; returns notch_model.build's dict. ``seed=False``
    skips the viscous seed solve (for loading saved fields)."""
    S = nm.build(MESH, ETA_BG, U_MMYR, PHI, ref, xi=0.0, seed=seed,
                 p_degree=1, p_continuous=True)
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


def solve_newton(stokes, budget, monitor, linear="exact"):
    """Consistent Newton; returns the wall time of the solve.

    ``linear="exact"``: every linear solve an LU factorisation of J.
    ``linear="production"``: the notch's own solver (Schur fieldsplit, FMG on the
    velocity block, Eisenstat-Walker), with the coupled fields grouped into the
    velocity split by the solver. ``linear="production_tight"``: the same
    preconditioner, every linear solve to rtol 1e-8."""
    stokes.consistent_jacobian = True
    stokes.petsc_options["snes_max_it"] = int(budget)
    if monitor:
        stokes.petsc_options["snes_monitor_short"] = None
        stokes.petsc_options["snes_linesearch_monitor"] = None
        stokes.petsc_options["ksp_converged_reason"] = None
    if linear in ("production", "production_tight"):
        if linear == "production_tight":
            # every Newton direction solved to a fixed, tight tolerance (no
            # Eisenstat-Walker): isolates the preconditioner from the inexact-Newton
            # forcing, so the Krylov count per step measures the preconditioner alone
            stokes.petsc_options.delValue("snes_ksp_ew")
            stokes.petsc_options.delValue("snes_ksp_ew_version")
            stokes.petsc_options["ksp_rtol"] = 1.0e-8
        t0 = time.time()
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


def measure(S, out_dir, name):
    """Band widths per side (km) from horizontal cuts; the raw profiles are saved."""
    spec = importlib.util.spec_from_file_location(
        "bw", os.path.join(_here, "band_width_vs_h.py"))
    argv, sys.argv = sys.argv, [sys.argv[0]]
    bw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bw)
    sys.argv = argv
    os.makedirs(out_dir, exist_ok=True)
    return bw.measure_bands(S, LEVELS, 4001, 1.85, H_KM,
                            profile_out=os.path.join(out_dir, f"profiles_{name}.npz"))


def strong_layer_range(S, expression):
    """Min and max of ``expression`` at the mesh nodes of the strong layer."""
    nodes = S["mesh"].X.coords
    strong = np.asarray(uw.function.evaluate(S["mat"].sym[0], nodes)).ravel() > 0.5
    values = np.asarray(uw.function.evaluate(expression, nodes)).ravel()[strong]
    return [float(np.nanmin(values)), float(np.nanmax(values))]


def load_coarse(path, coarse_ref, xi, extra=None):
    """A coarser run's saved fields (``write``'s npz) on a rebuilt coarse notch, for
    ``prolong``. ``extra`` maps the names of coupled fields to their
    (components, degree, continuous, units).

    Call this BEFORE building the fine notch: named expressions are shared between
    builds in one process (#767), so a coarse build made after the fine one rebinds
    the fine solver's strain-rate invariant to the coarse velocity."""
    coarse = build_notch(coarse_ref, xi, seed=False)
    saved = np.load(path)
    fields = dict(v=coarse["v"], p=coarse["p"])
    for key, (components, degree, continuous, units) in (extra or {}).items():
        fields[key] = uw.discretisation.MeshVariable(
            f"{key}_coarse", coarse["mesh"], components, degree=degree,
            continuous=continuous, units=units)
    for key, var in fields.items():
        if not np.allclose(np.asarray(var.coords), saved[f"{key}_coords"]):
            raise ValueError(f"{path}: saved {key} nodes do not match the rebuilt ref "
                             f"{coarse_ref} mesh")
        values = saved[key].reshape(var.array.shape)
        if var.units is not None:
            values = uw.utilities.UnitAwareArray(values, units=var.units)
        var.array[...] = values
    return fields


def prolong(coarse_fields, fine_fields):
    """Set each fine field from its coarse counterpart. The notch meshes are nested
    (each refinement splits the previous one), so the coarse P2 velocity and P1
    pressure / coupled fields are exactly representable on the fine mesh: evaluating
    the coarse finite-element interpolant at the fine nodes is an exact transfer."""
    for key, fine in fine_fields.items():
        # fine.coords is unit-aware (metres); evaluate converts it to model units.
        # A plain np.asarray would be read as model coordinates and miss the domain.
        values = uw.function.evaluate(coarse_fields[key].sym, fine.coords)
        fine.array[...] = values.reshape(fine.array.shape)


def write(out_dir, name, record, fields):
    """The run's record as json and its fields (values and coordinates) as npz."""
    if uw.mpi.rank == 0:
        with open(os.path.join(out_dir, name + ".json"), "w") as fh:
            json.dump(record, fh, indent=1, default=float)
        np.savez_compressed(
            os.path.join(out_dir, f"fields_{name}.npz"),
            **{key: np.asarray(var.array) for key, var in fields.items()},
            **{f"{key}_coords": np.asarray(var.coords) for key, var in fields.items()})
