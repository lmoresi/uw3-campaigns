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

The "solver" panels (``-uw_panels solver``, renders_solver/frame_N.png) show how the
solver behaves while the faults move: the mesh with the fault traces of this checkpoint
and of the one before it (a rebuild shows as the old trace beside the new), the strain
rate and the plastic strain on the same window, and under them a strip of the nonlinear
iterations per step over the last uw_window steps with the rebuilds, the faults formed
and retired and the cold starts marked. The strip reads the per-step "solver" sub-record
of records.json when the run has one and the older "newton" / "n_built" / "events" fields
otherwise. With ``-uw_band 1`` a checkpoint after which a fault moved, formed or was
retired also gets renders_solver/band_N.png: the strain rate before and after on a
window of half-height uw_band_zoom around that fault, each with its own trace, and the
velocity jump across the fault against depth for both (sampled uw_band_offset cells to
either side of the trace). The solver's split mesh is not checkpointed, so the mesh
drawn is the base mesh the fields live on.

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
from annulus_model import annulus_mesh, annulus_radii, clamp_radii

params = uw.Params(
    uw_run="~/+Simulations/zg95/annulus_regimes/runs/tau1x1.00",
    uw_watch=0,                 # 1: poll for new checkpoints until the run log says done
    uw_last=0,                  # 1: render only the latest checkpoint
    uw_zoom=0.0,                # > 0: a window of this half-height on the trench (renders/zoom_N.png)
    uw_panels="viscosity",      # "viscosity" or "strain" (see above)
    uw_zoom_theta=1.0e9,        # degrees: centre the zoom here instead of on the first fault (positive: 187 for -173)
    uw_renders="",              # output directory under the run (default renders, or renders_strain)
    uw_band=0,                  # solver panels: 1 adds the band view of a fault that just moved
    uw_band_zoom=0.2,           # half-height of the band view's window (layer depths)
    uw_band_offset=2.0,         # cells to either side of the trace where the velocity jump is sampled
    uw_window=150,              # steps of iteration history in the solver strip
    uw_solver_mesh="annulus.solver_mesh",   # the checkpointed solver mesh's file prefix (kaiju's driver)
)
if params.uw_panels == "solver" and params.uw_zoom <= 0:
    params.uw_zoom = 0.5        # the solver panels are a window on the trench
run = os.path.expanduser(params.uw_run)
renders = os.path.join(run, params.uw_renders or {"strain": "renders_strain", "solver": "renders_solver"}.get(
    params.uw_panels, "renders"))
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
if params.uw_panels in ("strain", "solver"):
    import sympy

    def strain_rate_sym(vel):
        E = (vel.sym.jacobian(mesh.X) + vel.sym.jacobian(mesh.X).T) / 2
        return sympy.sqrt((E[0, 0] ** 2 + E[1, 1] ** 2 + 2 * E[0, 1] ** 2) / 2)
    # the invariant evaluated at the mesh vertices (one cell's derivative per vertex):
    # an L2 projection rings on either side of the fault band and its undershoots
    # read as holes in the log scale
    edot_total_sym = strain_rate_sym(V)
if params.uw_panels == "solver":
    V_prev = uw.discretisation.MeshVariable("V_prev", mesh, mesh.dim, degree=2)   # the checkpoint before
    edot_prev_sym = strain_rate_sym(V_prev)
    cell_size = float(run_params["uw_cell"]) / 2 ** int(run_params["uw_refinement"])

# The house style of drawn figures (the uw-line-diagrams skill): its roles when the
# module is on the path, the same tokens otherwise, so a frame reads as one of the
# repository's figures.
try:
    import uwfig as F
    INK, MESH_GREY, VELOCITY, FORCE, ENERGY = F.INK, F.MESH, F.VELOCITY, F.FORCE, F.ENERGY
except ImportError:
    INK, MESH_GREY, VELOCITY, FORCE, ENERGY = "#1f2a33", "#9aa3aa", "#1b6f6a", "#a1522a", "#6b3d8f"
matplotlib.rcParams.update({"font.family": "sans-serif", "font.size": 8, "axes.linewidth": 0.6,
                            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]})


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


def trace_lines(state, z=0.01):
    """The fault traces of a state as one PolyData (None without faults), and the list of
    (name, xy) pairs in the state's own order."""
    lines = state.get("traces") or ([state["trace"]] if "trace" in state else [])
    names = [f["name"] for f in state.get("faults", [])]
    pairs = [(names[k] if k < len(names) else f"F{k}", np.asarray(xy)) for k, xy in enumerate(lines)]
    trace = None
    for _, xy in pairs:
        piece = pv.lines_from_points(np.c_[xy, np.full(len(xy), z)])
        trace = piece if trace is None else trace.merge(piece)
    return trace, pairs


