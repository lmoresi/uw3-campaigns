"""Why the plastic strain and the strain rate differ: three true-scale panels of an
annulus checkpoint around a chosen angle -- the total strain-rate invariant, the
plastic strain rate (the part the strain field records: edot_II (1 - eta_eff/eta(T))),
and the accumulated plastic strain -- with the T 0.7 healing isotherm and the run's
faults drawn on each.

    python strain_rate_panels.py -uw_run <run dir> -uw_index 3350 -uw_centre 10 -uw_window 40
"""
import json
import os
import sys

import numpy as np
import sympy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strain_band import polar_grid
from strain_fault import sample_checkpoint


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import underworld3 as uw
    from annulus_model import annulus_mesh, annulus_radii, clamp_radii

    params = uw.Params(
        uw_run="~/+Simulations/zg95/annulus_faults/runs/ra3x_tau1x1.50_lines",
        uw_index=3350,
        uw_centre=10.0,             # window centre (degrees, positive: PETSc eats a leading minus)
        uw_window=40.0,             # half-width (degrees)
        uw_out="",
    )
    run = os.path.expanduser(params.uw_run)
    index = int(params.uw_index)
    with open(os.path.join(run, f"state_{index:05d}.json")) as f:
        state = json.load(f)
    mesh = annulus_mesh(float(state["params"]["uw_cell"]), int(state["params"]["uw_refinement"]))
    r_o, r_i = annulus_radii()
    fields = {
        "T": uw.discretisation.MeshVariable("T", mesh, 1, degree=2),
        "V": uw.discretisation.MeshVariable("V", mesh, 2, degree=2),
        "plastic_strain": uw.discretisation.MeshVariable("plastic_strain", mesh, 1, degree=2),
        "edot_plastic": uw.discretisation.MeshVariable("edot_plastic", mesh, 1, degree=1),
    }
    theta, depth, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
    shape = (len(depth), len(theta))
    pts = clamp_radii(xy, r_o, r_i, 1e-10)
    s = sample_checkpoint(run, index, mesh, fields, pts)
    # the total strain-rate invariant, projected from the velocity (P1)
    V = fields["V"]
    E = (V.sym.jacobian(mesh.X) + V.sym.jacobian(mesh.X).T) / 2
    e_inv = uw.discretisation.MeshVariable("edot_total", mesh, 1, degree=1)
    proj = uw.systems.Projection(mesh, e_inv)
    proj.uw_function = sympy.sqrt((E[0, 0] ** 2 + E[1, 1] ** 2 + 2 * E[0, 1] ** 2) / 2)
    proj.smoothing = 1.0e-6
    proj.solve()
    s["edot_total"] = np.asarray(uw.function.evaluate(e_inv.sym[0], pts)).ravel()
    g = {k: v.reshape(shape) for k, v in s.items()}

    centre = np.deg2rad(params.uw_centre)
    half_arc = r_o * np.deg2rad(params.uw_window)

    def rel(a):
        return r_o * ((a - centre + np.pi) % (2 * np.pi) - np.pi)

    dth = rel(theta)
    order = np.argsort(dth)
    cols = order[np.abs(dth[order]) <= half_arc]
    panels = [("total strain rate (log10)", np.log10(np.maximum(g["edot_total"], 1e-3)), "viridis", None),
              ("plastic strain rate (log10): the recorded part", np.log10(np.maximum(g["edot"], 1e-3)), "viridis", None),
              ("accumulated plastic strain", g["gamma"], "magma_r", (0, max(1.0, float(np.percentile(g["gamma"], 99.9)))))]
    lo = float(np.percentile(panels[0][1][:, cols], 99.5))
    fig, axes = plt.subplots(3, 1, figsize=(14, 3 * (14 * 0.5 / (2 * half_arc)) + 1.6), squeeze=False)
    for ax, (title, field, cmap, lim) in zip(axes[:, 0], panels):
        vmin, vmax = lim if lim else (lo - 3.0, lo)
        im = ax.pcolormesh(dth[cols], depth, field[:, cols], cmap=cmap, vmin=vmin, vmax=vmax, shading="auto")
        ax.contour(dth[cols], depth, g["T"][:, cols], levels=[0.7], colors="#2471a3", linewidths=0.8)
        for tr in state.get("traces", []):
            tr = np.asarray(tr)
            ax.plot(rel(np.arctan2(tr[:, 1], tr[:, 0])), r_o - np.hypot(tr[:, 0], tr[:, 1]), color="#27ae60", lw=1.8)
        ax.set_ylim(depth[-1], 0)
        ax.set_xlim(-half_arc, half_arc)
        ax.set_aspect("equal")
        ax.set_ylabel("depth")
        ax.set_title(f"step {index}, t {state['t']:.4f}: {title}; T 0.7 (blue, healing below it), faults (green)",
                     fontsize=8, loc="left")
        fig.colorbar(im, ax=ax, pad=0.01, shrink=0.8)
    axes[-1, 0].set_xlabel(f"arc length along the surface from {params.uw_centre:.0f} deg (layer depths)")
    fig.tight_layout()
    out = params.uw_out or os.path.join(run, "renders", f"strain_rate_panels_{index}_{int(params.uw_centre)}.png")
    fig.savefig(out, dpi=120)
    print("->", out)


if __name__ == "__main__":
    main()
