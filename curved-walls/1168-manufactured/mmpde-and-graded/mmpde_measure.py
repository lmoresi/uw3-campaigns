"""#1168 after a real MMPDE move: the manufactured annulus solution on a mesh moved by
uw.meshing.node_redistribution with slip on both walls, as the annulus MMPDE runs call it
(slip_surfaces=True, skip_threshold=None, accel "none"; the phase-3 driver's mover).

    python mmpde_measure.py -uw_cell_size 0.05 -uw_kind s2 -uw_metric trench

Metrics (cell density):
  band    1 + 24 exp(-((r - 0.9)/0.06)^2)                       (radial band, as the MMPDE
                                                                  annulus probes use)
  trench  1 + 24 exp(-((r - 0.95)/0.06)^2 - (dtheta/0.25)^2)     (a band near the outer
                                                                  wall localised in angle,
                                                                  dtheta from theta = pi/2,
                                                                  like a trench)
After the move: the largest distance of a wall vertex from its circle, each wall's chord
lengths (max/min), and, at the P2 wall nodes, sum |r_i| and the correlation C of r with the
exact slip (r_i = W_i . t_g, as in ../circles/inconsistency_annulus.py). Then the two
rotated solves, default normal and normal=X/|X|, against the exact solution.
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured_annulus as ma
from underworld3.meshing.smoothing.graph import _pinned_mask

params = uw.Params(uw_cell_size=0.05, uw_kind="s2", uw_pressure_nullspace=True, uw_only="", uw_metric="trench", uw_n_outer=20, uw_detorque=False, uw_lu_default=False)
CELL = float(params.uw_cell_size)
KIND = str(params.uw_kind)
NULLSPACE = bool(params.uw_pressure_nullspace)
ONLY = str(params.uw_only)
METRIC = str(params.uw_metric)
N_OUTER = int(params.uw_n_outer)
DETORQUE = bool(params.uw_detorque)
LU_DEFAULT = bool(params.uw_lu_default)

mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
_xs, _ys = mesh.X
_r = sympy.sqrt(_xs**2 + _ys**2)
if METRIC == "band":
    density = 1 + 24 * sympy.exp(-(((_r - 0.9) / 0.06) ** 2))
elif METRIC == "trench":
    _dth = sympy.atan2(_xs, _ys)          # angle from theta = pi/2, in (-pi, pi]
    density = 1 + 24 * sympy.exp(-(((_r - 0.95) / 0.06) ** 2) - (_dth / 0.25) ** 2)
else:
    raise ValueError(METRIC)
uw.meshing.node_redistribution(mesh, density, slip_surfaces=True, skip_threshold=None,
                               method_kwargs=dict(accel="none", n_outer=N_OUTER))

# the walls after the move
_dm = mesh.dm
_coords = _dm.getCoordinatesLocal().array.reshape(-1, 2)
_csec = _dm.getCoordinateSection()
_fS, _fE = _dm.getHeightStratum(1)
_Wv, _Xv = [], []
_report = []
for _wall, _R in (("Upper", 1.0), ("Lower", 0.5)):
    _on = _pinned_mask(_dm, (_wall,))
    _xy = np.asarray(mesh.X.coords)[_on]
    _off = np.abs(np.hypot(_xy[:, 0], _xy[:, 1]) - _R).max() / _R
    _label = _dm.getLabel(_wall)
    _value = mesh.boundaries[_wall].value
    _facets = [int(q) for q in _label.getStratumIS(_value).getIndices() if _fS <= q < _fE]
    _W, _X, _L = {}, {}, []
    for _f in _facets:
        _a, _b = _dm.getCone(_f)
        _xa = _coords[_csec.getOffset(int(_a)) // 2]
        _xb = _coords[_csec.getOffset(int(_b)) // 2]
        _d = _xb - _xa
        _len = np.hypot(*_d)
        _L.append(_len)
        _n = np.array([_d[1], -_d[0]]) / _len
        _mid = (_xa + _xb) / 2
        if _n @ _mid < 0:
            _n = -_n
        for _key, _x, _w in ((int(_a), _xa, _len / 6), (int(_b), _xb, _len / 6), (_f, _mid, 2 * _len / 3)):
            _W[_key] = _W.get(_key, 0.0) + _w * _n
            _X[_key] = _x
    _keys = sorted(_W)
    _Wv += [_W[k] for k in _keys]
    _Xv += [_X[k] for k in _keys]
    _L = np.array(_L)
    _report.append(f"{_wall}: vertex off circle {_off:.1e} of R, chords {len(_L)}, "
                   f"max/min {_L.max() / _L.min():.3f}")
_Wv, _Xv = np.array(_Wv), np.array(_Xv)
_ng = _Xv / np.linalg.norm(_Xv, axis=1)[:, None]
_tg = np.stack([-_ng[:, 1], _ng[:, 0]], axis=1)
_rr = (_Wv * _tg).sum(axis=1)
_fu = sympy.lambdify((ma.x, ma.y), ma.fields(KIND)["u"], "numpy")
_u = np.array([np.asarray(_fu(*p_), dtype=float).ravel() for p_ in _Xv])
_s = (_u * _tg).sum(axis=1)
_C = (_rr * _s).sum() / np.sqrt((_rr**2).sum() * (_s**2).sum())
X, Y = mesh.X
F = ma.fields(KIND)
on_mesh = {ma.x: X, ma.y: Y}
u_e = F["u"].T.xreplace(on_mesh)
p_e = F["p"].xreplace(on_mesh)
f_e = F["f"].T.xreplace(on_mesh)
radial = sympy.Matrix([[X, Y]]) / sympy.sqrt(X**2 + Y**2)
rot = sympy.Matrix([[-Y, X]])

v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
area = uw.maths.Integral(mesh, 1.0).evaluate()
I_rr = uw.maths.Integral(mesh, rot.dot(rot)).evaluate()
mean_p_e = uw.maths.Integral(mesh, p_e).evaluate() / area
omega_e = uw.maths.Integral(mesh, u_e.dot(rot)).evaluate() / I_rr
ue_mod = u_e - omega_e * rot
norm_u = np.sqrt(uw.maths.Integral(mesh, ue_mod.dot(ue_mod)).evaluate())
norm_raw = np.sqrt(uw.maths.Integral(mesh, u_e.dot(u_e)).evaluate())
torque = uw.maths.Integral(mesh, f_e.dot(rot)).evaluate() / I_rr
if DETORQUE:
    f_e = f_e - torque * rot


def solve(method):
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    stokes.petsc_use_pressure_nullspace = NULLSPACE
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    for wall in ("Upper", "Lower"):
        if method == "essential (control)":
            stokes.add_essential_bc(u_e, wall)
        elif method == "rotated, default normal":
            stokes.add_rotated_freeslip_bc(0, wall)
            # direct MUMPS LU per increment (one pressure pin instead of the null
            # space); with the default normal the summed continuity row is already
            # implied by the wall constraint, so dropping one row changes nothing
            stokes._rotated_use_lu = LU_DEFAULT
        elif method == "rotated, normal=X/|X|":
            stokes.add_rotated_freeslip_bc(0, wall, normal=radial)
    stokes.solve(zero_init_guess=True)
    info = getattr(stokes, "_rotated_freeslip_info", None) or {}
    reason = stokes.snes.getConvergedReason()
    if info:
        uw.pprint(f"  [{method}] rotated solve: converged {info.get('converged')}, "
                  f"lu {bool(getattr(stokes, '_rotated_use_lu', False))}, "
                  f"rnorm {info.get('rnorm', float('nan')):.3e} (rnorm0 "
                  f"{info.get('rnorm0', float('nan')):.3e}), last ksp_reason "
                  f"{info.get('ksp_reason')}, ksp_its {info.get('ksp_its')}, "
                  f"vel_its_last {info.get('vel_its_last')}")
    mean_p = uw.maths.Integral(mesh, p.sym[0]).evaluate() / area
    omega_h = uw.maths.Integral(mesh, v.sym.dot(rot)).evaluate() / I_rr
    du = (v.sym - omega_h * rot) - ue_mod
    e_u = np.sqrt(uw.maths.Integral(mesh, du.dot(du)).evaluate()) / norm_u
    draw = v.sym - u_e
    e_raw = np.sqrt(uw.maths.Integral(mesh, draw.dot(draw)).evaluate()) / norm_raw
    return reason, e_u, e_raw, omega_h, mean_p - mean_p_e


uw.pprint(f"after the move ({METRIC}, n_outer {N_OUTER}): " + "; ".join(_report)
          + f"; sum |r| {np.abs(_rr).sum():.3e}, correlation C with the {KIND} slip {_C:+.4f}")
uw.pprint(f"detorque {DETORQUE}  forcing torque T {torque:+.3e}  metric {METRIC}  kind {KIND}  cell {CELL}  cells {mesh.dm.getHeightStratum(0)[1]}  "
          f"pressure nullspace {NULLSPACE}  omega_e {omega_e:+.4e}")
uw.pprint(f"{'method':26s} reason {'u L2':>10s} {'u L2 raw':>10s} {'omega_h':>11s} {'<p>-<p_e>':>11s}")
for method in ("essential (control)", "rotated, default normal", "rotated, normal=X/|X|"):
    if ONLY and not any(w in method for w in ONLY.split(",")):
        continue
    reason, e_u, e_raw, om, dp = solve(method)
    uw.pprint(f"{method:26s} {reason:6d} {e_u:10.3e} {e_raw:10.3e} {om:+11.3e} {dp:+11.3e}")
