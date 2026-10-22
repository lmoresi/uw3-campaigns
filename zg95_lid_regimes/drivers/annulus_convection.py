"""Yielding-lid convection in an annulus: the periodic counterpart of
``box_convection.py``, run to match the annulus lid's mobility and boundary layers to
the box's before the fault goes in.

The rheology, heating and transport are the box's (``annulus_model.py``). Lengths are
in units of the layer depth (r_o = 1 / 0.45, r_i = 0.55 / 0.45 for the campaign's
radius ratio), so every parameter and the clock are the box's without conversion; the
defaults are the box reference (tau1 / Ra = 1). Rotated strong free-slip on both
walls with the exact radial normal; T = 0 on the outer wall, 1 on the inner. Eulerian
SUPG transport. The velocity block uses geometric multigrid on the annulus's own
refinement hierarchy.

The initial state is the box's: interior at T_int with error-function boundary
layers, perturbed by cos(seed_modes theta) (2 seed_modes cells).

    mpirun -np 4 python annulus_convection.py -uw_out ~/+Simulations/zg95/annulus_regimes/runs/<name>

Restart, in the same directory or from another run's checkpoint (parameters may change
at the restart):

    mpirun -np 4 python annulus_convection.py -uw_out <dir> -uw_restart 200
    mpirun -np 4 python annulus_convection.py -uw_out <new dir> -uw_source <run dir> -uw_restart 200 -uw_tau1 1.4e6
"""
import json
import os
import sys
import time

import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annulus_model import (AnnulusDiagnostics, annulus_mesh, annulus_radii, free_slip_walls,
                           set_viscoplastic)

params = uw.Params(
    uw_out="~/+Simulations/zg95/annulus_regimes/runs/test",
    uw_source="",               # run directory to restart from (empty: uw_out itself)
    # Finest cell 1/32 as in the box, from a coarser base: the rotated walls leave a
    # rigid rotation in the coarse operator, so the coarse solve is a dense SVD,
    # repeated at every Newton increment. 124 coarse cells cost little; the box's
    # coarse cell (0.125, ~1.7k cells) made each increment take minutes.
    uw_cell=0.5,                # coarsest cell size (layer depths)
    uw_refinement=4,            # halvings of the coarsest mesh (multigrid levels - 1)
    uw_ra=9.1125e5,             # Rayleigh number on the basal viscosity
    uw_deta=3.0e4,              # viscosity contrast across the layer
    uw_tau0=2.025e4,            # yield stress at the surface
    uw_tau1=9.1125e5,           # yield stress gradient with depth
    uw_heating=1.4175,          # internal heating rate H
    uw_yield_softness=0.2,      # soft-min width delta of the yield law
    uw_T_int=0.8,               # initial interior temperature
    uw_seed_modes=5,            # azimuthal wavenumber of the initial perturbation
    uw_tol=1.0e-3,              # Stokes nonlinear tolerance
    uw_dt_mult=3.0,             # multiple of the SUPG accuracy estimate
    uw_courant=1.0,             # Courant limit: cells crossed per step by the fastest flow
    uw_dt_max=5.0e-3,           # step cap
    uw_steps=50,
    uw_ckpt_every=10,
    uw_restart=-1,              # checkpoint index to restart from (-1: fresh start)
    uw_verbose=0,               # 1: print every nonlinear iteration of the rotated solve
    uw_cold_switch=1.0e-2,      # a solve from rest runs Picard to this residual reduction, then Newton
)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
source = os.path.expanduser(params.uw_source) if params.uw_source else out
r_o, r_i = annulus_radii()

mesh = annulus_mesh(params.uw_cell, params.uw_refinement)
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
eta_T = set_viscoplastic(stokes, T.sym[0], deta, tau0, tau1, params.uw_yield_softness, r_o)
stokes.bodyforce = Ra * T.sym[0] * mesh.CoordinateSystem.unit_e_0
free_slip_walls(stokes)
stokes.tolerance = params.uw_tol
# Picard steps on the rotated path need the continuation tangent. A solve from rest
# runs Picard to uw_cold_switch of its starting residual, then Newton (pure Newton
# from rest stalled at tau1/Ra 1.5); warm solves switch to Newton at once.
stokes.consistent_jacobian = "continuation"
# the rotated path does not read the native hierarchy: register its coarse levels
set_custom_fmg(stokes, mesh._coarse_level_meshes()[:-1], field_id=0)

