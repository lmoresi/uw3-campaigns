"""#1151: one application of a factorisation of the preconditioner matrix, reported converged.

4 x 4 box, body force (0, cos(pi x)). Constrained: no slip on Bottom, no flow
through Left and Right by multipliers. Plain: no slip on Bottom, Left, Right.
"""
import sys
import warnings
import numpy as np
import sympy
import underworld3 as uw

warnings.simplefilter("ignore")


def build(kind, options):
    mesh = uw.meshing.StructuredQuadBox(elementRes=(4, 4), qdegree=3)
    v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
    cls = uw.systems.Stokes_Constrained if kind == "constrained" else uw.systems.Stokes
    stokes = cls(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    x, _y = mesh.X
    stokes.bodyforce = sympy.Matrix([[0.0, sympy.cos(sympy.pi * x)]])
    stokes.tolerance = 1.0e-10
    stokes.add_essential_bc((0.0, 0.0), "Bottom")
    if kind == "constrained":
        stokes.add_constraint_bc(0.0, "Left", normal=sympy.Matrix([[-1.0, 0.0]]))
        stokes.add_constraint_bc(0.0, "Right", normal=sympy.Matrix([[1.0, 0.0]]))
    else:
        stokes.add_essential_bc((0.0, 0.0), "Left")
        stokes.add_essential_bc((0.0, 0.0), "Right")
    for key, value in options.items():
        stokes.petsc_options[key] = value
    return stokes, v


def run(kind, options):
    stokes, v = build(kind, options)
    try:
        stokes.solve()
    except Exception as err:  # noqa: BLE001 - a probe reports whatever stops it
        return f"raised {type(err).__name__}: {str(err)[:160]}"
    speed = float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max())
    snes = stokes.snes
    return (f"snes {snes.getType():9s} reason {snes.getConvergedReason():2d} its {snes.getIterationNumber():2d} "
            f"ksp {snes.ksp.getType():8s} reason {snes.ksp.getConvergedReason():2d} its {snes.ksp.getIterationNumber():3d} "
            f"largest speed {speed:.10e}")


