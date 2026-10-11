"""The Spiegelman notch benchmark, built on the APPROVED recipe.

This REPLACES the model-building half of `fmg_contraction_probe.py` for anything that
runs the continuation. That file hand-rolls the yield law as a raw sympy Piecewise on a
ViscousFlowModel, using the SQRT soft-min family and its own delta constant. That is the
early attempt the campaign moved away from: the sqrt-softmin xi-march was flagged as the
WRONG TOOL, and the power-mean delta-continuation is what replaced it. Reusing that
builder silently reintroduces the sqrt homotopy, which is how this went wrong again.

What the approved recipe means concretely:

  * the yield law belongs to `ViscoPlasticFlowModel`, not to the driver -- so
    `yield_mode`, `yield_smoother` and `yield_softness` are MODEL-owned;
  * the smoother is the POWER MEAN (`yield_smoother="powermean"`), not the sqrt family;
  * delta is driven by `stokes.solve(homotopy=True)`, the landed Layer-2 API, which owns
    the march, the tangent choice and the revert-on-failure -- the driver does not
    re-implement it;
  * delta0 <= 1 for the power mean. Sharpness is s = 1/(delta + 0.001) and delta = 1 IS
    the harmonic mean; beyond that the p-norm collapses BELOW Min. (delta0 = 8 belongs to
    the SQRT family and is wrong here -- an easy and invisible way to get this wrong.)

Kept from the old harness because it is validated and independent of the yield law: the
notch mesh and its region/boundary labels, the units model, the weak inclusion as a P0
material variable, the compression BCs, and the FMG velocity block. The smoother is
gmres+sor per the measured Layer-3 result, not richardson (which existed only to make the
per-iteration reduction readable as a contraction factor).

xi -- the canonical rate term in the yield criterion, tau_y = sigma_y + 2 xi eta_ref
edot_II -- is carried as a LIVE P0 mesh variable so changing it is a data update rather
than a JIT recompile.
"""
import os
from enum import Enum

import numpy as np
import sympy

import underworld3 as uw
from underworld3.utilities.dm_labels import label_stratum_indices


class boundaries(Enum):
    Bottom = 3; Top = 4; Right = 2; Left = 1; Inner = 5


class boundaries3d(Enum):
    """The extruded notch (make_notch_mesh_3d.py): the 2-D groups plus the
    strike-normal faces."""
    Bottom = 3; Top = 4; Right = 2; Left = 1; Inner = 5; Front = 6; Back = 7


# The weak inclusion carries no load once the strong layer yields, so it is purely
# viscous: a yield stress it can never reach, rather than a special case in the law.
#
# "Never reached" must be relative to the STRESS SCALE, not a big number in Pa. A literal
# 1e30 Pa non-dimensionalises to ~1e20 here, putting 21 orders of magnitude into the
# yield-stress field and wrecking the operator. A few thousand times the stress scale is
# unreachable (it would need edot ~ 1e3 x the imposed rate) and keeps the range sane.
NO_YIELD_FACTOR = 1.0e3


def _stress_scale(eta_bg, v_mmyr, H_km):
    """eta * V / L in Pa -- the scale the non-dimensionalisation divides stresses by."""
    v_ms = v_mmyr * 1.0e-3 / 3.15576e7          # mm/yr -> m/s
    return eta_bg * v_ms / (H_km * 1.0e3)


def set_floor(S, value):
    """Set the viscosity floor: a value change on the EXPRESSION, so no recompile.

    ⚠️ THE ONLY set_floor. A second definition further down this module once shadowed this
    one and wrote only the dead `floor_var` field, so every call silently left the physics
    alone -- see `_set_floor_var_DEAD` for what that cost.
    """
    S["floor_expr"].sym = float(value)
    if S.get("floor_var") is not None:          # kept in step for older callers
        S["floor_var"].data[...] = float(value)


