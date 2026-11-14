"""One rank: does "the basis is tabulated at the un-rotated quadrature point" predict
PETSc's wrong nodal loads exactly?

Same case as exterior_load_against_exact.py (unit cube, load (0, 0, x) on Top,
P2, qdegree 4). If on a face with orientation o the load is read at the
physical point q and the basis at the point a fixed symmetry of the triangle
away, and the quadrature rule is symmetric, the value PETSc computes is the
exact integral of the load with its three vertex values permuted. For each of
the 6 x 6 choices (one permutation for orientation 1, one for orientation 2)
this assembles the prediction and counts the nodes where PETSc differs from it.
Also prints sum_i b_i x_i, which is the integral of x^2 over Top (1/3) when the
nodal loads b are right: a check that needs no node matching.
"""
from collections import Counter
from itertools import permutations

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
    faces, seen = [], Counter()
    for p in dm.getLabel("UW_Boundaries").getStratumIS(mesh.boundaries.Top.value).getIndices():
        if not f_start <= p < f_end:
            continue
        cell = dm.getSupport(p)[0]
        orientation = int(dm.getConeOrientation(cell)[list(dm.getCone(cell)).index(p)])
        seen[orientation] += 1
        v = np.array([xyz[section.getOffset(q):section.getOffset(q) + 3]
                      for q in dm.getTransitiveClosure(p)[0] if v_start <= q < v_end])
        faces.append((orientation, v))

    def assemble(choice):
        total = {}
        for orientation, v in faces:
            area = 0.5 * np.linalg.norm(np.cross(v[1] - v[0], v[2] - v[0]))
            f = v[list(choice.get(orientation, (0, 1, 2))), 0]
            for i in range(3):
                j, k = (i + 1) % 3, (i + 2) % 3
                for node, value in ((v[i], area * (f[i] / 30 - (f[j] + f[k]) / 60)),
                                    (0.5 * (v[i] + v[j]), area * (2 * (f[i] + f[j]) / 15 + f[k] / 15))):
                    total[key(node)] = total.get(key(node), 0.0) + value
        return total

    exact = assemble({})
    keys = list(exact)
    b = np.array([petsc[k] for k in keys])
    a = np.array([exact[k] for k in keys])
    b = b * np.sign(np.dot(a, b))
    size = np.abs(a).max()
    moment = float(sum(bi * k[0] for bi, k in zip(b, keys)))
    print(f"refinement {refinement}: Top faces by orientation {dict(sorted(seen.items()))}; sum b_i x_i = "
          f"{moment:.12f} (exact 1/3 = {1/3:.12f}); nodes differing from the exact load: "
          f"{int(np.count_nonzero(np.abs(b - a) > 1e-10 * size))} of {len(keys)}", flush=True)
    if set(seen) - {0}:
        results = []
        for p1 in permutations(range(3)):
            for p2 in permutations(range(3)):
                predicted = assemble({1: p1, 2: p2})
                c = np.array([predicted[k] for k in keys])
                results.append((int(np.count_nonzero(np.abs(b - c) > 1e-10 * size)), float(np.abs(b - c).max()), p1, p2))
        results.sort()
        for wrong, worst, p1, p2 in results[:3]:
            print(f"    vertex values permuted by {p1} at orientation 1 and {p2} at orientation 2: "
                  f"{wrong} nodes differ from PETSc, largest {worst:.2e}", flush=True)


for refinement in (0, 1, 2):
    run(refinement)
