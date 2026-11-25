"""UNFILED 64: hash the input and output of every velocity PC application (projection outside,
the multigrid inside) in test_1157's mu 1e-4 cold solve. python apply1157.py <tag>"""
import sys, runpy, hashlib
import numpy as np
from underworld3.utilities import rotated_bc

def hv(v):
    return hashlib.sha1(v.getArray(readonly=True).tobytes()).hexdigest()[:10]

C = rotated_bc._NullModeProjectedPC
N = [0]
def apply(self, pc, x, y):
    n = N[0]; N[0] += 1
    hx = hv(x)
    x.copy(self.work)
    self._project(self.work)
    hp = hv(self.work)
    self.inner.apply(self.work, y)
    hm = hv(y)
    self._project(y)
    if n < 2:
        import traceback
        print("STACK", n, " <- ".join(f"{f.name}:{f.lineno}" for f in traceback.extract_stack()[-8:-1]), flush=True)
        print("NORM", n, "%.17e" % x.norm(), flush=True)
        np.save(f"x{n}_{sys.argv[1]}.npy", x.getArray(readonly=True).copy())
    print(f"APP {n} in {hx} projected {hp} mg_out {hm} out {hv(y)}", flush=True)
C.apply = apply

T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_1157_rotated_warm_resolve_at_roundoff.py")
v, stokes = T["_annulus"]("mu", mu=1.0e-4)
stokes.solve(zero_init_guess=True)
print("TAG", sys.argv[1], "vel_its_last", stokes._rotated_freeslip_info["vel_its_last"], flush=True)
