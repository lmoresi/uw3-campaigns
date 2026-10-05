"""Two-panel frames of a ve_cylinder.py run, one per checkpoint:
top, the stress-history magnitude (second invariant of the carried polymer stress) with
streamlines; bottom, the vorticity with the tracers.

  python render_demo.py -uw_run grid -uw_title "grid (SUPG) momentum, grid stress"

Colour ranges are shared by every frame of every run in runs/ (set just beyond the
extremes after the ramp, so nothing clips and the runs compare). Resumable: frames
already written are kept; -uw_max_frames bounds one process (a macOS plotter leaks).
"""
import os, glob, re, time
# never lock a checkpoint a live run may be writing (a lock clash kills the run)
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
import numpy as np, pyvista as pv, h5py
import underworld3 as uw, underworld3.visualisation as vis
from matplotlib.colors import ListedColormap
import matplotlib.cm as mcm
from PIL import Image
pv.OFF_SCREEN = True

params = uw.Params(uw_run="grid", uw_title="", uw_every=1, uw_max_frames=60, uw_asinh=20.0,
                   uw_tau_asinh=0.0, uw_from_step=120, uw_top="auto", uw_mesh_file="dfg_5_c0.25.msh", uw_refinement=2,
                   uw_omega_max=0.0)
HERE = os.path.dirname(os.path.abspath(__file__))
run = str(params.uw_run)
cdir = os.path.join(HERE, "runs", run, "checkpoints")
frames = os.path.join(HERE, "runs", run, "frames")
os.makedirs(frames, exist_ok=True)


def settled(f):
    """A checkpoint the run finished writing: every file of that index older than a minute."""
    return time.time() - os.path.getmtime(f) > 60.0


def step_of(f, field):
    return int(re.search(rf"\.{field}\.(\d+)\.h5$", f).group(1))


def extreme(field):
    """Largest |value| of a field over every run's checkpoints after the ramp."""
    m = 0.0
    for f in glob.glob(os.path.join(HERE, "runs", "*", "checkpoints", f"checkpoint.mesh.{field}.*.h5")):
        # smoke runs are a set of their own
        if ("smoke" in f) != run.startswith("smoke") or step_of(f, field) < int(params.uw_from_step) or not settled(f):
            continue
        with h5py.File(f, "r") as h:
            m = max(m, float(np.abs(h["fields"][field][()]).max()))
    return m


# vorticity range: the extreme (at the walls) unless -uw_omega_max sets one for the wake
OMEGA_MAX, TAU_MAX = 1.05 * extreme("omega"), 1.05 * extreme("tauII")
if float(params.uw_omega_max) > 0:
    OMEGA_MAX = float(params.uw_omega_max)


def run_extreme(field):
    """Largest |value| (vector norm for U) of one field over this run's checkpoints after the ramp."""
    m = 0.0
    for f in glob.glob(os.path.join(cdir, f"checkpoint.mesh.{field}.*.h5")):
        if step_of(f, field) < int(params.uw_from_step) or not settled(f):
            continue
        with h5py.File(f, "r") as h:
            a = np.asarray(h["fields"][field][()])
            m = max(m, float(np.linalg.norm(a.reshape(len(a), -1), axis=1).max()))
    return m


# top panel: the stress-history magnitude, or the speed for a run that carries no stress (Wi = 0)
top_field = str(params.uw_top)
if top_field == "auto":
    top_field = "tau" if run_extreme("tauII") > 0.0 else "speed"
SPEED_MAX = 1.05 * run_extreme("U")
# the mesh is rebuilt exactly as ve_cylinder.py builds it: a refined mesh reloaded from its
# checkpoint comes back with cells joined to the wrong vertices (total area 93 for a 0.89 domain)
centre, radius = (0.2, 0.2), 0.05


def snap_to_circle(dm):
    c = dm.getCoordinatesLocal()
    xy = c.array.reshape(-1, 2) - centre
    r = np.sqrt((xy ** 2).sum(axis=1)).reshape(-1, 1)
    on = uw.cython.petsc_discretisation.petsc_dm_find_labeled_points_local(dm, "inclusion")
    xy[on] *= radius / r[on]
    c.array[...] = (xy + centre).reshape(-1)
    dm.setCoordinatesLocal(c)


refinement = int(params.uw_refinement)
mesh = uw.discretisation.Mesh(os.path.join(HERE, "runs", str(params.uw_mesh_file)), markVertices=True,
                              useMultipleTags=True, useRegions=True, qdegree=3, refinement=refinement,
                              refinement_callback=snap_to_circle if refinement else None)
V = uw.discretisation.MeshVariable("U", mesh, 2, degree=2)
OMEGA = uw.discretisation.MeshVariable("omega", mesh, 1, degree=1)
TAU = uw.discretisation.MeshVariable("tauII", mesh, 1, degree=1)
pvmesh = vis.mesh_to_pv_mesh(mesh)
lo, hi = np.asarray(mesh.X.coords).min(axis=0), np.asarray(mesh.X.coords).max(axis=0)
grey = np.array([0.93, 0.93, 0.92])
DIVERGING = ListedColormap(0.55 * mcm.get_cmap("RdBu_r")(np.linspace(0, 1, 256))[:, :3] + 0.45 * grey)
SEQUENTIAL = ListedColormap(0.7 * mcm.get_cmap("magma_r")(np.linspace(0.0, 0.85, 256))[:, :3] + 0.3 * grey)
gx, gy = np.meshgrid(np.linspace(0.02, 0.6, 5), np.linspace(lo[1] + 0.03, hi[1] - 0.03, 9))
seeds = pv.PolyData(np.c_[gx.ravel(), gy.ravel(), np.zeros(gx.size)])
SIZE = (1650, 360)


