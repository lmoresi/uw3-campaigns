"""#1083: does the native higher-order rendering accept exactly affine high-aspect cells?

For each case a continuous Lagrange variable is built on a structured box whose
cells have the stated aspect ratio, and _lagrange_subcell_connectivity is asked
for its table. None is a refusal; the caller then falls back to a Delaunay with
no warning.
"""
import warnings
import numpy as np
import underworld3 as uw
from underworld3.visualisation.visualisation import _lagrange_subcell_connectivity, meshVariable_to_pv_mesh_object

cases = [("P4", True, 4, 100), ("P5", True, 5, 10), ("P8", True, 8, 1), ("Q3", False, 3, 100), ("Q4", False, 4, 10),
         ("P3", True, 3, 1), ("Q2", False, 2, 1)]
for name, simplex, k, aspect in cases:
    if simplex:
        mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.5, regular=True)
    else:
        mesh = uw.meshing.StructuredQuadBox(elementRes=(2, 2), minCoords=(0, 0), maxCoords=(1, 1))
    # stretch in x: every cell stays exactly affine, its aspect ratio becomes `aspect`
    mesh.deform(np.asarray(mesh.X.coords) * np.array([float(aspect), 1.0]))
    v = uw.discretisation.MeshVariable(f"v{name}{aspect}", mesh, 1, degree=k)
    conn = _lagrange_subcell_connectivity(v)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        meshVariable_to_pv_mesh_object(v)
    print(f"{name} aspect {aspect}: native table {'refused (None)' if conn is None else conn.shape}; "
          f"warnings on render: {len(caught)}", flush=True)