def solver_info(r, previous):
    """One step's solver record, from the per-step "solver" sub-record (kaiju's driver:
    kind in ordinary / rebuild_same_set / rebuild_changed_set / restart_first /
    init_first, start warm or cold, cold_retry, nonlinear_its, picard_its, newton_its,
    converged, F0 and F_ref, ksp_its / vel_its / pres_its per increment, wall times,
    faults_before / faults_after, pc_fallbacks) or from the older fields (newton,
    n_built, events, vel_its) when the run has none. Returned: kind as the sub-record's
    (rebuild when n_built rose, else step), rebuild (bool), warm (True / False / None),
    nl_its, ksp_its (the sum over the increments), quality (F0 / F_ref or None), events
    (formed / retired names from the fault lists or the events text), converged."""
    sub = r.get("solver") or {}
    if sub:
        kind = sub.get("kind", "ordinary")
        before, after = sub.get("faults_before"), sub.get("faults_after")
        events = list(r.get("events") or [])
        if before is not None and after is not None and not events:
            events = [f"formed {n}" for n in after if n not in before] + [f"retired {n}" for n in before if n not in after]
        # the velocity block's iterations (the outer fieldsplit KSP takes one per Newton step)
        ksp = sub.get("vel_its") if sub.get("vel_its") is not None else sub.get("ksp_its")
        f0, f_ref = sub.get("F0"), sub.get("F_ref")
        return {"step": r["step"], "kind": kind, "rebuild": kind.startswith("rebuild"),
                "warm": {"warm": True, "cold": False}.get(sub.get("start")),
                "cold_retry": bool(sub.get("cold_retry")),
                "nl_its": sub.get("nonlinear_its", r.get("newton")),
                "picard_its": sub.get("picard_its"), "newton_its": sub.get("newton_its"),
                "ksp_its": int(np.sum(ksp)) if isinstance(ksp, (list, tuple)) else ksp,
                "quality": (f0 / f_ref) if f0 is not None and f_ref else None,
                "wall": sub.get("wall") or {}, "pc_fallbacks": sub.get("pc_fallbacks") or [],
                "events": events, "converged": bool(sub.get("converged", r.get("converged", True))),
                "raw": sub}     # the rest of the sub-record (F_history, ksp_summary, mesh, ...) for later panels
    rebuilt = previous is not None and r.get("n_built", 0) > previous.get("n_built", 0)
    vel = r.get("vel_its") or []
    return {"step": r["step"], "kind": "rebuild" if rebuilt else "step", "rebuild": rebuilt, "warm": None,
            "cold_retry": False, "nl_its": r.get("newton"), "picard_its": None, "newton_its": None,
            "ksp_its": int(np.sum(vel)) if vel else None, "quality": None, "wall": {}, "pc_fallbacks": [],
            "events": list(r.get("events") or []), "converged": bool(r.get("converged", True)), "raw": {}}