def panel(scalars, cmap, clim, title, lines=None, cloud=None):
    pl = pv.Plotter(off_screen=True, window_size=SIZE)
    pl.set_background("white")
    pl.add_mesh(pvmesh.copy(), scalars=scalars, cmap=cmap, clim=clim, show_edges=False,
                lighting=False, show_scalar_bar=False)
    if lines is not None and lines.n_points:
        pl.add_mesh(lines, color="black", line_width=0.7, opacity=0.8, lighting=False)
    if cloud is not None:
        pl.add_mesh(cloud, color="#222222", point_size=2.0, lighting=False)
    pl.add_text(title, font_size=10, color="black")
    pl.view_xy()
    cx, cy = 0.5 * (lo[0] + hi[0]), 0.5 * (lo[1] + hi[1])
    pl.enable_parallel_projection()
    pl.camera.focal_point = (cx, cy, 0.0); pl.camera.position = (cx, cy, 10.0)
    pl.camera.parallel_scale = 0.5 * (hi[1] - lo[1]) * 1.16
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


indices = sorted(step_of(f, "U") for f in glob.glob(os.path.join(cdir, "checkpoint.mesh.U.*.h5"))
                 if all(settled(g) for g in glob.glob(os.path.join(cdir, f"checkpoint.*{step_of(f, 'U'):05d}*"))))
indices = indices[::max(int(params.uw_every), 1)]
dt_line = open(os.path.join(HERE, "runs", run, "forces.csv")).read().splitlines()
times = {int(l.split(",")[0]): float(l.split(",")[1]) for l in dt_line[1:]}
title = str(params.uw_title) or run
s_om, s_tau = float(params.uw_asinh), float(params.uw_tau_asinh)
n_new = 0
for index in indices:
    out = os.path.join(frames, f"frame_{index:05d}.png")
    if os.path.exists(out):
        continue
    if n_new >= int(params.uw_max_frames):
        break
    n_new += 1
    V.read_timestep("checkpoint", "U", index, outputPath=cdir)
    OMEGA.read_timestep("checkpoint", "omega", index, outputPath=cdir)
    TAU.read_timestep("checkpoint", "tauII", index, outputPath=cdir)
    w = np.asarray(OMEGA.data[:, 0]); tau = np.asarray(TAU.data[:, 0])
    pvmesh.point_data["omega"] = np.arcsinh(w / s_om) if s_om > 0 else w
    pvmesh.point_data["tau"] = np.arcsinh(tau / s_tau) if s_tau > 0 else tau
    pvmesh.point_data["V"] = vis.vector_fn_to_pv_points(pvmesh, V.sym)
    om_clim = float(np.arcsinh(OMEGA_MAX / s_om)) if s_om > 0 else OMEGA_MAX
    tau_clim = float(np.arcsinh(TAU_MAX / s_tau)) if s_tau > 0 else TAU_MAX
    speed = max(float(np.linalg.norm(pvmesh.point_data["V"], axis=1).max()), 1e-12)
    lines = pvmesh.streamlines_from_source(seeds, vectors="V", integration_direction="forward",
                                           max_time=6.0 * (hi[0] - lo[0]) / speed, initial_step_length=0.2,
                                           max_step_length=0.5, max_steps=20000)
    cloud = None
    tf = os.path.join(cdir, f"checkpoint.tracers.{index:05d}.h5")
    if os.path.exists(tf):
        arrays = []
        with h5py.File(tf, "r") as h:
            h.visititems(lambda n, o: arrays.append(np.asarray(o[()])) if hasattr(o, "shape") and len(o.shape) == 2 and o.shape[1] in (2, 3) else None)
        if arrays:
            xy = arrays[0][:, :2]
            cloud = pv.PolyData(np.c_[xy, np.zeros(len(xy))])
    t = times.get(index, float("nan"))
    if top_field == "speed":
        pvmesh.point_data["speed"] = np.linalg.norm(pvmesh.point_data["V"], axis=1)
        top = panel("speed", SEQUENTIAL, (0.0, SPEED_MAX),
                    f"{title}   t = {t:.2f}   speed |u| (0 to {SPEED_MAX:.3g}) and streamlines", lines=lines)
    else:
        top = panel("tau", SEQUENTIAL, (0.0, tau_clim),
                    (f"{title}   t = {t:.2f}   stress-history magnitude tau_II (asinh, scale {s_tau:g}, 0 to {TAU_MAX:.3g}) and streamlines" if s_tau > 0 else f"{title}   t = {t:.2f}   stress-history magnitude tau_II (0 to {TAU_MAX:.3g}) and streamlines"), lines=lines)
    bottom = panel("omega", DIVERGING, (-om_clim, om_clim),
                   (f"vorticity (asinh, scale {s_om:g}, to +/-{OMEGA_MAX:.0f}) and tracers" if s_om > 0 else f"vorticity (-{OMEGA_MAX:.0f} to {OMEGA_MAX:.0f}, saturating at the walls) and tracers"), cloud=cloud)
    Image.fromarray(np.vstack([top, bottom])).save(out)
    print("wrote", out, flush=True)
