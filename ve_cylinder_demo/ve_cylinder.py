"""Viscoelastic vortex shedding past the DFG cylinder: a demonstrator of the transports.

  python ve_cylinder.py -uw_velocity_transport eulerian -uw_stress_transport eulerian -uw_label grid
  python ve_cylinder.py -uw_velocity_transport forward_nodes -uw_stress_transport forward_integration_points -uw_label forward

Channel 2.2 x 0.41, cylinder radius 0.05 at (0.2, 0.2), parabolic inflow (mean 1) ramped
over t_ramp. Oldroyd-B: polymer viscosity (1 - beta) eta, solvent beta eta, relaxation time
lambda = Wi D / U_mean, upper-convected, carried as a log-conformation history. Wi 0 is the
Newtonian reference. Checkpoints every `checkpoint_every` steps: velocity, projected vorticity,
the second invariant of the carried polymer stress, and passive tracers released at the inlet.

Restart: `-uw_snapshot_every N` writes a whole-model snapshot (every variable, the stress
history, the solver state) every N steps into runs/<label>/snapshots, keeping the last
`keep_snapshots`; `-uw_restart <snapshot.h5> -uw_restart_step <N>` loads one and continues
from step N (use a new label so the first run's record is kept).
"""
import os, time, faulthandler, signal
# `kill -USR1 <rank pid>` prints that rank's Python stack to the log: where a
# silent hang is stuck (ptrace is restricted, so py-spy cannot attach)
faulthandler.register(signal.SIGUSR1, all_threads=True)
import numpy as np, sympy
from enum import Enum
from mpi4py import MPI
import underworld3 as uw

params = uw.Params(uw_label="grid", uw_velocity_transport="eulerian", uw_stress_transport="eulerian",
                   uw_Re=200.0, uw_Wi=0.5, uw_beta=0.5, uw_store="log_conformation", uw_devss=0.0,
                   uw_resolution=20, uw_circle_ratio=0.25, uw_courant=1.0, uw_t_end=8.0, uw_ramp=0.5,
                   uw_checkpoint_every=4, uw_store_smoothing=0.0, uw_direct=0, uw_refinement=2, uw_log_every=25, uw_tracers=40, uw_tracer_halfwidth=0.012, uw_tracer_offset=0.024,
                   uw_snapshot_every=0, uw_keep_snapshots=4, uw_restart="", uw_restart_step=0, uw_fit_limiter=0, uw_ksp_max_it=0, uw_reconstruction="cell", uw_debug_recon=0, uw_cylinder_bc="noslip", uw_velocity_reconstruction="cell", uw_dump_history=0, uw_bubble_penalty=0.0, uw_relaxation="linear", uw_L2=100.0, uw_debug_fene=0, uw_relax=0, uw_integrator="etd", uw_vdegree=2, uw_custom_fmg=-1, uw_monitor=0, uw_inner_max_it=0, uw_kick=0.0, uw_kick_x=0.35, uw_kick_y=0.2, uw_kick_w=0.025, uw_reaction=0, uw_dt=0.0, uw_lagged_stretch=0, uw_theta=0.5, uw_mf_operator=0, uw_test_jacobian=0, uw_ksp_rtol=0.0, uw_snapback=0, uw_snes_max_it=0, uw_snapback_check=0, uw_stretch="implicit", uw_dump_jacobian="", uw_dump_newton="", uw_pc_flux="jacobian", uw_vsmoother="", uw_gamg_nsmooths=-1, uw_strategy="", uw_switch=0, uw_switch_margin=0.15, uw_switch_retry=10, uw_switch_wall=150.0, uw_wall_report="")
comm = uw.mpi.comm
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", str(params.uw_label))
ckdir = os.path.join(outdir, "checkpoints")
if uw.mpi.rank == 0:
    os.makedirs(ckdir, exist_ok=True)
comm.barrier()


class boundaries(Enum):
    bottom = 1; right = 2; top = 3; left = 4; inclusion = 5; All_Boundaries = 1001


# with refinement r the gmsh base is built 2^r coarser and refined back, the new
# vertices snapped to the circle: the hierarchy gives the velocity block FMG
refinement = int(params.uw_refinement)
res = int(params.uw_resolution) // 2 ** refinement
csize = 1.0 / res
csize_circle = float(params.uw_circle_ratio) * csize
width, height, radius, centre = 2.2, 0.41, 0.05, (0.2, 0.2)
D, U_mean, U0 = 2 * radius, 1.0, 1.5
mesh_file = os.path.join(os.path.dirname(outdir), f"dfg_{res}_c{float(params.uw_circle_ratio):g}.msh")
if uw.mpi.rank == 0 and not os.path.exists(mesh_file):
    import pygmsh
    with pygmsh.geo.Geometry() as geom:
        geom.characteristic_length_max = csize
        hole = geom.add_circle((centre[0], centre[1], 0.0), radius, make_surface=False, mesh_size=csize_circle)
        box = geom.add_rectangle(xmin=0.0, ymin=0.0, xmax=width, ymax=height, z=0, holes=[hole], mesh_size=csize)
        for curve, b in zip(box.surface.curve_loop.curves, ("bottom", "right", "top", "left")):
            geom.add_physical(curve, label=b)
        geom.add_physical(hole.curve_loop.curves, label="inclusion")
        geom.add_physical(box.surface, label="Elements")
        geom.generate_mesh(dim=2, verbose=False)
        geom.save_geometry(mesh_file)
comm.barrier()
def snap_to_circle(dm):
    c = dm.getCoordinatesLocal()
    xy = c.array.reshape(-1, 2) - centre
    r = np.sqrt((xy ** 2).sum(axis=1)).reshape(-1, 1)
    on = uw.cython.petsc_discretisation.petsc_dm_find_labeled_points_local(dm, "inclusion")
    xy[on] *= radius / r[on]
    c.array[...] = (xy + centre).reshape(-1)
    dm.setCoordinatesLocal(c)


mesh = uw.discretisation.Mesh(mesh_file, markVertices=True, useMultipleTags=True, useRegions=True,
                              boundaries=boundaries, qdegree=2 * int(params.uw_vdegree) - 1, refinement=refinement,
                              refinement_callback=snap_to_circle if refinement else None)
if int(params.uw_relax):
    # reshape the cells the refinement left around the cylinder (mesh.relax: MMPDE in
    # the ideal frame, sizes and topology kept, named boundaries pinned so the snapped
    # circle stays exact); res 20 near-cylinder min angle 22 -> 29 deg, 99th-percentile
    # max angle 105 -> 91 deg
    mesh.relax()
