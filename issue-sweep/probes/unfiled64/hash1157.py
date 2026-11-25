"""UNFILED 64: fingerprint every input of the rotated solve and the velocity MG it builds, for
test_1157's mu 1e-4 cold solve. Run several times and diff the HASH lines. python hash1157.py <tag>"""
import sys, runpy, hashlib, os
if os.environ.get("NO_MDOT"):
    sys.argv += ["-vec_mdot_use_gemv", "0"]
if os.environ.get("NO_MAXPY"):
    sys.argv += ["-vec_maxpy_use_gemv", "0"]
if os.environ.get("NO_GEMV"):
    sys.argv += ["-vec_mdot_use_gemv", "0", "-vec_maxpy_use_gemv", "0"]
if os.environ.get("MALLOC_DEBUG"):
    sys.argv += ["-malloc_debug"]
import numpy as np
from underworld3.utilities import rotated_bc

def h_mat(M):
    try:
        ai, aj, a = M.getValuesCSR()
        return hashlib.sha1(ai.tobytes() + aj.tobytes() + a.tobytes()).hexdigest()[:12] + f" nnz {len(a)}"
    except Exception as e:
        try:
            return "dense/other " + hashlib.sha1(M.convert("aij").getValuesCSR()[2].tobytes()).hexdigest()[:12]
        except Exception:
            return f"unhashable {type(M).__name__}"

def h_vec(v):
    a = v.getArray(readonly=True)
    return hashlib.sha1(a.tobytes()).hexdigest()[:12] + " |%.17e|" % float(np.linalg.norm(a))

_orig = rotated_bc._solve_rotated_iterative
CALL = [0]
def wrapped(solver, Ahat, bhat, Q, Qt, normal_rows, *a, **kw):
    k = CALL[0]; CALL[0] += 1
    print(f"HASH call{k} Ahat {h_mat(Ahat)}", flush=True)
    print(f"HASH call{k} bhat {h_vec(bhat)}", flush=True)
    print(f"HASH call{k} Q {h_mat(Q)}", flush=True)
    nsp = kw.get("nsp")
    if nsp is not None:
        print(f"HASH call{k} nsp constant {nsp.hasConstant()}", flush=True)
        for i, w in enumerate(nsp.getVecs()):
            print(f"HASH call{k} nsp[{i}] {h_vec(w)}", flush=True)
    for name in ("custom_Pl", "Mp"):
        obj = kw.get(name)
        if obj is None:
            continue
        for i, m in enumerate(obj if isinstance(obj, (list, tuple)) else [obj]):
            print(f"HASH call{k} {name}[{i}] {h_mat(m)}", flush=True)
    out = _orig(solver, Ahat, bhat, Q, Qt, normal_rows, *a, **kw)
    ctx = out[2]
    vk, pk = ctx["pc"].getFieldSplitSubKSP()
    pc = vk.getPC()
    if pc.getType() == "python":
        pc = pc.getPythonContext().inner
    vpc = vk.getPC()
    if vpc.getType() == "python":
        for i, m in enumerate(vpc.getPythonContext().modes):
            print(f"HASH call{k} mode{i} {h_vec(m)}", flush=True)
    print(f"HASH call{k} velpc {pc.getType()}", flush=True)
    if pc.getType() == "mg":
        for l in range(pc.getMGLevels()):
            A, P = pc.getMGSmoother(l).getOperators() if l else pc.getMGCoarseSolve().getOperators()
            print(f"HASH call{k} level{l} A {h_mat(A)}", flush=True)
            if l:
                print(f"HASH call{k} level{l} interp {h_mat(pc.getMGInterpolation(l))}", flush=True)
    print(f"HASH call{k} Uhat {h_vec(out[0])}", flush=True)
    return out
rotated_bc._solve_rotated_iterative = wrapped

T = runpy.run_path("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/sweep-2026-11-15/tests/test_1157_rotated_warm_resolve_at_roundoff.py")
v, stokes = T["_annulus"]("mu", mu=1.0e-4)
stokes.solve(zero_init_guess=True)
print("TAG", sys.argv[1], "vel_its_last", stokes._rotated_freeslip_info["vel_its_last"], flush=True)
