"""One rank: the load of a natural condition on `Internal`, with and without
the support order of its faces swapped, in 2-D (edges) and 3-D (triangles).
Plain Stokes, no constraint. The two meshes of a pair come from one gmsh call
each with the same arguments, so their nodes are compared by position in the
array after checking the coordinates are identical.
"""
from collections import Counter

import numpy as np
import sympy

import underworld3 as uw


def load(dim, swap, tag):
    if dim == 2:
        mesh = uw.meshing.AnnulusInternalBoundary(
            radiusOuter=1.0, radiusInternal=0.775, radiusInner=0.55, cellSize=0.1, qdegree=2)
    else:
        mesh = uw.meshing.SphericalShellInternalBoundary(
            radiusOuter=1.0, radiusInternal=0.775, radiusInner=0.55, cellSize=0.3, qdegree=2, degree=1)
    dm = mesh.dm
    f_start, f_end = dm.getHeightStratum(1)
    faces = [int(p) for p in dm.getLabel("UW_Boundaries").getStratumIS(
        mesh.boundaries.Internal.value).getIndices() if f_start <= p < f_end]
    seen = Counter()
    for face in faces:
        support = dm.getSupport(face)
        if swap:
            dm.setSupport(face, np.array(support[::-1], dtype=support.dtype))
        cell = dm.getSupport(face)[0]
        seen[int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(face)])] += 1
    velocity = uw.discretisation.MeshVariable(f"U{tag}", mesh, mesh.dim, degree=2, vtype=uw.VarType.VECTOR)
    pressure = uw.discretisation.MeshVariable(f"P{tag}", mesh, 1, degree=1, continuous=True)
    stokes = uw.systems.Stokes(mesh, velocityField=velocity, pressureField=pressure)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.bodyforce = sympy.Matrix([0.0] * dim).T
    unit_r = mesh.CoordinateSystem.unit_e_0
    theta = mesh.CoordinateSystem.xR[1]
    shape = sympy.cos(2 * theta) if dim == 2 else sympy.assoc_legendre(2, 0, sympy.cos(theta))
    stokes.add_natural_bc(shape * unit_r, "Internal")
    stokes._build()
    for var in stokes.fields.values():
        var.array[...] = 0.0
    rows = stokes.compute_volume_residual_fields()
    coords = np.asarray(stokes.fields["velocity"].coords).copy()
    return coords, np.asarray(rows["velocity"]).reshape(coords.shape[0], -1).copy(), len(faces), dict(sorted(seen.items()))


for dim in (2, 3):
    x0, f0, n0, o0 = load(dim, False, f"a{dim}")
    x1, f1, n1, o1 = load(dim, True, f"b{dim}")
    assert np.array_equal(x0, x1), "the two meshes differ"
    size = np.abs(f0).max()
    differing = int(np.count_nonzero(np.abs(f1 - f0).max(axis=1) > 1e-12 * size))
    loaded = int(np.count_nonzero(np.abs(f0).max(axis=1) > 1e-12 * size))
    print(f"{dim}-D: {n0} Internal faces; orientation in the first support cell {o0} -> swapped {o1}; "
          f"loaded nodes {loaded}; nodes whose load changes {differing}; largest change "
          f"{np.abs(f1 - f0).max():.3e} against a largest load of {size:.3e}; sum of the changes "
          f"{(f1 - f0).sum(axis=0)}", flush=True)
