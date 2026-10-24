"""Does a ridge develop? The surface velocity, its divergence and the lid thickness
around the annulus for a list of checkpoints, with the trench(es) marked. A ridge
is a divergence maximum with a thin lid under it; a plate is a flat v_theta.

    python surface_profile.py -uw_run <run dir> -uw_indices 0,20,59
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drivers"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strain_band import polar_grid
from strain_fault import sample_checkpoint


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import underworld3 as uw
    from annulus_model import annulus_mesh, annulus_radii, clamp_radii

    params = uw.Params(
        uw_run="~/+Simulations/zg95/annulus_faults/runs/slab_diffused",
        uw_indices="0,20,59",
        uw_T_lid=0.7,               # the lid base isotherm
        uw_depth_surface=0.005,     # where the surface velocity is read
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
    theta, depth, xy = polar_grid(r_o, n_theta=720, depth_max=0.4, n_depth=80)
    shape = (len(depth), len(theta))
    i_s = int(np.argmin(np.abs(depth - params.uw_depth_surface)))
    deg = np.degrees(theta)
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    for n, index in enumerate(indices):
        s = sample_checkpoint(run, index, mesh, fields, clamp_radii(xy, r_o, r_i, 1e-10))
        g = {k: v.reshape(shape) for k, v in s.items()}
        with open(os.path.join(run, f"state_{index:05d}.json")) as f:
            state = json.load(f)
        v_s = g["v_t"][i_s]
        # surface divergence along the arc, periodic, smoothed over ~1 degree
        dv = np.gradient(v_s, theta * r_o)
        k = 4
        dv = np.convolve(np.r_[dv[-k:], dv, dv[:k]], np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
        below = g["T"] > params.uw_T_lid
        lid = np.array([depth[np.argmax(below[:, j])] if below[:, j].any() else depth[-1] for j in range(len(theta))])
        lab = f"step {index}, t {state['t']:.4f}"
        axes[0].plot(deg, v_s, lw=1.2, label=lab)
        axes[1].plot(deg, dv, lw=1.2, label=lab)
        axes[2].plot(deg, lid, lw=1.2, label=lab)
        for i_r in np.where((dv[:-1] > 0) & (np.r_[dv[1:]] > 0) & (np.diff(np.sign(v_s)) > 0))[0]:
            axes[1].axvline(deg[i_r], color=f"C{n}", ls=":", lw=0.8)
        for fl in state.get("faults", []):
            axes[0].axvline(np.degrees(fl["theta"]), color=f"C{n}", ls="--", lw=0.8)
        for rg in state.get("ridges", []):
            axes[2].axvline(np.degrees(rg), color="k", ls="--", lw=0.8)
        print(f"{lab}: surface |v| max {np.abs(v_s).max():.1f}, divergence max {dv.max():.0f} at "
              f"{deg[np.argmax(dv)]:.0f} deg, lid min {lid.min():.3f} at {deg[np.argmin(lid)]:.0f} deg, "
              f"lid max {lid.max():.3f}, lid at 180 {lid[np.argmin(np.abs(np.abs(deg) - 180))]:.3f}")
    axes[0].set_ylabel("surface v_theta")
    axes[0].axhline(0, color="k", lw=0.5)
    axes[1].set_ylabel("surface divergence (dotted: ridges)")
    axes[1].axhline(0, color="k", lw=0.5)
    axes[2].set_ylabel(f"lid depth (T {params.uw_T_lid})")
    axes[2].invert_yaxis()
    axes[2].set_xlabel("theta (deg); dashed: trenches")
    axes[2].set_xlim(-180, 180)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    out = params.uw_out or os.path.join(run, "renders_strain", f"surface_profile_{'_'.join(map(str, indices))}.png")
    fig.savefig(out, dpi=110)
    print("->", out)


if __name__ == "__main__":
    main()
