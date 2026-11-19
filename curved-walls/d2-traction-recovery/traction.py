"""D2: wall tractions on the Kramer annulus, against the exact ones.

One solve per (case, cell size, build). Every wall-traction route available in
that build is read from the same solve and compared at the same wall nodes with
the exact traction of Kramer, Davies & Wilson (2021) (`assess`, through
`uw.analytic.CylindricalStokes`), evaluated at the node's radial projection onto
the true circle.

Cases (smooth density rho = (r/R_O)^K cos(N theta), viscosity 1):
  free  - free slip on both walls; compare sigma_rr
  zero  - zero slip on both walls; compare sigma_rr and sigma_r_theta

Builds:
  development     - rotated free slip / essential zero slip on the polygonal walls
  #857 (detected) - its lagged circular wall transfer, then its recovery methods

Gauge: sigma_rr carries the pressure constant (and free-slip topography removes
its mean), so every normal-traction trace has its own best constant removed,
per wall, before the error is taken. Shear is compared as it is.

Each route's sign convention differs (a constraint reaction is minus sigma_rr);
the sign that fits the exact trace is used and printed with the result.

    python traction.py -uw_case free -uw_cell 0.125
    python traction.py -uw_case zero -uw_cell 0.0625
Output: one JSON line per route, prefixed "ROW ".
"""
import json
import time

import numpy as np
import sympy

import underworld3 as uw

params = uw.Params(
    case=uw.Param("free", "free | zero: slip condition on both walls"),
    cell=uw.Param(0.125, "cell size of the annulus mesh"),
    updates=uw.Param(4, "lagged wall updates of the #857 transfer"),
    degree=uw.Param(6, "#857 reconstruction kernel degree"),
    halfwidth=uw.Param(5.0, "#857 reconstruction support, in mean edge lengths"),
    quadrature=uw.Param(12, "#857 Gauss points per wall edge"),
)
CASE = str(params.case)
CELL = float(params.cell)
N, K = 2, 3
R_I, R_O = 0.5, 1.0
WALLS = (("Lower", R_I, -1), ("Upper", R_O, 1))

mesh = uw.meshing.Annulus(radiusInner=R_I, radiusOuter=R_O, cellSize=CELL)
x, y = mesh.X
r = sympy.sqrt(x**2 + y**2)
theta = sympy.atan2(y, x)
v = uw.discretisation.MeshVariable("U", mesh, mesh.dim, degree=2)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
rho = ((r / R_O) ** K) * sympy.cos(N * theta)
stokes.bodyforce = -rho * sympy.Matrix([[x / r, y / r]])
stokes.petsc_use_pressure_nullspace = True

exact = uw.analytic.CylindricalStokes(mesh, n=N, k=K, r_inner=R_I, r_outer=R_O,
                                      density="smooth", boundary=CASE)

IS_857 = hasattr(uw.systems.Stokes, "add_cylindrical_wall_transfer")
BUILD = "857" if IS_857 else "development"

# Scalar P2 targets for the #857 recovery; created before the solve, as its
# methods require.
targets = {}
if IS_857:
    names = (["cbf", "recon"] if CASE == "free"
             else ["cbf_n", "cbf_s", "recon_n", "recon_s"])
    for wall, _, _ in WALLS:
        for name in names:
            targets[wall, name] = uw.discretisation.MeshVariable(
                f"T_{wall}_{name}", mesh, 1, degree=2)

walls = {}
if IS_857:
    for wall, radius, sign in WALLS:
        if CASE == "free":
            walls[wall] = stokes.add_cylindrical_wall_transfer(
                boundary=wall, radius=radius, sign=sign, viscosity=1.0,
                interface_radius=0.75, outer_radius=R_O, wavenumber=N,
                amplitude=0.0, quadrature=int(params.quadrature))
        else:
            walls[wall] = stokes.add_cylindrical_zero_slip_transfer(
                boundary=wall, radius=radius, sign=sign,
                quadrature=int(params.quadrature))
else:
    for wall, _, _ in WALLS:
        if CASE == "free":
            stokes.add_rotated_freeslip_bc(0.0, wall)
        else:
            stokes.add_dirichlet_bc((0.0, 0.0), wall)

