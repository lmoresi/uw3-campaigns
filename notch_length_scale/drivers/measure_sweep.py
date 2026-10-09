"""Band widths and the yield-floor check for every saved micromorphic run, from its
fields (no re-solve), so old and new runs are measured the same way.

For each ``fields_micro_ref<r>_xi<xi>_beta<b>_l<l>[_<tag>].npz`` the notch is rebuilt at
ref r, v, p and chi are loaded, and

* W from horizontal cuts (``measure_bands``, the campaign's estimator) and from vertical
  cuts at fixed |x| (``measure_bands_vertical``), which cross one limb each;
* the peak of edot_II above the background on the vertical cuts (non-dimensional,
  V/H units): with a length scale it should not change with h;
* the yield argument C_eff + sin(phi) p + H (e - chi) in the strong layer, against the
  residual-strength floor 0.02 C: its minimum, and the fraction of strong-layer nodes
  where it is below twice the floor (where the smooth floor's rounding acts).

The vertical-cut profiles are saved as ``vprofiles_<run>.npz`` for plotting.
Runs are processed one at a time, each build evaluated before the next (named
expressions are shared between builds, #767). Writes ../results/sweep_widths.json.
"""
import glob
import importlib.util
import json
import os
import re
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_pattern=uw.Param("fields_micro_ref*_xi0_*.npz", description="runs to measure"),
    uw_out=uw.Param("sweep_widths.json", description="output file in results/"),
)
RES = os.path.join(_here, "..", "results")
STATIONS = [-0.7, -0.6, -0.5, -0.4, 0.4, 0.5, 0.6, 0.7]     # x / H, i.e. +-12..21 km
NAME = re.compile(r"fields_micro_ref(\d)_xi([\d.]+)_beta([\d.]+)_l([\d.]+)(?:_(\w+))?\.npz")

spec = importlib.util.spec_from_file_location("bw", os.path.join(_here, "band_width_vs_h.py"))
argv, sys.argv = sys.argv, [sys.argv[0]]
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
sys.argv = argv


def side_widths(bands):
    return {side: (None if band is None else band["W_equiv_km"]) for side, band in bands.items()}


rows = []
for path in sorted(glob.glob(os.path.join(RES, "micromorphic", str(params.uw_pattern)))):
    match = NAME.match(os.path.basename(path))
    if match is None:
        continue
    ref, xi, beta, l_km, tag = match.groups()
    ref, xi, beta, l_km = int(ref), float(xi), float(beta), float(l_km)
    record_path = path.replace("fields_", "").replace(".npz", ".json")
    record = json.load(open(record_path)) if os.path.exists(record_path) else {}
    if not record.get("converged", False):
        continue

    S = cn.build_notch(ref, xi, seed=False)
    saved = np.load(path)
    chi = uw.discretisation.MeshVariable("chi", S["mesh"], 1, degree=1, units="1/s")
    for key, var in (("v", S["v"]), ("p", S["p"]), ("chi", chi)):
        values = saved[key].reshape(var.array.shape)
        if var.units is not None:
            values = uw.utilities.UnitAwareArray(values, units=var.units)
        var.array[...] = values

    m, e = S["mat"].sym[0], S["stokes"].Unknowns.Einv2
    H = uw.expression(r"H_{\chi}", uw.quantity(beta * cn.ETA_BG, "Pa*s"), "micromorphic modulus")
    argument = S["C_eff"] + np.sin(np.deg2rad(cn.PHI)) * S["p"].sym[0] + H * (e - chi.sym[0])
    # the ratio is evaluated as one expression so its units cancel inside evaluate
    nodes = S["mesh"].X.coords
    strong = np.asarray(uw.function.evaluate(m, nodes)).ravel() > 0.5
    over_floor = np.asarray(uw.function.evaluate(argument / (0.02 * S["C"]), nodes)).ravel()[strong]

    horizontal = cn.measure(S, os.path.join(RES, "micromorphic"),
                            os.path.basename(path)[7:-4])
    vertical = bw.measure_bands_vertical(
        S, STATIONS, 4001, 0.68, cn.H_KM,
        profile_out=os.path.join(RES, "micromorphic",
                                 "vprofiles_" + os.path.basename(path)[7:]))
    rows.append(dict(
        run=os.path.basename(path), ref=ref, xi=xi, beta=beta, l_km=l_km, tag=tag or "",
        h_min_km=float(S["mesh"].get_min_radius()) * cn.H_KM,
        nl_its=record.get("nl_its"), linear=record.get("linear", "exact"),
        W_horizontal_km=side_widths(horizontal), W_vertical_km=side_widths(vertical),
        dip_vertical_deg={s: (None if b is None else b["dip_deg"]) for s, b in vertical.items()},
        peak_vertical={s: (None if b is None else b["amp_max"]) for s, b in vertical.items()},
        yield_argument_min_over_floor=float(over_floor.min()),
        fraction_near_floor=float(np.mean(over_floor < 2.0)),
    ))
    uw.pprint(f"{rows[-1]['run']}: W_h {rows[-1]['W_horizontal_km']}  "
              f"W_v {rows[-1]['W_vertical_km']}  min arg/floor "
              f"{rows[-1]['yield_argument_min_over_floor']:.2f}")
    del S

if uw.mpi.rank == 0:
    with open(os.path.join(RES, str(params.uw_out)), "w") as fh:
        json.dump(rows, fh, indent=1)
