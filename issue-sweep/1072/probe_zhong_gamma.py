"""#1072: the Zhong spherical-shell response of test_1064 with Nitsche free slip.

`tests/test_1064_constrained_spherical_shell_response.py` is imported (put
`tests` on PYTHONPATH) and its `solve_response("nitsche", "default")` is run
unchanged apart from the Nitsche gamma (`-uw_gamma`). The test solves with
`snes_type ksponly`, whose SNES reason says nothing about the linear solve,
so we print the KSP reason, the linear iterations and the residual norms too.

Serial.
"""
import underworld3 as uw

import test_1064_constrained_spherical_shell_response as response

params = uw.Params(gamma=10.0)
gamma = float(params.gamma)
print(f"gamma={gamma}", flush=True)
response.NITSCHE_GAMMA = gamma

solved = {}
solve = uw.systems.Stokes.solve


def solve_and_keep(self, *args, **kwargs):
    out = solve(self, *args, **kwargs)
    solved["stokes"] = self
    return out


uw.systems.Stokes.solve = solve_and_keep

surface, cmb, reason = response.solve_response("nitsche", "default")
stokes = solved["stokes"]
ksp = stokes.snes.ksp
residual = stokes.snes.getFunction()[0].duplicate()
stokes.snes.computeFunction(stokes.snes.getSolution(), residual)

surface_error = abs(surface - response.ZHONG_SURFACE_VELOCITY) / response.ZHONG_SURFACE_VELOCITY
cmb_error = abs(cmb - response.ZHONG_CMB_VELOCITY) / response.ZHONG_CMB_VELOCITY
print(
    f"gamma {gamma:g}: surface {surface:.6e} ({100 * surface_error:.3f} % from Zhong) "
    f"cmb {cmb:.6e} ({100 * cmb_error:.3f} %) snes reason {reason} "
    f"ksp reason {ksp.getConvergedReason()} linear {ksp.getIterationNumber()} "
    f"ksp residual {ksp.getResidualNorm():.3e} |F(x)| {residual.norm():.3e}",
    flush=True,
)