eta_eff = stokes.constitutive_model.viscosity

# ----------------------------------------------------------------------------- energy
adv = uw.systems.AdvDiffusion(mesh, T, v.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = 1
adv.f = H
adv.add_dirichlet_bc(0.0, "Upper")
adv.add_dirichlet_bc(1.0, "Lower")

# P1 fields for the renders: log10 of the effective viscosity, and eta_eff / eta(T)
# (1 where the viscous branch holds, below 1 where the lid yields).
eta_projection = uw.systems.Projection(mesh, log_eta)
eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
ratio_projection = uw.systems.Projection(mesh, yield_ratio)
ratio_projection.uw_function = eta_eff / eta_T

diagnostics = AnnulusDiagnostics(T, v, eta_eff, eta_T, params.uw_heating)


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def checkpoint(step, t, records):
    eta_projection.solve()
    ratio_projection.solve()
    mesh.write_timestep("annulus", index=step, outputPath=out,
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
    radius = sympy.sqrt(x ** 2 + y ** 2)
    depth = r_o - radius
    theta = sympy.atan2(y, x)
    T0 = (params.uw_T_int * sympy.erf(depth / 0.1)
          + (1 - params.uw_T_int) * (1 - sympy.erf((1 - depth) / 0.1))
          - 0.04 * sympy.cos(params.uw_seed_modes * theta) * sympy.sin(sympy.pi * depth))
    T.array[:, 0, 0] = np.clip(np.asarray(uw.function.evaluate(T0, T.coords)).ravel(), 0.0, 1.0)
else:
    for var in (T, v, p):
        var.read_timestep("annulus", var.name, params.uw_restart, outputPath=source)
    with open(os.path.join(source, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    t, step = float(state["t"]), int(state["step"]) + 1
    with open(os.path.join(source, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]
    if source != out:
        with uw.selective_ranks(0) as selected:
            if selected:
                with open(os.path.join(out, "source.json"), "w") as f:
                    json.dump({"source": source, "index": params.uw_restart}, f, indent=1)

level_cells = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
               for m in mesh._coarse_level_meshes()]
uw.pprint(f"annulus r_o {r_o:.4f} r_i {r_i:.4f} (depth 1), levels (cells) {level_cells}, finest cell "
          f"{params.uw_cell / 2 ** params.uw_refinement:.4f}, Ra {params.uw_ra:.4g}, "
          f"deta {params.uw_deta:.3g}, tau {params.uw_tau0:.4g} + {params.uw_tau1:.4g} z "
          f"(tau1/Ra {params.uw_tau1 / params.uw_ra:.3g}), H {params.uw_heating:.4g}; output {out}")

# ----------------------------------------------------------------------------- time loop
for k in range(params.uw_steps):
    wall = time.perf_counter()
    cold = k == 0 and params.uw_restart < 0
    stokes.newton_switch_rtol = params.uw_cold_switch if cold else 1.0
    stokes.solve(zero_init_guess=cold, verbose=bool(params.uw_verbose))
    report = stokes.solve_report
    info = stokes._rotated_freeslip_info or {}
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
    record, profile = diagnostics.record()
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "dt_accuracy": dt_accuracy,
                   "newton": report.nl_its, "linear": report.ksp_its,
                   "converged": bool(report.converged), "reduction": report.reduction,
                   "vel_its": info.get("vel_its_last"), "pres_its": info.get("pres_its_last"),
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    records.append(record)
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} C {record['courant']:.2f} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"q_top {record['q_top']:6.2f} q_base {record['q_base']:6.2f} "
              f"yield {record['yield_frac']:.3f}/{record['yield_frac_lid']:.3f} | "
              f"newton {record['newton']} vel {record['vel_its']} pres {record['pres_its']} "
              f"conv {record['converged']} {record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == params.uw_steps - 1:
        checkpoint(step, t, records)
    step += 1

uw.pprint("done")
