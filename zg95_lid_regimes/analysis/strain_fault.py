"""Where should the fault be? Locate the active, saturated plastic-strain band of a
downwelling in an annulus checkpoint and fit a straight fault to it: the trench
angle, the dip and the dip direction.

The fields are sampled on an unrolled (theta, depth) grid. A point belongs to the
candidate band when its accumulated plastic strain is saturated (gamma >= gamma_sat),
it is still lithosphere (T <= T_lith, depth <= depth_max) and the flow there is
downward (v_r < 0). Connected clusters of such points are ranked by their current
plastic activity (the integral of edot_plastic), and the most active one is fitted
by weighted principal axes in Cartesian coordinates. The fitted line, extended to
the outer wall, gives the trench; its angle to the local horizontal is the dip.

    python strain_fault.py -uw_run <run dir> -uw_indices 2150,2250,2400
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
from strain_band import detect_fault, polar_grid


def sample_checkpoint(run, index, mesh, fields, xy):
    """T, V, plastic strain and its rate of a checkpoint, at the points ``xy``."""
    import underworld3 as uw
    out = {}
    for name, var in fields.items():
        var.read_timestep("annulus", name, index, outputPath=run)
    out["T"] = np.asarray(uw.function.evaluate(fields["T"].sym[0], xy)).ravel()
    v = np.asarray(uw.function.evaluate(fields["V"].sym, xy)).reshape(-1, 2)
    r = np.hypot(xy[:, 0], xy[:, 1])
    out["v_r"] = (v[:, 0] * xy[:, 0] + v[:, 1] * xy[:, 1]) / r
    out["v_t"] = (-v[:, 0] * xy[:, 1] + v[:, 1] * xy[:, 0]) / r
    out["gamma"] = np.asarray(uw.function.evaluate(fields["plastic_strain"].sym[0], xy)).ravel()
    out["edot"] = np.asarray(uw.function.evaluate(fields["edot_plastic"].sym[0], xy)).ravel()
    return out


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import underworld3 as uw
    from annulus_model import annulus_mesh, annulus_radii

    params = uw.Params(
        uw_run="~/+Simulations/zg95/annulus_faults/runs/tau1x1.50_fault_th0_dip45_fn_sw_reg10",
        uw_indices="2150,2250,2400",
        uw_gamma_sat=0.5,
        uw_T_lith=0.6,
        uw_depth_max=0.45,
        uw_window=40.0,             # half-width of the plotted theta window (degrees)
        uw_out="",                  # figure (default: <run>/renders/strain_fault_<indices>.png)
        uw_prefer_model=0,          # 1: prefer the band nearest the run's own fault (the driver's tracking)
    )
    run = os.path.expanduser(params.uw_run)
    indices = [int(i) for i in str(params.uw_indices).split(",")]
    with open(os.path.join(run, f"state_{indices[0]:05d}.json")) as f:
        p = json.load(f)["params"]
    mesh = annulus_mesh(float(p["uw_cell"]), int(p["uw_refinement"]))
    r_o, r_i = annulus_radii()
    fields = {
        "T": uw.discretisation.MeshVariable("T", mesh, 1, degree=2),
        "V": uw.discretisation.MeshVariable("V", mesh, 2, degree=2),
        "plastic_strain": uw.discretisation.MeshVariable("plastic_strain", mesh, 1, degree=2),
        "edot_plastic": uw.discretisation.MeshVariable("edot_plastic", mesh, 1, degree=1),
    }
    theta, depth, xy = polar_grid(r_o)
    shape = (len(depth), len(theta))

    fig, axes = plt.subplots(len(indices), 1, figsize=(13, 3.2 * len(indices)), squeeze=False)
    results = []
    for ax, index in zip(axes[:, 0], indices):
        s = sample_checkpoint(run, index, mesh, fields, xy)
        g = {k: v.reshape(shape) for k, v in s.items()}
        with open(os.path.join(run, f"state_{index:05d}.json")) as f:
            state = json.load(f)
        found = detect_fault(theta, depth, g["gamma"], g["edot"], g["T"], g["v_r"], r_o,
                             params.uw_gamma_sat, params.uw_T_lith, params.uw_depth_max,
                             prefer=state.get("theta_trench") if params.uw_prefer_model else None)
        centre = found["theta_t"] if found else state.get("theta_trench", 0.0)
        dth = (np.degrees(theta - centre) + 180) % 360 - 180
        order = np.argsort(dth)
        win = np.abs(dth[order]) <= params.uw_window
        cols = order[win]
        im = ax.pcolormesh(dth[cols], depth, g["gamma"][:, cols], cmap="magma_r", vmin=0,
                           vmax=max(1.0, float(np.percentile(g["gamma"], 99.9))), shading="auto")
        ax.contour(dth[cols], depth, g["T"][:, cols], levels=[0.3, 0.6, 0.8], colors="#2471a3",
                   linewidths=0.6)
        ax.contour(dth[cols], depth, g["v_r"][:, cols], levels=[0.0], colors="0.5", linewidths=0.6,
                   linestyles="--")
        # the explicit fault of the run (its trace), in the same coordinates
        for n, tr in enumerate(state.get("traces") or ([state["trace"]] if "trace" in state else [])):
            tr = np.asarray(tr)
            tth = (np.degrees(np.arctan2(tr[:, 1], tr[:, 0]) - centre) + 180) % 360 - 180
            ax.plot(tth, r_o - np.hypot(tr[:, 0], tr[:, 1]), color="#27ae60", lw=2,
                    label="model fault" if n == 0 else None)
        if found:
            seg = np.array([found["trench"], found["tip"]])
            sth = (np.degrees(np.arctan2(seg[:, 1], seg[:, 0]) - centre) + 180) % 360 - 180
            ax.plot(sth, r_o - np.hypot(seg[:, 0], seg[:, 1]), color="#c0392b", lw=2.5,
                    label=f"detected: dip {found['dip']:.0f}, dir {found['direction']:+d}")
            pth = (np.degrees(np.arctan2(found["points"][:, 1], found["points"][:, 0]) - centre) + 180) % 360 - 180
            ax.scatter(pth, r_o - np.hypot(found["points"][:, 0], found["points"][:, 1]), s=1.5,
                       color="#c0392b", alpha=0.3)
            results.append({"index": index, "t": state["t"], "theta_t_deg": np.degrees(found["theta_t"]),
                            "dip": found["dip"], "direction": found["direction"],
                            "linearity": found["linearity"], "n_points": found["n_points"],
                            "model_theta_t_deg": np.degrees(state.get("theta_trench", np.nan))})
        ax.set_ylim(depth[-1], 0)
        ax.set_xlim(-params.uw_window, params.uw_window)
        ax.set_ylabel("depth")
        ax.set_title(f"step {index}, t {state['t']:.4f}: plastic strain; T 0.3/0.6/0.8 (blue), "
                     f"v_r = 0 (grey dashed); theta relative to "
                     f"{'detected' if found else 'model'} trench {np.degrees(centre):.1f} deg",
                     fontsize=8, loc="left")
        ax.legend(fontsize=7, loc="lower right")
        fig.colorbar(im, ax=ax, pad=0.01)
    axes[-1, 0].set_xlabel("theta from the trench (degrees)")
    fig.tight_layout()
    out = params.uw_out or os.path.join(run, "renders", f"strain_fault_{'_'.join(map(str, indices))}.png")
    fig.savefig(out, dpi=120)
    for r in results:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print("->", out)


if __name__ == "__main__":
    main()
