"""How far the given radial normal X/|X| is from the consistent one on the gmsh annulus,
and how strongly the exact slip of manufactured_annulus.py is tied to the extra
constraint it would add.

    python inconsistency_annulus.py -uw_cell_size 0.05

As in ../inconsistency.py: at each P2 velocity node i on a wall, W_i = sum over its
facets of (integral of the node's basis function over the facet) n_f; the default
normal is W_i/|W_i|. With the given normal n_g and its tangent t_g, a uniform
pressure puts the force r_i = W_i . t_g on node i's free row, and the continuity
row of the constant pressure becomes sum_i r_i u_t,i = 0 over both walls. Reported
per mesh: sum |r|, max |r|, and the correlation C of r with each exact slip, and
the largest difference between the two solved velocity fields (default normal
against X/|X|) for the "s2" slip.
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured_annulus as ma
import slide

params = uw.Params(uw_cell_size=0.05, uw_slide="none")
CELL = float(params.uw_cell_size)
SLIDE = str(params.uw_slide)
mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=CELL, qdegree=4)
slide.slide(mesh, SLIDE)
dm = mesh.dm
coords = dm.getCoordinatesLocal().array.reshape(-1, 2)
csec = dm.getCoordinateSection()
fS, fE = dm.getHeightStratum(1)
v0, v1 = dm.getDepthStratum(0)

Wv, Xv, Vx = [], [], []
for wall in ("Upper", "Lower"):
    label = dm.getLabel(wall)
    value = mesh.boundaries[wall].value
    facets = [int(q) for q in label.getStratumIS(value).getIndices() if fS <= q < fE]
    W, X = {}, {}
    for f in facets:
        a, b = dm.getCone(f)
        xa = coords[csec.getOffset(int(a)) // 2]
        xb = coords[csec.getOffset(int(b)) // 2]
        d = xb - xa
        L = np.hypot(*d)
        n = np.array([d[1], -d[0]]) / L
        mid = (xa + xb) / 2
        if n @ mid < 0:
            n = -n                      # radial outward; the sign does not change r's magnitude
        for key, x, w in ((int(a), xa, L / 6), (int(b), xb, L / 6), (f, mid, 2 * L / 3)):
            W[key] = W.get(key, 0.0) + w * n
            X[key] = x
    keys = sorted(W)
    Wv += [W[k] for k in keys]
    Xv += [X[k] for k in keys]
    Vx += [v0 <= k < v1 for k in keys]
Wv, Xv, Vx = np.array(Wv), np.array(Xv), np.array(Vx)
ng = Xv / np.linalg.norm(Xv, axis=1)[:, None]
tg = np.stack([-ng[:, 1], ng[:, 0]], axis=1)
r = (Wv * tg).sum(axis=1)
angle = np.degrees(np.arcsin(np.clip((Wv[:, 0] * ng[:, 1] - Wv[:, 1] * ng[:, 0])
                                     / np.linalg.norm(Wv, axis=1), -1, 1)))
uw.pprint(f"slide {SLIDE} cell {CELL}: {len(r)} wall nodes; angle default vs radial: vertices max "
          f"{np.abs(angle[Vx]).max():.3e} deg, midpoints max {np.abs(angle[~Vx]).max():.3e} deg; "
          f"sum |r| {np.abs(r).sum():.3e}, max |r| {np.abs(r).max():.3e}, sum r {r.sum():+.3e}")
for kind in ma.H:
    fu = sympy.lambdify((ma.x, ma.y), ma.fields(kind)["u"], "numpy")
    u = np.array([np.asarray(fu(*xy), dtype=float).ravel() for xy in Xv])
    s = (u * tg).sum(axis=1)
    C = (r * s).sum() / np.sqrt((r**2).sum() * (s**2).sum())
    uw.pprint(f"  slip {kind:7s}: correlation C {C:+.4f}, sum r s {(r * s).sum():+.3e}")

# the two solves themselves, "s2"
X, Y = mesh.X
F = ma.fields("s2")
f_e = F["f"].T.xreplace({ma.x: X, ma.y: Y})
radial = sympy.Matrix([[X, Y]]) / sympy.sqrt(X**2 + Y**2)
out = {}
for name, normal in (("default", None), ("radial", radial)):
    v = uw.discretisation.MeshVariable(f"U{name}", mesh, 2, degree=2)
    p = uw.discretisation.MeshVariable(f"P{name}", mesh, 1, degree=1)
    stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
    stokes.saddle_preconditioner = 1.0
    stokes.bodyforce = f_e
    stokes.tolerance = 1.0e-10
    stokes.petsc_use_pressure_nullspace = True
    stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
    stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
    for wall in ("Upper", "Lower"):
        stokes.add_rotated_freeslip_bc(0, wall, normal=normal)
    stokes.solve(zero_init_guess=True)
    out[name] = np.array(v.array).reshape(-1, 2).copy()
diff = np.abs(out["default"] - out["radial"]).max() / np.abs(out["default"]).max()
uw.pprint(f"  s2 solves: max |v_default - v_radial| / max |v| = {diff:.3e}")
