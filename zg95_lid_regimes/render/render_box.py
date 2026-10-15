"""Render the checkpoints of a box_convection.py run, and its diagnostic history.

Each checkpoint N gives renders/frame_N.png with three panels over the box:
temperature with velocity streamlines, log10 of the effective viscosity, and
eta_eff / eta(T) (white where the viscous branch holds, dark where the lid
yields). renders/history.png plots the per-step diagnostics from records.json.

    python render_box.py -uw_run ~/+Simulations/zg95/box_regimes/runs/<name>            # all, once
    python render_box.py -uw_run <dir> -uw_watch 1      # keep rendering new checkpoints until the run ends

Serial only.
"""
import glob
import json
import os
import re
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

pv.OFF_SCREEN = True

params = uw.Params(
    uw_run="~/+Simulations/zg95/box_regimes/runs/mobile_ref_H1.42",
    uw_watch=0,                 # 1: poll for new checkpoints until the run log says done
)
run = os.path.expanduser(params.uw_run)
renders = os.path.join(run, "renders")
os.makedirs(renders, exist_ok=True)

# The mesh is rebuilt from the run's own parameters rather than read from the
# checkpoint: a refined mesh reloaded from disk has its cells joined to the wrong
# vertices (open roadmap bug), which scrambles anything drawn on the mesh's cells.
# read_timestep remaps by coordinate, so the fields land on the rebuilt mesh.
with open(sorted(glob.glob(os.path.join(run, "state_*.json")))[0]) as f:
    run_params = json.load(f)["params"]
mesh = uw.meshing.UnstructuredSimplexBox(
    minCoords=(0.0, 0.0), maxCoords=(float(run_params["uw_width"]), 1.0),
    cellSize=float(run_params["uw_cell"]), refinement=int(run_params["uw_refinement"]),
    qdegree=3, regular=False)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
V = uw.discretisation.MeshVariable("V", mesh, mesh.dim, degree=2)
log_eta = uw.discretisation.MeshVariable("log10_eta", mesh, 1, degree=1)
yield_ratio = uw.discretisation.MeshVariable("yield_ratio", mesh, 1, degree=1)
x0, x1 = (float(c) for c in (mesh.X.coords[:, 0].min(), mesh.X.coords[:, 0].max()))
width = x1 - x0


def checkpoint_indices():
    files = glob.glob(os.path.join(run, "box.mesh.T.*.h5"))
    return sorted(int(re.search(r"\.T\.(\d+)\.h5", f).group(1)) for f in files)


def field_mesh(var, name):
    """T (P2) on the Delaunay of its own DOFs; the P1 fields on the mesh's own cells,
    evaluated at its vertices (exact for P1), so VTK interpolates within elements."""
    if var.degree > 1:
        pv_mesh = vis.meshVariable_to_pv_mesh_object(var)
        pv_mesh.point_data[name] = np.asarray(var.array[:, 0, 0])
        return pv_mesh
    pv_mesh = vis.mesh_to_pv_mesh(mesh)
    pv_mesh.point_data[name] = np.asarray(
        uw.function.evaluate(var.sym[0], np.ascontiguousarray(pv_mesh.points[:, :2]))).ravel()
    return pv_mesh


def streamlines():
    pv_V = vis.meshVariable_to_pv_mesh_object(V)
    vec = np.zeros((pv_V.n_points, 3))
    vec[:, :2] = np.asarray(V.array[:, 0, :])
    pv_V["V"] = vec
    pv_V.set_active_vectors("V")
    sx, sy = np.meshgrid(np.linspace(x0 + 0.1, x1 - 0.1, int(6 * width)), np.linspace(0.15, 0.85, 4))
    seed = pv.PolyData(np.c_[sx.ravel(), sy.ravel(), np.zeros(sx.size)])
    vmax = float(np.linalg.norm(vec, axis=1).max())
    return pv_V.streamlines_from_source(
        seed, vectors="V", integration_direction="both", max_step_length=0.05,
        initial_step_length=0.01, max_steps=400, terminal_speed=max(vmax * 1e-4, 1e-9)), vmax


def place_camera(pl):
    pl.view_xy()
    pl.camera.parallel_projection = True
    pl.camera.focal_point = (0.5 * (x0 + x1), 0.5, 0.0)
    pl.camera.position = (0.5 * (x0 + x1), 0.5, 10.0)
    pl.camera.parallel_scale = 0.62