def build(msh, eta_bg, v_mmyr, phi, refinement, xi=0.0, seed=True, H_km=30.0,
          unique_params=False,
          rate_source="live", fas_source=False, p_degree=1, p_continuous=True,
          strategy=None, floor_scalar=None, residual_strength=0.02,
          weak_ramp=None):
    """The notch benchmark on ViscoPlasticFlowModel with the power-mean soft-min.

    Returns a dict with the solver, the fields, the live xi variable and the viscous
    seed, mirroring the old harness's shape so existing callers can be moved over.
    """
    model = uw.Model()
    model.set_reference_quantities(length=uw.quantity(H_km, "km"),
                                   velocity=uw.quantity(v_mmyr, "mm/yr"),
                                   viscosity=uw.quantity(eta_bg, "Pa*s"))
    # ⚠️ TWO BUILDS IN ONE PROCESS SHARE THEIR PARAMETERS BY DEFAULT.
    # `uw.expression` is interned in a CLASS-LEVEL dict keyed by display name
    # (underworld3#767), so a second `build()` returns the SAME objects and overwrites
    # their values -- retroactively changing the first model's physics. Measured: building
    # a second model at floor 0.3 moved the first model's floor_expr from 1e-2 to 0.3,
    # with distinct meshes, distinct solvers and distinct material fields.
    #
    # `unique_params=True` gives this build its OWN parameter objects via
    # `_unique_name_generation`, which keeps the display names (so the maths still reads
    # \eta_{bg}, C, ...) while making them independent -- distinguished internally by
    # _uw_id. Needed by anything holding two models at once: a two-branch continuation, a
    # bifurcation probe, an A/B comparison, a resolution study in one process.
    #
    # Default False so existing callers are unchanged; they get the shared objects they
    # have always had.
    _u = dict(_unique_name_generation=True) if unique_params else {}
    V_conv = uw.expression(r"V", uw.quantity(v_mmyr, "mm/yr"), "convergence", **_u)
    rho_0 = uw.expression(r"\rho", uw.quantity(2700, "kg/m**3"), "density", **_u)
    g = uw.expression(r"g", uw.quantity(9.81, "m/s**2"), "gravity", **_u)
    C = uw.expression(r"C", uw.quantity(1e8, "Pa"), "cohesion", **_u)
    eta_bg_e = uw.expression(r"\eta_{bg}", uw.quantity(eta_bg, "Pa*s"), "strong layer",
                             **_u)
    eta_b = uw.expression(r"\eta_b", uw.quantity(1e21, "Pa*s"), "weak inclusion", **_u)

    plex = uw.discretisation._from_gmsh(msh, useMultipleTags=True, useRegions=True)
    # THE MESH ARRIVES IN KILOMETRES and must be divided by H before UW3 sees it.
    # make_notch_mesh.py builds with S = 30 ("H.magnitude -- non-dimensional -> km"), so
    # the raw coordinates span x = -60..60, y = -30..0 km. UW3 reads raw coordinates as
    # ALREADY non-dimensional, so handing them over unscaled gives a non-dimensional mesh
    # of O(100) that then dimensionalises to 3600 x 900 km -- 30x too large in every
    # direction. That is fatal, not cosmetic: the body force enters as rho*g*H (30x too
    # big) while the viscous stress scale is eta*V/L (30x too small), so buoyancy
    # overwhelms the imposed convergence by ~900x and the linear solve stalls at rho = 1.
    # Dividing by H gives a non-dimensional mesh of O(1) -- x = -2..2, y = -1..0 -- which
    # dimensionalises to the benchmark's 120 x 30 km.
    _cv = plex[1].getCoordinates()
    _cv.scale(1.0 / H_km)
    plex[1].setCoordinates(_cv)
    dim = plex[1].getDimension()
    mesh = uw.discretisation.Mesh(
        plex[1], boundaries=boundaries if dim == 2 else boundaries3d,
        useMultipleTags=True, useRegions=True,
        coordinate_system_type=uw.coordinates.CoordinateSystemType.CARTESIAN,
        qdegree=3, refinement=refinement)

    v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2, continuous=True)
    # PRESSURE SPACE. Default P1 continuous (Taylor-Hood). `p_degree=0,
    # p_continuous=False` gives P2/P0, which the fault work ruled for the same reason
    # that applies here: DRUCKER-PRAGER YIELD READS THE PRESSURE (tau_y = C + sin(phi)*p),
    # so a continuous pressure smears the yield strength across the band exactly as it
    # smeared the fault traction (measured there: traction error 2.21% -> 0.00%, answer
    # moved 23%). P2/P0 is inf-sup stable and its Schur complement is a plain cell-wise
    # mass matrix. ⚠️ P1-DISCONTINUOUS was tried in the fault work and is UNSTABLE here
    # (pressure ~200x too large) — P0, not P1disc.
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=int(p_degree),
                                       continuous=bool(p_continuous))
    mat = uw.discretisation.MeshVariable("mat", mesh, 1, degree=0, continuous=False)
    # xi lives as a P0 FIELD, not a constant: a constant would be folded into the
    # generated C source (JIT #302) and every xi station would pay a recompile.
    xi_var = uw.discretisation.MeshVariable("xicap", mesh, 1, degree=0, continuous=False)
    # The dropping viscosity floor, also a live P0 field for the same reason as xi.
    floor_var = uw.discretisation.MeshVariable("etamin", mesh, 1, degree=0, continuous=False)
    # FROZEN strain-rate ratio for the coarse-damage warm start (rate_source="field"):
    # holds edot_II/edot_ref taken from a COARSE solve, as DATA. The live-rate homotopy
    # puts the weakening feedback inside the Newton tangent (and its ladder stations
    # diverged on entry); freezing the pattern cuts the loop — the pinned problem is
    # plain DP with spatially-varying cohesion, the band pre-selected by the coarse
    # model. A surrogate for the missing first-timestep softening history.
    rate_var = uw.discretisation.MeshVariable("rfrz", mesh, 1, degree=0, continuous=False)

    cS, cE = mesh.dm.getHeightStratum(0)

    def _cells(label, value):
        # empty-safe (#589): on a rank whose local label lacks the value, getStratumIS
        # returns a NULL-handle IS (falsy, but not None) and getIndices() on it
        # segfaults -- at np 16 some ranks own no weak cell
        q = label_stratum_indices(mesh.dm.getLabel(label), value)
        return q[(q >= cS) & (q < cE)] - cS

    mat.data[...] = 1
    mat.data[_cells("Weak", 100)] = 0
    xi_var.data[...] = float(xi)
    rate_var.data[...] = 0.0

    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
    cm = stokes.constitutive_model

    # ---- MASKS AS MULTIPLIERS, NOT Piecewise ---------------------------------------
    # `mat` is a P0 field holding exactly 0 or 1, so `m*a + (1-m)*b` has the same VALUE
    # as `Piecewise((a, m > 0.5), (b, True))` while being smooth, differentiable and
    # branch-free. The conditional form bought nothing and the symbolic path could not
    # digest it: the adjoint sensitivity to the viscosity floor — which reaches the
    # residual only through two of these Piecewise masks — came back as nan while every
    # parameter outside them differentiated cleanly.
    m_strong = mat.sym[0]
    strong = mat.sym[0] > 0.5          # kept: some callers still read it
    # The weak inclusion's viscosity, optionally ramped along strike (3-D):
    # weak_ramp = (z0_km, w_km) gives log10 eta_b(z) = 22 - tanh((z0 - z) / w), i.e.
    # 1e21 (as above) well below z0 and 1e23 (the strong layer) well above it, a
    # smoothed, restricted notch whose weak segment z < z0 is half of a notch of
    # length 2 z0 mirrored in the u_z = 0 face. Built on the raw (non-dimensional)
    # coordinate, so z0 and w are divided by H.
    eta_b_eff = eta_b
    if weak_ramp is not None:
        z0_nd, w_nd = weak_ramp[0] / H_km, weak_ramp[1] / H_km
        z = mesh.CoordinateSystem.N[2]      # the raw (non-dimensional) z coordinate symbol
        eta_b_eff = eta_b * 10 ** (1 - sympy.tanh((z0_nd - z) / w_nd))
    visc_lin = m_strong * eta_bg_e + (1 - m_strong) * eta_b_eff
    cm.Parameters.shear_viscosity_0 = visc_lin

    # Drucker-Prager: pressure-dependent cohesion, floored at zero so tension cannot
    # produce a negative yield stress. The rate term is the canonical xi -- additive,
    # smooth, coercive, and xi -> 0 recovers DP exactly.
    fc = np.sin(np.deg2rad(phi))
    # epsilon = 0 IS exactly Max; smooth_max keeps the floor SYMBOLIC (a plain
    # sympy.Max on a UWexpression cannot resolve the fuzzy compare and recurses to
    # stack death), which the JIT constants[] contract requires.
    # ---- THE COHESION HOMOTOPY (Louis, 2026-07-30) ----------------------------------
    #
    #     C_eff = C * (1 + alpha / (1 + edot_II / edot_ref))
    #
    # ONE parameter that does two things, and both vanish together at alpha = 0:
    #
    #   * RAMP DOWN. At large alpha unstrained material has cohesion C*(1+alpha) -- it
    #     barely yields, so the problem is diffuse, unique and easy. alpha -> 0 removes
    #     the elevation.
    #   * SOFTENING WITH STRAIN RATE, SATURATING AT THE TARGET. Within a given alpha,
    #     C_eff falls from C*(1+alpha) toward C* as edot grows, so wherever strain
    #     concentrates the material is RELATIVELY weaker and localisation is
    #     self-reinforcing. It saturates exactly at C*: the softening can never take
    #     cohesion below the true value.
    #
    # At alpha = 0 the bracket is identically 1 for every edot. No residual softening to
    # unwind, no separate landing step, and NO SECOND AXIS -- which is what confounded the
    # xi/delta work, where two parameters were open at once.
    #
    # C_eff >= C always, so the regularised problem is never WEAKER than the target. That
    # is the same "approach from above" the yield_anchor work (PR #475) found to be the
    # safe direction for a homotopy entry.
    #
    # WHY THIS AND NOT xi: xi is rate-STRENGTHENING (tau_y = sigma_y + 2 xi eta_bg edot),
    # so it resists strain concentration -- it stabilises and DIFFUSES the band. The
    # intent was damage: weaken the band so the structure appears on its own. Opposite
    # signs. This is the weakening one.
    #
    # A uw.expression CONSTANT, not a P0 field. The "constants get folded into the C
    # source so every station recompiles" reasoning that put xi on a mesh variable is
    # folklore: MEASURED, a uw.expression inside the yield law lands in
    # constants_manifest, updates in ~10 ms, and gives a result identical to a full
    # rebuild to 5e-13. Ramping it is a data update.
    alpha = uw.expression(r"\alpha", 0.0,
                          "cohesion homotopy: elevates C and softens it toward the "
                          "target with strain rate; 0 = the stated problem")
    # The reference strain rate, built from the SAME quantities as the velocity BC and the
    # mesh scale rather than a hand-computed SI number. A hand-computed
    # `quantity(v*1e-3/3.15576e7/(H*1e3), "1/s")` landed three decades off: measured, it
    # gave Einv2/edot_ref ~ 1000, so the softening had SATURATED everywhere and alpha = 8
    # moved tau_y by 0.8% instead of several hundred per cent. Composing V/H from the
    # expressions themselves keeps the non-dimensionalisation UW3's business, not mine.
    edot_ref = uw.expression(
        r"\dot\varepsilon_{\textrm{ref}}",
        V_conv / uw.quantity(H_km, "km"),
        "imposed strain-rate scale V/H -- sets where the softening turns over")
    # rate_source picks what drives the softening bracket:
    #   "live"  — the iterate's own Einv2 (Louis's homotopy; feedback inside the tangent)
    #   "field" — the FROZEN ratio in rate_var (coarse-damage pinning; pure data, the
    #             tangent never sees the weakening pattern move)
    if rate_source == "field":
        _r = rate_var.sym[0]
    else:
        _r = stokes.Unknowns.Einv2 / edot_ref
    C_eff = C * (1 + alpha / (1 + _r))
    # ⚠️ RULING (Louis, 2026-09-18; memory project_gradient_damage_loop_gain): NO hard Max /
    # Min. A tension floor at EXACTLY zero makes eta_pl = tau_y / (2 edot) zero in tension —
    # a zero-viscosity cell with an undefined tangent, a singular operator, and every
    # DIVERGED_LINEAR_SOLVE traced on the gradient-damage fixture. The fix is a POSITIVE
    # residual strength with a rounded floor. This line carried smooth_max(..., 0, 0) — the
    # exact Max — through the whole Spiegelman campaign until 2026-09-30.
    # residual_strength = 0 reproduces the old hard floor, for comparison only.
    if float(residual_strength) > 0:
        _smin = float(residual_strength) * C
        sigma_y = uw.maths.smooth_max(C_eff + fc * p.sym[0], _smin, _smin)
    else:
        sigma_y = uw.maths.smooth_max(C_eff + fc * p.sym[0], sympy.sympify(0), sympy.sympify(0))
    tau_y = sigma_y + 2.0 * xi_var.sym[0] * eta_bg_e * stokes.Unknowns.Einv2
    yield_none = uw.expression(
        r"\tau_{y,\infty}",
        uw.quantity(NO_YIELD_FACTOR * _stress_scale(eta_bg, v_mmyr, H_km), "Pa"),
        "unreachable yield stress: the weak inclusion is purely viscous")
    yield_full = m_strong * tau_y + (1 - m_strong) * yield_none
    cm.Parameters.yield_stress = yield_full

    # The approved smoother, and the model owns the march.
    cm.yield_smoother = "powermean"
    cm.yield_mode = "softmin"

    # A MATERIAL-DEPENDENT viscosity floor, for the dropping-floor route.
    #
    # A global floor is wrong on this benchmark. MEASURED (localisation_regime.py): the
    # domain minimum of eta_eff is 1.000e-02 at every eta*V tested, and that is the WEAK
    # SUBSTRATE (1e21/1e23), not yielded material -- yielded material only reaches a
    # median of ~0.41 even at eta*V = 1.25e24. So a floor high enough to bind on the
    # plastic viscosity is O(0.1) and would clip a PHYSICAL material property. The weak
    # layer is purely viscous and must not be floored at all.
    #
    # So the floor is a Piecewise on the material, exactly as visc_lin is: active in the
    # strong layer, and set to zero in the weak one where smooth_max(eta, 0, eps) leaves
    # a positive viscosity essentially untouched. The rounding scale is material-dependent
    # for the same reason.
    #
    # `floor` is carried as a LIVE P0 FIELD, not a constant, so a ramp is a data write
    # rather than a JIT recompile -- the same reason xi is a field (#302).
    floor_var.data[...] = 0.0
    # ---- THE FLOOR IS AN EXPRESSION, FULL STOP --------------------------------------
    # The floor is one number, uniform over the strong layer, so it is a SCALAR and it
    # belongs in a uw.expression. There is NO trade here, contrary to an earlier note in
    # this file: a uw.expression lands in `constants_manifest` and is passed as a RUN-TIME
    # CONSTANT, so changing its value does NOT recompile the kernel — the same reason
    # `alpha` above is an expression rather than a field. So the expression ramps exactly
    # as cheaply as a P0 field did, AND it can be differentiated.
    #
    # The P0 field bought nothing and cost the symbolic path: `solver.sensitivity` takes a
    # scalar and integrates, while a FIELD's sensitivity is a dual on its own space and
    # comes from `gradient(..., fields=[...])`. Asking for a field through the scalar call
    # fails several frames down in array arithmetic —
    #     TypeError: unsupported operand type(s) for +: 'int' and 'MutableDenseNDimArray'
    #
    # Set it with `set_floor(S, value)`; `floor_var` is kept only so older callers that
    # write to it do not break, and it is NOT read by the constitutive law any more.
    floor_expr = uw.expression(
        r"\eta_{\min}", float(floor_scalar if floor_scalar is not None else 0.0),
        "viscosity floor as a fraction of eta_bg (strong layer only)", **_u)
    cm.Parameters.shear_viscosity_min = m_strong * floor_expr * eta_bg_e
    # Rounding a few per cent of the floor: enough to keep the corner differentiable for
    # the consistent tangent, small enough not to move the floor's location.
    cm.viscosity_min_rounding = 0.05 * m_strong * floor_expr * eta_bg_e

    # FAS tau source (opt-in): a velocity-space (P2) vector field added to the body
    # force, zero by default. A manual two-level FAS cycle writes the lumped-lifted
    # tau correction into it, making the coarse solver target the FINE grid's defect
    # (N_c(u_c) = N_c(R u_f) + R(f - N_f(u_f))) instead of its own problem. Ramping
    # it is a data write; fas_source=False builds exactly the stated model.
    tau_var = None
    if fas_source:
        tau_var = uw.discretisation.MeshVariable("taufas", mesh, mesh.dim, degree=2)
        tau_var.data[...] = 0.0
        stokes.bodyforce = sympy.Matrix(
            [tau_var.sym[0], -rho_0 * g + tau_var.sym[1]])
    else:
        stokes.bodyforce = sympy.Matrix([0, -rho_0 * g] + [0] * (mesh.dim - 2))
    if mesh.dim == 2:
        stokes.add_dirichlet_bc((sympy.oo, 0.0), "Bottom")
        stokes.add_dirichlet_bc((V_conv, 0.0), "Left")
        stokes.add_dirichlet_bc((-V_conv, 0.0), "Right")
    else:
        # The extruded notch: the 2-D conditions with u_z = 0 on the side walls (the
        # plane-strain extrusion), and u_z = 0 alone on the strike-normal faces, which
        # are symmetry planes. Not rotated free-slip: it refuses a coupled field.
        stokes.add_dirichlet_bc((sympy.oo, 0.0, sympy.oo), "Bottom")
        stokes.add_dirichlet_bc((V_conv, 0.0, 0.0), "Left")
        stokes.add_dirichlet_bc((-V_conv, 0.0, 0.0), "Right")
        stokes.add_dirichlet_bc((sympy.oo, sympy.oo, 0.0), "Front")
        stokes.add_dirichlet_bc((sympy.oo, sympy.oo, 0.0), "Back")
    # The 1/mu mass matrix IS the Schur preconditioner for variable-viscosity Stokes, and
    # the mu that belongs there is the viscosity the momentum operator actually has --
    # the EFFECTIVE one, including yielding. Using the linear viscosity is right only for
    # the viscous seed, which is why it looked correct and survived: once the power-mean
    # pulls yielding material to eta_eff ~ 0.02, a preconditioner built on eta = 1
    # mis-scales the pressure block ~50x exactly where the solve is hardest.
    #
    # Measured on the delta-homotopy entry at eta_bg*V = 5e23 (schur_pc_probe):
    #   1/visc_lin  + penalty=0  ->  DIVERGED_LINE_SEARCH
    #   1/visc_lin  + penalty=1  ->  converges (the AL term compensates)
    #   1/eta_eff   + penalty=0  ->  converges
    # So the augmented-Lagrangian penalty was standing in for the right preconditioner.
    # Prefer the preconditioner: AL wrecks the multigrid smoother, and the velocity block
    # here is FMG -- at eta_bg*V = 1e26 the LINEAR seed alone goes DIVERGED_MAX_IT (50
    # iterations, 32 s) with penalty=1 where penalty=0 converges in 6 iterations and 5 s.
    # ---- THE FROZEN LINEAR SOLVER (measured 2026-07-29; hold it fixed) --------------
    #
    # Every earlier configuration decision here was made on the LINEAR SEED, and one of
    # them (penalty) cost the eta*V = 5e23 cell. These were decided on PLASTIC solves at
    # ref=2, and the arms are recorded so the next person can see what was compared.
    #
    # penalty = 0 -- NOT a preconditioner choice. `penalty` adds lambda*K*div(u)*I to F1,
    # the RESIDUAL flux, so it is part of the operator; UW3's own docstring warns that the
    # recovered p is then the Lagrange multiplier and that a pressure-dependent
    # constitutive law needs p_mech. This IS a pressure-dependent law (Drucker-Prager on
    # p.sym[0]), and the correction is not available: K is the EFFECTIVE viscosity, so
    # p_mech = p - lambda*eta_eff*div u would make eta_eff implicit in itself. Measured at
    # 2.5e23, both arms from the same seed: ||lambda K div u||/||p|| = 1.32e-2,
    # ||dv||/||v|| = 1.69e-3, ||dp||/||p|| = 2.71e-3 -- five orders above tolerance, so
    # not the same discrete problem (though the yielded area is unchanged at 25.35%).
    # And penalty=1 needed 9 nonlinear iterations to penalty=0's 6, despite winning the
    # FIRST step 0.160 vs 0.334. A better first step is not a better solve.
    stokes.penalty = 0.0
    #
    # Schur mu = the EFFECTIVE viscosity. The 1/mu mass matrix wants the viscosity the
    # momentum operator actually has, and once material yields that is eta_eff, not the
    # linear one. Measured where it can move the answer (under `preonly`, where the
    # preconditioner is applied once and so enters the step): 23 vs 46 velocity cycles and
    # |F|/|F0| 0.334 vs 0.440 against 1/visc_lin.
    stokes.saddle_preconditioner = 1 / cm.viscosity
    #
    # tolerance 1e-6 (Louis's ruling: 1e-5/1e-6 is plenty, 1e-9 is overkill). Set it
    # BEFORE any explicit fieldsplit rtol override -- the setter re-derives both inner
    # margins from it, and that ordering only became meaningful once #477 was fixed.
    #
    # ⚠️ BUT THE COST ARGUMENT FOR LOOSENING IT DOES NOT HOLD HERE, and the earlier claim
    # in this file that tight margins are "why a 6-iteration solve cost 2132 multigrid
    # cycles" was measuring the wrong currency. One-factor, 2.5e23, gmres outer:
    #     1e-06 -> nl= 5, vel=1390, 111.3s, |F|/|F0| 8.06e-05
    #     1e-08 -> nl= 6, vel=2170, 110.7s, |F|/|F0| 1.86e-06
    # ONE extra nonlinear iteration and 1.5x the multigrid cycles buys ~40x in residual at
    # IDENTICAL wall clock. At this problem size the cost is dominated by per-Newton-step
    # overhead (Jacobian assembly, preconditioner setup), not by multigrid cycles -- so
    # minimising NONLINEAR iterations is what matters and the inner tolerance is nearly
    # free. Raise this to 1e-8 whenever a sharper answer is wanted; it is not the expense.
    stokes.tolerance = 1.0e-6
    # TANGENT AND OUTER-KSP CAP LEFT AT THEIR DEFAULTS, deliberately. The
    # `nonlinear-solver` skill prescribes consistent Newton for non-elastic DP, and a
    # bounded outer KSP so a hostile step fails fast. Both were tried here and MEASURED to
    # make no difference to the thing that is actually blocking (entry_config_probe, the
    # delta-homotopy entry at xi=0.3 from the viscous seed):
    #     frozen / no cap  DIVERGED_LINEAR_SOLVE 45.3 s
    #     frozen / cap 80  DIVERGED_LINEAR_SOLVE 45.0 s
    #     newton / no cap  DIVERGED_LINEAR_SOLVE 47.0 s
    #     newton / cap 80  DIVERGED_LINEAR_SOLVE 44.8 s
    # Setting consistent_jacobian ALSO changes warm-start bookkeeping (a diverged solve
    # clears has_solution, and zero_init_guess then auto-detects a COLD start), which is
    # the likely reason a xi ladder carrying it landed on v=0 instead of the seed. Since
    # it buys nothing measurable here, do not carry a change that alters restart semantics
    # for no gain. Revisit when the entry itself is fixed.
    stokes.petsc_options["snes_type"] = "newtonls"
    stokes.petsc_options["snes_linesearch_type"] = "bt"
    stokes.petsc_options["snes_error_if_not_converged"] = "false"

    # OUTER KRYLOV: LEFT DELIBERATELY AT THE UW3 DEFAULT (gmres). This was overridden to
    # fgmres and the override has been REVERTED -- the evidence did not support it.
    #
    # What is established: PETSc's gmres is LEFT-preconditioned, so it converges on
    # ||M^-1 r|| while fgmres is right-preconditioned and converges on the TRUE residual;
    # and with both sub-blocks being Krylov solves the preconditioner VARIES between
    # applications, so ||M^-1 r|| is not a fixed quantity to converge on. At the cliff,
    # same problem and same preconditioner, gmres reported CONVERGED_RTOL at 200 outer
    # iterations where fgmres needed 877.
    #
    # What is NOT established is which is better here. One-factor sweep at 2.5e23
    # (tolerance_vs_outer.py), everything else identical:
    #     tol    outer   | nl  outer_its   vel    wall     |F|/|F0|
    #     1e-06  gmres   |  5      29     1390  111.3s   8.0598e-05
    #     1e-06  fgmres  | 33     102     2853  275.5s   1.3530e-05
    #     1e-08  gmres   |  6      43     2170  110.7s   1.8557e-06
    #     1e-08  fgmres  | 34     114     4017  291.2s   2.4318e-07
    # fgmres lands 6-7x closer but takes ~6x the nonlinear iterations to do it, and 33
    # iterations to beat what gmres does in 6 is not "converging further" -- a MORE
    # accurate linear solve giving WORSE Newton behaviour is backwards, which usually
    # means the arms are not stopping against the same atol and the |F|/|F0| column is
    # not comparing what it appears to. Needs an equal-accuracy run before either is
    # defaulted.
    #
    # ⚠️ AND IT IS NOT SEPARABLE FROM THE SCHUR DESIGN: at the cliff the segregated
    # (Citcom) pressure arms could not complete a single Newton step under gmres and ran
    # fine under fgmres. So "which outer" and "which pressure design" are one question.
    # If you switch the pressure block to a real Krylov solve, switch the outer too.

    # The MG SMOOTHER is left at the FMG bundle's own choice. Overriding it to fgmres
    # (which every probe in this study did, on the assumption that a flexible smoother was
    # needed) is MEASURED INERT: four pairs at 2.5e23, identical residuals to five
    # significant figures, velocity cycles within 2%.

    vp = "fieldsplit_velocity_"
    stokes.petsc_options[vp + "ksp_type"] = "fgmres"
    stokes.petsc_options[vp + "ksp_gmres_restart"] = 30
    # ⚠️ A STRATEGY OWNS THE VELOCITY BLOCK OUTRIGHT. The option bundle treats a key it
    # did not write as the caller's and leaves it alone, so hand-pinning
    # `mg_levels_pc_type = sor` below would silently beat `strategy="bulletproof"` and the
    # run would measure SOR while reporting Schwarz. Deleting the keys afterwards is NOT
    # the fix — measured 2026-09-19, the bundle then raises KeyError looking for them.
    # When a strategy is asked for, none of these are written in the first place.
    if strategy is not None:
        stokes.strategy = str(strategy)
    if strategy is None:
        # The hand-tuned FMG velocity block: full multigrid, Galerkin coarse operators,
        # and a FLEXIBLE smoother (the smoother's own PC varies between applications).
        # Reachable only on a mesh WITH a hierarchy -- the FMG bundle rewrites these keys
        # on every _build and latches a user override on pc_type alone.
        stokes.petsc_options[vp + "pc_type"] = "mg"
        stokes.petsc_options[vp + "pc_mg_type"] = "full"
        stokes.petsc_options[vp + "pc_mg_galerkin"] = "both"
        stokes.petsc_options[vp + "mg_levels_ksp_type"] = "gmres"
        stokes.petsc_options[vp + "mg_levels_ksp_max_it"] = 4
        stokes.petsc_options[vp + "mg_levels_ksp_norm_type"] = "none"
        stokes.petsc_options[vp + "mg_levels_pc_type"] = "sor"
        stokes.petsc_options[vp + "mg_coarse_pc_type"] = "redundant"
        stokes.petsc_options[vp + "mg_coarse_redundant_pc_type"] = "lu"
        stokes.petsc_options[vp + "mg_coarse_redundant_pc_factor_shift_type"] = "nonzero"

    # PRESSURE: `preonly` makes the whole fieldsplit a block PRECONDITIONER and puts the
    # coupling work in the outer loop (Elman/Silvester/Wathen). Giving this block a real
    # Krylov solve instead writes CITCOM -- the Schur system is solved, the outer becomes
    # a formality at one or two iterations, and UW3's inner margins were designed for that
    # shape. Both are legitimate; the choice is problem-dependent and stays OPEN
    # (Louis, 2026-07-29: "we can try both on real problems").
    # On THIS problem, at the cliff, the block design is what runs: the segregated arms
    # (fgmres at rtol 1e-2 and at the 0.1*tol margin) spent ~15000 velocity cycles on ONE
    # Newton step -- 30x the block design PER STEP -- and never completed a step inside a
    # 150 s/step budget. To switch, override fieldsplit_pressure_ksp_type/rtol AFTER
    # `stokes.tolerance` is set.
    pp = "fieldsplit_pressure_"
    stokes.petsc_options[pp + "ksp_type"] = "preonly"
    stokes.petsc_options[pp + "pc_type"] = "bjacobi"

    # Viscous seed: the DP viscosity and its tangent are singular at edot = 0, so the
    # first plastic Jacobian needs an everywhere-nonzero strain rate to be evaluable at
    # all. This is regularisation, not approximation, and it runs under the same config.
    v_lin = p_lin = None
    if seed:
        # Both laws were built above, so this SETS each in turn -- it never reads a
        # Parameter and writes it back, which nests a UWexpression in itself (#447).
        # Seed on the HARD Min with an unreachable yield stress: eta = min(eta_ve, huge)
        # is eta_ve EXACTLY, so the seed is a genuinely linear solve. Routing it through
        # the power-mean instead leaves the soft-min algebra in the loop for a problem
        # that has no plasticity in it, which is both pointless and (measured) does not
        # converge.
        cm.yield_mode = "min"
        cm.Parameters.yield_stress = yield_none
        stokes.solve(zero_init_guess=True)
        v_lin, p_lin = v.data.copy(), p.data.copy()
        cm.Parameters.yield_stress = yield_full
        cm.yield_mode = "softmin"

    # yield_none / yield_full are returned so a caller can re-run the VISCOUS problem on
    # the already-built solver -- the linear control for any velocity-block diagnosis,
    # and the one arm that must be instrumented the same way as the plastic one.
    return dict(model=model, mesh=mesh, stokes=stokes, cm=cm, v=v, p=p,
                mat=mat, xi_var=xi_var, eta_bg=eta_bg_e,
                # Exposed for ADJOINT SENSITIVITY: a parameter must be handed to
                # `solver.sensitivity` as the uw.expression the residual carries,
                # not its value — differentiating a fresh expression of the same
                # value returns ZERO silently.
                C=C, eta_b=eta_b, rho_0=rho_0, g_accel=g, floor_expr=floor_expr,
                yield_none=yield_none, yield_full=yield_full, floor_var=floor_var,
                alpha=alpha, edot_ref=edot_ref, rate_var=rate_var,
                # Yield diagnostics: the pressure-dependent strength BEFORE the tension
                # floor, and after it.
                tension_measure=C_eff + fc * p.sym[0], sigma_y=sigma_y, C_eff=C_eff,
                V_conv=V_conv, v_mmyr=v_mmyr, tau_var=tau_var,
                v_lin=v_lin, p_lin=p_lin, ncells=cE - cS)