csize_circle = csize_circle / 2 ** refinement          # the cylinder cell after refinement
x, y = mesh.X
# Taylor-Hood P(k)/P(k-1), -uw_vdegree k (2 by default). The stress history is
# continuous of degree k-1, so P3 velocity lifts it from P1 to P2; the
# quadrature degree 2k-1 is 3 for P2 (as before) and 5 for P3
vdeg = int(params.uw_vdegree)
v = uw.discretisation.MeshVariable("U", mesh, 2, degree=vdeg)
p = uw.discretisation.MeshVariable("P", mesh, 1, degree=vdeg - 1)

eta = U_mean * D / float(params.uw_Re)             # rho = 1
Wi, beta = float(params.uw_Wi), float(params.uw_beta)
vt, st = str(params.uw_velocity_transport), str(params.uw_stress_transport)
import inspect


def _accepted(callable_, wanted, defaults):
    """The keyword arguments ``callable_`` takes, from ``wanted``; one it does not
    take is dropped when it holds its default and refused otherwise (the same
    driver runs on builds with and without the forward-from-nodes options)."""
    names = inspect.signature(callable_).parameters
    out = {}
    for k, val in wanted.items():
        if k in names:
            out[k] = val
        elif val != defaults.get(k):
            raise ValueError(f"this build has no {k!r} option (asked for {val!r})")
    return out


ns = uw.systems.NavierStokes(mesh, v, p, rho=1.0, order=1,
                             **_accepted(uw.systems.NavierStokes.__init__, {"velocity_transport": vt},
                                         {"velocity_transport": "eulerian"}))
if float(params.uw_theta) != 0.5:
    # 1.0 = backward Euler: damps the high-Courant modes Crank-Nicolson leaves undamped
    ns.theta = float(params.uw_theta)
    uw.pprint(f"momentum theta = {ns.theta}")
# the native velocity FMG needs PETSc's DMCreateInjection between the refined
# levels, which it cannot build for P3 ("Could not locate matching functional for
# injection"); underworld3's own transfers over the same coarse levels need none.
# -uw_custom_fmg 1/0 forces it; the default (-1) uses it above P2
if refinement and (int(params.uw_custom_fmg) == 1 or (int(params.uw_custom_fmg) < 0 and vdeg > 2)):
    ns.set_custom_fmg(mesh._coarse_level_meshes()[:-1], field_id=0)
if Wi > 0:
    lam = Wi * D / U_mean
    eta_p, eta_s = (1 - beta) * eta, beta * eta
    ns.stress_transport = st
    VEP = uw.constitutive_models.ViscoElasticPlasticFlowModel
    ns.constitutive_model = VEP(
        ns.Unknowns, order=1, integrator=str(params.uw_integrator), objective_rate="upper_convected",
        stress_history=str(params.uw_store),
        **_accepted(VEP.__init__,
                    {"element": "jeffreys" if beta > 0 else "maxwell",
                     "relaxation": str(params.uw_relaxation),
                     "stretch_in_momentum": str(params.uw_stretch)},
                    {"element": "jeffreys" if beta > 0 else "maxwell", "relaxation": "linear",
                     "stretch_in_momentum": "implicit"}))
    cm = ns.constitutive_model
    if str(params.uw_relaxation) == "fene_p":
        cm.Parameters.extensibility = float(params.uw_L2)
    cm.Parameters.shear_viscosity_0 = eta_p
    cm.Parameters.shear_modulus = eta_p / lam
    cm.Parameters.solvent_viscosity = eta_s
    if int(params.uw_fit_limiter):
        ns.DFDt.fit_limiter = True
    if float(params.uw_store_smoothing) > 0:
        # alpha = c h^2 in the projection that stores the new stress (the
        # semi-Lagrangian histories; the wake cells run near Courant 0.25)
        ns.DFDt.store_smoothing = float(params.uw_store_smoothing)
    if float(params.uw_devss) > 0:
        ns.devss_viscosity = float(params.uw_devss) * eta
    if int(params.uw_lagged_stretch):
        # EXPERIMENTAL: one factor of the quadratic stretching terms from the
        # extrapolated advecting velocity, so each step is linear in the velocity
        # 2 = the unknown itself through the same hook (must reproduce the default)
        cm.lagged_stretch_velocity = v.sym if int(params.uw_lagged_stretch) == 2 else ns._a_var.sym
        uw.pprint(f"stretching terms linearised about the {'unknown (identity check)' if int(params.uw_lagged_stretch) == 2 else 'extrapolated'} velocity")
else:
    ns.constitutive_model = uw.constitutive_models.ViscousFlowModel
    ns.constitutive_model.Parameters.shear_viscosity_0 = eta
    cm = ns.constitutive_model

# inflow: the parabola, ramped; the entering fluid carries the fully developed
# Oldroyd-B channel stress of that profile
ramp = uw.function.expression(r"r_{\mathrm{in}}", 1.0e-6, "inflow ramp")
Vb = 4.0 * U0 * y * (height - y) / height ** 2
ns.add_dirichlet_bc((ramp * Vb, 0.0), "left")
for b in ("top", "bottom"):
    ns.add_dirichlet_bc((0.0, 0.0), b)
if str(params.uw_cylinder_bc) == "freeslip":
    # strong rotated free-slip on the cylinder: u.n = 0 per node, tangential flow free
    ns.add_rotated_freeslip_bc(0, "inclusion")
else:
    ns.add_dirichlet_bc((0.0, 0.0), "inclusion")
ns.bodyforce = sympy.Matrix([[0.0, 0.0]])
if Wi > 0:
    gd = ramp * sympy.diff(Vb, y)
    # the fully developed Oldroyd-B channel stress of the inflow profile; for
    # FENE-P the exact profile needs the cubic in f at each y, and at the
    # inlet's shear rates (Wi_wall = 6 lambda U0/H) the correction is f - 1 ~
    # 2 Wi_wall^2 / L^2, below 1% at L^2 = 100
    ns.DFDt.inflow_value = sympy.Matrix([[2 * lam * eta_p * gd ** 2, eta_p * gd], [eta_p * gd, 0.0]])
ns.tolerance = 1.0e-6
if int(params.uw_inner_max_it):
    # the Schur (pressure) solve applies an inner velocity solve per iteration, each
    # capped at 200 by default and neither raising on failure: a stalled block costs
    # up to 200 x 200 velocity cycles per outer iteration, silently (a "hang"). Cap
    # both lower and make a stalled block an error, so the step fails visibly
    n_in = int(params.uw_inner_max_it)
    for b in ("velocity", "pressure"):
        ns.petsc_options[f"fieldsplit_{b}_ksp_max_it"] = n_in
        ns.petsc_options[f"fieldsplit_{b}_ksp_error_if_not_converged"] = None
