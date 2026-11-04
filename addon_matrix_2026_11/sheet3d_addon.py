"""A clean 3-D add-on for the patch-solve probes: a uniform base, a disc sheet
placed conforming in it (add_conforming_sheet), split, and the base's own levels
under it (set_custom_fmg), so the finest pair differs only around the sheet.
No adapt. Shear between Bottom (at rest) and Top (unit x velocity), the sheet
frictionless. uw_div sets the sheet's element size as the fixtures' H_NEAR / div;
uw_cover forces the 0.75 cover gate's threshold (0.9 takes the 79 % patch at
div 4, the default declines it).

    python sheet3d_addon.py -uw_tests ~/uw3/tests/parallel -uw_div 4 -uw_cover 0.9
"""
import json
import os
import resource
import sys
import time

import sympy
import underworld3 as uw
from underworld3.utilities import custom_mg
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_split import split_fault

params = uw.Params(
    uw_tests="",              # the checkout's tests/parallel (for fault_fixtures)
    uw_ref=1,                 # base refinement (cellSize 0.2)
    uw_div=4.0,               # sheet element size H_NEAR / uw_div
    uw_cover=0.75,            # the cover gate's threshold for this run
    uw_out="records/sheet3d.json",
)
sys.path.insert(0, os.path.expanduser(params.uw_tests))
from fault_fixtures import H_NEAR, disc_sheet  # noqa: E402

custom_mg._FAC_COVER_MAX = float(params.uw_cover)
wall = time.perf_counter()
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0, 0.0, 0.0), maxCoords=(1.0, 1.0, 1.0),
                                         cellSize=0.2, regular=False, qdegree=2,
                                         refinement=int(params.uw_ref))
levels = base._coarse_level_meshes()[:-1] + [base]
pts, tris = disc_sheet()
mesh = split_fault(base.add_conforming_sheet(pts, tris, "Fault",
                                             size=H_NEAR / float(params.uw_div)), "Fault")
t_mesh = time.perf_counter() - wall
v = uw.discretisation.MeshVariable("v", mesh, 3, degree=2)
p = uw.discretisation.MeshVariable("p", mesh, 1, degree=1)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = sympy.Matrix([0, 0, 0])
stokes.tolerance = 1e-4
stokes.add_dirichlet_bc((0.0, 0.0, 0.0), "Bottom")
stokes.add_dirichlet_bc((1.0, 0.0, 0.0), "Top")
stokes.add_fault_bc(0.0, "Fault")
set_custom_fmg(stokes, levels, field_id=0)
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_solve = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
h = stokes._custom_mg["hierarchy"]
record = {
    "probe": "sheet3d_addon", "np": uw.mpi.size, "ref": int(params.uw_ref),
    "div": float(params.uw_div), "cover": float(params.uw_cover), "t_mesh_s": round(t_mesh, 1),
    "gate": h.fac_gate[-1], "converged": info.get("converged"),
    "vel_its_last": info.get("vel_its_last"), "t_solve_s": round(t_solve, 1),
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
