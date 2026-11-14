"""One rank: Nitsche free slip on the outer wall of a spherical shell, with the
velocity set to a rigid rotation.

A rigid rotation has no strain rate and, on a sphere about the origin, no
component along the radial unit vector at ANY point, on the sphere or on a flat
face inside it. P2 holds it exactly. So with the normal written as the radial
unit vector every term of the residual is zero to round-off, whatever the mesh,
provided the velocity and the normal are evaluated at the same point. The
residual of a radial velocity (u = x) through the same term gives the scale.

Three forms of the normal: the solver's default, the radial unit vector passed
explicitly, and PETSc's own face normal (`mesh.Gamma`).
"""
from collections import Counter

import numpy as np

import underworld3 as uw

params = uw.Params(uw_cell_size=0.5)
CELL_SIZE = float(params.uw_cell_size)
count = 0


def residual(refinement, form):
    global count
    count += 1
    kwargs = {} if refinement == 0 else {"refinement": refinement}
    mesh = uw.meshing.SphericalShell(radiusInner=0.55, radiusOuter=1.0, cellSize=CELL_SIZE,
                                     qdegree=2, **kwargs)
    velocity = uw.discretisation.MeshVariable(f"U{count}", mesh, 3, degree=2, vtype=uw.VarType.VECTOR)
    pressure = uw.discretisation.MeshVariable(f"P{count}", mesh, 1, degree=1, continuous=True)
    stokes = uw.systems.Stokes(mesh, velocityField=velocity, pressureField=pressure)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.bodyforce = 0.0 * mesh.CoordinateSystem.unit_e_0
    normal = {"default": None, "radial": mesh.CoordinateSystem.unit_e_0, "face": mesh.Gamma}[form]
    stokes.add_nitsche_bc(0.0, "Upper", normal=normal)
    stokes._build()

    dm = stokes.dm
    f_start, f_end = dm.getHeightStratum(1)
    seen = Counter()
    for p in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Upper.value).getIndices():
        if f_start <= p < f_end:
            cell = dm.getSupport(p)[0]
            seen[int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(p)])] += 1

    u = stokes.fields["velocity"]
    x = np.asarray(u.coords)
    out = {}
    for name, field in (("rotation", np.stack([-x[:, 1], x[:, 0], 0 * x[:, 0]], axis=1)), ("radial", x)):
        for var in stokes.fields.values():
            var.array[...] = 0.0
        u.array[:, 0, :] = field
        rows = np.asarray(stokes.compute_volume_residual_fields()["velocity"]).reshape(len(x), -1)
        out[name] = np.abs(rows).max(axis=1)
    scale = out["radial"].max()
    wall = np.linalg.norm(x, axis=1) > 0.9
    nonzero = out["rotation"] > 1e-10 * scale
    print(f"refinement {refinement}, normal {form}: Upper faces by orientation {dict(sorted(seen.items()))}; "
          f"velocity nodes {len(x)}; rigid rotation: nodes with a residual {int(nonzero.sum())} "
          f"(of them at r > 0.9: {int((nonzero & wall).sum())}), largest {out['rotation'].max():.3e}; "
          f"radial velocity: largest {scale:.3e}; ratio {out['rotation'].max() / scale:.3e}", flush=True)


for refinement in (0, 1, 2):
    for form in ("default", "radial", "face"):
        try:
            residual(refinement, form)
        except Exception as exc:
            print(f"refinement {refinement}, normal {form}: {type(exc).__name__}: {str(exc)[:160]}", flush=True)
