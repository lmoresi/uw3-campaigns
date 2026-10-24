"""Render the checkpoints of an annulus_convection.py run, and its diagnostic history.
The counterpart of ``render_box.py``.

Each checkpoint N gives renders/frame_N.png with panels over the annulus. The
"viscosity" panels: temperature with velocity streamlines, log10 of the effective
viscosity, eta_eff / eta(T) (white where the viscous branch holds, dark where the lid
yields) and, for a strain-weakening run, the plastic strain. The "strain" panels
(``-uw_panels strain``): temperature with streamlines, log10 of the strain-rate
invariant (projected from the checkpoint's velocity, so a fault shows as the band of
high strain rate across the cells its slip is smeared over), log10 of the plastic
strain rate (the part the damage records) and the plastic strain (the damage). The
fault traces are drawn on every panel. renders/history.png plots the per-step
diagnostics from records.json.

    python render_annulus.py -uw_run ~/+Simulations/zg95/annulus_regimes/runs/<name>    # all, once
    python render_annulus.py -uw_run <dir> -uw_watch 1  # keep rendering new checkpoints until the run ends

Serial only.
"""
import glob
import json
import os
import re
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

pv.OFF_SCREEN = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
from annulus_model import annulus_mesh, annulus_radii

params = uw.Params(
    uw_run="~/+Simulations/zg95/annulus_regimes/runs/tau1x1.00",
    uw_watch=0,                 # 1: poll for new checkpoints until the run log says done
    uw_last=0,                  # 1: render only the latest checkpoint
    uw_zoom=0.0,                # > 0: a window of this half-height on the trench (renders/zoom_N.png)
    uw_panels="viscosity",      # "viscosity" or "strain" (see above)
    uw_zoom_theta=1.0e9,        # degrees: centre the zoom here instead of on the first fault (positive: 187 for -173)
    uw_renders="",              # output directory under the run (default renders, or renders_strain)
)
run = os.path.expanduser(params.uw_run)
renders = os.path.join(run, params.uw_renders or ("renders_strain" if params.uw_panels == "strain" else "renders"))
os.makedirs(renders, exist_ok=True)

# The mesh is rebuilt from the run's own parameters rather than read from the
# checkpoint: a refined mesh reloaded from disk has its cells joined to the wrong
# vertices (open roadmap bug), which scrambles anything drawn on the mesh's cells.
# read_timestep remaps by coordinate, so the fields land on the rebuilt mesh.
while params.uw_watch and not glob.glob(os.path.join(run, "state_*.json")):
    time.sleep(30)              # a watcher started with the run waits for its first checkpoint
with open(sorted(glob.glob(os.path.join(run, "state_*.json")))[0]) as f:
    run_params = json.load(f)["params"]
mesh = annulus_mesh(float(run_params["uw_cell"]), int(run_params["uw_refinement"]))
r_o, r_i = annulus_radii()
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
V = uw.discretisation.MeshVariable("V", mesh, mesh.dim, degree=2)
log_eta = uw.discretisation.MeshVariable("log10_eta", mesh, 1, degree=1)
yield_ratio = uw.discretisation.MeshVariable("yield_ratio", mesh, 1, degree=1)
plastic_strain = uw.discretisation.MeshVariable("plastic_strain", mesh, 1, degree=2)
edot_plastic = uw.discretisation.MeshVariable("edot_plastic", mesh, 1, degree=1)
if params.uw_panels == "strain":
    import sympy
    _E = (V.sym.jacobian(mesh.X) + V.sym.jacobian(mesh.X).T) / 2
    # the invariant evaluated at the mesh vertices (one cell's derivative per vertex):
    # an L2 projection rings on either side of the fault band and its undershoots
    # read as holes in the log scale
    edot_total_sym = sympy.sqrt((_E[0, 0] ** 2 + _E[1, 1] ** 2 + 2 * _E[0, 1] ** 2) / 2)


def checkpoint_indices():
    files = glob.glob(os.path.join(run, "annulus.mesh.T.*.h5"))
    return sorted(int(re.search(r"\.T\.(\d+)\.h5", f).group(1)) for f in files)


marker_vars = {name: uw.discretisation.MeshVariable(name, mesh, 1, degree=1) for name in ("crust", "slab", "over")}
MARKER_COLOURS = {"crust": ("#1e8449", "white"), "slab": ("#d35400", "#f5b041"), "over": ("#6c3483", "#bb8fce")}