if float(params.uw_ksp_rtol) > 0:
    # a fixed outer linear tolerance in place of Eisenstat-Walker's adaptive one
    # (EW loosens the linear solve when Newton is slow, which can feed a stall)
    ns.petsc_options["snes_ksp_ew"] = "false"
    ns.petsc_options["ksp_rtol"] = float(params.uw_ksp_rtol)
    uw.pprint(f"Eisenstat-Walker off, ksp_rtol {float(params.uw_ksp_rtol):g}")
if int(params.uw_snes_max_it) > 0:
    # a Newton cap: with snap-back, a step that cannot converge is detected in
    # this many iterations rather than by the guard's hang timer
    ns.petsc_options["snes_max_it"] = int(params.uw_snes_max_it)
if int(params.uw_test_jacobian):
    # diagnosis: compare the assembled Jacobian with a finite-difference one (small runs only)
    ns.petsc_options["snes_test_jacobian"] = None
if str(params.uw_strategy):
    # the solver's named strategy: "bulletproof" is gmres x8 + ASM on the velocity levels
    ns.strategy = str(params.uw_strategy)
    uw.pprint(f"solver strategy {ns.strategy}")
if str(params.uw_vsmoother):
    # the velocity multigrid's level smoother: the default Chebyshev/Jacobi
    # assumes an SPD block; "gmres_sor" / "gmres_asm" do not
    ksp_t, pc_t = str(params.uw_vsmoother).split("_")
    ns.petsc_options["fieldsplit_velocity_mg_levels_ksp_type"] = ksp_t
    ns.petsc_options["fieldsplit_velocity_mg_levels_pc_type"] = pc_t
    if pc_t == "asm":
        ns.petsc_options["fieldsplit_velocity_mg_levels_sub_pc_type"] = "ilu"
    uw.pprint(f"velocity smoother {ksp_t} + {pc_t}")
if int(params.uw_gamg_nsmooths) >= 0:
    ns.petsc_options["fieldsplit_velocity_pc_gamg_agg_nsmooths"] = int(params.uw_gamg_nsmooths)
    uw.pprint(f"GAMG prolongator smoothing steps {int(params.uw_gamg_nsmooths)}")
if str(params.uw_pc_flux) != "jacobian":
    # the velocity block of the preconditioning matrix from the model's
    # stretch-free flux; the Jacobian (the Newton step) is unchanged
    if hasattr(type(ns), "preconditioner_flux"):
        ns.preconditioner_flux = str(params.uw_pc_flux)
        uw.pprint(f"preconditioner_flux = {ns.preconditioner_flux}")
    else:
        uw.pprint("this build has no preconditioner_flux; option ignored")
if int(params.uw_mf_operator):
    # diagnosis: Newton on the matrix-free (finite-difference) Jacobian action, the
    # assembled Jacobian kept as the preconditioner -- tests whether the assembled
    # tangent is exact
    ns.petsc_options["snes_mf_operator"] = None
    uw.pprint("snes_mf_operator: matrix-free Jacobian action")
if int(params.uw_monitor):
    # diagnosis: every nonlinear residual and every Krylov outcome, the inner blocks too
    ns.petsc_options["snes_monitor"] = None
    ns.petsc_options["ksp_converged_reason"] = None
    ns.petsc_options["snes_converged_reason"] = None
    for b in ("velocity", "pressure"):
        ns.petsc_options[f"fieldsplit_{b}_ksp_converged_reason"] = None
if int(params.uw_ksp_max_it):
    # a stalled Krylov solve fails the step (and is reported) instead of spinning
    ns.petsc_options["ksp_max_it"] = int(params.uw_ksp_max_it)
if int(params.uw_direct) and uw.mpi.size == 1:
    # testing only: a direct velocity solve in place of FMG (serial; MUMPS, the
    # parallel direct solver, segfaults in this PETSc build)
    ns.petsc_options["fieldsplit_velocity_ksp_type"] = "preonly"
    ns.petsc_options["fieldsplit_velocity_pc_type"] = "lu"

dt = float(params.uw_courant) * csize_circle / U0
if float(params.uw_dt) > 0:
    # a fixed timestep, independent of the cylinder cell: refine the wall without
    # cutting the step (the implicit schemes are not bound to the finest cell's Courant)
    uw.pprint(f"timestep fixed at {float(params.uw_dt):g} (Courant {params.uw_courant} on the cylinder cell would give {dt:g}; "
              f"cylinder-cell Courant now {float(params.uw_dt) * U0 / csize_circle:.2f})")
    dt = float(params.uw_dt)
if Wi > 0:
    cm.Parameters.dt_elastic = dt

# fields saved at the checkpoints, all projected (never a pointwise derivative)
omega = uw.discretisation.MeshVariable("omega", mesh, 1, degree=1)
omega_proj = uw.systems.Projection(mesh, omega)
omega_proj.uw_function = v.sym[1].diff(x) - v.sym[0].diff(y)
omega_proj.smoothing = 0.0
tau_ii = uw.discretisation.MeshVariable("tauII", mesh, 1, degree=1)
tau_proj = uw.systems.Projection(mesh, tau_ii)
sigma = (cm._carried_stress_sym(0) if Wi > 0          # the carried polymer stress (decoded)
         else 2 * eta * sympy.Matrix(mesh.vector.strain_tensor(v.sym)))
tau_proj.uw_function = sympy.sqrt(0.5 * (sigma[0, 0] ** 2 + 2 * sigma[0, 1] ** 2 + sigma[1, 1] ** 2))
tau_proj.smoothing = 0.0

# drag and lift from the boundary traction
stress = ns.stress
traction = stress * sympy.Matrix([mesh.Gamma[0], mesh.Gamma[1]])
F_x = uw.maths.BdIntegral(mesh, -traction[0], "inclusion")
F_y = uw.maths.BdIntegral(mesh, -traction[1], "inclusion")

