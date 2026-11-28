"""H7 UNFILED 73: the Schur round-off test fires on a warm re-solve after a uniform viscosity
change (viscosity 1 + T, T 0 -> 1): the pressure equations already hold, the velocity
correction is divergence-free. Case 'drop': the context's reference to the test is dropped
(and collected) at the warm solve's first velocity sub-KSP monitor call, mid-solve."""
import sys, gc, numpy as np, sympy
import underworld3 as uw
case = sys.argv[1] if len(sys.argv) > 1 else "fire"
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.2, qdegree=3)
import hashlib
_c = np.round(np.asarray(mesh.dm.getCoordinatesLocal().array), 12)
_c = _c.reshape(-1, 2); _c = _c[np.lexsort(_c.T)]
_fp = hashlib.sha1(_c.tobytes()).hexdigest()[:8]
_cs, _ce = mesh.dm.getHeightStratum(0)
PART = uw.mpi.comm.allgather((_ce - _cs, _fp))
T = uw.discretisation.MeshVariable("T73", mesh, 1, degree=1)
def build(tag):
    v = uw.discretisation.MeshVariable(f"V73{tag}", mesh, 2, degree=2); p = uw.discretisation.MeshVariable(f"P73{tag}", mesh, 1, degree=1)
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
cold_fired = ctx["schur_roundoff"].fired
from petsc4py import PETSc
def _mhash(M):
    ia, ja, a = M.getValuesCSR()
    rs, re = M.getOwnershipRange()
    h = hashlib.sha1(np.asarray(ja).tobytes() + np.asarray(a).tobytes() + np.asarray(ia).tobytes()).hexdigest()[:6]
    return f"{M.getSize()[0]}:{h}"
_vpc = ctx["ksp"].getPC().getFieldSplitSubKSP()[0].getPC()
_lv = []
try:
    for l in range(_vpc.getMGLevels()):
        _lv.append(_mhash(_vpc.getMGSmoother(l).getOperators()[0]))
except Exception as e:
    _lv.append(f"err {type(e).__name__}")
LEVELS = uw.mpi.comm.allgather((_vpc.getType(), _lv))
_A = ctx["ksp"].getOperators()[0]
AH = uw.mpi.comm.allgather(_mhash(_A))
_info0 = s._rotated_freeslip_info
JH = uw.mpi.comm.allgather(_mhash(s.snes.getJacobian()[0]))
QH = uw.mpi.comm.allgather(_mhash(_info0["Q"]))
_rows = np.asarray(sorted(_info0["normal_rows"]))
_J = s.snes.getJacobian()[0]; _Qt = _info0["Qt"]
_P = []
for _k in range(6):
    _B = _J.ptap(_Qt); _P.append(_mhash(_B)); _B.destroy()
PH = uw.mpi.comm.allgather(_P)
def _shash(M):
    ia, ja, a = M.getValuesCSR()
    rows = np.repeat(np.arange(len(ia) - 1), np.diff(ia))
    o = np.lexsort((ja, rows))
    return hashlib.sha1(np.asarray(ja)[o].tobytes() + np.asarray(a)[o].tobytes()).hexdigest()[:6]
from underworld3.utilities import rotated_bc as _rb
_F = _J.ptap(_Qt)
_F.zeroRowsColumns(_info0["normal_rows"], diag=_rb._velocity_diag_scale(_F, s))
_D = _A.copy(); _D.axpy(-1.0, _F)
_dn = _D.norm(PETSc.NormType.FROBENIUS) / _F.norm(PETSc.NormType.FROBENIUS)
SH = uw.mpi.comm.allgather((_shash(_A), _shash(_F)))

_ty = (_J.getType(), _Qt.getType())
RH = uw.mpi.comm.allgather(hashlib.sha1(_rows.tobytes()).hexdigest()[:6])
T.array[...] = 1.0
_ph = []
try:
    _psub = ctx["ksp"].getPC().getFieldSplitSubKSP()[1]
    _psub.setMonitor(lambda k, it, rn: _ph.append(float(rn)))
    _ptol = _psub.getTolerances()
except Exception as e:
    _ptol = str(e)
if case == "drop":
    vel_sub, _ = ctx["ksp"].getPC().getFieldSplitSubKSP()
    state = {"done": 0}
    def drop(ksp, its, rnorm):
        if not state["done"]:
            state["done"] = 1
            ctx["schur_roundoff"] = None
            gc.collect()
    vel_sub.setMonitor(drop)
s.solve(zero_init_guess=False)
info = s._rotated_freeslip_info
t2 = s._rotated_linear_cache["ctx"]["schur_roundoff"]
warm_fired = t2.fired if t2 is not None else "dropped"
vf, f = build("b"); f.solve()
rel = np.linalg.norm(np.asarray(v.array) - np.asarray(vf.array)) / np.linalg.norm(np.asarray(vf.array))
print(f"PT {_ptol} PH {[_ph[0], min(_ph), _ph[-1], len(_ph)] if _ph else None} AH {AH} RESULT {case} np{uw.mpi.size}: cold fired {cold_fired}; warm fired {warm_fired}, pres its {info['pres_its_last']}, vel its {info['vel_its_last']}, converged {info['converged']}; warm vs fresh {rel:.1e}", flush=True)
