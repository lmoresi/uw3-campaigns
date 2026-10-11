"""The edot_II profiles of the matched-width pairs (micromorphic beta 0.1 against
Cosserat (l, c) at the same W), on the cut x = -15 km, over the outside background,
from checkpoints (no re-solve), plus W and the peak by the current estimator.
Collective (global_evaluate); built one at a time. Writes ../results/<uw_out>."""
import json
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_ref=uw.Param(3, description="refinement of the runs to read"),
    uw_out=uw.Param("matched_profiles_ref3.json", description="output file in results/"),
)
RES = os.path.join(_here, "..", "results")
REF = int(params.uw_ref)
# the matched pairs: (pair, model, l in km, c for Cosserat)
PAIRS = [("P1", "micromorphic", 0.25, None), ("P1", "cosserat", 0.14, 1),
         ("P2", "micromorphic", 0.5, None), ("P2", "cosserat", 0.236, 1),
         ("P2", "cosserat", 0.25, 0.1),
         ("P3", "micromorphic", 1.0, None), ("P3", "cosserat", 0.37, 1),
         ("P3", "cosserat", 0.5, 0.054)]


def checkpoint_name(model, l_km, c):
    """Ref 3: the exact-LU runs (micromorphic sweep, Cosserat map / confirmation).
    Ref 4: the tight-FMG, grid-sequenced efficiency runs at np 8."""
    if model == "micromorphic":
        base = f"micro_ref{REF}_xi0_beta0.1_l{l_km:g}"
        return base if REF == 3 else base + "_production_tight_np8_eff"
    base = f"cosserat_ref{REF}_xi0_c{c:g}_l{l_km:g}_P1"
    if REF == 3:
        return base + ("_np4_cmap" if (l_km, c) == (0.25, 0.1) else "_np4_cmatch")
    return base + "_production_tight_np8_eff"


RUNS = [(pair, model,
         f"micromorphic l = {l_km:g} km" if model == "micromorphic"
         else f"Cosserat l = {l_km:g} km, c = {c:g}",
         model, checkpoint_name(model, l_km, c)) for pair, model, l_km, c in PAIRS]

rows = []
for pair, model, label, directory, name in RUNS:
    checkpoints = os.path.join(RES, directory, "checkpoints")
    if not os.path.exists(os.path.join(checkpoints, name + ".mesh.U.00000.h5")):
        uw.pprint(f"missing {name}")
        continue
    S = cn.build_notch(REF, 0.0, seed=False)
    S["v"].read_timestep(name, S["v"].name, 0, outputPath=checkpoints)
    width = cn.integral_width(S, 9.0, "outside")
    y = np.linspace(-0.68, -0.02, 2001)
    f = np.asarray(uw.function.global_evaluate(
        S["stokes"].Unknowns.Einv2, np.column_stack([np.full_like(y, -0.5), y]))).ravel()
    y_km = y * cn.H_KM
    i = int(np.argmax(f - np.median(f)))
    background = float(np.median(f[np.abs(y_km - y_km[i]) >= 9.0]))
    rows.append(dict(pair=pair, model=model, label=label, run=name, ref=REF,
                     W_km=width["median"], peak=width["peak_over_background"],
                     y_km=y_km[::2].tolist(), over_background=(f[::2] / background).tolist()))
    uw.pprint(f"{name}: W {width['median']:.3f}  peak {width['peak_over_background']:.3f}")
    del S

with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        json.dump(rows, open(os.path.join(RES, str(params.uw_out)), "w"), indent=1)
