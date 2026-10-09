"""Does the integral width's window cap W? For saved runs (checkpoints, no re-solve),
W for windows of +-6, 9, 12 km and the background from the whole cut or from outside
the window, plus each cut's profile at its ends relative to the peak (a tail still
raised there is outside what any window on this cut can see). Collective (global
evaluate), so serial or mpirun. Writes ../results/<uw_out>."""
import json
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

RES = os.path.join(_here, "..", "results")
CHECKPOINTS = os.path.join(RES, "micromorphic", "checkpoints")
params = uw.Params(
    uw_refs=uw.Param("3,4", description="refinements to check, comma-separated"),
    uw_out=uw.Param("window_check.json", description="output file in results/"),
)
RUNS = [(3, "micro_ref3_xi0_beta0.1_l1"), (4, "micro_ref4_xi0_beta0.1_l1_production_tight"),
        (3, "micro_ref3_xi0_beta0.1_l2"), (4, "micro_ref4_xi0_beta0.1_l2_production_tight"),
        (3, "micro_ref3_xi0_beta0.1_l0.5"), (4, "micro_ref4_xi0_beta0.1_l0.5_production_tight"),
        (5, "micro_ref5_xi0_beta0.1_l1_production_tight_np16"),
        (5, "micro_ref5_xi0_beta0.1_l0.5_production_tight_np16")]
REFS = {int(r) for r in str(params.uw_refs).split(",")}
RUNS = [run for run in RUNS if run[0] in REFS]
rows = []
for ref, name in RUNS:
    S = cn.build_notch(ref, 0.0, seed=False)
    chi = uw.discretisation.MeshVariable("chi", S["mesh"], 1, degree=1, units="1/s")
    for var in (S["v"], S["p"], chi):
        var.read_timestep(name, var.name, 0, outputPath=CHECKPOINTS)
    row = dict(run=name, ref=ref, W={})
    for window in (6.0, 9.0, 12.0, 30.0):
        for background in ("cut", "outside"):
            row["W"][f"{window:g}km_{background}"] = cn.integral_width(S, window, background)["median"]
    # the profile's ends: (f - median) / (peak - median) at the top and bottom of each cut
    y = np.linspace(-0.68, -0.02, 4001)
    ends = []
    for xs in cn.STATIONS:
        f = np.asarray(uw.function.global_evaluate(
            S["stokes"].Unknowns.Einv2, np.column_stack([np.full_like(y, xs), y]))).ravel()
        g = f - np.median(f)
        ends.append([float(g[0] / g.max()), float(g[-1] / g.max()),
                     float(y[int(np.argmax(g))] * cn.H_KM)])
    row["ends_bottom_top_peaky"] = ends
    rows.append(row)
    uw.pprint(name, {k: round(v, 3) for k, v in row["W"].items()})
    del S
with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        json.dump(rows, open(os.path.join(RES, str(params.uw_out)), "w"), indent=1)