start = time.perf_counter()
if IS_857:
    if CASE == "free":
        stokes.solve_cylindrical_wall_updates(walls=walls, updates=int(params.updates))
    else:
        stokes.solve_cylindrical_zero_slip_updates(walls=walls, updates=int(params.updates))
else:
    stokes.solve()
solve_time = time.perf_counter() - start
reason = stokes.snes.getConvergedReason()


def wall_nodes(wall):
    """The P2 velocity-trace nodes on `wall`, by label (same set for every route)."""
    from underworld3.utilities.boundary_flux import _boundary_field_nodes
    nodes, *_ = _boundary_field_nodes(stokes, wall, 0)
    return np.array([node[2] for node in nodes]).reshape(-1, 2)


def exact_on_circle(coords, radius):
    """Exact sigma_rr and sigma_r_theta at the radial projection onto the circle."""
    on = radius * coords / np.linalg.norm(coords, axis=1)[:, None]
    phi = np.arctan2(on[:, 1], on[:, 0])
    sol = exact._above
    srr = np.array([sol.radial_stress(radius, a) for a in phi])
    srt = np.array([sol.tau_rphi(radius, a) for a in phi])
    return srr, srt


def lookup(coords, field_coords, values):
    """Values of a nodal array at `coords`, by nearest node (same node set)."""
    tree = uw.kdtree.KDTree(np.ascontiguousarray(field_coords))
    dist, index = tree.query(np.ascontiguousarray(coords), 1)
    dist = np.asarray(dist).ravel()
    assert dist.max() < 1e-9 * R_O, dist.max()
    return np.asarray(values)[np.asarray(index).ravel()]


def errors(coords, values, reference, radius, gauge):
    """Relative errors with the better sign and (for sigma_rr) the best constant."""
    best = None
    for s in (1.0, -1.0):
        e = s * values - reference
        if gauge:
            e = e - e.mean()
        scale = np.abs(reference - (reference.mean() if gauge else 0.0)).max()
        l2 = np.sqrt(np.mean(e**2)) / scale
        if best is None or l2 < best[0]:
            on_circle = np.abs(np.linalg.norm(coords, axis=1) - radius) < 1e-9 * radius
            mid = ~on_circle
            best = (l2, np.abs(e).max() / scale,
                    np.sqrt(np.mean(e[mid] ** 2)) / scale if mid.any() else np.nan,
                    np.sqrt(np.mean(e[on_circle] ** 2)) / scale if on_circle.any() else np.nan,
                    s)
    return dict(l2=best[0], max=best[1], l2_mid=best[2], l2_vertex=best[3], sign=best[4])


def emit(route, wall, quantity, err, cost=None):
    row = dict(build=BUILD, case=CASE, cell=CELL, route=route, wall=wall,
               quantity=quantity, solve_s=solve_time, cost_s=cost,
               reason=int(reason), **err)
    print("ROW " + json.dumps(row), flush=True)


# Raw stress from the FE fields, evaluated at the wall nodes.
radial = sympy.Matrix([[x / r, y / r]])
tangent = sympy.Matrix([[-y / r, x / r]])
sigma = stokes.stress
srr_expr = (radial * sigma * radial.T)[0, 0]
srt_expr = (radial * sigma * tangent.T)[0, 0]

