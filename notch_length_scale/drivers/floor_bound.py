"""Does the residual-strength floor of the micromorphic yield law ever engage?

The yield argument is  a = C_eff + sin(phi) p + H (edot_II - chi),  floored at
s_min = 0.02 C. Since edot_II >= 0 and C_eff >= C (the cohesion bracket only adds),

    a >= C + sin(phi) p - H chi,

which needs only the saved nodal pressure and chi (both P1, same nodes). If that lower
bound stays above s_min at every strong-layer node, the floor cannot engage anywhere.
Everything is non-dimensional: stresses by eta_bg V / H, rates by V / H.

(Evaluating the full argument with uw.function.evaluate on a rebuilt notch mixes
non-dimensional and dimensional terms - edot_II comes back negative at some nodes and
C_eff with units Pa/s - so this bound uses saved arrays only.)
Writes ../results/floor_bound.json.
"""
import glob
import json
import os
import re

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(_here, "..", "results", "micromorphic")
ETA_BG, V_MMYR, H_KM, PHI, C_PA = 1.0e23, 5.0, 30.0, 30.0, 1.0e8
SECONDS_PER_YEAR = 365.25 * 24 * 3600
RATE = V_MMYR * 1.0e-3 / SECONDS_PER_YEAR / (H_KM * 1.0e3)      # V / H, 1/s
STRESS = ETA_BG * RATE                                             # Pa
NAME = re.compile(r"fields_micro_ref(\d)_xi([\d.]+)_beta([\d.]+)_l([\d.]+)(?:_(\w+))?\.npz")

rows = []
for path in sorted(glob.glob(os.path.join(M, "fields_micro_ref*_xi0_*.npz"))):
    match = NAME.match(os.path.basename(path))
    ref, xi, beta, l_km, tag = match.groups()
    f = np.load(path)
    if not np.allclose(f["p_coords"], f["chi_coords"]):
        raise ValueError(f"{path}: pressure and chi nodes differ")
    p = f["p"].ravel()                          # non-dimensional
    chi = f["chi"].ravel() / RATE               # saved in 1/s
    y = np.asarray(f["p_coords"])[:, 1]
    strong = y > -0.7 * H_KM * 1.0e3            # the strong layer sits above the weak one
    bound = (C_PA / STRESS + np.sin(np.deg2rad(PHI)) * p - float(beta) * chi)[strong]
    floor = 0.02 * C_PA / STRESS
    rows.append(dict(run=os.path.basename(path), ref=int(ref), beta=float(beta),
                     l_km=float(l_km), tag=tag or "",
                     min_lower_bound_over_floor=float(bound.min() / floor),
                     max_beta_chi_over_cohesion=float(float(beta) * chi.max() / (C_PA / STRESS))))
    print(f"{rows[-1]['run']}: min lower bound / floor {rows[-1]['min_lower_bound_over_floor']:.1f}"
          f"   max H chi / C {rows[-1]['max_beta_chi_over_cohesion']:.2f}")

with open(os.path.join(_here, "..", "results", "floor_bound.json"), "w") as fh:
    json.dump(rows, fh, indent=1)