def iteration_strip(index, width_px, height_px=320, dpi=150):
    """The nonlinear iterations per step up to this checkpoint (last uw_window steps),
    rebuilds as rust ticks, faults formed (up) and retired (down) as markers, cold
    starts and failed solves marked; a PIL image width_px wide."""
    from PIL import Image
    path = os.path.join(run, "records.json")
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            rec = [r for r in json.load(f) if r["step"] <= index]
        rec = rec[-int(params.uw_window):]
        rows = [solver_info(r, rec[k - 1] if k else None) for k, r in enumerate(rec)]
    fig, ax = plt.subplots(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
    fig.subplots_adjust(left=0.05, right=0.99, bottom=0.22, top=0.8)
    if rows:
        steps = np.array([r["step"] for r in rows])
        its = np.array([np.nan if r["nl_its"] is None else r["nl_its"] for r in rows], float)
        ax.plot(steps, its, "-", lw=0.8, color=INK, label="nonlinear iterations")
        ax.plot(steps, its, "o", ms=2.2, color=INK)
        top = np.nanmax(its) if np.isfinite(its).any() else 1.0
        for r in rows:
            if r["rebuild"]:        # a changed fault set is the heavier rebuild: full line; same set dashed
                ax.axvline(r["step"], color=FORCE, lw=0.8, alpha=0.9,
                           ls=(0, (3, 2)) if r["kind"] == "rebuild_same_set" else "-")
        cold = [r["step"] for r in rows if r["warm"] is False or r["cold_retry"]]
        if cold:
            ax.plot(cold, its[np.isin(steps, cold)], "s", ms=4, mfc="none", mec=ENERGY, label="cold start")
        fallback = [r["step"] for r in rows if r["pc_fallbacks"]]
        if fallback:
            ax.plot(fallback, its[np.isin(steps, fallback)], "D", ms=4, mfc="none", mec=FORCE, label="PC fallback")
        failed = [r["step"] for r in rows if not r["converged"]]
        if failed:
            ax.plot(failed, its[np.isin(steps, failed)], "x", ms=5, color=FORCE, label="not converged")
        for r in rows:
            for e in r["events"]:
                formed = e.startswith("formed")
                name = e.split()[1] if len(e.split()) > 1 else ""
                ax.plot([r["step"]], [top * 1.08], "^" if formed else "v", ms=5, color=VELOCITY, clip_on=False)
                ax.annotate(name, (r["step"], top * 1.08), xytext=(0, 5), textcoords="offset points",
                            ha="center", fontsize=6, color=VELOCITY, annotation_clip=False)
        ax.set_ylim(0, top * 1.15)
        ax.set_xlim(steps[0], max(steps[-1], steps[0] + 1))
        handles, labels = ax.get_legend_handles_labels()
        ksp = np.array([np.nan if r["ksp_its"] is None else r["ksp_its"] for r in rows], float)
        if np.isfinite(ksp).any():          # the linear (velocity) iterations, summed over the step
            ax2 = ax.twinx()
            ax2.plot(steps, ksp, "-", lw=0.8, color=VELOCITY)
            ax2.set_ylim(0, np.nanmax(ksp) * 1.15)
            ax2.set_ylabel("linear iterations", fontsize=7, color=VELOCITY)
            ax2.tick_params(labelsize=6, colors=VELOCITY)
            ax2.spines["top"].set_visible(False)
            handles.append(plt.Line2D([], [], color=VELOCITY, lw=0.8)); labels.append("linear (velocity) iterations")
        handles.append(plt.Line2D([], [], color=FORCE, lw=0.8)); labels.append("rebuild")
        handles.append(plt.Line2D([], [], marker="^", ls="", color=VELOCITY, ms=5)); labels.append("fault formed / retired")
        ax.legend(handles, labels, fontsize=6, loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=4,
                  frameon=False, borderaxespad=0.0)
    ax.set_xlabel("step", fontsize=7)
    ax.set_ylabel("iterations", fontsize=7)
    ax.tick_params(labelsize=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    plt.close(fig)
    return img.resize((width_px, round(img.height * width_px / img.width)))


def previous_checkpoint(index):
    before = [k for k in checkpoint_indices() if k < index]
    return before[-1] if before else None


def trace_frame(xy):
    """Unit tangent and left normal along a polyline."""
    xy = np.asarray(xy, float)
    tangent = np.gradient(xy, axis=0)
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1), 1e-12)[:, None]
    return xy, tangent, np.c_[-tangent[:, 1], tangent[:, 0]]


def solver_velocity_jump(xy, index):
    """The solver's own velocity jump across a fault trace, read from the split-mesh
    checkpoint <uw_solver_mesh>.V.NNNNN.h5 (kaiju's driver): its DOF coordinates are
    nudged onto their own side of the fault, so the nearest DOF on each side within a cell
    of a trace point gives the discontinuous V there. None when the file is absent or
    unreadable; NaN where a side has no DOF within reach."""
    path = os.path.join(run, f"{params.uw_solver_mesh}.V.{index:05d}.h5")
    if not os.path.exists(path):
        return None
    try:
        import h5py
        from scipy.spatial import cKDTree
        with h5py.File(path, "r") as f:
            coords = np.asarray(f["coords"])[:, :2]
            values = np.asarray(f["values"]).reshape(len(coords), -1)[:, :2]
    except Exception as e:           # noqa: BLE001 - fall back to the base-mesh field
        print(f"   solver velocity {os.path.basename(path)} not read: {e}", flush=True)
        return None
    xy, tangent, normal = trace_frame(xy)
    tree = cKDTree(coords)
    reach = 1.5 * cell_size
    jump = np.full(len(xy), np.nan)
    for i, (p, t, n) in enumerate(zip(xy, tangent, normal)):
        near = tree.query_ball_point(p, reach)
        if not near:
            continue
        near = np.asarray(near)
        side = (coords[near] - p) @ n
        along = np.abs((coords[near] - p) @ t)
        # the DOF nearest the fault LINE on each side (the nudged on-fault DOFs of a split
        # mesh), among those within half a cell along the trace of this point
        on_line = along <= 0.5 * cell_size
        plus, minus = near[on_line & (side > 0)], near[on_line & (side <= 0)]
        if len(plus) == 0 or len(minus) == 0:
            continue
        a = plus[np.argmin(side[on_line & (side > 0)])]
        b = minus[np.argmax(side[on_line & (side <= 0)])]
        jump[i] = (values[a] - values[b]) @ t
    depth = r_o - np.hypot(xy[:, 0], xy[:, 1])
    return depth, jump