def set_alpha(S, alpha):
    """Live cohesion-homotopy update -- a constants[] repack, no recompile.

    alpha = 0 IS the stated problem: the bracket is identically 1 for every strain rate,
    so both the cohesion elevation and the strain-rate softening vanish together. Large
    alpha gives a stronger, more diffuse, uniquely-solvable problem whose weakest material
    is wherever the strain is highest -- so a band is the preferred structure and appears
    without needing to be found.
    """
    S["alpha"].sym = float(alpha)
    S["stokes"]._update_constants()


def set_V(S, frac):
    """Live LOAD ramp — scale the imposed convergence velocity to frac * target.

    This is NOT the same continuation as the cohesion ramp (Louis, 2026-07-30):
    tau_y = C + sin(phi) p, and p is mostly lithostatic, so lowering V elevates the
    WHOLE yield stress (frictional part included) relative to the driving stress,
    where the C-ramp elevates only the cohesion share. V_conv is a uw.expression
    constant used in the BCs and edot_ref; the units model's reference velocity stays
    at the TARGET V, so the non-dimensionalisation is unchanged and a station is a
    constants[] repack. frac = 1 restores the stated problem exactly.
    """
    S["V_conv"].sym = uw.quantity(float(frac) * S["v_mmyr"], "mm/yr")
    S["stokes"]._update_constants()


