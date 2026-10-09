"""Band widths, peaks and the yield-floor bound for saved micromorphic runs, from their
checkpoints (no re-solve), so old and new runs are measured the same way.

For each checkpoint ``results/micromorphic/checkpoints/micro_ref<r>_xi<xi>_beta<b>_l<l>[_<tag>]``
the notch is rebuilt at ref r, v, p and chi are read (``read_timestep``, remapped by
coordinates: any decomposition), and ``coupled_notch.measure`` gives

* W from horizontal cuts (the campaign's older estimator) and from vertical cuts at
  fixed |x| (the settled one, one limb per cut);
* the peak of edot_II over the far-field background on the vertical cuts;

and ``coupled_notch.floor_bound_over_floor`` the lower bound of the yield argument over
the residual-strength floor. Everything is collective, so this runs serially or under
mpirun alike. Runs are processed one at a time, each measured before the next build
(named expressions are shared between builds, #767). Writes ../results/<out>.
"""
import glob
import json
import os
import re
import sys

import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

params = uw.Params(
    uw_pattern=uw.Param("micro_ref*_xi0_*", description="checkpoint names to measure "
                                                     "(glob, without the .mesh suffix)"),
    uw_out=uw.Param("sweep_widths.json", description="output file in results/"),
    uw_model=uw.Param("micromorphic", description="micromorphic (field chi) or cosserat "
                                                  "(field omega)"),
)
RES = os.path.join(_here, "..", "results")
MODEL = str(params.uw_model)
CHECKPOINTS = os.path.join(RES, MODEL, "checkpoints")
FIELD = dict(micromorphic="chi", cosserat="omega")[MODEL]
NAME = dict(
    micromorphic=re.compile(r"micro_ref(\d)_xi([\d.]+)_beta([\d.]+)_l([\d.]+)(?:_(\w+))?$"),
    cosserat=re.compile(r"cosserat_ref(\d)_xi([\d.]+)_c([\d.]+)_l([\d.]+)_P(\d)(?:_(\w+))?$"),
)[MODEL]

names = sorted({os.path.basename(p).split(".mesh.")[0]
                for p in glob.glob(os.path.join(CHECKPOINTS, str(params.uw_pattern) + ".mesh.U.00000.h5"))})
rows = []
for name in names:
    match = NAME.match(name)
    if match is None:
        continue
    if MODEL == "micromorphic":
        ref, xi, beta, l_km, tag = match.groups()
        degree = 1
    else:
        ref, xi, beta, l_km, degree, tag = match.groups()   # beta holds c here
    ref, xi, beta, l_km, degree = int(ref), float(xi), float(beta), float(l_km), int(degree)
    record_path = os.path.join(RES, MODEL, name + ".json")
    record = json.load(open(record_path)) if os.path.exists(record_path) else {}
    if not record.get("converged", False):
        continue

    S = cn.build_notch(ref, xi, seed=False)
    coupled = uw.discretisation.MeshVariable(FIELD, S["mesh"], 1, degree=degree, units="1/s")
    for var in (S["v"], S["p"], coupled):
        var.read_timestep(name, var.name, 0, outputPath=CHECKPOINTS)

    measured = cn.measure(S, os.path.join(RES, MODEL), name)
    rows.append(dict(
        run=name, ref=ref, xi=xi, beta=beta, l_km=l_km, tag=tag or "",
        h_min_km=float(S["mesh"].get_min_radius()) * cn.H_KM,
        nl_its=record.get("nl_its"), linear=record.get("linear", "exact"),
        W_horizontal_km=measured["W_horizontal_km"], W_vertical_km=measured["W_vertical_km"],
        W_integral_km=measured["W_integral_km"], relative_peak=measured["relative_peak"],
        dip_vertical_deg={s: (None if b is None else b["dip_deg"])
                          for s, b in measured["bands_vertical"].items()},
        floor_bound_over_floor=(cn.floor_bound_over_floor(S, coupled, beta)
                                if MODEL == "micromorphic" else None),
    ))
    uw.pprint(f"{name}: W_int {rows[-1]['W_integral_km']['median']:.2f}  "
              f"peak {rows[-1]['relative_peak']}")
    del S

with uw.selective_ranks(0) as rank0:      # the body runs on every rank: test the flag
    if rank0:
        with open(os.path.join(RES, str(params.uw_out)), "w") as fh:
            json.dump(rows, fh, indent=1)
