"""One rank: a load that varies over the Top wall of a 3-D box, PETSc's nodal
values against the exact integrals, on an unrefined and a refined mesh.

The load is (0, 0, x), linear, and the velocity is P2, so each nodal integral
on a flat triangle has a closed form in the vertex values f_i and the area A:
vertex i: A (f_i/30 - (f_j + f_k)/60); edge ij: A (2 (f_i + f_j)/15 + f_k/15).
qdegree 4 makes PETSc's quadrature exact for the same integrals. Nodes are
matched by coordinates rounded to MATCH decimals (edge nodes are midpoints).
"""
from collections import Counter

import numpy as np
import sympy

import underworld3 as uw

MATCH = 9          # decimals; the box is the unit cube


def key(x):
    return tuple(np.round(x, MATCH) + 0.0)


def run(refinement):
    kwargs = {} if refinement == 0 else {"refinement": refinement}
    mesh = uw.meshing.UnstructuredSimplexBox(
        minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=0.25, qdegree=4, **kwargs)
    tag = f"r{refinement}"
    velocity = uw.discretisation.MeshVariable(f"U{tag}", mesh, 3, degree=2, vtype=uw.VarType.VECTOR)
    pressure = uw.discretisation.MeshVariable(f"P{tag}", mesh, 1, degree=1, continuous=True)
    stokes = uw.systems.Stokes(mesh, velocityField=velocity, pressureField=pressure)
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.bodyforce = sympy.Matrix([0.0, 0.0, 0.0]).T
    x = mesh.CoordinateSystem.X[0]
    stokes.add_natural_bc(sympy.Matrix([0.0, 0.0, x]).T, "Top")
    stokes._build()
    for var in stokes.fields.values():
        var.array[...] = 0.0
    rows = stokes.compute_volume_residual_fields()
    coords = np.asarray(stokes.fields["velocity"].coords)
    petsc = {key(c): r[2] for c, r in zip(coords, np.asarray(rows["velocity"]).reshape(len(coords), -1))}

    dm = stokes.dm
    f_start, f_end = dm.getHeightStratum(1)
    v_start, v_end = dm.getDepthStratum(0)
    section, xyz = dm.getCoordinateSection(), dm.getCoordinatesLocal().array
    exact, node_orientations, seen = {}, {}, Counter()
    for p in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Top.value).getIndices():
        if not f_start <= p < f_end:
            continue
        cell = dm.getSupport(p)[0]
        orientation = int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(p)])
        seen[orientation] += 1
        v = np.array([xyz[section.getOffset(q):section.getOffset(q) + 3]
                      for q in dm.getTransitiveClosure(p)[0] if v_start <= q < v_end])
        area = 0.5 * np.linalg.norm(np.cross(v[1] - v[0], v[2] - v[0]))
        f = v[:, 0]
        for i in range(3):
            j, k = (i + 1) % 3, (i + 2) % 3
            for node, value in ((v[i], area * (f[i] / 30 - (f[j] + f[k]) / 60)),
                                (0.5 * (v[i] + v[j]), area * (2 * (f[i] + f[j]) / 15 + f[k] / 15))):
                exact[key(node)] = exact.get(key(node), 0.0) + value
                node_orientations.setdefault(key(node), set()).add(orientation)
    missing = [k for k in exact if k not in petsc]
    a = np.array([exact[k] for k in exact if k in petsc])
    b = np.array([petsc[k] for k in exact if k in petsc])
    sign = np.sign(np.dot(a, b))
    wrong = [k for k in exact if k in petsc and abs(sign * petsc[k] - exact[k]) > 1e-10 * np.abs(a).max()]
    on_rotated = sum(1 for k in wrong if node_orientations[k] - {0})
    clean_nodes = sum(1 for k in exact if not (node_orientations[k] - {0}))
    print(f"refinement {refinement}: Top faces by orientation in their cell {dict(sorted(seen.items()))}; "
          f"nodes {len(exact)} (unmatched {len(missing)}); total load exact {a.sum():.12f}, PETSc {sign * b.sum():.12f}; "
          f"nodes that differ from the exact value: {len(wrong)}, of which {on_rotated} touch a face with a "
          f"non-zero orientation; nodes touching only orientation-0 faces: {clean_nodes}; "
          f"largest difference {np.abs(sign * b - a).max():.3e} against a largest load of {np.abs(a).max():.3e}",
          flush=True)


for refinement in (0, 1, 2):
    run(refinement)
