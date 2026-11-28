"""Row 120 (a): what turning off PETSc's GEMV path for VecMDot/VecMAXPY costs.

One process times four representative solves. Run it twice: once with PETSC_OPTIONS
unset (the default GEMV path) and once with

    PETSC_OPTIONS="-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0"

then compare the two JSON files with ``gemv_timing_compare.py``. Each case is built once,
solved once to warm up (JIT, setup), then solved ``uw_repeats`` times from the same initial
state; each repeat's wall time and iteration counts are recorded.

Cases:
  annulus_rotated_fmg  2-D annulus, rotated free slip on both walls, FMG hierarchy
  shell_stokes         3-D spherical shell, rotated free slip on both walls
  vep_box              visco-elasto-plastic box step, velocity GMRES restart 30
  advdiff              advection-diffusion step on a box

    python gemv_timing.py -uw_out default.json
    PETSC_OPTIONS="-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0" python gemv_timing.py -uw_out off.json
"""
import json
import os
import time

import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(
    uw_out=uw.Param("gemv_timing.json", description="where the results go"),
    uw_repeats=uw.Param(5, description="timed solves per case, after one warm-up"),
    uw_scale=uw.Param(1.0, description="cell sizes are divided by this (2 = finer)"),
    uw_cases=uw.Param("annulus_rotated_fmg,shell_stokes,vep_box,advdiff",
                      description="comma-separated subset"),
)
S = float(params.uw_scale)


def stokes_on(mesh, p_continuous=True):
    v = uw.discretisation.MeshVariable("V", mesh, mesh.dim, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1, continuous=p_continuous)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1
    return s


def radial_load(mesh, k=3):
    r = sympy.sqrt(sum(x ** 2 for x in mesh.X))
    return sympy.Matrix(mesh.X) / r * sympy.cos(k * sympy.atan2(mesh.X[1], mesh.X[0]))


def case_annulus():
    mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.55, cellSize=0.1 / S,
                              refinement=1, qdegree=3)
    s = stokes_on(mesh)
    s.bodyforce = radial_load(mesh)
    s.add_rotated_freeslip_bc(0, "Upper")
    s.add_rotated_freeslip_bc(0, "Lower")
    return s, (lambda: s.solve(zero_init_guess=True)), {}


def case_shell():
    mesh = uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.55, cellSize=0.25 / S,
                                     refinement=1, qdegree=3)
    s = stokes_on(mesh)
    s.bodyforce = radial_load(mesh, k=2)
    s.add_rotated_freeslip_bc(0, "Upper")
    s.add_rotated_freeslip_bc(0, "Lower")
    return s, (lambda: s.solve(zero_init_guess=True)), {}


def case_vep():
    mesh = uw.meshing.UnstructuredSimplexBox(cellSize=0.1 / S, refinement=1)
    v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.bodyforce = sympy.Matrix([[0.0, -1.0]])
    cm = uw.constitutive_models.ViscoElasticPlasticFlowModel(s.Unknowns, order=1)
    s.constitutive_model = cm
    cm.Parameters.shear_viscosity_0 = 1.0
    cm.Parameters.shear_modulus = 1.0
    cm.Parameters.dt_elastic = sympy.Rational(1, 10)
    cm.Parameters.yield_stress = uw.expression(r"C", 0.5) + uw.expression(r"\mu", 0.3) * p.sym[0]
    cm.Parameters.yield_stress_min = uw.expression(r"\tau_{\min}", 0.01)
    s.add_dirichlet_bc((1.0, 0.0), "Top")
    for side in ("Bottom", "Left", "Right"):
        s.add_dirichlet_bc((0.0, 0.0), side)
    s.petsc_options["fieldsplit_velocity_ksp_type"] = "gmres"
    s.petsc_options["fieldsplit_velocity_ksp_gmres_restart"] = 30
    v0 = np.zeros_like(s.u.array)
    v0[:, 0, 0] = s.u.coords[:, 1]
    s.u.array[...] = v0
    # a step advances the elastic history, so a repeat is a FRESH solver's first step
    # (the JIT cache makes the rebuild cheap; the setup is inside the timing, alike in
    # both runs)
    return s, (lambda: s.solve(zero_init_guess=False, timestep=0.1)), {"fresh": case_vep}


