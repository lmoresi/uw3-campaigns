"""Is the FAC patch block near-singular, or only badly scaled? (serial only)

The library factors each patch block with PETSc's LU and a nonzero shift: its own
LU and ILU do not pivot, and unshifted they take a zero pivot on the rotated
Galerkin block, whose diagonal falls to ~1e-5 beside the constraints. MUMPS,
which pivots, factored the same blocks with no shift (kaiju report 17). A small
diagonal is not a small singular value, so this probe measures the blocks the
library actually factors (PCASM's local submatrices, overlap included) and, for
comparison, the whole finest-level velocity operator:

- symmetry: |A - A^T|_F / |A|_F
- the diagonal: min and max |a_ii|
- the 2-norm condition number, sigma_max / sigma_min (sigma_min from the inverse
  by Lanczos on A^-T A^-1 with a sparse LU, sigma_max by Lanczos on A^T A)
- the same for the Jacobi-scaled D^-1/2 A D^-1/2, D = |diag A|: if that is modest,
  the trouble is scaling, which pivoting or diagonal scaling removes; if not, the
  block is ill-conditioned in itself.

It runs the row 5 driver with its own arguments and prints one PROBECOND line.

    python probe_patch_conditioning.py -uw_case ti -uw_zone none -uw_n_rungs 80 -uw_out records/x.json
"""
import json
import os
import runpy
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(HERE, "row5_networks.py")

from underworld3.utilities import custom_mg  # noqa: E402

RESULT = {}


def _csr(M):
    ai, aj, av = M.getValuesCSR()
    return sp.csr_matrix((av, aj, ai), shape=M.getSize())


def _sigma_extremes(A):
    """The largest and smallest singular values of the sparse square A."""
    n = A.shape[0]
    AT = A.T.tocsr()
    big = spla.eigsh(spla.LinearOperator((n, n), matvec=lambda x: AT @ (A @ x)),
                     k=1, which="LA", return_eigenvectors=False, tol=1e-6)
    lu = spla.splu(A.tocsc())
    inv = spla.eigsh(spla.LinearOperator(
        (n, n), matvec=lambda x: lu.solve(lu.solve(x), trans="T")),
        k=1, which="LA", return_eigenvectors=False, tol=1e-6)
    return float(np.sqrt(big[0])), float(1.0 / np.sqrt(inv[0]))


def _measure(A):
    d = np.abs(A.diagonal())
    s_max, s_min = _sigma_extremes(A)
    scale = sp.diags(1.0 / np.sqrt(d))
    As = (scale @ A @ scale).tocsr()
    t_max, t_min = _sigma_extremes(As)
    return {
        "rows": int(A.shape[0]),
        "asymmetry": float(spla.norm(A - A.T) / spla.norm(A)),
        "diag_min": float(d.min()), "diag_max": float(d.max()),
        "sigma_max": s_max, "sigma_min": s_min, "cond": s_max / s_min,
        "cond_jacobi_scaled": t_max / t_min,
    }


def _probe_set_up(pc, fac_keys):
    _set_up(pc, fac_keys)
    levels = [l for l in range(1, pc.getMGLevels())
              if any(k.startswith(f"mg_levels_{l}_") for k in (fac_keys or []))]
    if not levels or RESULT:
        return
    smoother = pc.getMGSmoother(levels[-1])
    asm = smoother.getPC().getCompositePC(1)
    RESULT["blocks"] = [_measure(_csr(k.getOperators()[1])) for k in asm.getASMSubKSP()]
    RESULT["level"] = _measure(_csr(smoother.getOperators()[1]))


_set_up = custom_mg._set_up_fac_smoothers
custom_mg._set_up_fac_smoothers = _probe_set_up
runpy.run_path(sys.argv[0], run_name="__main__")
print("PROBECOND " + json.dumps(RESULT), flush=True)
