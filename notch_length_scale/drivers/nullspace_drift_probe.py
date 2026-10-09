"""Is the closed-box pressure drift under monolithic MUMPS LU pre-existing?

Plain Stokes (no coupled field) in a closed box, pressure null space declared, exact
Newton with MUMPS LU of the Jacobian, and a strain-rate-dependent viscosity so the solve
takes several Newton steps (a constant pressure leaves the residual unchanged, so drift
shows only over repeated steps). Reports the final |F| and the pressure mean on rank 0.
Run under mpirun -n 3, several times.
"""
import numpy as np
import sympy
import underworld3 as uw

mesh = uw.meshing.UnstructuredSimplexBox(
    minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=1.0 / 8, qdegree=3)
stokes = uw.systems.Stokes(mesh)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1 + stokes.Unknowns.Einv2 ** 2
stokes.add_dirichlet_bc((1.0, 0.0), "Top")
stokes.add_dirichlet_bc((0.0, 0.0), "Bottom")
stokes.add_dirichlet_bc((0.0, 0.0), "Left")
stokes.add_dirichlet_bc((0.0, 0.0), "Right")
stokes.petsc_use_pressure_nullspace = True
stokes.consistent_jacobian = True
stokes.saddle_preconditioner = 0
stokes.petsc_options["pc_type"] = "lu"
stokes.petsc_options["pc_factor_mat_solver_type"] = "mumps"
stokes.petsc_options["ksp_type"] = "preonly"
stokes.petsc_options["snes_rtol"] = 1.0e-12
stokes.petsc_options["snes_atol"] = 1.0e-14
stokes.solve()
p_mean = uw.maths.Integral(mesh, stokes.p.sym[0]).evaluate()
uw.pprint(f"[drift] reason {stokes.snes.getConvergedReason()}  its {stokes.snes.getIterationNumber()}  "
          f"|F| {stokes.snes.getFunctionNorm():.3e}  pressure mean {p_mean:.3e}")