def case_advdiff():
    mesh = uw.meshing.UnstructuredSimplexBox(cellSize=0.05 / S, refinement=1)
    T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
    vel = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
    x, y = mesh.X
    vel.array[:, 0, 0] = -np.sin(np.pi * vel.coords[:, 1]) * np.cos(np.pi * vel.coords[:, 0])
    vel.array[:, 0, 1] = np.cos(np.pi * vel.coords[:, 1]) * np.sin(np.pi * vel.coords[:, 0])
    ad = uw.systems.AdvDiffusion(mesh, u_Field=T, V_fn=vel)
    ad.constitutive_model = uw.constitutive_models.DiffusionModel
    ad.constitutive_model.Parameters.diffusivity = 1.0e-3
    ad.add_dirichlet_bc(1.0, "Bottom")
    ad.add_dirichlet_bc(0.0, "Top")
    T0 = np.exp(-((T.coords[:, 0] - 0.5) ** 2 + (T.coords[:, 1] - 0.3) ** 2) / 0.01)
    T.array[:, 0, 0] = T0
    return ad, (lambda: ad.solve(timestep=0.01)), {"T0": T0}


CASES = {"annulus_rotated_fmg": case_annulus, "shell_stokes": case_shell,
         "vep_box": case_vep, "advdiff": case_advdiff}


def restore(solver, state):
    if "u0" in state:
        solver.u.array[...] = state["u0"]
    if "T0" in state:
        solver.u.array[:, 0, 0] = state["T0"]


def counts(solver):
    snes = solver.snes
    info = getattr(solver, "_rotated_freeslip_info", None) or {}
    return {"snes_its": int(snes.getIterationNumber()),
            "linear_its": int(snes.getLinearSolveIterations()),
            "reason": int(snes.getConvergedReason()),
            "rotated_ksp_its": (tuple(info["ksp_its"]) if isinstance(info.get("ksp_its"), list)
                                else info.get("ksp_its")),
            "rotated_newton_its": info.get("nonlinear_iterations")}


results = {"PETSC_OPTIONS": os.environ.get("PETSC_OPTIONS", ""), "np": uw.mpi.size,
           "repeats": int(params.uw_repeats), "scale": S, "cases": {}}
for name in str(params.uw_cases).split(","):
    try:
        solver, solve, state = CASES[name]()
        solve()                                   # warm-up: JIT, setup
        runs = []
        for _ in range(int(params.uw_repeats)):
            if "fresh" in state:
                solver, solve, _state = state["fresh"]()
            restore(solver, state)
            uw.mpi.comm.Barrier()
            t0 = time.perf_counter()
            solve()
            uw.mpi.comm.Barrier()
            wall = uw.mpi.comm.allreduce(time.perf_counter() - t0, op=uw.mpi.MPI.MAX) \
                if hasattr(uw.mpi, "MPI") else time.perf_counter() - t0
            runs.append({"wall": wall, **counts(solver)})
        results["cases"][name] = runs
        uw.pprint(f"{name}: walls {[round(r['wall'], 3) for r in runs]} "
                  f"its {[(r['snes_its'], r['linear_its'], r['rotated_ksp_its']) for r in runs]}")
    except Exception as exc:                      # noqa: BLE001 - recorded, the others still run
        results["cases"][name] = {"error": f"{type(exc).__name__}: {exc}"}
        uw.pprint(f"{name}: FAILED {type(exc).__name__}: {exc}")

if uw.mpi.rank == 0:
    with open(str(params.uw_out), "w") as f:
        json.dump(results, f, indent=1)
