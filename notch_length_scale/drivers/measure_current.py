"""Band width and peak with the CURRENT estimator, for every (ref, l) of the
micromorphic beta = 0.1, xi = 0 runs (or, with -uw_model cosserat, the Cosserat
c = 1, xi = 0 runs), from checkpoints (no re-solve):

* W: the integral width, background = median of each cut outside +-9 km of its peak
  (``coupled_notch.integral_width(S, 9, "outside")``), median over the 8 cuts;
* peak: (max - background) / background on the same cuts, median over the cuts;
* the edot_II profile on the fixed cut x = -15 km (the left band), over the same
  background, for the overlay figure.

Runs are the tables' canonical ones (``coupled_notch.canonical_run``). Collective
(global_evaluate), so serial or under mpirun; built one at a time, coarse first (#767).
Writes ../results/current_widths.json."""
import json
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_l=uw.Param("0.25,0.5,1,2", description="length scales l (km), comma-separated"),
    uw_refs=uw.Param("1,2,3,4,5", description="refinements, comma-separated"),
    uw_profile_x=uw.Param(-0.5, description="x / H of the profile cut (-0.5: x = -15 km)"),
    uw_out=uw.Param("current_widths.json", description="output file in results/"),
    uw_model=uw.Param("micromorphic", description="micromorphic | cosserat (c = 1, P1)"),
)
RES = os.path.join(_here, "..", "results")
MODEL = str(params.uw_model)
CHECKPOINTS = os.path.join(RES, MODEL, "checkpoints")
WINDOW_KM, BACKGROUND = 9.0, "outside"

rows = []
for ref in [int(r) for r in str(params.uw_refs).split(",")]:
    for l_km in [float(l) for l in str(params.uw_l).split(",")]:
        name = cn.canonical_run(ref, l_km, model=MODEL)
        if not os.path.exists(os.path.join(CHECKPOINTS, name + ".mesh.U.00000.h5")):
            continue
        S = cn.build_notch(ref, 0.0, seed=False)
        S["v"].read_timestep(name, S["v"].name, 0, outputPath=CHECKPOINTS)
        width = cn.integral_width(S, WINDOW_KM, BACKGROUND)

        y = np.linspace(-0.68, -0.02, 4001)
        xs = float(params.uw_profile_x)
        f = np.asarray(uw.function.global_evaluate(
            S["stokes"].Unknowns.Einv2, np.column_stack([np.full_like(y, xs), y]))).ravel()
        y_km = y * cn.H_KM
        i = int(np.argmax(f - np.median(f)))
        background = float(np.median(f[np.abs(y_km - y_km[i]) >= WINDOW_KM]))

        rows.append(dict(run=name, model=MODEL, ref=ref, l_km=l_km,
                         h_min_km=float(S["mesh"].get_min_radius()) * cn.H_KM,
                         W_km=width["median"], W_spread_km=width["spread"],
                         peak=width["peak_over_background"],
                         profile=dict(x_km=xs * cn.H_KM, y_km=y_km[::4].tolist(),
                                      over_background=(f[::4] / background).tolist())))
        uw.pprint(f"{name}: W {width['median']:.3f} km  peak {width['peak_over_background']:.3f}")
        del S

with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        json.dump(rows, open(os.path.join(RES, str(params.uw_out)), "w"), indent=1)
