"""Add-on matrix row 3: the FAC cover gate on a UNIFORMLY refined finest level, the case
the 0.75 gate exists to skip. UnstructuredSimplexBox(cellSize=1/8, refinement=2), no
fault, simple shear on the walls, custom FMG on the base levels; records the finest
level's structural patch and subdomain against its rows. UW_FAC_COVER=1.01 forces the
gate open so the fraction is recorded.

    UW_FAC_COVER=1.01 python uniform_level_gate.py
"""
import json
import os
import sys

import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import row7_common as rc  # noqa: E402  (the collective-safe patch reader)

params = uw.Params(uw_out="records/uniform.json")
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 8,
                                         regular=False, qdegree=2, refinement=2)
levels = base._coarse_level_meshes()[:-1]
x, y = base.X
v = uw.discretisation.MeshVariable("v", base, 2, degree=2)
p = uw.discretisation.MeshVariable("p", base, 1, degree=1, continuous=True)
stokes = uw.systems.Stokes(base, velocityField=v, pressureField=p)
stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
for wall in ("Bottom", "Top", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), wall)
stokes.petsc_use_pressure_nullspace = True
set_custom_fmg(stokes, levels, field_id=0)
stokes.solve()
h = stokes._custom_mg["hierarchy"]
last = h.level_patch_rows[-1]
rows = int(h.transfers[-1].getSize()[0])          # the finest level's reduced rows
rec = {"cover_max": float(os.environ.get("UW_FAC_COVER", 0.75)), "taken": last is not None,
       "level_rows": rows}
_patch = rc.finest_patch(h)       # the hierarchy's record (no collective on new builds)
if _patch["taken"]:
    rec["patch_owned_rows"] = _patch["patch_owned_rows"]
    rec["subdomain_rows"] = _patch["subdomain_rows"]
    rec["patch_fraction"] = rec["patch_owned_rows"] / rows
    rec["subdomain_fraction"] = rec["subdomain_rows"] / rows
uw.pprint("UNIFORM " + json.dumps(rec))
with uw.selective_ranks(0) as selected:
    if selected:
        json.dump(rec, open(params.uw_out, "w"), indent=1)
