"""Why a prolonged start has a large residual: compare the prolonged ref-3 state with
the converged ref-3 solution, field by field, and the residual of each."""
import os
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

M = os.path.join(_here, "..", "results", "micromorphic")
coarse = cn.load_coarse(os.path.join(M, "fields_micro_ref2_xi0_beta0.1_l1.npz"), 2, 0.0,
                        dict(chi=(1, 1, True, "1/s")))
S = cn.build_notch(3, 0.0, seed=False)
mesh, stokes = S["mesh"], S["stokes"]
m, e = S["mat"].sym[0], stokes.Unknowns.Einv2
chi = uw.discretisation.MeshVariable("chi", mesh, 1, degree=1, units="1/s")
H = uw.expression(r"H_{\chi}", uw.quantity(0.1 * cn.ETA_BG, "Pa*s"), "micromorphic modulus")
ell = uw.expression(r"\ell", uw.quantity(1.0, "km"), "micromorphic length")
stokes.add_coupled_field(chi, F0=H * (chi.sym[0] - m * e),
                         F1=H * ell ** 2 * chi.sym.jacobian(mesh.CoordinateSystem.N))
cn.yield_stress_with_shift(S, m * H * (e - chi.sym[0]))
fine = dict(v=S["v"], p=S["p"], chi=chi)

converged = np.load(os.path.join(M, "fields_micro_ref3_xi0_beta0.1_l1.npz"))
cn.prolong(coarse, fine)
for key, var in fine.items():
    a = np.asarray(var.array).ravel()
    b = converged[key].ravel()
    print(f"{key}: prolonged range [{a.min():.3e},{a.max():.3e}]  converged range "
          f"[{b.min():.3e},{b.max():.3e}]  max|diff|/max|conv| "
          f"{np.abs(a - b).max() / np.abs(b).max():.3e}", flush=True)

stokes.petsc_options["snes_max_it"] = 0
stokes.petsc_options["snes_monitor_short"] = None
stokes.consistent_jacobian = True
print("residual of the prolonged state:", flush=True)
stokes.solve(zero_init_guess=False)
for key, var in fine.items():
    values = converged[key].reshape(var.array.shape)
    if var.units is not None:
        values = uw.utilities.UnitAwareArray(values, units=var.units)
    var.array[...] = values
print("residual of the converged ref-3 state, loaded the same way:", flush=True)
stokes.solve(zero_init_guess=False)
