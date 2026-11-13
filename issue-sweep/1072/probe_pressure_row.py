"""#1072: is the Nitsche pressure-row boundary term in the residual and the Jacobian,
and is the assembled system solvable?

For test_1060's box with the Top and Bottom condition made by Nitsche, and with
no condition there (same unknowns):
- the residual at one random state, velocity rows and pressure rows apart;
- the Jacobian against differences of the residual (the problem is linear);
- the smallest singular values of J, its right and left null vectors, and the
  part of the right-hand side along the left null vector, which is the smallest
  residual any solver can reach.

Serial. `-uw_res N` sets the resolution.
"""
import numpy as np
import underworld3 as uw
from petsc4py import PETSc
from probe_p_blocks import build, params  # prints the banner and the block table again

res = params.res


def dense(M):
    ia, ja, a = M.getValuesCSR()
    import scipy.sparse as sp
    return sp.csr_matrix((a, ja, ia), shape=M.getSize()).toarray()


def residual(s, x):
    f = x.duplicate()
    s.snes.computeFunction(x, f)
    out = f.array.copy()
    f.destroy()
    return out


print("\n===== pressure row =====", flush=True)
state = {}
for method in ("none", "nitsche", "essential"):
    s = build(method, res)
    try:
        s.solve()
    except Exception as err:
        print(method, "solve raised", type(err).__name__)
    J, P, _ = s.snes.getJacobian()
    _, ises, _ = s.dm.createFieldDecomposition()
    iu, ip = ises[0].getIndices().copy(), ises[1].getIndices().copy()
    x = J.createVecRight()
    n = x.getSize()
    rng = np.random.default_rng(1072)
    xr = rng.standard_normal(n)
    x.array[:] = xr
    F = residual(s, x)
    x.array[:] = 0.0
    F0 = residual(s, x)
    Jd = dense(J)
    # the residual is affine in the unknowns, so differences give its Jacobian exactly
    Jfd = np.empty((n, n))
    for j in range(n):
        x.array[:] = 0.0
        x.array[j] = 1.0
        Jfd[:, j] = residual(s, x) - F0
    state[method] = dict(F=F, F0=F0, J=Jd, Jfd=Jfd, iu=iu, ip=ip, xr=xr)
    print(f"{method}: unknowns {n} (u {iu.size}, p {ip.size}); "
          f"|J - dF/dx| u rows {np.linalg.norm((Jd - Jfd)[iu]):.3e}, p rows {np.linalg.norm((Jd - Jfd)[ip]):.3e}; "
          f"|J| {np.linalg.norm(Jd):.3e}", flush=True)

    U, sv, Vt = np.linalg.svd(Jd)
    print(f"  smallest singular values {sv[-4:][::-1]}, largest {sv[0]:.3e}")
    r, l = Vt[-1], U[:, -1]
    one_p = np.zeros(n); one_p[ip] = 1.0; one_p /= np.linalg.norm(one_p)
    b = -F0
    print(f"  right null vector: |u part| {np.linalg.norm(r[iu]):.3e}, overlap with constant pressure {abs(r @ one_p):.6f}")
    print(f"  left  null vector: |u part| {np.linalg.norm(l[iu]):.3e}, overlap with constant pressure {abs(l @ one_p):.6f}")
    print(f"  right-hand side |b| {np.linalg.norm(b):.6e}; along the left null vector {abs(l @ b):.6e}; "
          f"along constant pressure {abs(one_p @ b):.6e}")
    xl, *_ = np.linalg.lstsq(Jd, b, rcond=1e-12)
    print(f"  least-squares residual |J x - b| {np.linalg.norm(Jd @ xl - b):.6e}", flush=True)

a, c = state["none"], state["nitsche"]
print("\nresidual at one random state, Nitsche minus no condition:")
print(f"  velocity rows {np.linalg.norm((c['F'] - a['F'])[a['iu']]):.6e}")
print(f"  pressure rows {np.linalg.norm((c['F'] - a['F'])[a['ip']]):.6e}")
print("Jacobian from residual differences, Nitsche minus no condition:")
d = c["Jfd"] - a["Jfd"]
iu, ip = a["iu"], a["ip"]
for name, (rr, cc) in {"uu": (iu, iu), "up": (iu, ip), "pu": (ip, iu), "pp": (ip, ip)}.items():
    print(f"  {name}: {np.linalg.norm(d[np.ix_(rr, cc)]):.6e}")
