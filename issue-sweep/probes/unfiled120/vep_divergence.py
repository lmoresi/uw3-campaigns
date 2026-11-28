"""Row 120: how far a yielding VEP run drifts from the GEMV path's last-bit noise.

The VEP box of gemv_timing.py, stepped ``uw_steps`` times; every step's velocity,
pressure and carried stress, and its iteration counts, are saved to
``<uw_out>-step<k>.npz``. Run it in separate processes with PETSC_OPTIONS unset (the
GEMV path) and with "-vec_mdot_use_gemv 0 -vec_maxpy_use_gemv 0", then compare with
vep_divergence_compare.py.
"""
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(
    uw_out=uw.Param("vep", description="prefix of the per-step files"),
    uw_steps=uw.Param(10, description="time steps"),
    uw_cellsize=uw.Param(0.2, description="base cell size (refinement 1)"),
    uw_tolerance=uw.Param(0.0, description="solver tolerance (0: the default)"),
)

mesh = uw.meshing.UnstructuredSimplexBox(cellSize=float(params.uw_cellsize), refinement=1)
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
if float(params.uw_tolerance) > 0:
    s.tolerance = float(params.uw_tolerance)
v0 = np.zeros_like(s.u.array)
v0[:, 0, 0] = s.u.coords[:, 1]
s.u.array[...] = v0

for k in range(int(params.uw_steps)):
    s.solve(zero_init_guess=False, timestep=0.1)
    stress = np.array(s.Unknowns.DFDt.psi_star[0].array)
    np.savez(f"{params.uw_out}-step{k}.npz", v=np.array(v.array), p=np.array(p.array), stress=stress,
             snes_its=s.snes.getIterationNumber(), linear_its=s.snes.getLinearSolveIterations(),
             reason=s.snes.getConvergedReason(), tolerance=s.tolerance)
    uw.pprint(f"step {k}: snes {s.snes.getIterationNumber()} linear "
              f"{s.snes.getLinearSolveIterations()} reason {s.snes.getConvergedReason()}")
