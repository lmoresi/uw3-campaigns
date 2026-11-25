"""UNFILED 64 option 3: the velocity sub-solve's floor on test_1157's mu 1e-4 case. For every
velocity sub-solve: iterations, reason, relative residual at stop, the plateau, and the right-
hand side's component along the projected null mode. With a rtol argument, the velocity sub-KSP
rtol is overridden from the probe (the library is untouched).

    python floor1157.py <tag> [vel rtol override] [cold|warm]"""
import sys, runpy, time, os
import numpy as np
from petsc4py import PETSc
tag = sys.argv[1]
arg = sys.argv[2] if len(sys.argv) > 2 else "-"
floor_rule = arg.startswith("floor")
override = float(arg) if arg not in ("-",) and not floor_rule else None
FLOOR_C = float(arg[5:] or 2.0) if floor_rule else None
if os.environ.get("NO_MDOT"):
    sys.argv += ["-vec_mdot_use_gemv", "0"]
from underworld3.utilities import rotated_bc

APPS = []
MONITORED = set()
BASE = {}
cur = {}
def monitor(ksp, its, rnorm):
    if its == 0:
        b = ksp.getRhs()
        pc = ksp.getPC()
        ratio = None
        if pc.getType() == "python":
            modes = pc.getPythonContext().modes
            bn = b.norm()
            ratio = max(abs(b.dot(m)) for m in modes) / bn if bn else 0.0
        if floor_rule and ratio is not None:
            r, a, d, m = ksp.getTolerances()
            base = BASE.setdefault(ksp.handle, r)
            ksp.setTolerances(rtol=max(base, FLOOR_C * ratio), atol=a, divtol=d, max_it=m)
        cur.clear(); cur.update(r0=rnorm, hist=[rnorm], ratio=ratio)
        APPS.append(cur.copy())
    else:
        APPS[-1]["hist"].append(rnorm)

_orig_set = rotated_bc._set_absolute_target
def set_target(ksp, abs_target, bhat, ctx):
    out = _orig_set(ksp, abs_target, bhat, ctx)
    vk, pk = ksp.getPC().getFieldSplitSubKSP()
    if override is not None:
        r, a, d, m = vk.getTolerances()
        vk.setTolerances(rtol=override, atol=a, divtol=d, max_it=m)
    if vk.handle not in MONITORED:
        vk.setMonitor(monitor)
        MONITORED.add(vk.handle)
    return out
rotated_bc._set_absolute_target = set_target

T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_1157_rotated_warm_resolve_at_roundoff.py")
v, stokes = T["_annulus"]("mu", mu=1.0e-4)
t0 = time.time()
stokes.solve(zero_init_guess=True)
t_cold = time.time() - t0
info = stokes._rotated_freeslip_info
n_cold = len(APPS)
V = np.asarray(v.array).copy()
np.save(f"vfloor_{tag}.npy", V)
its = [len(a["hist"]) - 1 for a in APPS]
rel_end = [a["hist"][-1] / a["r0"] if a["r0"] else 0 for a in APPS]
rel_min = [min(a["hist"]) / a["r0"] if a["r0"] else 0 for a in APPS]
ratio = [a["ratio"] for a in APPS]
capped = sum(1 for i in its if i >= 200)
ref = T["_annulus"]("ref", mu=1.0e-4, lu=True)
ref[1].solve(zero_init_guess=True)
VR = np.asarray(ref[0].array)
err = float(np.linalg.norm(V - VR) / np.linalg.norm(VR))
print(f"FLOOR {tag} rtol {arg} err-vs-LU {err:.2e} cold: velocity sub-solves {n_cold}, total vel its {sum(its)}, "
      f"capped {capped}, outer {info['ksp_its']} pres {info['pres_its_last']} converged {info['converged']}, "
      f"wall {t_cold:.2f}s |v| {np.linalg.norm(V):.15e}", flush=True)
for i, a in enumerate(APPS):
    if i < 3 or its[i] > 20 or i == n_cold - 1:
        print(f"APP {i} its {its[i]} r0 {a['r0']:.3e} rel_end {rel_end[i]:.2e} rel_min {rel_min[i]:.2e} "
              f"rhs-along-mode {ratio[i]:.2e}" if ratio[i] is not None else f"APP {i} its {its[i]}", flush=True)
