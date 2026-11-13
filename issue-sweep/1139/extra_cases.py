"""Extra add_condition cases. Serial. usage: python extra_cases.py <case>"""
import sys, json, hashlib, warnings
import numpy as np, sympy
import underworld3 as uw
from truth_table import stokes2d, stokes3d

def run(case):
    out = {"case": case}
    if case.startswith("s3"):
        mesh, s, v, p = stokes3d()
    else:
        mesh, s, v, p = stokes2d()
    calls = {
        "blist_short":   lambda: s.add_dirichlet_bc((0.0), ["Top", "Left"], [1]),
        "blist_full":    lambda: s.add_dirichlet_bc((None, 0.0), ["Top", "Left"]),
        "dup_001_len2":  lambda: s.add_dirichlet_bc((0.01, 0.05), "Left", (0, 0, 1)),
        "dup_11_full":   lambda: s.add_dirichlet_bc((None, 0.05), "Left", (1, 1)),
        "neg_m1_0_len1": lambda: s.add_dirichlet_bc((0.05,), "Left", (-1, 0)),
        "nat_scalar":    lambda: s.add_natural_bc(0.05, "Left"),
        "nat_len1_c0":   lambda: s.add_natural_bc((0.05,), "Left", 0),
        "s3_len2_c12_b": lambda: s.add_dirichlet_bc((0.01, 0.05), "Left", (1, 2)),
        "s3_scalar_c1":  lambda: s.add_dirichlet_bc(0.05, "Left", 1),
        "c01_len1":      lambda: s.add_dirichlet_bc((0.05,), "Left", (0, 1)),
        "npfloat_c1":    lambda: s.add_dirichlet_bc(np.float64(0.05), "Left", 1),
        "empty_c1":      lambda: s.add_dirichlet_bc((), "Left", 1),
    }
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            calls[case]()
        out["add"] = "accepted"
        out["fn"] = [str(b.fn) for b in s.essential_bcs[2:]] + [str(b.fn) for b in s.natural_bcs]
        out["components"] = [list(map(int, b.components)) for b in s.essential_bcs[2:]] + [list(map(int, b.components)) for b in s.natural_bcs]
    except Exception as e:
        out["add"] = f"{type(e).__name__}: {e}"
        print("RESULT " + json.dumps(out)); return
    try:
        s.solve()
        out["solve"] = "ran"
        out["snes_reason"] = int(s.snes.getConvergedReason())
        out["u_hash"] = hashlib.sha256(np.ascontiguousarray(v.array).tobytes()).hexdigest()[:16]
    except Exception as e:
        out["solve"] = f"{type(e).__name__}: {str(e)[:200]}"
    print("RESULT " + json.dumps(out))

run(sys.argv[1])