# passive tracers, released each step near the inlet, as two smoke trails close to
# the centreline. They are aimed at the cylinder (radius 0.05): a tracer that lingers
# at the wall in a closed recirculation bubble can cross the facet under RK2 on the
# extrapolated velocity and is deleted as outside the domain (res 40 forward runs kept
# 15% of their tracers when seeded on the centreline), so expect thinner trails
tracers = uw.swarm.Swarm(mesh=mesh)
# two smoke sources, one a little above and one a little below the midline (each
# `tracer_offset` from the cylinder's centreline, bunched within `tracer_halfwidth`),
# so each shear layer is seeded by its own streak; the default offset of twice the
# halfwidth leaves a gap between the trails about as wide as one source
u_ = np.linspace(-1.0, 1.0, max(int(params.uw_tracers) // 2, 2))
bunch = np.arctanh(u_ * np.tanh(2.0)) / 2.0 * float(params.uw_tracer_halfwidth)
seed_y = np.concatenate([centre[1] - float(params.uw_tracer_offset) + bunch,
                         centre[1] + float(params.uw_tracer_offset) + bunch])
seed = np.c_[np.full_like(seed_y, 1.5 * csize_circle), seed_y]
tracers.add_particles_with_coordinates(seed)


def checkpoint(index):
    omega_proj.solve()
    if Wi > 0:
        # the invariant of the decoded stress read AT the nodes (the carried
        # field is nodal P1, so this is exact there): an L2 projection of it
        # undershoots to negative values beside the wall peaks (Gibbs) and
        # paints fringes that are not in the carried field
        tau_ii.data[:, 0] = np.asarray(uw.function.evaluate(tau_proj.uw_function, np.asarray(tau_ii.coords))).reshape(-1)
    else:
        tau_proj.solve()
    mesh.petsc_save_checkpoint(index=index, meshVars=[v, omega, tau_ii],
                               outputPath=os.path.join(ckdir, "checkpoint"))
    tracers.write_timestep("checkpoint", "tracers", index=index, outputPath=ckdir, force_sequential=True)


n_steps = int(np.ceil(float(params.uw_t_end) / dt))
csv = open(os.path.join(outdir, "forces.csv"), "w") if uw.mpi.rank == 0 else None
if csv:
    csv.write("step,t,cd,cl,tau_max,fit_overshoot,fit_cells\n")
# -uw_reaction 1: also the CONSISTENT drag and lift, the momentum residual summed over
# the cylinder's velocity nodes (the volume / weak-form force, inertia included),
# beside the boundary-traction measure, in forces_reaction.csv
rcsv, cyl_nodes = None, None
if int(params.uw_reaction):
    from underworld3.utilities.boundary_flux import _boundary_field_nodes
    rcsv = open(os.path.join(outdir, "forces_reaction.csv"), "w") if uw.mpi.rank == 0 else None
    if rcsv:
        rcsv.write("step,t,cd_traction,cl_traction,cd_reaction,cl_reaction,cd_theta,cl_theta,"
                   "cd_devss,cl_devss,cd_stab,cl_stab\n")
    # the traction of the stress the momentum equation actually assembles: the theta-rule
    # blend of the new stress and the carried history level (minus the pressure)
    sig_theta = ns._viscous_flux() - sympy.eye(2) * p.sym[0]
    tr_theta = sig_theta * sympy.Matrix([mesh.Gamma[0], mesh.Gamma[1]])
    Fth_x = uw.maths.BdIntegral(mesh, -tr_theta[0], "inclusion")
    Fth_y = uw.maths.BdIntegral(mesh, -tr_theta[1], "inclusion")
    uw.pprint(f"momentum time-scheme weights of the spatial operator: {ns.DuDt.spatial_weights()}")
    # the other terms of F1, each as a wall traction: whatever the reaction holds beyond
    # theta + devss + stabilisation is the volume (inertia) part
    nvec = sympy.Matrix([mesh.Gamma[0], mesh.Gamma[1]])
    def _bd_pair(flux):
        tr = sympy.Matrix(flux) * nvec
        return (uw.maths.BdIntegral(mesh, -tr[0], "inclusion"), uw.maths.BdIntegral(mesh, -tr[1], "inclusion"))
    F_devss = _bd_pair(ns._devss_flux())
    F_stab = _bd_pair(ns._stabilisation_flux())


def reaction_force():
    """Total force on the cylinder from the assembled volume residual at its nodes:
    each rank's partial at a node shared across a cut sums to the whole."""
    global cyl_nodes
    if cyl_nodes is None:
        nodes, lsec, *_ = _boundary_field_nodes(ns, "inclusion", field_id=0)
        nc = lsec.getFieldComponents(0)
        cyl_nodes = [(lsec.getFieldOffset(q, 0) + s * nc, nc) for q, s, _c in nodes]
    ra = np.asarray(ns._assemble_volume_reaction()).ravel()
    f = np.zeros(2)
    for off, nc in cyl_nodes:
        f += ra[off:off + 2]
    return comm.allreduce(f, op=MPI.SUM)
def choose_reconstruction():
    """The forward histories: one global L2 projection of the arrivals in place of
    the per-cell fit. Done at the same point of the sequence as the run that wrote
    a snapshot (the projector makes variables the snapshot holds by name)."""
    if Wi > 0 and str(params.uw_reconstruction) != "cell":
        ns.DFDt.reconstruction = str(params.uw_reconstruction)
    if vt == "forward_nodes" and str(params.uw_velocity_reconstruction) != "cell":
        ns.DuDt.reconstruction = str(params.uw_velocity_reconstruction)
        if float(params.uw_bubble_penalty) > 0:
            # the P2 velocity projection's prior of zero quadratic content, as a
            # fraction of the cell mass
            ns.DuDt.bubble_penalty = float(params.uw_bubble_penalty)


snapdir = os.path.join(outdir, "snapshots")
start = int(params.uw_restart_step)
if str(params.uw_restart):
    # a snapshot loads into variables that already exist, and some (the cell-size
    # field, projection targets) are made by the first solve: take one step to build
    # them, then load the snapshot over everything it changed
    ramp.sym = 1.0e-6
    ns.solve(timestep=dt, zero_init_guess=False)
    omega_proj.solve(); tau_proj.solve()
    choose_reconstruction()
    uw.get_default_model().load_state(str(params.uw_restart))
    uw.pprint(f"restarted from {params.uw_restart} at step {start}")
    if float(params.uw_kick) != 0.0:
        # an impulsive, one-signed transverse velocity: a Gaussian blob of v_y
        # (amplitude kick x U_mean, centre (kick_x, kick_y), width kick_w) added to
        # the velocity and to every carried velocity history (a semi-Lagrangian
        # momentum history would otherwise hand the next step the unkicked field)
        A, xk, yk, wk = (float(params.uw_kick) * U_mean, float(params.uw_kick_x),
                         float(params.uw_kick_y), float(params.uw_kick_w))
        hist = [ps for ps in getattr(ns.DuDt, "psi_star", []) or []
                if hasattr(ps, "coords") and np.asarray(ps.data).shape[-1] == 2]
        for var in [v] + hist:
            X = np.asarray(var.coords)
            arr = np.array(var.data)
            arr[:, 1] += A * np.exp(-((X[:, 0] - xk) ** 2 + (X[:, 1] - yk) ** 2) / wk ** 2)
            var.data[...] = arr
        uw.pprint(f"kicked v_y by {A:g} at ({xk:g}, {yk:g}), width {wk:g}: velocity + {len(hist)} history level(s)")
else:
    checkpoint(0)
    choose_reconstruction()


def snapshot(index):
    if uw.mpi.rank == 0:
        os.makedirs(snapdir, exist_ok=True)
    comm.barrier()
    uw.get_default_model().save_state(file=os.path.join(snapdir, f"step{index:05d}.snap.h5"))
    comm.barrier()
    if uw.mpi.rank == 0:
        import shutil
        kept = sorted(f for f in os.listdir(snapdir) if f.endswith(".snap.h5"))
        for f in kept[:-int(params.uw_keep_snapshots)]:
            os.remove(os.path.join(snapdir, f))
            shutil.rmtree(os.path.join(snapdir, f.replace(".snap.h5", ".snap.bulk")), ignore_errors=True)



if int(params.uw_debug_recon):
    # one carry reconstructed both ways from the same arrivals, saved per rank
    hist = ns.DFDt
    fit_once = hist._fit_arrivals

    def fit_both(X, values, cell=None, inflow=None):
        if cell is not None:
            return fit_once(X, values, cell=cell, inflow=inflow)
        before = np.array(hist.psi_star[0].data)
        out = {}
        for r in ("cell", "global"):
            hist.psi_star[0].data[:, :] = before
            hist._reconstruction = r
            fit_once(np.array(X), np.array(values), inflow=inflow)
            out[r] = np.array(hist.psi_star[0].data)
        np.savez(os.path.join(outdir, f"recon_rank{uw.mpi.rank}.npz"), coords=np.asarray(hist.psi_star[0].coords),
                 before=before, cell=out["cell"], glob=out["global"])
        hist._fit_arrivals = fit_once

    hist._fit_arrivals = fit_both

if int(params.uw_dump_history) and Wi > 0:
    # the carried stress as stored (the log-conformation components at the
    # store's own points), the stress decoded from it at those points, and
    # the projected invariant the checkpoints hold, for a ringing comparison
    h = ns.DFDt
    X = np.asarray(h.psi_star[0].coords); D = np.array(h.psi_star[0].data)
    sig = cm._carried_stress_sym(0)
    dec = np.column_stack([np.asarray(uw.function.evaluate(sig[i, j], X)).reshape(-1) for (i, j) in ((0, 0), (0, 1), (1, 1))])
    tau_proj.solve()
    tp = np.asarray(uw.function.evaluate(tau_ii.sym[0], X)).reshape(-1)
    np.savez(os.path.join(outdir, f"history_rank{uw.mpi.rank}.npz"), X=X, log_conf=D, decoded=dec, tau_proj=tp)
    uw.pprint("dumped the carried stress; stopping")
    raise SystemExit

t, wall = start * dt, 0.0
orchestration_model = uw.get_default_model()
n_snap = int(params.uw_snapback)
snap_log = []


def advance(h, depth=0):
    """One step of length h. With -uw_snapback N, a step whose Newton solve does not
    converge is rolled back to the in-memory state saved before it and retaken as
    two half steps, down to N halvings. Returns the number of solves accepted."""
    token = orchestration_model.save_state() if n_snap else None
    if Wi > 0:
        cm.Parameters.dt_elastic = h
    ns.solve(timestep=h, zero_init_guess=False)
    reason = int(ns.snes.getConvergedReason())
    if not n_snap or reason > 0:
        return 1
    if depth >= n_snap:
        uw.pprint(f"snap back: dt {h:g} still not converged (reason {reason}) at the halving limit; accepted")
        snap_log.append((h, "accepted unconverged"))
        return 1
    orchestration_model.load_state(token)
    uw.pprint(f"snap back: Newton failed (reason {reason}) at dt {h:g}; restored, retaking as 2 x {h / 2:g}")
    snap_log.append((h, "halved"))
    return advance(h / 2, depth + 1) + advance(h / 2, depth + 1)


# -uw_switch 1: the momentum's share of the stretch switches per step. Implicit while the
# velocity block's diagonal margin (min / mean) holds; a step whose Newton fails is
# restored and retaken with "linear", and a converged step whose margin has fallen
# below -uw_switch_margin sends the next steps to "linear". After -uw_switch_retry
# linear steps the implicit form is tried again (the wait doubles each time the
# retry falls back, up to 8x). Both forms store the same stress: no state crosses.
switch = dict(retry=int(params.uw_switch_retry), wait=0, trial=False, log=None)


def velocity_diag_margin():
    """min / mean of the diagonal of the assembled Jacobian's velocity block."""
    J = ns.snes.getJacobian()[0]
    _, isets, _ = ns.dm.createFieldDecomposition()
    d = J.createSubMatrix(isets[0], isets[0]).getDiagonal().getArray()
    lo = comm.allreduce(float(d.min()) if d.size else float("inf"), op=MPI.MIN)
    total = comm.allreduce(float(d.sum()), op=MPI.SUM)
    count = comm.allreduce(int(d.size), op=MPI.SUM)
    return lo / (total / count)


def _switch_log(mode, reason, margin, note=""):
    if uw.mpi.rank == 0:
        if switch["log"] is None:
            new = not os.path.exists(os.path.join(outdir, "stretch_modes.csv"))
            switch["log"] = open(os.path.join(outdir, "stretch_modes.csv"), "a")
            if new:
                switch["log"].write("step,mode,reason,margin,note\n")
        switch["log"].write(f"{current_step[0]},{mode},{reason},{margin:.5f},{note}\n")
        switch["log"].flush()


def _go_linear(note):
    if switch["trial"]:
        switch["retry"] = min(2 * switch["retry"], 8 * int(params.uw_switch_retry))
    switch["trial"] = False
    switch["wait"] = 0
    cm.stretch_in_momentum = "linear"
    uw.pprint(f"step {current_step[0]}: stretch -> linear ({note}); next implicit try in {switch['retry']} steps")


def advance_switching(h):
    if cm.stretch_in_momentum != "implicit":
        switch["wait"] += 1
        if switch["wait"] > switch["retry"]:
            cm.stretch_in_momentum = "implicit"
            switch["trial"] = True
            uw.pprint(f"step {current_step[0]}: stretch -> implicit (trial)")
    cm.Parameters.dt_elastic = h
    if cm.stretch_in_momentum == "implicit":
        token = orchestration_model.save_state()
        # an implicit attempt that grinds inside one Newton step (inner solves at
        # their caps) is stopped by the wall-clock deadline and counts as a failure
        ns.guard(wall_per_step=float(params.uw_switch_wall))
        try:
            ns.solve(timestep=h, zero_init_guess=False)
        finally:
            ns.unguard()
        reason = int(ns.snes.getConvergedReason())
        if getattr(ns.solve_report, "deadline_expired", False):
            reason = min(reason, -3)
        if reason > 0:
            margin = velocity_diag_margin()
            if margin >= float(params.uw_switch_margin):
                if switch["trial"]:
                    switch["retry"] = int(params.uw_switch_retry)
                switch["trial"] = False
                _switch_log("implicit", reason, margin)
                return 1
            _switch_log("implicit", reason, margin, "low margin: kept")
            _go_linear(f"margin {margin:.3f}")
            return 1
        _switch_log("implicit", reason, float("nan"),
                    "deadline: restored" if getattr(ns.solve_report, "deadline_expired", False)
                    else "failed: restored")
        orchestration_model.load_state(token)
        cm.Parameters.dt_elastic = h
        _go_linear(f"Newton reason {reason}")
    ns.solve(timestep=h, zero_init_guess=False)
    reason = int(ns.snes.getConvergedReason())
    _switch_log(cm.stretch_in_momentum, reason, velocity_diag_margin() if reason > 0 else float("nan"))
    return 1


if int(params.uw_snapback_check):
    # the machinery's own test: save, solve, restore, solve again -- the two
    # solutions must agree to round-off
    ramp.sym = min(1.0, max((t + dt) / float(params.uw_ramp), 1.0e-6))   # the first step's inflow
    tok = orchestration_model.save_state()
    ns.solve(timestep=dt, zero_init_guess=False)
    v1 = np.array(v.array[...]); c1 = 2 * float(F_x.evaluate()) / (U_mean ** 2 * D)
    orchestration_model.load_state(tok)
    ns.solve(timestep=dt, zero_init_guess=False)
    v2 = np.array(v.array[...]); c2 = 2 * float(F_x.evaluate()) / (U_mean ** 2 * D)
    dv = comm.allreduce(float(np.abs(v1 - v2).max()) if v1.size else 0.0, op=MPI.MAX)
    uw.pprint(f"snapback check: max |v1 - v2| = {dv:.3e}, cd {c1:.8f} vs {c2:.8f}")
    orchestration_model.load_state(tok)


def dump_jacobian(base):
    """The assembled Jacobian and preconditioning matrix of the current Newton
    iterate, the global velocity rows and their coordinates, for an offline spectrum."""
    from petsc4py import PETSc
    J, P = ns.snes.getJacobian()[:2]
    names, isets, _ = ns.dm.createFieldDecomposition()
    for mat, tag in ((J, "J"), (P, "P")):
        viewer = PETSc.Viewer().createBinary(f"{base}_{tag}.bin", "w", comm=PETSc.COMM_WORLD)
        mat.view(viewer); viewer.destroy()
    # coordinates of each owned velocity dof: vertices from the coordinate
    # section, edge dofs (P2) at the edge centroid
    dm = ns.dm
    gsec = dm.getGlobalSection()
    csec = dm.getCoordinateSection(); cvec = dm.getCoordinatesLocal().array
    vStart, vEnd = dm.getDepthStratum(0)
    idx, xy = [], []
    for pt in range(*gsec.getChart()):
        nd = gsec.getFieldDof(pt, 0)
        off = gsec.getFieldOffset(pt, 0)
        if nd <= 0 or off < 0:
            continue
        if vStart <= pt < vEnd:
            co = csec.getOffset(pt); x = cvec[co:co + 2]
        else:
            x = dm.computeCellGeometryFVM(pt)[1][:2]
        for k in range(nd):
            idx.append(off + k); xy.append(x)
    rows = comm.gather(np.asarray(isets[0].getIndices()), root=0)
    cidx = comm.gather(np.asarray(idx, dtype=np.int64), root=0)
    cxy = comm.gather(np.asarray(xy, dtype=float).reshape(-1, 2), root=0)
    if uw.mpi.rank == 0:
        np.save(f"{base}_velocity_rows.npy", np.concatenate(rows))
        np.save(f"{base}_dof_index.npy", np.concatenate(cidx))
        np.save(f"{base}_dof_xy.npy", np.concatenate(cxy))
        print(f"[0] dumped Jacobian {os.path.basename(base)}: fields {names}", flush=True)


def wall_report(step_no):
    """The elastic wall layer on rays normal to the cylinder, in the wall frame
    (n outward, t = n rotated anticlockwise): shear rate, local Weissenberg
    number, the carried stress, N1 = s_tt - s_nn, tr c and the Pakdel-McKinley
    M = sqrt(lam |u_t| / r * N1 / |s_tn|). Written to wall_<step>.csv, summarised
    on rank 0; the half-width of the tension layer is set against the wall cell."""
    lam = Wi * D / U_mean
    G = float(sympy.sympify(uw.function.expressions.unwrap(cm.Parameters.shear_modulus)))
    angles = np.deg2rad(np.arange(0.0, 360.0, 15.0))
    dists = np.geomspace(1.0e-4, 3.0e-2, 28)
    A, Dd = np.meshgrid(angles, dists, indexing="ij")
    r = radius + Dd
    pts = np.stack([centre[0] + r * np.cos(A), centre[1] + r * np.sin(A)], axis=-1).reshape(-1, 2)
    Lsym = sympy.Matrix(v.sym).reshape(1, 2).jacobian(mesh.X[:2])
    S = sympy.Matrix(cm._carried_stress_sym(0))
    ev = lambda e: np.asarray(uw.function.global_evaluate(e, pts)).reshape(-1)
    L = np.stack([[ev(Lsym[i, j]) for j in range(2)] for i in range(2)]).transpose(2, 0, 1)
    sig = np.stack([[ev(S[i, j]) for j in range(2)] for i in range(2)]).transpose(2, 0, 1)
    vel = np.stack([ev(v.sym[0, 0]), ev(v.sym[0, 1])], axis=1)
    # the total physical stress (tension positive): after the step the carried stress
    # is this step's polymer stress; add the solvent's 2 eta_s D and take the pressure
    pres = ev(p.sym[0])
    if uw.mpi.rank != 0:
        return
    n = np.stack([np.cos(A), np.sin(A)], axis=-1).reshape(-1, 2)
    t = np.stack([-n[:, 1], n[:, 0]], axis=1)
    Dm = 0.5 * (L + np.transpose(L, (0, 2, 1)))
    total = sig + 2 * beta * eta * Dm - pres[:, None, None] * np.eye(2)
    gdot = 2 * np.einsum("ki,kij,kj->k", t, Dm, n)
    s_tt = np.einsum("ki,kij,kj->k", t, sig, t)
    s_nn = np.einsum("ki,kij,kj->k", n, sig, n)
    s_tn = np.einsum("ki,kij,kj->k", t, sig, n)
    N1 = s_tt - s_nn
    trc = np.trace(sig, axis1=1, axis2=2) / G + 2.0            # tr(sigma/G + I)
    if str(params.uw_relaxation) == "fene_p":
        # sigma/G + I = f c with f = 1 + (tr(f c) - d)/L^2
        trc = trc / (1.0 + (trc - 2.0) / float(params.uw_L2))
    eps_tt = np.einsum("ki,kij,kj->k", t, Dm, t)            # stretching along the wall direction
    principal = np.linalg.eigvalsh(0.5 * (total + np.transpose(total, (0, 2, 1))))
    tot_tt = np.einsum("ki,kij,kj->k", t, total, t)
    ut = np.abs(np.einsum("ki,ki->k", t, vel))
    M = np.sqrt(np.maximum(lam * ut / r.reshape(-1) * N1 / np.maximum(np.abs(s_tn), 1e-30), 0.0))
    rows = np.column_stack([np.rad2deg(A).reshape(-1), Dd.reshape(-1), gdot, lam * np.abs(gdot),
                            s_tt, s_nn, s_tn, N1, trc, ut, M, lam * eps_tt,
                            pres, tot_tt, principal[:, 1], principal[:, 0]])
    np.savetxt(os.path.join(outdir, f"wall_{step_no:05d}.csv"), rows, delimiter=",",
               header="angle,d,gdot,Wi_local,s_tt,s_nn,s_tn,N1,trc,u_t,M,Wi_ext,p,total_tt,sigma1,sigma2", comments="")
    na, nd = A.shape
    R = rows.reshape(na, nd, -1)
    k = int(np.argmax(R[:, 0, 7]))                          # the angle of largest wall tension
    prof = R[k, :, 7]
    half = dists[np.argmax(prof < 0.5 * prof[0])] if (prof < 0.5 * prof[0]).any() else float("nan")
    print(f"[0] wall report step {step_no}: lam {lam:g}, wall cell {csize_circle:.4g}", flush=True)
    for j in range(na):
        w = R[j, 0]
        print(f"    angle {w[0]:5.0f}: gdot {w[2]:9.2f} Wi_loc {w[3]:6.2f} N1/|s_tn| "
              f"{w[7] / max(abs(w[6]), 1e-30):7.2f} tr c {w[8]:8.2f} M {w[10]:6.2f} | p {w[12]:9.3f} "
              f"total_tt {w[13]:9.3f} sigma1 {w[14]:9.3f} sigma2 {w[15]:9.3f}", flush=True)
    print(f"    largest wall tension at angle {R[k, 0, 0]:.0f}: N1 {prof[0]:.4g}, "
          f"half-width {half:.4g} = {half / csize_circle:.2f} wall cells; max tr c on the rays "
          f"{R[:, :, 8].max():.2f}", flush=True)
    j180 = int(np.argmin(np.abs(R[:, 0, 0] - 180.0)))           # the upstream stagnation streamline
    print(f"    stagnation streamline: max lam * eps_tt {R[j180, :, 11].max():.3f} "
          f"(Oldroyd-B extensional stress unbounded above 0.5)", flush=True)


# -uw_dump_newton "50:1,6,12" dumps the Jacobian inside step 50's Newton solve,
# at the monitor calls of the listed iterations (each holds the previous iterate's Jacobian)
newton_dumps = {}
if str(params.uw_dump_newton):
    for item in str(params.uw_dump_newton).split(";"):
        st, its = item.split(":")
        newton_dumps[int(st)] = {int(k) for k in its.split(",")}
current_step = [0]


def _newton_dump_monitor(snes, its, fnorm):
    if its in newton_dumps.get(current_step[0], ()) and its > 0:
        dump_jacobian(os.path.join(outdir, f"jacobian_{current_step[0]:05d}_newton{its:02d}"))


monitored_snes = [None]

for step in range(start, n_steps):
    current_step[0] = step + 1
    if step == start + 1 and not globals().get("_pc_reported"):
        # what the velocity block actually ran: multigrid flavour and level smoother
        _pc_reported = True
        try:
            sub = ns.snes.getKSP().getPC().getFieldSplitSubKSP()[0]
            vpc = sub.getPC()
            info = f"velocity ksp {sub.getType()} pc {vpc.getType()}"
            if vpc.getType() in ("mg", "gamg"):
                n = vpc.getMGLevels()
                sm = vpc.getMGSmoother(n - 1)
                info += (f" levels {n} mg type {vpc.getMGType()} finest smoother "
                         f"{sm.getType()} x{sm.getTolerances()[3]} + {sm.getPC().getType()}")
            uw.pprint(info)
        except Exception as err:
            uw.pprint(f"velocity pc report failed: {err}")
    # the solver may rebuild its SNES; attach the dump monitor to whichever is live
    if newton_dumps and getattr(ns, "snes", None) is not None and ns.snes is not monitored_snes[0]:
        ns.snes.setMonitor(_newton_dump_monitor)
        monitored_snes[0] = ns.snes
    ramp.sym = min(1.0, max((t + dt) / float(params.uw_ramp), 1.0e-6))
    t0 = time.perf_counter()
    if int(params.uw_lagged_stretch) and step == start:
        _u0 = np.array(v.array[...]); _up = np.array(ns._u_prev.array[...])
    n_solves = advance_switching(dt) if int(params.uw_switch) else advance(dt)
    if Wi > 0:
        cm.Parameters.dt_elastic = dt
    if n_solves > 1:
        uw.pprint(f"step {step + 1}: taken in {n_solves} substeps")
    if int(params.uw_lagged_stretch) and step == start:
        _a = np.array(ns._a_var.array[...]); _u1 = np.array(v.array[...])
        _m = lambda q: comm.allreduce(float(np.abs(q).max()) if q.size else 0.0, op=uw.MPI.MAX)
        uw.pprint(f'DEBUG a-check: |u1|={_m(_u1):.4g} |a-(2u0-up)|={_m(_a-(2*_u0-_up)):.4g} |a-u1|={_m(_a-_u1):.4g} |u1-u0|={_m(_u1-_u0):.4g} |u0-up|={_m(_u0-_up):.4g}')
    wall += time.perf_counter() - t0
    tracers.advection(v.sym, dt, order=2, corrector=False, evalf=False)
    tracers.add_particles_with_coordinates(seed)
    t += dt
    ck = (step + 1) % int(params.uw_checkpoint_every) == 0
    if ck:
        checkpoint(step + 1)
    cd = 2 * float(F_x.evaluate()) / (U_mean ** 2 * D)
    cl = 2 * float(F_y.evaluate()) / (U_mean ** 2 * D)
    tmax = comm.allreduce(float(np.asarray(tau_ii.data).max()) if ck else float("nan"), op=MPI.MAX)
    # the forward-IP fit's overshoot beyond the range of its arrivals (every rank)
    hist = getattr(ns, "DFDt", None)
    over = comm.allreduce(float(getattr(hist, "_fit_overshoot", float("nan"))), op=MPI.MAX)
    n_over = comm.allreduce(int(getattr(hist, "_fit_overshoot_cells", -1)), op=MPI.SUM)
    if csv:
        csv.write(f"{step + 1},{t:.5f},{cd:.6f},{cl:.6f},{tmax:.6e},{over:.4e},{n_over}\n"); csv.flush()
    if int(params.uw_reaction):
        fr = reaction_force()
        cdr, clr = 2 * fr[0] / (U_mean ** 2 * D), 2 * fr[1] / (U_mean ** 2 * D)
        cdt = 2 * float(Fth_x.evaluate()) / (U_mean ** 2 * D)
        clt = 2 * float(Fth_y.evaluate()) / (U_mean ** 2 * D)
        sc = 2 / (U_mean ** 2 * D)
        cdd, cld = sc * float(F_devss[0].evaluate()), sc * float(F_devss[1].evaluate())
        cds, cls = sc * float(F_stab[0].evaluate()), sc * float(F_stab[1].evaluate())
        if rcsv:
            rcsv.write(f"{step + 1},{t:.5f},{cd:.6f},{cl:.6f},{cdr:.6f},{clr:.6f},{cdt:.6f},{clt:.6f},"
                       f"{cdd:.6f},{cld:.6f},{cds:.6f},{cls:.6f}\n"); rcsv.flush()
    dbg = int(params.uw_debug_fene)
    if dbg and str(params.uw_relaxation) == "fene_p" and ((step + 1) % 10 == 0 or dbg <= step + 1 <= dbg + 25):
        # every tenth step, and every step for 25 steps from the one uw_debug_fene names
        # the spring factor of the stress the step produced, before the floor, at
        # the nodes of the spring-factor field, and the record's own factor
        cm = ns.constitutive_model
        fsym = 1 + sympy.Matrix(cm.history_flux).trace() / (cm.Parameters.shear_modulus * cm.Parameters.extensibility)
        fr = np.asarray(uw.function.evaluate(fsym, np.asarray(cm._fene_f.coords_nd))).reshape(-1)
        frec = np.asarray(cm._fene_f.data).reshape(-1)
        lo = comm.allreduce(float(fr.min()), op=MPI.MIN); hi = comm.allreduce(float(fr.max()), op=MPI.MAX)
        nlow = comm.allreduce(int((fr < 1 - 2 / float(params.uw_L2)).sum()), op=MPI.SUM)
        rmax = comm.allreduce(float(frec.max()), op=MPI.MAX)
        # the record itself: tr c at the nodes (decoded from the log store), where
        # its maximum sits, and the stress trace there and at the quadrature points
        from underworld3.constitutive_models import _expm_sym2
        hist = ns.DFDt
        rec = _expm_sym2(sympy.Matrix(hist.psi_star[0].sym))
        trc_sym = rec.trace() / cm._fene_spring_factor_of_record(rec)   # tr c of the record
        X = np.asarray(cm._fene_f.coords_nd)
        trc = np.asarray(uw.function.evaluate(trc_sym, X)).reshape(-1)
        trs = np.asarray(uw.function.evaluate(sympy.Matrix(cm.history_flux).trace() / cm.Parameters.shear_modulus, X)).reshape(-1)
        i = int(trc.argmax()); loc = (float(trc[i]), float(trs[i]), float(X[i, 0]), float(X[i, 1]), float(fr[i]))
        tmax_all = comm.allreduce(float(trc.max()), op=MPI.MAX)
        # the encode before the nodal projection, sampled at the P2 velocity nodes
        # (vertices and edge midpoints): is the quadrature-level record bounded?
        qp = np.asarray(v.coords)
        trs_q = np.asarray(uw.function.evaluate(sympy.Matrix(cm.history_flux).trace() / cm.Parameters.shear_modulus, qp)).reshape(-1)
        enc = cm.encode_history(cm.history_flux)
        psi_q = np.stack([np.asarray(uw.function.evaluate(enc[i, j], qp)).reshape(-1) for i in range(2) for j in range(2)], axis=1).reshape(-1, 2, 2)
        trfc_q = np.exp(np.linalg.eigvalsh(0.5 * (psi_q + np.transpose(psi_q, (0, 2, 1))))).sum(axis=1)
        trc_q = trfc_q / (1 + (trfc_q - 2) / float(params.uw_L2))
        qlo = comm.allreduce(float(trs_q.min()), op=MPI.MIN); qhi = comm.allreduce(float(trs_q.max()), op=MPI.MAX)
        qc = comm.allreduce(float(trc_q.max()), op=MPI.MAX)
        uw.pprint(f"fene step {step + 1} f_of_stress min {lo:.3f} max {hi:.3f} below_floor {nlow} f_record max {rmax:.3f} "
                  f"| tr c nodes max {tmax_all:.2f} qp max {qc:.2f} | tr s/G nodes [{lo*0+float(trs.min()):.1f},{float(trs.max()):.1f}] qp [{qlo:.1f},{qhi:.1f}]")
        if float(trc.max()) == tmax_all:
            print(f"  worst node: tr c {loc[0]:.2f} tr s/G {loc[1]:.1f} f_raw {loc[4]:.3f} at ({loc[2]:.4f},{loc[3]:.4f})", flush=True)
    if str(params.uw_wall_report) and (step + 1) in {int(k) for k in str(params.uw_wall_report).split(",")}:
        wall_report(step + 1)
    if str(params.uw_dump_jacobian) and (step + 1) in {int(k) for k in str(params.uw_dump_jacobian).split(",")}:
        # diagnosis: the assembled Jacobian of the last Newton iterate, its
        # preconditioning matrix and the velocity rows, for an offline spectrum
        from petsc4py import PETSc
        J, P = ns.snes.getJacobian()[:2]
        names, isets, _ = ns.dm.createFieldDecomposition()
        base = os.path.join(outdir, f"jacobian_{step + 1:05d}")
        for mat, tag in ((J, "J"), (P, "P")):
            viewer = PETSc.Viewer().createBinary(f"{base}_{tag}.bin", "w", comm=PETSc.COMM_WORLD)
            mat.view(viewer); viewer.destroy()
        rows = comm.gather(np.asarray(isets[0].getIndices()), root=0)
        if uw.mpi.rank == 0:
            np.save(f"{base}_velocity_rows.npy", np.concatenate(rows))
            uw.pprint(f"dumped Jacobian at step {step + 1}: fields {names}")
    if int(params.uw_snapshot_every) and (step + 1) % int(params.uw_snapshot_every) == 0:
        snapshot(step + 1)
    if not np.isfinite(cd) or abs(cd) > 1.0e3:
        uw.pprint(f"STOPPED step {step + 1} t {t:.4f}: cd {cd}")
        break
    if (step + 1) % int(params.uw_log_every) == 0 or step == 0:
        uw.pprint(f"{params.uw_label} step {step + 1:5d}/{n_steps} t {t:.3f} cd {cd:.4f} cl {cl:+.4f} "
                  f"s/step {wall / (step + 1 - start):.2f}")
uw.pprint(f"DONE {params.uw_label} steps {step + 1} t {t:.3f} s/step {wall / (step + 1 - start):.2f}")