def marker_outlines(index):
    """The particle-carried layers of the checkpoint (the weak crust, the compositional
    slab) as (name, 0.5 contour) pairs; empty when the checkpoint has none."""
    lines = []
    for name, var in marker_vars.items():
        if not os.path.exists(os.path.join(run, f"annulus.mesh.{name}.{index:05d}.h5")):
            continue
        var.read_timestep("annulus", name, index, outputPath=run)
        line = field_mesh(var, name).contour([0.5], scalars=name)
        if line.n_points:
            line.points[:, 2] = 0.02
            lines.append((name, line))
    return lines


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
    # seeds on four circles through the layer, about six per layer depth around each
    radius = r_o - np.array([0.15, 0.38, 0.62, 0.85])
    seeds = [(rr * np.cos(th), rr * np.sin(th)) for rr in radius
             for th in np.linspace(0.0, 2 * np.pi, int(6 * 2 * np.pi * rr), endpoint=False)]
    seed = pv.PolyData(np.c_[np.asarray(seeds), np.zeros(len(seeds))])
    vmax = float(np.linalg.norm(vec, axis=1).max())
    return pv_V.streamlines_from_source(
        seed, vectors="V", integration_direction="both", max_step_length=0.05,
        initial_step_length=0.01, max_steps=400, terminal_speed=max(vmax * 1e-4, 1e-9)), vmax


def place_camera(pl, theta_trench=None):
    """The whole annulus, or with ``uw_zoom`` a window on the trench, centred on the
    layer's mid-depth below it."""
    pl.view_xy()
    pl.camera.parallel_projection = True
    if params.uw_zoom_theta < 1.0e8:
        theta_trench = np.deg2rad(params.uw_zoom_theta)
    if params.uw_zoom > 0 and theta_trench is not None:
        # centred 0.4 below the trench, a little low so the colour bar sits under the layer
        r_c = r_o - 0.4
        cx, cy = r_c * np.cos(theta_trench), r_c * np.sin(theta_trench)
        cy -= 0.15 * params.uw_zoom
        pl.camera.focal_point = (cx, cy, 0.0)
        pl.camera.position = (cx, cy, 10.0)
        pl.camera.parallel_scale = params.uw_zoom
        return
    # the view sits low so the colour bar fits under the annulus
    pl.camera.focal_point = (0.0, -0.1 * r_o, 0.0)
    pl.camera.position = (0.0, -0.1 * r_o, 10.0)
    pl.camera.parallel_scale = 1.18 * r_o


def render_strain(index, state, trace, strm, vmax, bar, outline=()):
    """The strain panels: T with streamlines, log10 strain rate, log10 plastic strain
    rate, plastic strain; the faults on every panel, the crust's outline on the first two."""
    t = state["t"]
    pl = pv.Plotter(off_screen=True, shape=(1, 4), window_size=(3200, 860), border=False)
    pl.set_background("white")
    pv_T = field_mesh(T, "T")
    T_hi = max(1.0, np.ceil(20 * pv_T["T"].max()) / 20)
    # the invariant per cell, at the centroid (the gradient of P2 is linear in the cell,
    # so this is the cell mean); evaluating a derivative exactly at a vertex returned a
    # near-zero value on about 1% of the lid's vertices (an evaluate artefact at points
    # on a vertex), which read as dark hexagons
    pv_e = vis.mesh_to_pv_mesh(mesh)
    centres = np.ascontiguousarray(pv_e.cell_centers().points[:, :2])
    pv_e.cell_data["log10 strain rate"] = np.log10(np.maximum(np.asarray(uw.function.evaluate(
        edot_total_sym, centres)).ravel(), 1e-2))
    pv_ep = field_mesh(edot_plastic, "log10 plastic strain rate")
    pv_ep["log10 plastic strain rate"] = np.log10(np.maximum(pv_ep["log10 plastic strain rate"], 1e-2))
    # two and a half decades under the frame's maximum: the fault bands (1e3) against
    # the yielding lid (1e2) and the plate interiors (below 1e1, dark)
    e_hi = max(3.0, np.ceil(2 * np.percentile(pv_e.cell_data["log10 strain rate"], 99.9)) / 2)
    e_lo = e_hi - 2.5
    pv_g = field_mesh(plastic_strain, "plastic strain")
    g_hi = max(1.0, np.ceil(2 * pv_g["plastic strain"].max()) / 2)
    fault_colour = ("#c0392b", "white", "white", "#2471a3")
    fault_width = (3, 1, 1, 3)     # thin on the strain-rate panels: a 3 px line hides the one-cell band
    fields = [(pv_T, "T", "RdBu_r", (0.0, T_hi)),
              (pv_e, "log10 strain rate", "viridis", (e_lo, e_hi)),
              (pv_ep, "log10 plastic strain rate", "viridis", (e_lo, e_hi)),
              (pv_g, "plastic strain", "magma_r", (0.0, g_hi))]
    for n, (pv_mesh, name, cmap, clim) in enumerate(fields):
        pl.subplot(0, n)
        pl.add_mesh(pv_mesh, scalars=name, cmap=cmap, clim=clim, lighting=False,
                    scalar_bar_args=dict(title=name, **bar))
        if n == 0:
            if strm.n_points > 0:
                pl.add_mesh(strm, color="black", line_width=1.0, lighting=False)
            pl.add_text(f"step {index}, t = {t:.4f}, |v|max {vmax:.0f}", font_size=11, color="black")
        if trace is not None:
            pl.add_mesh(trace, color=fault_colour[n], line_width=fault_width[n], lighting=False)
        if n < 2:
            for name, line in outline:
                pl.add_mesh(line, color=MARKER_COLOURS[name][n], line_width=(1.5, 1.0)[n], lighting=False)
        place_camera(pl, state.get("theta_trench"))
    for bar_actor in pl.scalar_bars.values():
        bar_actor.SetTextPositionToPrecedeScalarBar()
    prefix = "zoom" if params.uw_zoom > 0 else "frame"
    out = os.path.join(renders, f"{prefix}_{index:05d}.png")
    pl.screenshot(out)
    pl.close()
    return out


