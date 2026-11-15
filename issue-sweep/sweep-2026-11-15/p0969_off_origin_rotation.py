"""#969: an annulus moved off the origin, rotated free slip on both walls.

The rotation about the moved centre is an exact null mode of the constraint. The
probe reports the warnings raised, the solver's convergence, and the rigid
rotation about the moved centre left in the answer (times R over the rms speed).
"""
import warnings
import numpy as np
import sympy
import underworld3 as uw

params = uw.Params(delta=1.0e-3)
delta = float(params.delta)
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.2, refinement=1)
mesh.deform(np.asarray(mesh.X.coords) + np.array([delta, 0.0]))
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
st = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
st.constitutive_model = uw.constitutive_models.ViscousFlowModel
st.constitutive_model.Parameters.shear_viscosity_0 = 1.0
x, y = mesh.X
xc = x - delta
r = sympy.sqrt(xc ** 2 + y ** 2)
st.bodyforce = sympy.Matrix([[xc / r * sympy.cos(3 * sympy.atan2(y, xc)), y / r * sympy.cos(3 * sympy.atan2(y, xc))]])
st.add_rotated_freeslip_bc(0.0, "Upper")
st.add_rotated_freeslip_bc(0.0, "Lower")
st.tolerance = 1.0e-8
st.petsc_use_pressure_nullspace = True
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    st.solve()
for w in caught:
    print("warning:", str(w.message)[:200])
X = np.asarray(v.coords)
V = np.asarray(v.array).reshape(-1, 2)
t = np.column_stack([-X[:, 1], X[:, 0] - delta])
omega = (V * t).sum() / (t * t).sum()
vrms = np.sqrt((V ** 2).sum(axis=1).mean())
print(f"delta {delta}: reason {st.snes.getConvergedReason()}, rigid rotation about (delta, 0) "
      f"x R / v_rms = {abs(omega) * 1.0 / vrms:.3e}")
