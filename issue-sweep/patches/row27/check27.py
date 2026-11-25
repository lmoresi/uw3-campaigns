"""Row 27 checks. (a) Which KSPs share the velocity block A_vv (and so its transpose null space).
(b) After a BC change and after a mesh move, the transpose null space matches the modes the
new setup admits (never a stale one)."""
import runpy
import numpy as np
from underworld3.utilities import rotated_bc
T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_0895_rotated_velocity_subsolve_null_mode_rhs.py")

def state(stokes, label):
    ctx = stokes._rotated_linear_cache["ctx"]
    vk, pk = ctx["pc"].getFieldSplitSubKSP()
    A_vv = vk.getOperators()[0]
    tns = A_vv.getTransposeNullSpace()
    n_tns = 0 if tns is None or tns.handle == 0 else len(tns.getVecs())
    shell = vk.getPC()
    n_shell = len(shell.getPythonContext().modes) if shell.getType() == "python" else 0
    print(f"STATE {label}: admitted {ctx['projected_null_modes']} shell modes {n_shell} "
          f"A_vv transpose null space {n_tns} A_vv handle {A_vv.handle}", flush=True)
    return ctx, vk, A_vv

# (a)
v, stokes = T["_annulus"]("a")
stokes.solve(zero_init_guess=True)
ctx, vk, A_vv = state(stokes, "free-slip both")
mg = vk.getPC().getPythonContext().inner
L = mg.getMGLevels()
for l in range(L):
    k = mg.getMGCoarseSolve() if l == 0 else mg.getMGSmoother(l)
    print(f"SHARE MG level {l} ({k.getType()}) operator is A_vv: {k.getOperators()[0].handle == A_vv.handle}")
S = ctx["pc"].getFieldSplitSubKSP()[1].getOperators()[0]
try:
    inner = S.getSchurComplementKSP()
    print(f"SHARE Schur complement inner KSP is the velocity sub-KSP: {inner.handle == vk.handle}; "
          f"its operator is A_vv: {inner.getOperators()[0].handle == A_vv.handle}")
except Exception as e:
    print("SHARE Schur", type(S), e)
print(f"SHARE SchurRoundoffTest A10 is a separate submatrix of Ahat: {ctx['schur_roundoff'].A10.handle != A_vv.handle}")

# (b1) BC change on the same solver: free-slip lower -> no-slip lower
v2, s2 = T["_annulus"]("b")
s2.solve(zero_init_guess=True)
state(s2, "b: before the BC change")
s2.add_dirichlet_bc((0.0, 0.0), "Lower")
try:
    s2.solve(zero_init_guess=True)
    state(s2, "b: after adding no-slip on Lower")
except Exception as e:
    print("BCCHANGE raised", type(e).__name__, str(e)[:200])

# (b2) a mesh move: deform the annulus radially (not a rigid rotation), re-solve
v3, s3 = T["_annulus"]("c")
s3.solve(zero_init_guess=True)
state(s3, "c: before the move")
mesh = s3.mesh
X = np.asarray(mesh.X.coords).copy()
r = np.hypot(X[:, 0], X[:, 1]); th = np.arctan2(X[:, 1], X[:, 0])
rn = r + 0.01 * np.sin(3 * th) * (r - 0.5) * (1.0 - r) * 4
mesh.deform(np.column_stack([rn * np.cos(th), rn * np.sin(th)]))
s3.solve(zero_init_guess=True)
state(s3, "c: after a non-rigid move")
