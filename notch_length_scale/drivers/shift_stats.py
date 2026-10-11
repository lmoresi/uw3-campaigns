"""The yield-stress shift the micromorphic law actually applies, s = m H (e - chi),
over the strong layer (m = 1), from checkpoints: max s / C (strengthening, at the
band centre) and min s / C (weakening, on the flanks), with max H chi / C (the floor
bound, a different quantity: since e >= 0, s >= -H chi) beside them.

e = edot_II(u) is evaluated at chi's own P1 nodes (each rank its own nodes, exact
there) and chi is read at the same nodes; in model units s / C = beta (eta_bg V/H / C)
(e - chi). Nodes where e evaluates <= 0 on the rebuilt model (the weak inclusion's
corners) are left out. The extremes are global (a scratch P1 variable's collective
min / max). Writes ../results/<uw_out>."""
import glob
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
    uw_pattern=uw.Param("micro_ref3_xi0_beta*", description="checkpoint names (glob)"),
    uw_out=uw.Param("shift_stats.json", description="output file in results/"),
)
RES = os.path.join(_here, "..", "results")
CK = os.path.join(RES, "micromorphic", "checkpoints")
RATE = cn.U_MMYR * 1.0e-3 / (365.25 * 24 * 3600) / (cn.H_KM * 1.0e3)    # V/H, 1/s
STRESS_OVER_C = cn.ETA_BG * RATE / 1.0e8
NAME = re.compile(r"micro_ref(\d)_xi([\d.]+)_beta([\d.]+)_l([\d.]+)")

names = sorted({os.path.basename(p).split(".mesh.")[0] for p in
                glob.glob(os.path.join(CK, str(params.uw_pattern) + ".mesh.chi.00000.h5"))})
rows = []
for name in names:
    m = NAME.match(name)
    if m is None:
        continue
    ref, xi, beta, l_km = int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    S = cn.build_notch(ref, xi, seed=False)
    chi = uw.discretisation.MeshVariable("chi", S["mesh"], 1, degree=1, units="1/s")
    for var in (S["v"], chi):
        var.read_timestep(name, var.name, 0, outputPath=CK)
    nodes = chi.coords
    e = np.asarray(uw.function.evaluate(S["stokes"].Unknowns.Einv2, nodes)).ravel()
    strong = np.asarray(uw.function.evaluate(S["mat"].sym[0], nodes)).ravel() > 0.5
    chi_nd = np.asarray(chi.array).ravel() / RATE
    keep = strong & (e > 0)
    shift = beta * STRESS_OVER_C * (e - chi_nd)
    floor = beta * STRESS_OVER_C * chi_nd
    scratch = uw.discretisation.MeshVariable("shift_scratch", S["mesh"], 1, degree=1)
    out = {}
    for key, values in (("s", shift), ("Hchi", floor)):
        scratch.array[:, 0, 0] = np.where(keep, values, -np.inf)
        out[key + "_max"] = float(scratch.max())
        scratch.array[:, 0, 0] = np.where(keep, values, np.inf)
        out[key + "_min"] = float(scratch.min())
    rows.append(dict(run=name, ref=ref, beta=beta, l_km=l_km, max_s_over_C=out["s_max"],
                     min_s_over_C=out["s_min"], floor_bound_max_Hchi_over_C=out["Hchi_max"]))
    uw.pprint(f"{name}: s/C max {out['s_max']:.3f} min {out['s_min']:.3f}  "
              f"max H chi/C {out['Hchi_max']:.3f}")
    del S

with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        json.dump(rows, open(os.path.join(RES, str(params.uw_out)), "w"), indent=1)
