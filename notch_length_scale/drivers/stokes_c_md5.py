"""Generated-C fingerprint of ordinary Stokes solves, to prove the coupled-field plumbing
leaves them byte-identical.

Runs three solvers that never call ``add_coupled_field``: an isoviscous box (Picard),
a Drucker-Prager box (consistent Newton) and a block-constrained box (multipliers, the
other extra-field path). Every JIT bundle a solve generates is fingerprinted by the md5
of its C header. Run on the branch base and on the branch; the lists must agree.
"""
import hashlib
import os
import re

import sympy
import underworld3 as uw
import underworld3.utilities._jitextension as jx

params = uw.Params(
    uw_res=uw.Param(6, description="cells per side"),
    uw_dump=uw.Param("", description="directory to write each C header into"),
)
seen = []
_generate = jx.generate_c_source


def fingerprinted(*args, **kwargs):
    modname, codeguys, diag = _generate(*args, **kwargs)
    # each bundle's C names carry a random five-letter prefix; normalise it
    header = re.sub(r"\b[A-Z]{5}_petsc_", "X_petsc_", dict(codeguys)["cy_ext.h"])
    seen.append(hashlib.md5(header.encode()).hexdigest())
    if str(params.uw_dump):
        os.makedirs(str(params.uw_dump), exist_ok=True)
        with open(os.path.join(str(params.uw_dump), f"header_{len(seen)}.h"), "w") as fh:
            fh.write(header)
    return modname, codeguys, diag


jx.generate_c_source = fingerprinted


def box():
    return uw.meshing.UnstructuredSimplexBox(
        minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
        cellSize=1.0 / int(params.uw_res), qdegree=3)


def driven(stokes):
    stokes.add_dirichlet_bc((1.0, 0.0), "Top")
    stokes.add_dirichlet_bc((0.0, 0.0), "Bottom")
    stokes.add_dirichlet_bc((None, 0.0), "Left")
    stokes.add_dirichlet_bc((None, 0.0), "Right")


def report(label, start):
    uw.pprint(f"[md5] {label}: " + " ".join(seen[start:]))


start = len(seen)
mesh = box()
stokes = uw.systems.Stokes(mesh)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
x, y = mesh.X
stokes.bodyforce = sympy.Matrix([0, -sympy.sin(sympy.pi * x)])
driven(stokes)
stokes.solve()
report("isoviscous", start)

start = len(seen)
mesh = box()
stokes = uw.systems.Stokes(mesh)
stokes.constitutive_model = uw.constitutive_models.ViscoPlasticFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.constitutive_model.Parameters.yield_stress = 0.3 + 0.1 * stokes.p.sym[0]
stokes.consistent_jacobian = True
driven(stokes)
stokes.petsc_options["snes_max_it"] = 5
stokes.solve()
report("drucker-prager newton", start)

start = len(seen)
mesh = box()
stokes = uw.systems.Stokes_Constrained(mesh)
x, y = mesh.X
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.bodyforce = sympy.Matrix([0, -sympy.sin(sympy.pi * x)])
stokes.add_dirichlet_bc((0.0, 0.0), "Top")
stokes.add_dirichlet_bc((0.0, 0.0), "Bottom")
stokes.add_constraint_bc(0.0, "Left", normal=sympy.Matrix([[-1.0, 0.0]]))
stokes.add_constraint_bc(0.0, "Right", normal=sympy.Matrix([[1.0, 0.0]]))
stokes.solve()
report("block-constrained", start)