def render(index):
    for var in (T, V, log_eta, yield_ratio):
        var.read_timestep("box", var.name, index, outputPath=run)
    with open(os.path.join(run, f"state_{index:05d}.json")) as f:
        state = json.load(f)
    t = state["t"]
    trace = None
    if "trace" in state:
        xy = np.asarray(state["trace"])
        trace = pv.lines_from_points(np.c_[xy, np.full(len(xy), 0.01)])
    strm, vmax = streamlines()
    bar = dict(vertical=True, position_x=0.9, position_y=0.15, height=0.7, width=0.03,
               color="black", title_font_size=14, label_font_size=12)
    pl = pv.Plotter(off_screen=True, shape=(3, 1), window_size=(1800, 1450), border=False)
    pl.set_background("white")

    # Colour ranges always cover the frame's extremes: with internal heating the
    # interior can be hotter than the base, and its viscosity below the basal one.
    pv_T = field_mesh(T, "T")
    pv_eta = field_mesh(log_eta, "log10 eta")
    T_hi = max(1.0, np.ceil(20 * pv_T["T"].max()) / 20)
    eta_lo = min(0.0, np.floor(2 * pv_eta["log10 eta"].min()) / 2)
    eta_hi = max(4.5, np.ceil(2 * pv_eta["log10 eta"].max()) / 2)

    pl.subplot(0, 0)
    pl.add_mesh(pv_T, scalars="T", cmap="RdBu_r", clim=(0.0, T_hi),
                lighting=False, scalar_bar_args=dict(title="T", **bar))
    if strm.n_points > 0:
        pl.add_mesh(strm, color="black", line_width=1.0, lighting=False)
    pl.add_text(f"step {index}, t = {t:.4f}, |v|max {vmax:.0f}", font_size=11, color="black")
    if trace is not None:
        pl.add_mesh(trace, color="#c0392b", line_width=3, lighting=False)
    place_camera(pl)

    pl.subplot(1, 0)
    pl.add_mesh(pv_eta, scalars="log10 eta", cmap="viridis",
                clim=(eta_lo, eta_hi), lighting=False,
                scalar_bar_args=dict(title="log10 eta_eff", **bar))
    if trace is not None:
        pl.add_mesh(trace, color="#c0392b", line_width=3, lighting=False)
    place_camera(pl)

    pl.subplot(2, 0)
    pl.add_mesh(field_mesh(yield_ratio, "eta_eff / eta(T)"), scalars="eta_eff / eta(T)",
                cmap="bone", clim=(0.0, 1.0), lighting=False,
                scalar_bar_args=dict(title="eta_eff / eta(T)", **bar))
    place_camera(pl)

    out = os.path.join(renders, f"frame_{index:05d}.png")
    pl.screenshot(out)
    pl.close()
    return out


def history():
    with open(os.path.join(run, "records.json")) as f:
        rec = json.load(f)
    t = np.array([r["t"] for r in rec])
    panels = [
        ("vrms", ["vrms", "vsurf_rms"]),
        ("mobility", ["mobility"]),
        ("lid depth, T_mid", ["lid_depth", "T_mid"]),
        ("heat flux", ["q_top", "q_base"]),
        ("yielded fraction", ["yield_frac", "yield_frac_lid"]),
        ("Newton iterations", ["newton"]),
    ]
    fig, axes = plt.subplots(len(panels), 1, figsize=(10, 2.0 * len(panels)), sharex=True)
    for ax, (title, keys) in zip(axes, panels):
        for key in keys:
            ax.plot(t, [r[key] for r in rec], lw=0.8, label=key)
        ax.set_ylabel(title, fontsize=9)
        ax.grid(alpha=0.3)
        if len(keys) > 1:
            ax.legend(fontsize=8, loc="upper right")
    axes[-1].set_xlabel("t (diffusion times on the layer depth)")
    fig.suptitle(os.path.basename(run), fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(renders, "history.png"), dpi=120)
    plt.close(fig)


def run_finished():
    log = os.path.join(run, "run.log")
    if not os.path.exists(log):
        return False
    with open(log) as f:
        return "done" in f.read()[-200:]


done = set()
while True:
    finished = run_finished()
    for index in checkpoint_indices():
        frame = os.path.join(renders, f"frame_{index:05d}.png")
        if os.path.exists(frame):
            done.add(index)
        if index not in done and os.path.exists(os.path.join(run, f"state_{index:05d}.json")):
            print("->", render(index), flush=True)
            done.add(index)
    history()
    if not params.uw_watch or finished:
        break
    time.sleep(30)
