"""Yielding-lid convection in a box: the base models for the faulted-lithosphere
campaign, before any fault is added.

The rheology is Moresi & Solomatov (1998): a temperature-dependent viscosity
normalised on the base, capped by a yield stress that grows with depth,

    eta(T)  = deta ** (1 - T)                (1 at the basal temperature)
    tau_y   = tau0 + tau1 * (1 - y)          (depth measured from the surface)
    eta_eff = softmin(eta(T), tau_y / (2 edot_II))

with Ra on the basal viscosity, a layer of depth 1, and internal heating H (the
source term of the energy equation). Internal heating warms the interior, which
lowers the viscosity beneath the lid.

Free-slip on all four walls (a zero normal component, exact on flat walls),
T = 0 on the top and 1 on the base. Eulerian SUPG transport. The Stokes velocity
block uses geometric multigrid on the box's own refinement hierarchy.

The defaults are the annulus mobile-lid case of the ZG95 campaign rescaled to the
layer depth (annulus depth 0.45 in units of the outer radius): Ra = 1e7 * 0.45**3,
H = 7 * 0.45**2, tau0 = 1e5 * 0.45**2, tau1 = 1e7 * 0.45**3.

    mpirun -np 4 python box_convection.py -uw_out ~/+Simulations/zg95/box_regimes/runs/<name> \\
        -uw_heating 1.42 -uw_steps 600

Restart (parameters may change at the restart, as in the paper's step experiments):

    mpirun -np 4 python box_convection.py -uw_out <same dir> -uw_restart 200 -uw_deta 1e5
"""
import json
import os
import time

import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(
    uw_out="~/+Simulations/zg95/box_regimes/runs/test",
    uw_width=4.0,               # aspect ratio of the box (depth 1)
    uw_cell=0.125,              # coarsest cell size
    uw_refinement=2,            # halvings of the coarsest mesh (multigrid levels - 1)
    uw_ra=9.1125e5,             # Rayleigh number on the basal viscosity
    uw_deta=3.0e4,              # viscosity contrast across the layer
    uw_tau0=2.025e4,            # yield stress at the surface
    uw_tau1=9.1125e5,           # yield stress gradient with depth
    uw_heating=1.4175,          # internal heating rate H
    uw_yield_softness=0.2,      # soft-min width delta of the yield law
    uw_T_int=0.8,               # initial interior temperature
    uw_seed_cells=4,            # convection cells in the initial perturbation
    uw_tol=1.0e-3,              # Stokes nonlinear tolerance
    uw_dt_mult=3.0,             # multiple of the SUPG accuracy estimate
    uw_courant=1.0,             # Courant limit: cells crossed per step by the fastest flow
    uw_dt_max=5.0e-3,           # step cap (annulus 1e-3 in outer-radius units)
    uw_steps=50,
    uw_ckpt_every=10,
    uw_restart=-1,              # checkpoint index to restart from (-1: fresh start)
)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
width = float(params.uw_width)

mesh = uw.meshing.UnstructuredSimplexBox(
    minCoords=(0.0, 0.0), maxCoords=(width, 1.0), cellSize=params.uw_cell,
    refinement=params.uw_refinement, qdegree=3, regular=False)
x, y = mesh.X

v = uw.discretisation.MeshVariable("V", mesh, mesh.dim, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1, continuous=True)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
log_eta = uw.discretisation.MeshVariable("log10_eta", mesh, 1, degree=1)
yield_ratio = uw.discretisation.MeshVariable("yield_ratio", mesh, 1, degree=1)

Ra = uw.expression(r"\mathrm{Ra}", params.uw_ra, "Rayleigh number on the basal viscosity")
deta = uw.expression(r"\Delta\eta", params.uw_deta, "viscosity contrast across the layer")
tau0 = uw.expression(r"\tau_0", params.uw_tau0, "yield stress at the surface")
tau1 = uw.expression(r"\tau_1", params.uw_tau1, "yield stress gradient with depth")
H = uw.expression(r"H", params.uw_heating, "internal heating rate")

