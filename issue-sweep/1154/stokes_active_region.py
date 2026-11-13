"""Stokes with set_active_region: does the solve run? (one rank)

    python stokes_active_region.py            # with set_active_region
    python stokes_active_region.py -uw_region 0   # the same solve without it
"""
import faulthandler

faulthandler.enable()

import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(uw_region=1)

mesh = uw.meshing.BoxInternalBoundary(
    minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), zintCoord=0.5,
    cellSize=0.2, simplex=True, qdegree=3)
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)

stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = sympy.Matrix([[0.0, sympy.cos(sympy.pi * mesh.X[0])]])
for wall in ("Top", "Bottom", "Left", "Right"):
    stokes.add_essential_bc((0.0, 0.0), wall)

value = mesh.regions.Outer.value
label = mesh.dm.getLabel("Outer")
print(f"label Outer: region value {value}, points at that value "
      f"{label.getStratumSize(value)}, points at value 1 {label.getStratumSize(1)}", flush=True)
if int(params.uw_region):
    stokes.set_active_region("Outer", value)
    print("set_active_region called", flush=True)

stokes.solve()
print(f"solved: reason {stokes.snes.getConvergedReason()}, "
      f"max |v| {np.abs(np.asarray(v.array)).max():.8e}", flush=True)