def _set_floor_var_DEAD(S, floor):
    """DEAD. Wrote only `floor_var`, which the constitutive law no longer reads.

    ⚠️ THIS SHADOWED `set_floor` ABOVE AND SILENTLY DID NOTHING. Two definitions of the
    same name in one module: Python keeps the LAST, so every `nm.set_floor(S, value)` call
    wrote the dead P0 field and left `floor_expr` -- the expression the constitutive law
    actually holds -- untouched.

    What it cost (2026-09-22). Every continuation ladder in this campaign ran at whatever
    floor its model was BUILT with:
      * a warm ladder reported J identical to six digits across a 30x change in floor, and
        nl identical at 27, which was read as a convergence artefact and filed as
        underworld3#770 -- but the problem was simply never changed;
      * a "warm from floor 0.3" route then reported J = 4.38e-4 at a nominal floor of 1e-2,
        read as TWO SOLUTIONS 25% apart at the same parameters. It was one solution at each
        of two different floors.

    Renamed rather than deleted so the name cannot shadow again, and kept so this note has
    somewhere to live.
    """
    with uw.synchronised_array_update():
        S["floor_var"].data[...] = float(floor)


def set_xi(S, xi):
    """Live xi update -- a P0 data write, no recompile."""
    with uw.synchronised_array_update():
        S["xi_var"].data[...] = float(xi)


def restore_seed(S):
    with uw.synchronised_array_update():
        S["v"].data[...] = S["v_lin"]
        S["p"].data[...] = S["p_lin"]
