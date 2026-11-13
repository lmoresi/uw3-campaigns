"""#1072: what the Nitsche system looks like with the pressure-row boundary term put back.

The term PETSc never integrates is  s * int_Gamma q (n.d)(u.d - g)  in the
continuity row. Its matrix is the transpose of the change the Nitsche condition
makes to the velocity-pressure block, so it can be added to the assembled J
here without touching the library. We try s = +1 (the sign `add_nitsche_bc`
writes in `fn_p`) and s = -1, and compare each solution with the essential-BC
solution on the unknowns the two share.

Serial. `-uw_res N` sets the resolution.
"""
import numpy as np
import underworld3 as uw
from probe_p_blocks import build, params
from probe_pressure_row import state  # runs that probe again; reuses its matrices

iu, ip = state["nitsche"]["iu"], state["nitsche"]["ip"]
n = state["nitsche"]["J"].shape[0]
dUP = (state["nitsche"]["J"] - state["none"]["J"])[np.ix_(iu, ip)]
b = -state["nitsche"]["F0"]
one_p = np.zeros(n); one_p[ip] = 1.0; one_p /= np.linalg.norm(one_p)


def dof_map(s):
    """(mesh point, velocity component) -> global unknown, for unconstrained velocity unknowns."""
    dm = s.dm
    sec, gsec = dm.getLocalSection(), dm.getGlobalSection()
    p0, p1 = sec.getChart()
    out = {}
    for q in range(p0, p1):
        nd = sec.getFieldDof(q, 0)
        if nd == 0:
            continue
        off = gsec.getFieldOffset(q, 0)
        fixed = set(int(c) for c in sec.getFieldConstraintIndices(q, 0))
        k = 0
        for c in range(nd):
            if c in fixed:
                continue
            out[(q, c)] = off + k
            k += 1
    return out


maps, sols = {}, {}
for method in ("essential", "nitsche"):
    s = build(method, params.res)
    try:
        s.solve()
    except Exception:
        pass
    maps[method] = dof_map(s)
    sols[method + "_snes"] = s.snes.getSolution().array.copy()

Je, be = state["essential"]["J"], -state["essential"]["F0"]
xe = np.linalg.lstsq(Je, be, rcond=1e-12)[0]
common = sorted(set(maps["essential"]) & set(maps["nitsche"]))
wall = sorted(set(maps["nitsche"]) - set(maps["essential"]))
ie = np.array([maps["essential"][k] for k in common])
inn = np.array([maps["nitsche"][k] for k in common])
iw = np.array([maps["nitsche"][k] for k in wall])
print(f"\n===== the missing block =====\nshared velocity unknowns {len(common)}, wall-normal unknowns only Nitsche has {len(wall)}")
print(f"essential: dense solve against its own SNES solution, shared unknowns: "
      f"{np.linalg.norm(xe[ie] - sols['essential_snes'][ie]) / np.linalg.norm(xe[ie]):.3e}")


def report(tag, J):
    U, sv, Vt = np.linalg.svd(J)
    l, r = U[:, -1], Vt[-1]
    x = np.linalg.lstsq(J, b, rcond=1e-12)[0]
    print(f"{tag}: smallest singular values {sv[-1]:.3e}, {sv[-2]:.3e}; "
          f"right null vector on constant pressure {abs(r @ one_p):.6f}, left {abs(l @ one_p):.6f}; "
          f"|l.b| {abs(l @ b):.3e}; least-squares residual {np.linalg.norm(J @ x - b):.3e}")
    print(f"    velocity against essential on shared unknowns {np.linalg.norm(x[inn] - xe[ie]) / np.linalg.norm(xe[ie]):.4e}; "
          f"largest wall-normal velocity {np.abs(x[iw]).max():.4e}; |J - J^T| {np.linalg.norm(J - J.T):.3e}; "
          f"|J_pu + J_up^T| {np.linalg.norm(J[np.ix_(ip, iu)] + J[np.ix_(iu, ip)].T):.3e}", flush=True)
    return x


J0 = state["nitsche"]["J"]
report("as assembled      ", J0)
for sgn in (+1.0, -1.0):
    J = J0.copy()
    J[np.ix_(ip, iu)] += sgn * dUP.T
    report(f"with the term, s={sgn:+.0f}", J)
xs = sols["nitsche_snes"]
print(f"the SNES solution of the Nitsche solve: velocity against essential {np.linalg.norm(xs[inn] - xe[ie]) / np.linalg.norm(xe[ie]):.4e}; "
      f"largest wall-normal velocity {np.abs(xs[iw]).max():.4e}")
