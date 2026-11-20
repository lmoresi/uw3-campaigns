"""The tangential force a uniform pressure exerts on the ellipse's rotated nodes
when the normal is given, and how strongly each flow's slip is tied to it.

    python inconsistency.py -uw_cell_size 0.1

At each P2 velocity node i on the ellipse, W_i = sum over its facets f of
(integral of phi_i over f) n_f: |f|/6 n_f at a vertex, 2|f|/3 n_f at a midpoint.
The default normal is W_i / |W_i|, so a uniform pressure does no work on the free
(tangential) direction. With a given normal n_g, the free direction t_g is not
perpendicular to W_i, and a uniform pressure c puts the force c r_i,
r_i = W_i . t_g, on node i's free row. The continuity row of the constant
pressure test function is then sum_i r_i u_t,i = 0 (plus the inner wall), a
constraint on the slip, with the mean pressure as its multiplier.

Reported: |r| summary and where it is largest, and for each flow the
correlation C = sum r_i s_i / sqrt(sum r_i^2 sum s_i^2) of r with that flow's
slip s_i = u(x_i).t_g,i, using
  (a) #1168's flow (radial body force cos 4 theta, rotated free slip on both
      walls, default normal), and
  (b) the exact slip of manufactured.py's two-wall solution ("both"), and
  (c) of its odd-odd variant ("both-xy").
"""
import numpy as np
import sympy
import underworld3 as uw

import manufactured
import measure_mesh

params = uw.Params(uw_cell_size=0.1)
CELL = float(params.uw_cell_size)
mesh = measure_mesh.ellipse_mesh(CELL)
A = measure_mesh.A
dm = mesh.dm
cdim = 2
coords = dm.getCoordinatesLocal().array.reshape(-1, cdim)
csec = dm.getCoordinateSection()
fS, fE = dm.getHeightStratum(1)
facets = [int(q) for q in dm.getLabel("Outer").getStratumIS(measure_mesh.boundaries.Outer.value).getIndices()
          if fS <= q < fE]  # the label also marks the wall's vertices

W, X = {}, {}
for f in facets:
    a, b = dm.getCone(int(f))
    xa = coords[csec.getOffset(int(a)) // cdim]
    xb = coords[csec.getOffset(int(b)) // cdim]
    d = xb - xa
    L = np.hypot(*d)
    n = np.array([d[1], -d[0]]) / L
    mid = (xa + xb) / 2
    if n @ mid < 0:
        n = -n
    for key, x, w in ((int(a), xa, L / 6), (int(b), xb, L / 6), (int(f), mid, 2 * L / 3)):
        W[key] = W.get(key, 0.0) + w * n
        X[key] = x
keys = sorted(W)
Wv = np.array([W[k] for k in keys])
Xv = np.array([X[k] for k in keys])
ng = np.stack([2 * Xv[:, 0] / A**2, 2 * Xv[:, 1]], axis=1)
ng /= np.linalg.norm(ng, axis=1)[:, None]
tg = np.stack([-ng[:, 1], ng[:, 0]], axis=1)
r = (Wv * tg).sum(axis=1)
theta = np.degrees(np.arctan2(Xv[:, 1], Xv[:, 0]))
v0, v1 = dm.getDepthStratum(0)
is_vertex = np.array([v0 <= k < v1 for k in keys])
angle = np.degrees(np.arcsin(np.clip((Wv[:, 0] * ng[:, 1] - Wv[:, 1] * ng[:, 0])
                                     / np.linalg.norm(Wv, axis=1), -1, 1)))
uw.pprint(f"cell {CELL}: {len(keys)} wall nodes ({is_vertex.sum()} vertices); "
          f"sum |W| = {np.linalg.norm(Wv, axis=1).sum():.4f} (perimeter of the ellipse 7.9327)")
uw.pprint(f"  angle between default and given normal: vertices max {np.abs(angle[is_vertex]).max():.3e} deg, "
          f"midpoints max {np.abs(angle[~is_vertex]).max():.3e} deg")
uw.pprint(f"  r: sum {r.sum():+.3e}, sum |r| {np.abs(r).sum():.3e}, max |r| {np.abs(r).max():.3e}")
order = np.argsort(-np.abs(r))[:8]
uw.pprint("  largest |r| at theta (deg): " + ", ".join(f"{theta[i]:.1f} ({r[i]:+.2e}, "
          f"{'vertex' if is_vertex[i] else 'midpoint'})" for i in order))


def correlation(slip):
    return (r * slip).sum() / np.sqrt((r**2).sum() * (slip**2).sum()), (r * slip).sum()


# (a) #1168's flow, default normal
x, y = mesh.X
v = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.saddle_preconditioner = 1.0
stokes.bodyforce = sympy.cos(4 * sympy.atan2(y, x)) * sympy.Matrix([[x, y]]) / sympy.sqrt(x**2 + y**2)
stokes.tolerance = 1.0e-10
stokes.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
stokes.petsc_options["fieldsplit_velocity_pc_type"] = "lu"
stokes.petsc_options["fieldsplit_velocity_pc_factor_mat_solver_type"] = "mumps"
stokes.add_rotated_freeslip_bc(0, "Outer")
stokes.add_rotated_freeslip_bc(0, "Inner")
stokes.solve(zero_init_guess=True)
u_nodes = uw.function.evaluate(v.sym, Xv).reshape(-1, 2)
slip_a = (u_nodes * tg).sum(axis=1)
C, S = correlation(slip_a)
uw.pprint(f"(a) #1168's flow: slip rms {np.sqrt((slip_a**2).mean()):.3e}; sum r s = {S:+.3e}; correlation {C:+.4f}")
uw.pprint(f"    slip at the largest-|r| nodes: " + ", ".join(f"{slip_a[i]:+.2e}" for i in order))

# (b), (c) the manufactured two-wall solutions
for label, variant in (("(b)", "both"), ("(c)", "both-xy")):
    F = manufactured.fields(variant)
    fu = sympy.lambdify((manufactured.x, manufactured.y), F["u"], "numpy")
    u_b = np.array([np.asarray(fu(*xy), dtype=float).ravel() for xy in Xv])
    slip_b = (u_b * tg).sum(axis=1)
    C, S = correlation(slip_b)
    uw.pprint(f"{label} manufactured {variant}: slip rms {np.sqrt((slip_b**2).mean()):.3e}; "
              f"sum r s = {S:+.3e}; correlation {C:+.4f}")
    uw.pprint(f"    slip at the largest-|r| nodes: " + ", ".join(f"{slip_b[i]:+.2e}" for i in order))