def velocity_jump(xy, vel, index=None):
    """The tangential velocity jump across a fault trace ``xy`` (surface end first)
    against depth, with the source it came from: the solver's split-mesh V when checkpoint
    ``index`` carries it, else the field ``vel`` sampled uw_band_offset cells to either side."""
    if index is not None:
        got = solver_velocity_jump(xy, index)
        if got is not None:
            return got[0], got[1], "solver mesh"
    xy, tangent, normal = trace_frame(xy)
    off = params.uw_band_offset * cell_size
    inset = 1.5 * cell_size
    plus = clamp_radii(xy + off * normal, r_o, r_i, inset)
    minus = clamp_radii(xy - off * normal, r_o, r_i, inset)
    v_plus = np.asarray(uw.function.evaluate(vel.sym, np.ascontiguousarray(plus))).reshape(-1, 2)
    v_minus = np.asarray(uw.function.evaluate(vel.sym, np.ascontiguousarray(minus))).reshape(-1, 2)
    jump = np.einsum("ij,ij->i", v_plus - v_minus, tangent)
    depth = r_o - np.hypot(xy[:, 0], xy[:, 1])
    return depth, jump, f"base mesh, {params.uw_band_offset:g} cells either side"


def moved_faults(state, prev_state):
    """The faults that moved between two checkpoints: formed since, or with a trench or
    dip change beyond the rebuild thresholds; with the retired ones (in the old state only)."""
    old = {f["name"]: f for f in prev_state.get("faults", [])}
    new = {f["name"]: f for f in state.get("faults", [])}
    moved, retired = [], [n for n in old if n not in new]
    for name, f in new.items():
        g = old.get(name)
        if g is None:
            moved.append(name)
        elif "points" in f and "points" in g:      # a crust-following fault: its polyline moved
            a, b = np.asarray(f["points"], float), np.asarray(g["points"], float)
            from scipy.spatial import cKDTree
            gap = max(cKDTree(b).query(a)[0].max(), cKDTree(a).query(b)[0].max())
            if gap > 0.5 * cell_size:
                moved.append(name)
        elif (abs(wrap_angle(f["theta"] - g["theta"])) * r_o > 0.5 * cell_size
              or abs(f["dip"] - g["dip"]) > 1.0):
            moved.append(name)
    return moved, retired


