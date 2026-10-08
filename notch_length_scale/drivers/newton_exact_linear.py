"""Newton on the notch with every linear solve EXACT: MUMPS LU of the true Jacobian.

If the iteration then converges in a handful of steps where the production solve (FMG
velocity block, Schur fieldsplit, Eisenstat-Walker) crawls or fails, the slow tail is the
linear solver and not the tangent or the nonlinear landscape. Cold start from the viscous
seed, the scan's default/newton configuration; band widths with the scan's estimator.
"""
import json
import os
import sys
import time

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import notch_model as nm

params = uw.Params(
    uw_xi=uw.Param(0.01, description="xi (eta_reg = xi * eta_bg)"),
    uw_ref=uw.Param(3, description="refinement"),
    uw_budget=uw.Param(60, description="Newton iterations"),
    uw_out=uw.Param("", description="json output"),
    uw_snes=uw.Param("newtonls", description="SNES type: newtonls (line search) or newtontr (trust region)"),
)
ETA_BG, U_MMYR, H_KM = 1.0e23, 5.0, 30.0
MESH = os.path.join(_here, "..", "meshes", "notch_mesh1.msh")
xi = float(params.uw_xi)

S = nm.build(MESH, ETA_BG, U_MMYR, 30.0, int(params.uw_ref), xi=0.0, seed=True,
             p_degree=1, p_continuous=True)
cm = S["cm"]
cm.yield_mode = "softmin"; cm.yield_smoother = "sqrt"; cm.yield_anchor = "onset"
cm.yield_softness = 0.1
if xi > 0.0:
    cm.Parameters.plastic_rate_strengthening = uw.quantity(xi * ETA_BG, "Pa*s")
st = S["stokes"]
st.consistent_jacobian = True
# the PC matrix = the Jacobian: no 1/eta pressure-mass block (that block is the
# Schur preconditioner's; LU of it is not a solve of J)
st.saddle_preconditioner = 0
st.petsc_options["snes_max_it"] = int(params.uw_budget)
st.petsc_options["snes_monitor_short"] = None
st.petsc_options["snes_linesearch_monitor"] = None

Solver = uw.systems.Stokes
_orig = Solver._snes_solve_with_retries


def _exact_linear(self, gvec, divergence_retries=0, verbose=False):
    ksp = self.snes.getKSP()
    J, P = ksp.getOperators()
    ksp.setOperators(J, J)            # factor the operator itself, not the Schur Pmat
    ksp.setType("preonly")
    pc = ksp.getPC()
    pc.setType("lu")
    pc.setFactorSolverType("mumps")
    if str(params.uw_snes) != self.snes.getType():
        self.snes.setType(str(params.uw_snes))
    return _orig(self, gvec, divergence_retries=divergence_retries, verbose=verbose)


Solver._snes_solve_with_retries = _exact_linear
t0 = time.time()
st.solve(zero_init_guess=False)
rep = st.solve_report
spec = __import__("importlib.util").util.spec_from_file_location(
    "bw", os.path.join(_here, "band_width_vs_h.py"))
sys.argv = [sys.argv[0]]
bw = __import__("importlib.util").util.module_from_spec(spec)
spec.loader.exec_module(bw)
bands = bw.measure_bands(S, [-0.7, -0.6, -0.5, -0.4], 4001, 1.85, H_KM)
W = {k: (None if v is None else v.get("W_equiv_km")) for k, v in bands.items()}
out = dict(xi=xi, ref=int(params.uw_ref), reason=rep.reason_str, its=rep.nl_its,
           ksp=rep.ksp_its, seconds=time.time() - t0, bands=W)
uw.pprint(f"[exact-LU {params.uw_snes}] ref {params.uw_ref} xi {xi}: {rep.reason_str} its {rep.nl_its} "
          f"({out['seconds']:.0f} s)  W_L/W_R {W}")
name = str(params.uw_out) or os.path.join(
    _here, "..", "results", "recipe_scan", "exact_lu", f"newton_lu_{params.uw_snes}_xi{xi:g}_ref{params.uw_ref}.json")
os.makedirs(os.path.dirname(name), exist_ok=True)
if uw.mpi.rank == 0:
    with open(name, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