for wall, radius, sign in WALLS:
    coords = wall_nodes(wall)
    ref_rr, ref_rt = exact_on_circle(coords, radius)
    gauge = True

    t0 = time.perf_counter()
    raw_rr = np.asarray(uw.function.evaluate(srr_expr, coords)).ravel()
    raw_rt = np.asarray(uw.function.evaluate(srt_expr, coords)).ravel()
    cost_raw = time.perf_counter() - t0
    emit("raw FE stress at nodes", wall, "sigma_rr",
         errors(coords, raw_rr, ref_rr, radius, gauge), cost_raw)
    if CASE == "zero":
        emit("raw FE stress at nodes", wall, "sigma_rt",
             errors(coords, raw_rt, ref_rt, radius, False), cost_raw)

    if CASE == "free":
        # The constraint reaction of the rotated solve (development), or of the
        # rotated solve inside #857's lagged transfer.
        for mass in ("lumped", "consistent"):
            t0 = time.perf_counter()
            xs, vals = stokes.boundary_normal_traction(wall, mass=mass)
            cost = time.perf_counter() - t0
            vals = lookup(coords, np.asarray(xs).reshape(-1, 2), np.asarray(vals).ravel())
            emit(f"rotated reaction ({mass})", wall, "sigma_rr",
                 errors(coords, vals, ref_rr, radius, gauge), cost)
        if IS_857:
            cbf, recon = targets[wall, "cbf"], targets[wall, "recon"]
            t0 = time.perf_counter()
            stokes.recover_cylindrical_topography(wall=walls[wall], field=cbf,
                                                  buoyancy_scale=-1.0)
            cost_cbf = time.perf_counter() - t0
            t0 = time.perf_counter()
            stokes.reconstruct_cylindrical_trace(
                wall=walls[wall], source=cbf, target=recon,
                degree=int(params.degree), halfwidth_edges=float(params.halfwidth))
            cost_recon = time.perf_counter() - t0
            for name, field, cost in (("857 circular CBF", cbf, cost_cbf),
                                      ("857 CBF + reconstruction", recon, cost_cbf + cost_recon)):
                vals = lookup(coords, field.coords, np.asarray(field.array)[:, 0, 0])
                emit(name, wall, "sigma_rr", errors(coords, vals, ref_rr, radius, gauge), cost)
    else:
        # Essential-condition reaction (consistent boundary flux), as a vector,
        # resolved on the true radial frame.
        for mass in ("lumped", "consistent"):
            t0 = time.perf_counter()
            xs, flux = stokes.boundary_flux(wall, mass=mass)
            cost = time.perf_counter() - t0
            xs = np.asarray(xs).reshape(-1, 2)
            flux = np.asarray(flux).reshape(-1, 2)
            fx = lookup(coords, xs, flux[:, 0])
            fy = lookup(coords, xs, flux[:, 1])
            rhat = coords / np.linalg.norm(coords, axis=1)[:, None]
            that = np.c_[-rhat[:, 1], rhat[:, 0]]
            tr = fx * rhat[:, 0] + fy * rhat[:, 1]
            tt = fx * that[:, 0] + fy * that[:, 1]
            emit(f"boundary_flux CBF ({mass})", wall, "sigma_rr",
                 errors(coords, tr, ref_rr, radius, gauge), cost)
            emit(f"boundary_flux CBF ({mass})", wall, "sigma_rt",
                 errors(coords, tt, ref_rt, radius, False), cost)
        if IS_857:
            f = {n: targets[wall, n] for n in ("cbf_n", "cbf_s", "recon_n", "recon_s")}
            t0 = time.perf_counter()
            stokes.recover_cylindrical_zero_slip_traction(
                wall=walls[wall], normal_field=f["cbf_n"], shear_field=f["cbf_s"],
                recovered_normal_field=f["recon_n"], recovered_shear_field=f["recon_s"],
                viscosity=1.0, pressure_jump=sympy.Integer(0),
                degree=int(params.degree), halfwidth_edges=float(params.halfwidth),
                quadrature=2 * int(params.quadrature))
            cost = time.perf_counter() - t0
            for name, nkey, skey in (("857 circular CBF", "cbf_n", "cbf_s"),
                                     ("857 CBF + reconstruction", "recon_n", "recon_s")):
                vn = lookup(coords, f[nkey].coords, np.asarray(f[nkey].array)[:, 0, 0])
                vs = lookup(coords, f[skey].coords, np.asarray(f[skey].array)[:, 0, 0])
                emit(name, wall, "sigma_rr", errors(coords, vn, ref_rr, radius, gauge), cost)
                emit(name, wall, "sigma_rt", errors(coords, vs, ref_rt, radius, False), cost)

print(f"DONE build={BUILD} case={CASE} cell={CELL} reason={reason} "
      f"solve_s={solve_time:.2f} velocity_error={exact.error('velocity', v):.3e}", flush=True)
