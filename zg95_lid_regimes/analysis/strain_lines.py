"""Faults fitted to the damage of annulus checkpoints: up to N straight lines extracted
from the saturated plastic strain of the lithosphere (``strain_band.fit_fault_lines``),
each as long as its damage is deep, drawn over the unrolled plastic strain with the
run's own faults.

    python strain_lines.py -uw_run <run dir> -uw_indices 2830,2850 -uw_centre 15 -uw_window 60
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strain_band import fit_fault_lines, polar_grid
from strain_fault import sample_checkpoint


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import underworld3 as uw
    from annulus_model import annulus_mesh, annulus_radii, clamp_radii

    params = uw.Params(
        uw_run="~/+Simulations/zg95/annulus_faults/runs/tau1x1.50_faults_damage",
        uw_indices="2830",
        uw_gamma_sat=0.5,
        uw_T_lith=0.6,
        uw_depth_min=0.02,
        uw_depth_max=0.45,
        uw_n_max=6,
        uw_min_damage=0.005,
        uw_width=0.035,
        uw_centre=15.0,             # plotted window centre (degrees)
        uw_window=60.0,             # plotted half-width (degrees)
        uw_out="",
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
    theta, depth, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
    shape = (len(depth), len(theta))
    # true scale: arc length along the outer wall against depth, both in layer depths
    half_arc = r_o * np.deg2rad(params.uw_window)
    fig, axes = plt.subplots(len(indices), 1, figsize=(14, 14 * 0.5 / (2 * half_arc) * len(indices) + 1.2),
                             squeeze=False)
    centre = np.deg2rad(params.uw_centre)

    def rel(a):
        """arc length along the outer wall from the window centre (layer depths)"""
        return r_o * ((a - centre + np.pi) % (2 * np.pi) - np.pi)

    for ax, index in zip(axes[:, 0], indices):
        s = sample_checkpoint(run, index, mesh, fields, clamp_radii(xy, r_o, r_i, 1e-10))
        g = {k: v.reshape(shape) for k, v in s.items()}
        with open(os.path.join(run, f"state_{index:05d}.json")) as f:
            state = json.load(f)
        lines = fit_fault_lines(theta, depth, g["gamma"], g["T"], r_o, params.uw_gamma_sat, params.uw_T_lith,
                                params.uw_depth_min, params.uw_depth_max, params.uw_n_max,
                                params.uw_min_damage, params.uw_width)
        dth = rel(theta)
        order = np.argsort(dth)
        cols = order[np.abs(dth[order]) <= half_arc]
        im = ax.pcolormesh(dth[cols], depth, g["gamma"][:, cols], cmap="magma_r", vmin=0,
                           vmax=max(1.0, float(np.percentile(g["gamma"], 99.9))), shading="auto")
        ax.contour(dth[cols], depth, g["T"][:, cols], levels=[0.3, 0.6, 0.8], colors="#2471a3", linewidths=0.6)
        for n, tr in enumerate(state.get("traces") or ([state["trace"]] if "trace" in state else [])):
            tr = np.asarray(tr)
            ax.plot(rel(np.arctan2(tr[:, 1], tr[:, 0])), r_o - np.hypot(tr[:, 0], tr[:, 1]),
                    color="#27ae60", lw=2, label="model faults" if n == 0 else None)
        for n, ln in enumerate(lines):
            # the fitted fault from the trench to the deepest damage along it
            s_end = (ln["depth_bottom"]) / max(-ln["down"] @ (ln["trench"] / np.linalg.norm(ln["trench"])), 0.2)
            seg = np.array([ln["trench"] + ln["down"] * f for f in np.linspace(0, s_end, 20)])
            ax.plot(rel(np.arctan2(seg[:, 1], seg[:, 0])), r_o - np.hypot(seg[:, 0], seg[:, 1]),
                    color="#c0392b", lw=2.2, label="fitted to the damage" if n == 0 else None)
            print(f"step {index}: line {n}: trench {np.degrees(ln['theta_t']):.1f} deg, phi {ln['phi']:.0f}, "
                  f"depth {ln['depth_top']:.2f}-{ln['depth_bottom']:.2f}, damage {ln['damage']:.3f}, "
                  f"{ln['n_points']} points")
        ax.set_ylim(depth[-1], 0)
        ax.set_xlim(-half_arc, half_arc)
        ax.set_aspect("equal")
        ax.set_ylabel("depth")
        ax.set_title(f"step {index}, t {state['t']:.4f}: plastic strain, {len(lines)} faults fitted to the "
                     f"damage (red), the run's faults (green); theta from {params.uw_centre:.0f} deg",
                     fontsize=8, loc="left")
        ax.legend(fontsize=7, loc="lower right")
        fig.colorbar(im, ax=ax, pad=0.01, shrink=0.8)
    axes[-1, 0].set_xlabel(f"arc length along the surface from {params.uw_centre:.0f} deg (layer depths; "
                           f"1 layer depth = {np.degrees(1 / r_o):.1f} deg)")
    fig.tight_layout()
    out = params.uw_out or os.path.join(run, "renders", f"strain_lines_{'_'.join(map(str, indices))}.png")
    fig.savefig(out, dpi=120)
    print("->", out)


if __name__ == "__main__":
    main()