def wrap_angle(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def render_band(index, prev, state, prev_state, bar):
    """Before/after a fault moved: the strain rate on a window around the fault at the
    previous checkpoint (its old trace) and at this one (its new trace), and the velocity
    jump across the fault against depth for both."""
    from PIL import Image
    moved, retired = moved_faults(state, prev_state)
    if not moved and not retired:
        return None
    name = (moved or retired)[0]
    _, pairs_new = trace_lines(state, z=0.02)
    _, pairs_old = trace_lines(prev_state, z=0.02)
    xy_new = dict(pairs_new).get(name)
    xy_old = dict(pairs_old).get(name)
    centre_xy = xy_new if xy_new is not None else xy_old
    cx, cy = centre_xy.mean(axis=0)
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 860), border=False)
    pl.set_background("white")
    panels = [("before", prev, V_prev, edot_prev_sym, prev_state), ("after", index, V, edot_total_sym, state)]
    pv_e = {}
    for n, (label, k, vel, sym, st) in enumerate(panels):
        pv_mesh = vis.mesh_to_pv_mesh(mesh)
        centres = np.ascontiguousarray(pv_mesh.cell_centers().points[:, :2])
        pv_mesh.cell_data["log10 strain rate"] = np.log10(np.maximum(np.asarray(
            uw.function.evaluate(sym, centres)).ravel(), 1e-2))
        pv_e[label] = pv_mesh
    e_hi = max(3.0, np.ceil(2 * max(np.percentile(m.cell_data["log10 strain rate"], 99.9) for m in pv_e.values())) / 2)
    edges = vis.mesh_to_pv_mesh(mesh).extract_all_edges()
    for n, (label, k, vel, sym, st) in enumerate(panels):
        pl.subplot(0, n)
        pl.add_mesh(pv_e[label], scalars="log10 strain rate", cmap="viridis", clim=(e_hi - 2.5, e_hi),
                    lighting=False, scalar_bar_args=dict(title="log10 strain rate", **bar))
        pl.add_mesh(edges, color=MESH_GREY, line_width=0.4, lighting=False, opacity=0.6)
        trace, _ = trace_lines(st, z=0.02)
        if trace is not None:
            pl.add_mesh(trace, color="white", line_width=2.0, lighting=False)
        other = xy_old if label == "after" else xy_new
        if other is not None:        # the other state's position of this fault, for the eye
            ghost = pv.lines_from_points(np.c_[other, np.full(len(other), 0.03)])
            pl.add_mesh(ghost, color=FORCE, line_width=1.5, lighting=False)
        pl.add_text(f"{label}: step {k}, t = {st['t']:.4f}", font_size=11, color="black")
        pl.view_xy()
        pl.camera.parallel_projection = True
        pl.camera.focal_point = (cx, cy, 0.0)
        pl.camera.position = (cx, cy, 10.0)
        pl.camera.parallel_scale = params.uw_band_zoom
    for bar_actor in pl.scalar_bars.values():
        bar_actor.SetTextPositionToPrecedeScalarBar()
    shot = Image.fromarray(np.asarray(pl.screenshot(return_img=True)))
    pl.close()
    # the jump across the fault: before on the old trace, after on the new one
    dpi = 150
    fig, ax = plt.subplots(figsize=(800 / dpi, 860 / dpi), dpi=dpi)
    fig.subplots_adjust(left=0.2, right=0.95, bottom=0.12, top=0.9)
    sources = set()
    for label, xy, vel, k, ls in (("before", xy_old, V_prev, prev, (0, (4, 2))), ("after", xy_new, V, index, "-")):
        if xy is None:
            continue
        depth, jump, source = velocity_jump(xy, vel, k)
        sources.add(source)
        ax.plot(jump, depth, ls=ls, lw=1.0, color=VELOCITY, label=f"{label} ({name})")
    ax.invert_yaxis()
    ax.axvline(0, color=INK, lw=0.5)
    ax.set_xlabel(f"tangential velocity jump across the fault ({'; '.join(sorted(sources))})", fontsize=7)
    ax.set_ylabel("depth", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=6, frameon=False, loc="lower right")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.canvas.draw()
    plot = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    plt.close(fig)
    plot = plot.resize((round(plot.width * shot.height / plot.height), shot.height))
    canvas = Image.new("RGB", (shot.width + plot.width, shot.height), "white")
    canvas.paste(shot, (0, 0))
    canvas.paste(plot, (shot.width, 0))
    out = os.path.join(renders, f"band_{index:05d}.png")
    canvas.save(out)
    return out


def solver_mesh_edges(index):
    """The edges of the solver's own (split, placed-ladder) mesh when the checkpoint
    carries it (<uw_solver_mesh>.NNNNN.h5), else the base mesh's. A mesh reloaded from
    disk can come back with its cells joined to the wrong vertices (open roadmap bug):
    the fallback is taken when the reload fails or returns no cells."""
    path = os.path.join(run, f"{params.uw_solver_mesh}.{index:05d}.h5")
    if os.path.exists(path):
        try:
            solver_mesh = uw.discretisation.Mesh(path)
            edges = vis.mesh_to_pv_mesh(solver_mesh).extract_all_edges()
            if edges.n_points:
                return edges, True
        except Exception as e:           # noqa: BLE001 - any failure falls back to the base mesh
            print(f"   solver mesh {os.path.basename(path)} not drawn: {e}", flush=True)
    return vis.mesh_to_pv_mesh(mesh).extract_all_edges(), False


