"""#925 round 2: what one structural LU on one rank costs at higher rank counts.

The #925 fix (fc58912c) builds the finest level's structural FAC patch from every
rank's rows and hands it whole to the rank owning most of them, so with no zone
keyed it is one LU on one rank, as in serial. Before (e67aa114) it was one block
per rank. This probe times both on the widest structural patch the split gate
takes: tests/parallel/test_1134's welded add-on, an NVB child of base_2d adapted
along the fault with width 1.0, then add_fault (patch + halo about 96 % of the
level). Run it on each overlay at np 1, 4, 8, 16 and compare the RECORD lines.

    mpirun -np 8 python probe_925_one_rank_lu.py -uw_tests ~/uw3/tests/parallel -uw_hn 4
"""
import json
import os
import resource
import sys
import time

import numpy as np
import underworld3 as uw

params = uw.Params(
    uw_tests="",          # the checkout's tests/parallel (for fault_fixtures)
    uw_hn=4,              # h_near = H_BASE / uw_hn along the guide
    uw_out="records/probe925_one_rank_lu.json",
)
sys.path.insert(0, os.path.expanduser(params.uw_tests))
from fault_fixtures import H_BASE, TIP_A, TIP_B, TRACE, base_2d  # noqa: E402

hn = float(params.uw_hn)
base = base_2d()
pts = np.column_stack([np.linspace(TIP_A[0], TIP_B[0], 9),
                       np.linspace(TIP_A[1], TIP_B[1], 9), np.zeros(9)])
guide = uw.meshing.Surface("guide_wide", base, pts)
guide.discretize()
child = base.adapt(guide.refinement_metric_function(
    h_near=H_BASE / hn, h_far=H_BASE, width=1.0, profile="linear"),
    max_levels=int(np.log2(hn)))
mesh = child.add_fault([("Flt", TRACE)], split_levels=False)

x, y = mesh.X
stokes = uw.systems.Stokes(mesh)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1
stokes.tolerance = 1.0e-6
stokes.petsc_use_pressure_nullspace = True
for side in ("Top", "Bottom", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), side)
stokes.add_fault_bc(0, "Flt")

wall = time.perf_counter()
stokes.solve()
t_first = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_again = time.perf_counter() - wall
info2 = stokes._rotated_freeslip_info

h = (getattr(stokes, "_custom_mg", None) or {}).get("hierarchy")
summary = getattr(h, "patch_summary", None)
finest = summary[-1] if summary else None
record = {
    "probe": "925_one_rank_lu", "hn": hn, "np": uw.mpi.size,
    "gate": h.fac_gate[-1] if h is not None else None,
    "patch_blocks_per_rank": finest["block_rows_per_rank"] if finest else None,
    "patch_owned_rows": finest["owned_rows"] if finest else None,
    "converged": info.get("converged"), "ksp_its": info.get("ksp_its"),
    "vel_its_last": info.get("vel_its_last"),
    "vel_its_last_again": info2.get("vel_its_last"),
    "t_solve_first_s": round(t_first, 2), "t_solve_again_s": round(t_again, 2),
    # ru_maxrss is bytes on macOS, kilobytes on Linux
    "peak_rss_mb_per_rank": [round(m / (2 ** 20 if sys.platform == "darwin" else 2 ** 10), 1)
        for m in uw.mpi.comm.allgather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)],
}
uw.pprint("RECORD " + json.dumps(record))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
