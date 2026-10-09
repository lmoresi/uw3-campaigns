"""Which preconditioner the coupled notch actually gets: one Newton step on the
production solver with ksp_view, micromorphic coupling at ref 1."""
import os
import sys

import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

S = cn.build_notch(1, 0.0, seed=True)
mesh, stokes = S["mesh"], S["stokes"]
m, e = S["mat"].sym[0], stokes.Unknowns.Einv2
chi = uw.discretisation.MeshVariable("chi", mesh, 1, degree=1, units="1/s")
H = uw.expression(r"H_{\chi}", uw.quantity(0.1 * cn.ETA_BG, "Pa*s"), "micromorphic modulus")
ell = uw.expression(r"\ell", uw.quantity(1.0, "km"), "micromorphic length")
stokes.add_coupled_field(chi, F0=H * (chi.sym[0] - m * e),
                         F1=H * ell ** 2 * chi.sym.jacobian(mesh.CoordinateSystem.N))
cn.yield_stress_with_shift(S, m * H * (e - chi.sym[0]))
stokes.petsc_options["ksp_view"] = None
cn.solve_newton(stokes, 1, True, "production")
uw.pprint("pc_fallbacks:", stokes.pc_fallbacks)
opts = stokes.petsc_options.getAll()
uw.pprint({k: v for k, v in opts.items() if k.startswith(("fieldsplit_0", "pc_fieldsplit"))})