# ----------------------------------------------------------------------------- Stokes
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
eta_T = sympy.exp(sympy.log(deta) * (1 - T.sym[0]))
stokes.constitutive_model.Parameters.shear_viscosity_0 = eta_T
stokes.constitutive_model.Parameters.shear_viscosity_min = 1
stokes.constitutive_model.Parameters.yield_stress = tau0 + tau1 * (1 - y)
stokes.constitutive_model.yield_softness = params.uw_yield_softness
stokes.bodyforce = Ra * T.sym[0] * mesh.CoordinateSystem.unit_e_1
stokes.add_essential_bc((None, 0.0), "Top")
stokes.add_essential_bc((None, 0.0), "Bottom")
stokes.add_essential_bc((0.0, None), "Left")
stokes.add_essential_bc((0.0, None), "Right")
stokes.tolerance = params.uw_tol

eta_eff = stokes.constitutive_model.viscosity

# ----------------------------------------------------------------------------- energy
adv = uw.systems.AdvDiffusion(mesh, T, v.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = 1
adv.f = H
adv.add_dirichlet_bc(0.0, "Top")
adv.add_dirichlet_bc(1.0, "Bottom")

# P1 fields for the renders: log10 of the effective viscosity, and eta_eff / eta(T)
# (1 where the viscous branch holds, below 1 where the lid yields). Low order keeps
# the projected viscosity positive.
eta_projection = uw.systems.Projection(mesh, log_eta)
eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
ratio_projection = uw.systems.Projection(mesh, yield_ratio)
ratio_projection.uw_function = eta_eff / eta_T

# ----------------------------------------------------------------------------- diagnostics
# All integrals, so every value is global on every rank. The heat fluxes are the
# conductive fluxes out of the top and into the base, per unit width: with no
# motion and no heating both are 1. In a statistically steady state
# q_top = q_base + H, and H / q_top is the internally heated fraction.
yielded = sympy.Piecewise((1, eta_eff / eta_T < sympy.Rational(9, 10)), (0, True))
in_lid = sympy.Piecewise((1, y > sympy.Rational(2, 3)), (0, True))
dTdy = T.sym[0].diff(y)
integrals = {
    "v2": uw.maths.Integral(mesh, v.sym.dot(v.sym)),
    "T": uw.maths.Integral(mesh, T.sym[0]),
    "yielded": uw.maths.Integral(mesh, yielded),
    "yielded_lid": uw.maths.Integral(mesh, yielded * in_lid),
    "vs2": uw.maths.BdIntegral(mesh, v.sym[0] ** 2, "Top"),
    "q_top": uw.maths.BdIntegral(mesh, -dTdy, "Top"),
    "q_base": uw.maths.BdIntegral(mesh, -dTdy, "Bottom"),
}

profile_y = np.linspace(0.0, 1.0, 65)
profile_x = np.linspace(0.0, width, int(32 * width) + 1)
profile_xy = np.array([[px, py] for py in profile_y for px in profile_x])


def temperature_profile():
    """Horizontally averaged T at 65 heights, and the lid thickness: the depth at
    which that profile first reaches 0.8 of its mid-depth value (the annulus
    campaign's definition). Collective: every rank evaluates the same points."""
    Tg = np.asarray(uw.function.global_evaluate(T.sym[0], profile_xy)).reshape(
        len(profile_y), len(profile_x))
    profile = Tg.mean(axis=1)
    T_mid = profile[len(profile_y) // 2]
    from_top = profile[::-1]
    reached = np.flatnonzero(from_top >= 0.8 * T_mid)
    lid = float(1.0 - profile_y[::-1][reached[0]]) if reached.size else float("nan")
    return profile, float(T_mid), lid


def diagnostics():
    val = {name: float(integral.evaluate()) for name, integral in integrals.items()}
    area = width * 1.0
    vrms = np.sqrt(val["v2"] / area)
    vsurf = np.sqrt(val["vs2"] / width)
    profile, T_mid, lid = temperature_profile()
    record = {
        "vrms": vrms,
        "vsurf_rms": vsurf,
        "mobility": vsurf / max(vrms, 1e-30),
        "q_top": val["q_top"] / width,
        "q_base": val["q_base"] / width,
        "T_mean": val["T"] / area,
        "T_mid": T_mid,
        "lid_depth": lid,
        "yield_frac": val["yielded"] / area,
        "yield_frac_lid": val["yielded_lid"] / (area / 3),
    }
    record["internal_fraction"] = float(params.uw_heating) / max(record["q_top"], 1e-30)
    return record, profile


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def checkpoint(step, t, records):
    eta_projection.solve()
    ratio_projection.solve()
    mesh.write_timestep("box", index=step, outputPath=out,
                        meshVars=[v, p, T, log_eta, yield_ratio])
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, f"state_{step:05d}.json"), "w") as f:
                json.dump({"step": step, "t": t, "params": params.to_dict()}, f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- initial state
records = []
t, step = 0.0, 0
if params.uw_restart < 0:
    depth = 1 - y
    T0 = (params.uw_T_int * sympy.erf(depth / 0.1)
          + (1 - params.uw_T_int) * (1 - sympy.erf((1 - depth) / 0.1))
          - 0.04 * sympy.cos(sympy.pi * params.uw_seed_cells * x / width) * sympy.sin(sympy.pi * depth))
    T.array[:, 0, 0] = np.clip(np.asarray(uw.function.evaluate(T0, T.coords)).ravel(), 0.0, 1.0)
else:
    for var in (T, v):
        var.read_timestep("box", var.name, params.uw_restart, outputPath=out)
    # a fault run's checkpoint carries no pressure; the first solve then starts cold
    if os.path.exists(os.path.join(out, f"box.mesh.P.{params.uw_restart:05d}.h5")):
        p.read_timestep("box", p.name, params.uw_restart, outputPath=out)
    with open(os.path.join(out, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    t, step = float(state["t"]), int(state["step"]) + 1
    with open(os.path.join(out, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]

uw.pprint(f"box {width} x 1, finest cell {params.uw_cell / 2 ** params.uw_refinement:.4f}, "
          f"Ra {params.uw_ra:.4g}, deta {params.uw_deta:.3g}, tau {params.uw_tau0:.4g} + "
          f"{params.uw_tau1:.4g} z, H {params.uw_heating:.4g}; output {out}")

# ----------------------------------------------------------------------------- time loop
for k in range(params.uw_steps):
    wall = time.perf_counter()
    stokes.solve()
    report = stokes.solve_report
    t_stokes = time.perf_counter() - wall
    # The implicit SUPG step is stable at any size; the accuracy estimate (field
    # change per step) under-reads the rate during an overturn, so the step is also
    # held to a Courant limit on the fastest cell.
    dt_accuracy = params.uw_dt_mult * float(adv.estimate_dt())
    adv.estimate_dt(basis="resolution", direction_aware=True)   # sets adv.dt_adv
    dt_crossing = adv.dt_adv
    dt = min(dt_accuracy, params.uw_courant * dt_crossing, params.uw_dt_max)
    adv.solve(timestep=dt)
    t += dt
    record, profile = diagnostics()
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "dt_accuracy": dt_accuracy,
                   "newton": report.nl_its, "linear": report.ksp_its,
                   "converged": bool(report.converged), "reduction": report.reduction,
                   "residuals": list(report.history),
                   "sub_its": {name: sub.its for name, sub in report.sub.items()},
                   "sub_capped": {name: sub.capped for name, sub in report.sub.items()},
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    records.append(record)
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} C {record['courant']:.2f} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"q_top {record['q_top']:6.2f} q_base {record['q_base']:6.2f} "
              f"yield {record['yield_frac']:.3f}/{record['yield_frac_lid']:.3f} | "
              f"newton {record['newton']} lin {record['linear']} sub {record['sub_its']} "
              f"capped {record['sub_capped']} {record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == params.uw_steps - 1:
        checkpoint(step, t, records)
    step += 1

uw.pprint("done")
