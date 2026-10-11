"""The yield-stress shift the micromorphic law actually applies, s = m H (e - chi),
over the strong layer (m = 1), from checkpoints: max s / C (strengthening, at the
band centre) and min s / C (weakening, on the flanks), with max H chi / C (the floor
bound, a different quantity: since e >= 0, s >= -H chi) beside them.

e = edot_II(u) is L2-projected onto chi's own P1 space and compared node by node; in model units s / C = beta (eta_bg V/H / C)
(e - chi). Nodes where the projected e is <= 0 (the projection's overshoot at the notch)
are left out. The extremes are global (a scratch P1 variable's collective
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
    # e by L2 projection onto chi's P1 space, in the same units as chi (1/s). A
    # point evaluate of Unknowns.Einv2 on the rebuilt model comes back in 1/s^0.5
    # (the units mix of evaluate on a rebuilt model), so e and chi could not be
    # compared: the first versions of this script read e as ~0 (max s < 0
    # everywhere, min s = -max H chi exactly). The projection goes through the
    # solver's compiled, consistently scaled path, as chi itself did.
    e_var = uw.discretisation.MeshVariable("e_proj", S["mesh"], 1, degree=1, units="1/s")
    projection = uw.systems.Projection(S["mesh"], e_var)
    projection.uw_function = S["stokes"].Unknowns.Einv2
    projection.smoothing = 0.0
    projection.solve()
    e_nd = np.asarray(e_var.array).ravel() / RATE
    nodes = np.asarray(chi.coords) / (cn.H_KM * 1.0e3)
    strong = np.asarray(uw.function.evaluate(S["mat"].sym[0], nodes)).ravel() > 0.5
    chi_nd = np.asarray(chi.array).ravel() / RATE
    e = e_nd
    keep = strong & (e > 0)
    shift = beta * STRESS_OVER_C * (e - chi_nd)
    floor = beta * STRESS_OVER_C * chi_nd
    scratch = uw.discretisation.MeshVariable("shift_scratch", S["mesh"], 1, degree=1)
    # the band region: the stretch of the limbs the width cuts sample (9 <= |x| <= 24
    # km), away from the notch tip, where e (and so s) is largest but not band-like
    band = keep & (np.abs(nodes[:, 0]) * cn.H_KM >= 9.0) & (np.abs(nodes[:, 0]) * cn.H_KM <= 24.0)
    out = {}
    for key, values, where in (("s", shift, keep), ("Hchi", floor, keep), ("s_band", shift, band)):
        scratch.array[:, 0, 0] = np.where(where, values, -np.inf)
        out[key + "_max"] = float(scratch.max())
        scratch.array[:, 0, 0] = np.where(where, values, np.inf)
        out[key + "_min"] = float(scratch.min())
    rows.append(dict(run=name, ref=ref, beta=beta, l_km=l_km, max_s_over_C=out["s_max"],
                     min_s_over_C=out["s_min"], band_max_s_over_C=out["s_band_max"],
                     band_min_s_over_C=out["s_band_min"],
                     floor_bound_max_Hchi_over_C=out["Hchi_max"]))
    uw.pprint(f"{name}: s/C max {out['s_max']:.3f} min {out['s_min']:.3f}  "
              f"band max {out['s_band_max']:.3f} min {out['s_band_min']:.3f}  "
              f"max H chi/C {out['Hchi_max']:.3f}")
    del S

with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        json.dump(rows, open(os.path.join(RES, str(params.uw_out)), "w"), indent=1)