def render(index):
    # a strain-weakening run also carries the accumulated plastic strain: a fourth panel
    has_strain = os.path.exists(os.path.join(run, f"annulus.mesh.plastic_strain.{index:05d}.h5"))
    if params.uw_panels == "strain" and not has_strain:
        raise RuntimeError("the strain panels need a strain-weakening run (plastic_strain in the checkpoint)")
    for var in (T, V, log_eta, yield_ratio) + ((plastic_strain,) if has_strain else ()):
        var.read_timestep("annulus", var.name, index, outputPath=run)
    if params.uw_panels == "strain":
        edot_plastic.read_timestep("annulus", "edot_plastic", index, outputPath=run)
    with open(os.path.join(run, f"state_{index:05d}.json")) as f:
        state = json.load(f)
    t = state["t"]
    # every fault of the frame (a multi-fault state lists them all under "traces")
    trace = None
    lines = state.get("traces") or ([state["trace"]] if "trace" in state else [])
    for xy in (np.asarray(x) for x in lines):
        piece = pv.lines_from_points(np.c_[xy, np.full(len(xy), 0.01)])
        trace = piece if trace is None else trace.merge(piece)
    strm, vmax = streamlines()
    bar = dict(vertical=False, position_x=0.2, position_y=0.04, height=0.05, width=0.6,
               color="black", title_font_size=14, label_font_size=12)
    outline = marker_outlines(index)
    if params.uw_panels == "strain":
        return render_strain(index, state, trace, strm, vmax, bar, outline)
    panels = 4 if has_strain else 3
    pl = pv.Plotter(off_screen=True, shape=(1, panels), window_size=(800 * panels, 860), border=False)
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
    for name, line in outline:
        pl.add_mesh(line, color=MARKER_COLOURS[name][0], line_width=1.5, lighting=False)
    place_camera(pl, state.get("theta_trench"))

    pl.subplot(0, 1)
    pl.add_mesh(pv_eta, scalars="log10 eta", cmap="viridis",
                clim=(eta_lo, eta_hi), lighting=False,
                scalar_bar_args=dict(title="log10 eta_eff", **bar))
    if trace is not None:
        pl.add_mesh(trace, color="#c0392b", line_width=3, lighting=False)
    for name, line in outline:
        pl.add_mesh(line, color=MARKER_COLOURS[name][1], line_width=1.0, lighting=False)
    place_camera(pl, state.get("theta_trench"))

    pl.subplot(0, 2)
    pl.add_mesh(field_mesh(yield_ratio, "eta_eff / eta(T)"), scalars="eta_eff / eta(T)",
                cmap="bone", clim=(0.0, 1.0), lighting=False,
                scalar_bar_args=dict(title="eta_eff / eta(T)", **bar))
    place_camera(pl, state.get("theta_trench"))

    if has_strain:
        pv_g = field_mesh(plastic_strain, "plastic strain")
        g_hi = max(1.0, np.ceil(2 * pv_g["plastic strain"].max()) / 2)
        pl.subplot(0, 3)
        pl.add_mesh(pv_g, scalars="plastic strain", cmap="magma_r", clim=(0.0, g_hi),
                    lighting=False, scalar_bar_args=dict(title="plastic strain", **bar))
        if trace is not None:
            pl.add_mesh(trace, color="#2471a3", line_width=3, lighting=False)
        place_camera(pl, state.get("theta_trench"))

    # horizontal bars: labels under the bar, so they clear the title above it
    for bar_actor in pl.scalar_bars.values():
        bar_actor.SetTextPositionToPrecedeScalarBar()

    prefix = "zoom" if params.uw_zoom > 0 else "frame"
    out = os.path.join(renders, f"{prefix}_{index:05d}.png")
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
    indices = checkpoint_indices()
    for index in (indices[-1:] if params.uw_last else indices):
        frame = os.path.join(renders, f"{'zoom' if params.uw_zoom > 0 else 'frame'}_{index:05d}.png")
        if os.path.exists(frame):
            done.add(index)
        if index not in done and os.path.exists(os.path.join(run, f"state_{index:05d}.json")):
            print("->", render(index), flush=True)
            done.add(index)
    history()
    if not params.uw_watch or finished:
        break
    time.sleep(30)
