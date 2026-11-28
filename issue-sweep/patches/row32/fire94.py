"""UNFILED 94 on H7's warm re-solve fixture (annulus, viscosity 1 + T, T 0 -> 1).
usage: fire94.py <cell>   env OLD=1 patches the old NORM_1 diag scale back in
(to provoke both iteration classes), UW94_FLOOR=1 switches the pressure floor on."""
import os, sys, hashlib, json
import numpy as np, sympy
import underworld3 as uw
from underworld3.utilities import rotated_bc as rb
from petsc4py import PETSc
if os.environ.get("OLD") == "1":
    def _old_scale(Ahat, solver):
        d = Ahat.getDiagonal(); vis = solver._subdict["velocity"][0]
        sub = d.getSubVector(vis); n = sub.getSize()
        s_ = sub.norm(PETSc.NormType.NORM_1) / max(n, 1)
        d.restoreSubVector(vis, sub); d.destroy()
        return float(s_) if s_ > 0.0 else 1.0
    rb._velocity_diag_scale = _old_scale
cell = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=cell, qdegree=3)
T = uw.discretisation.MeshVariable("T94", mesh, 1, degree=1)
def build(tag):
    v = uw.discretisation.MeshVariable(f"V94{tag}", mesh, 2, degree=2); p = uw.discretisation.MeshVariable(f"P94{tag}", mesh, 1, degree=1)
    s = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1.0 + T.sym[0]
    X = mesh.X; r = sympy.sqrt(X[0]**2 + X[1]**2); th = sympy.atan2(X[1], X[0])
    s.bodyforce = sympy.cos(3 * th) * sympy.sin(sympy.pi * (r - 0.5) / 0.5) * sympy.Matrix([X[0] / r, X[1] / r])
    s.add_rotated_freeslip_bc(0, "Lower"); s.add_rotated_freeslip_bc(0, "Upper")
    s.petsc_use_pressure_nullspace = True; s.tolerance = 1.0e-8
    return v, s
v, s = build("a")
s.solve()
ctx = s._rotated_linear_cache["ctx"]
cold = s._rotated_freeslip_info
cold_p = max(i for i in cold["pres_its_last"] if i is not None)
T.array[...] = 1.0
s.solve(zero_init_guess=False)
info = s._rotated_freeslip_info
t2 = s._rotated_linear_cache["ctx"]["schur_roundoff"]
_fl = rb._SCHUR_PRESSURE_FLOOR
rb._SCHUR_PRESSURE_FLOOR = False
vf, f = build("b"); f.tolerance = 1.0e-10; f.solve()
rb._SCHUR_PRESSURE_FLOOR = _fl
data = np.concatenate(uw.mpi.comm.allgather(np.asarray(v.data).ravel()))
fresh = np.concatenate(uw.mpi.comm.allgather(np.asarray(vf.data).ravel()))
rel = float(np.linalg.norm(data - fresh) / np.linalg.norm(fresh))
if uw.mpi.rank == 0:
    print("REC " + json.dumps(dict(np=uw.mpi.size, cell=cell, old=os.environ.get("OLD") == "1", c=rb._SCHUR_PRESSURE_FLOOR_C, floor=rb._SCHUR_PRESSURE_FLOOR,
          cold_p=cold_p, mismatch=t2.scale_mismatch, warm_p=info["pres_its_last"], warm_v=info["vel_its_last"], outer=info["ksp_its"],
          capped=info.get("sub_capped"), fired=t2.fired, floored=t2.floored, vs_ref=rel,
          hash=hashlib.sha1(data.tobytes()).hexdigest()[:8])), flush=True)
