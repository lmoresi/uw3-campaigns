"""What the refusal's example does when followed, where it is not what the caller asked. Serial."""
import sys, json, warnings
import numpy as np, sympy
import underworld3 as uw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from truth_table import stokes2d, stokes3d, poisson

def wall(var, axis, at):
    X = np.asarray(var.coords)
    return np.abs(X[:, axis] - at) < 1e-9

# 1. scalar field: message for add_dirichlet_bc(0.0, "Top", 1) says e.g. (None, 0.0)
mesh, s, t, _ = poisson()
try:
    s.add_dirichlet_bc(0.0, "Top", 1)
except ValueError as e:
    print("poisson refusal:", e)
s.add_dirichlet_bc((None, 0.0), "Top")
bc = s.essential_bcs[-1]
print("poisson stored", bc.fn, list(map(int, bc.components)))
s.solve()
on = wall(t, 1, 1.0)
print("poisson T on Top min/max", float(np.asarray(t.array)[on, 0, 0].min()), float(np.asarray(t.array)[on, 0, 0].max()), "reason", s.snes.getConvergedReason())

# 2. the cheat sheet's old line: (0.0,), "Left", (0, 1) with 0.05 to tell values apart
mesh, s, v, p = stokes2d()
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s.add_dirichlet_bc((0.05,), "Left", (0, 1))
except ValueError as e:
    print("stokes2d refusal:", e)
s.add_dirichlet_bc((None, 0.05), "Left")
s.solve()
on = wall(v, 0, 0.0) & (np.asarray(v.coords)[:, 1] > 1e-9)
a = np.asarray(v.array)[on, 0, :]
print("stokes2d following the example: u_x on Left", float(a[:, 0].min()), float(a[:, 0].max()), "u_y", float(a[:, 1].min()), float(a[:, 1].max()))

# 3. 3-D (0.01, 0.05), "Left", (1, 2)
mesh, s, v, p = stokes3d()
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s.add_dirichlet_bc((0.01, 0.05), "Left", (1, 2))
except ValueError as e:
    print("stokes3d refusal:", e)
s.add_dirichlet_bc((None, None, 0.01), "Left")
s.solve()
on = wall(v, 0, 0.0) & (np.asarray(v.coords)[:, 2] > 1e-9)
a = np.asarray(v.array)[on, 0, :]
print("stokes3d following the example: u_y on Left", float(a[:, 1].min()), float(a[:, 1].max()), "u_z", float(a[:, 2].min()), float(a[:, 2].max()))

# 4. a quantity in other units
mesh, s, v, p = stokes2d()
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s.add_dirichlet_bc(uw.quantity(5.0, "cm/yr"), "Left", 1)
except ValueError as e:
    print("quantity refusal:", e)
