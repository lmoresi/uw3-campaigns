"""Review r2 probe (serial): what the second sweep costs per Jacobian.
Time of snes.computeJacobian(x, J, P) under the branch's routine and under PETSc's
one pass, same solver, alternating blocks; minimum of each block is reported."""
import ctypes
import importlib.util
import sys
import time
from pathlib import Path

import sympy
from petsc4py import PETSc

import underworld3 as uw
from underworld3.cython import generic_solvers as solvers_module

worktree = Path(sys.argv[1])
cell_size = float(sys.argv[2])
spec = importlib.util.spec_from_file_location(
    "t0786", worktree / "tests/test_0786_stokes_jacobian_and_preconditioner_one_call_each.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0),
                                         cellSize=cell_size, qdegree=3)
v = uw.discretisation.MeshVariable("V", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = sympy.Matrix([0, sympy.cos(sympy.pi * mesh.X[0])])
for wall in ("Left", "Right"):
    stokes.add_essential_bc((0.0, 0.0), wall)
stokes.add_nitsche_bc(0.0, "Top")
stokes.add_nitsche_bc(0.0, "Bottom")
stokes.petsc_options["snes_type"] = "ksponly"
stokes.solve()

J, P, _ = stokes.snes.getJacobian()
x = stokes.snes.getSolution()
cells = mesh.dm.getHeightStratum(0)
print(f"cells {cells[1] - cells[0]}, unknowns {x.getSize()}")

uw_library = ctypes.CDLL(solvers_module.__file__)
try:
    set_uw = uw_library.UW_DMPlexSetSNESLocalFEM
    set_uw.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p]
    set_uw.restype = ctypes.c_int
except AttributeError:
    set_uw = None
print("UW_DMPlexSetSNESLocalFEM reachable through ctypes:", set_uw is not None)


def best(n=5):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        stokes.snes.computeJacobian(x, J, P)
        times.append(time.perf_counter() - t0)
    return min(times)


for block in range(3):
    if set_uw is not None:
        assert set_uw(stokes.dm.handle, False, None) == 0
    assert not t._has_the_one_pass_assembly_of_petsc(stokes.dm)
    two = best()
    t._use_the_one_pass_assembly_of_petsc(stokes.dm)
    one = best()
    print(f"block {block}: two calls {two:.4f} s, PETSc one pass {one:.4f} s, ratio {two / one:.3f}")
    if set_uw is None:
        break