def render_solver(index, state, strm, vmax, bar):
    """The solver panels: the mesh with the old and new fault traces, the strain rate
    and the plastic strain on the trench window, the iteration strip underneath."""
    from PIL import Image
    prev = previous_checkpoint(index)
    prev_state = None
    if prev is not None:
        with open(os.path.join(run, f"state_{prev:05d}.json")) as f:
            prev_state = json.load(f)
        V_prev.read_timestep("annulus", "V", prev, outputPath=run)
    trace, _ = trace_lines(state, z=0.02)
    old_trace = trace_lines(prev_state, z=0.015)[0] if prev_state else None
    pl = pv.Plotter(off_screen=True, shape=(1, 3), window_size=(2400, 860), border=False)
    pl.set_background("white")
    edges, own_mesh = solver_mesh_edges(index)
    pv_e = vis.mesh_to_pv_mesh(mesh)
    centres = np.ascontiguousarray(pv_e.cell_centers().points[:, :2])
    pv_e.cell_data["log10 strain rate"] = np.log10(np.maximum(np.asarray(uw.function.evaluate(
        edot_total_sym, centres)).ravel(), 1e-2))
    e_hi = max(3.0, np.ceil(2 * np.percentile(pv_e.cell_data["log10 strain rate"], 99.9)) / 2)
    pv_g = field_mesh(plastic_strain, "plastic strain")
    g_hi = max(1.0, np.ceil(2 * pv_g["plastic strain"].max()) / 2)
    # the mesh panel: a flat tint of T (muted) under the edges so the plates read
    pv_T = field_mesh(T, "T")
    pl.subplot(0, 0)
    pl.add_mesh(pv_T, scalars="T", cmap="RdBu_r", clim=(0.0, 1.0), lighting=False, opacity=0.35,
                show_scalar_bar=False)
    pl.add_mesh(edges, color=MESH_GREY, line_width=0.5, lighting=False)
    if old_trace is not None:
        pl.add_mesh(old_trace, color=FORCE, line_width=2.0, lighting=False, opacity=0.9)
    if trace is not None:
        pl.add_mesh(trace, color=INK, line_width=2.5, lighting=False)
    rec_line = f"step {index}, t = {state['t']:.4f}" + ("; solver mesh" if own_mesh else "; base mesh")
    if prev is not None:
        rec_line += f"; traces: step {prev} (rust), step {index} (ink)"
    pl.add_text(rec_line, font_size=11, color="black")
    place_camera(pl, state.get("theta_trench"))
    pl.subplot(0, 1)
    pl.add_mesh(pv_e, scalars="log10 strain rate", cmap="viridis", clim=(e_hi - 2.5, e_hi),
                lighting=False, scalar_bar_args=dict(title="log10 strain rate", **bar))
    if strm.n_points > 0:
        pl.add_mesh(strm, color="white", line_width=0.6, lighting=False, opacity=0.5)
    if trace is not None:
        pl.add_mesh(trace, color="white", line_width=1.0, lighting=False)
    place_camera(pl, state.get("theta_trench"))
    pl.subplot(0, 2)
    pl.add_mesh(pv_g, scalars="plastic strain", cmap="magma_r", clim=(0.0, g_hi), lighting=False,
                scalar_bar_args=dict(title="plastic strain", **bar))
    if trace is not None:
        pl.add_mesh(trace, color="#2471a3", line_width=2.0, lighting=False)
    place_camera(pl, state.get("theta_trench"))
    for bar_actor in pl.scalar_bars.values():
        bar_actor.SetTextPositionToPrecedeScalarBar()
    shot = Image.fromarray(np.asarray(pl.screenshot(return_img=True)))
    pl.close()
    strip = iteration_strip(index, shot.width)
    canvas = Image.new("RGB", (shot.width, shot.height + strip.height), "white")
    canvas.paste(shot, (0, 0))
    canvas.paste(strip, (0, shot.height))
    out = os.path.join(renders, f"frame_{index:05d}.png")
    canvas.save(out)
    if params.uw_band and prev_state is not None:
        band = render_band(index, prev, state, prev_state, bar)
        if band:
            print("->", band, flush=True)
    return out


def render(index):
    # a strain-weakening run also carries the accumulated plastic strain: a fourth panel
    has_strain = os.path.exists(os.path.join(run, f"annulus.mesh.plastic_strain.{index:05d}.h5"))
    if params.uw_panels in ("strain", "solver") and not has_strain:
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
    if params.uw_panels == "solver":
        return render_solver(index, state, strm, vmax, bar)
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
        prefix = "zoom" if params.uw_zoom > 0 and params.uw_panels != "solver" else "frame"
        frame = os.path.join(renders, f"{prefix}_{index:05d}.png")
        if os.path.exists(frame):
            done.add(index)
        if index not in done and os.path.exists(os.path.join(run, f"state_{index:05d}.json")):
            print("->", render(index), flush=True)
            done.add(index)
    history()
    if not params.uw_watch or finished:
        break
    time.sleep(30)
