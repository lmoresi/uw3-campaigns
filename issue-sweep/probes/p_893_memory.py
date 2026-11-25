"""#893, serial: peak memory of a Stokes solve whose custom-FMG coarse tail holds an
unsplit placed-ribbon ladder level, against the unplaced tail, on an annulus.

    python p_893_memory.py <cellSize> <placed: 0|1> [top radius, default 0.9]

A fresh process per case: ru_maxrss is the process's peak. Under MPI each rank
reports its own peak; RES prints the largest and the sum over ranks, and the
global cell count of each level. PETSc options on the command line reach the
solve (underworld3 initialises petsc4py with sys.argv), so

    mpirun -n 8 python p_893_memory.py 0.025 1 -mat_product_algorithm scalable

compares the Galerkin product algorithms."""
import resource
import sys
import time

import numpy as np
import sympy

import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.place_surface import place_fault_ribbon_2d

cell = float(sys.argv[1])
placed = sys.argv[2] == "1"
r_top = float(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("-") else 0.9


def peak_mb():
    # ru_maxrss is in bytes on macOS, kilobytes on Linux
    scale = 1.0e6 if sys.platform == "darwin" else 1.0e3
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / scale


def over_ranks(x):
    xs = uw.mpi.comm.allgather(x)
    return max(xs), sum(xs)


base = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=cell, refinement=2,
                          qdegree=2)
L0, L1 = base._coarse_level_meshes()[:2]
h = cell / 4
th = np.radians(80.0)
dip = np.radians(35.0)
top = np.array([np.cos(th), np.sin(th)]) * r_top
inward = -np.array([np.cos(th - dip), np.sin(th - dip)])
n = int(0.3 / h)
trace = top + (np.arange(n + 1) * h)[:, None] * inward
fine = place_fault_ribbon_2d(base, [("Fault", trace)], 2 * h, margin_rings=1, clearance=0.7,
                             split=False, mesher="ladder")[0]
if placed:
    t2 = top + (np.arange(n // 2 + 1) * 2 * h)[:, None] * inward
    mid = place_fault_ribbon_2d(L1, [("Fault", t2)], 4 * h, margin_rings=1, clearance=0.7,
                                split=False, mesher="ladder")[0]
    levels = [L0, L1, mid]
else:
    levels = [L0, L1]
x, y = fine.X
r = sympy.sqrt(x ** 2 + y ** 2)
v = uw.discretisation.MeshVariable("V", fine, 2, degree=2)
p = uw.discretisation.MeshVariable("P", fine, 1, degree=1)
s = uw.systems.Stokes(fine, velocityField=v, pressureField=p)
s.constitutive_model = uw.constitutive_models.ViscousFlowModel
s.constitutive_model.Parameters.shear_viscosity_0 = 1.0
s.bodyforce = sympy.cos(3 * sympy.atan2(y, x)) * sympy.Matrix([x / r, y / r]).T
s.add_dirichlet_bc((0.0, 0.0), "Lower")
s.add_dirichlet_bc((0.0, 0.0), "Upper")
s.tolerance = 1e-6
set_custom_fmg(s, levels, field_id=0)
m0, t0 = peak_mb(), time.time()
s.solve()
m1, dt = peak_mb(), time.time() - t0
cells = [over_ranks(m.dm.getHeightStratum(0)[1])[1] for m in levels + [fine]]
b_max, b_sum = over_ranks(m0)
a_max, a_sum = over_ranks(m1)
its = s.snes.getKSP().getPC().getFieldSplitSubKSP()[0].getIterationNumber()
uw.pprint(f"RES np {uw.mpi.size} cell {cell} top {r_top} placed {int(placed)} cells {cells} "
          f"peak per rank before {b_max:.0f} MB after {a_max:.0f} MB "
          f"(sum {b_sum:.0f} -> {a_sum:.0f} MB) solve {dt:.1f}s vel its {its} "
          f"converged {s.snes.getConvergedReason()}")
