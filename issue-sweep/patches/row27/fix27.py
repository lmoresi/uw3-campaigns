"""Row 27 broader fixtures: counts and answers per solve, for a before/after comparison.

    python fix27.py <tag> <case>
cases: loop (annulus, mu 1e-4, 8 warm solves with a moving forcing), shell (3-D spherical
shell, rotated free-slip both walls), ti (annulus, transversely isotropic, radial director,
eta_1 = 0.01 eta_0), shell_mu1, ti_mu1."""
import sys, time, json
import numpy as np
import sympy
tag, case = sys.argv[1], sys.argv[2]
sys.argv = sys.argv[:1]
import underworld3 as uw
from underworld3.utilities import custom_mg

def info_of(s):
    i = s._rotated_freeslip_info
    ctx = s._rotated_linear_cache["ctx"]
    return dict(outer=i["ksp_its"], vel=i["vel_its_last"], pres=i["pres_its_last"],
                capped=i.get("sub_capped"), conv=bool(i["converged"]),
                modes=ctx.get("projected_null_modes"))

out = []
if case in ("loop", "ti", "ti_mu1"):
    mu = 1.0e-4 if case in ("loop", "ti") else 1.0
    mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.1, refinement=2, qdegree=3)
    v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    X = mesh.X
    r = sympy.sqrt(X[0] ** 2 + X[1] ** 2)
    th = sympy.atan2(X[1], X[0])
    if case == "loop":
        s.constitutive_model = uw.constitutive_models.ViscousFlowModel
        s.constitutive_model.Parameters.shear_viscosity_0 = mu
    else:
        s.constitutive_model = uw.constitutive_models.TransverseIsotropicFlowModel
        P = s.constitutive_model.Parameters
        P.shear_viscosity_0 = mu
        P.shear_viscosity_1 = 0.01 * mu
        P.director = sympy.Matrix([X[0] / r, X[1] / r])
    phase = uw.function.expression(r"\phi", 0.0, "forcing phase")
    s.bodyforce = (1.0e3 * sympy.cos(4 * th + phase) * sympy.sin(sympy.pi * (r - 0.5) / 0.5)
                   * sympy.Matrix([X[0] / r, X[1] / r]))
    s.add_rotated_freeslip_bc(0, "Lower")
    s.add_rotated_freeslip_bc(0, "Upper")
    s.petsc_use_pressure_nullspace = True
    s.tolerance = 1.0e-6
    custom_mg.set_custom_fmg(s, mesh._coarse_level_meshes()[:-1], field_id=0)
    steps = 8 if case == "loop" else 1
    for k in range(steps):
        phase.sym = 0.1 * k
        t0 = time.time()
        s.solve(zero_init_guess=(k == 0))
        d = info_of(s); d["wall"] = round(time.time() - t0, 3); d["step"] = k
        V = np.asarray(v.array).copy(); np.save(f"f27_{tag}_{case}_{k}.npy", V)
        d["vnorm"] = float(np.linalg.norm(V)); out.append(d)
else:
    mu = 1.0e-4 if case in ("shell", "shell_n") else 1.0
    mesh = uw.meshing.SphericalShell(radiusOuter=1.0, radiusInner=0.55, cellSize=0.3, refinement=1, qdegree=3)
    v = uw.discretisation.MeshVariable("V", mesh, 3, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = mu
    X = mesh.X
    r = sympy.sqrt(X[0] ** 2 + X[1] ** 2 + X[2] ** 2)
    s.bodyforce = 1.0e3 * (X[2] / r) * (X[0] / r) * sympy.sin(sympy.pi * (r - 0.55) / 0.45) * \
        sympy.Matrix([X[0] / r, X[1] / r, X[2] / r])
    nrm = mesh.CoordinateSystem.unit_e_0 if case.endswith("_n") else None
    s.add_rotated_freeslip_bc(0, "Lower", normal=nrm)
    s.add_rotated_freeslip_bc(0, "Upper", normal=nrm)
    s.petsc_use_pressure_nullspace = True
    s.tolerance = 1.0e-6
    custom_mg.set_custom_fmg(s, mesh._coarse_level_meshes()[:-1], field_id=0)
    t0 = time.time()
    s.solve(zero_init_guess=True)
    d = info_of(s); d["wall"] = round(time.time() - t0, 3); d["step"] = 0
    V = np.asarray(v.array).copy(); np.save(f"f27_{tag}_{case}_0.npy", V)
    d["vnorm"] = float(np.linalg.norm(V)); d["cells"] = mesh.dm.getHeightStratum(0)[1]; out.append(d)
for d in out:
    print("F27", tag, case, json.dumps(d), flush=True)
