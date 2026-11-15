"""#1069: after narrow rewires, how many kernels does a natural BC's boundary weak form hold?

Poisson with a Robin flux on Top. Build and solve, then force the in-place rewire
twice, changing the Robin coefficient each time. After each, the PetscDS is viewed and the kernel names listed for
boundary_residual_f0 are counted.
"""
import os, re
from petsc4py import PETSc
import underworld3 as uw

here = os.path.dirname(os.path.abspath(__file__))
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0), maxCoords=(1.0, 1.0), cellSize=0.25, qdegree=3)
T = uw.discretisation.MeshVariable("Tp", mesh, 1, degree=2)
s = uw.systems.Poisson(mesh, u_Field=T)
s.constitutive_model = uw.constitutive_models.DiffusionModel
s.constitutive_model.Parameters.diffusivity = 1.0
s.f = 1.0
s.add_dirichlet_bc(0.0, "Bottom")
kk = uw.expression(r"k_{R}", -1.0)
s.add_natural_bc([-kk * T.sym[0] + 0.2], "Top")


def count(tag):
    path = os.path.join(here, f"out_1069_{tag}.txt")
    v = PETSc.Viewer().createASCII(path)
    s.dm.getDS().view(v)
    v.destroy()
    txt = open(path).read()
    lines = [l for l in txt.splitlines() if "UW" in l and "_petsc_eqn_" in l]
    sec = txt.split("boundary_residual_f0")[1].split("\n", 2)[1] if "boundary_residual_f0" in txt else ""
    print(f"{tag}: boundary_residual_f0 entry: {sec.strip()}")
    print(f"{tag}: kernels listed there: {len(re.findall(r'_petsc_eqn_', sec))}")


s.solve(zero_init_guess=True)
count("build")
for r, value in ((1, -(1 + mesh.X[0])), (2, -(2 + mesh.X[1]))):
    kk.sym = value                      # changes the maths, so the JIT key
    s._needs_function_rewire = True     # the narrow route: kernels only, BCs kept
    s.solve(zero_init_guess=True)
    count(f"rewire{r}")
