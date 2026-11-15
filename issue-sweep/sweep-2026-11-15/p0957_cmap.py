"""#957: plot_scalar and plot_vector with their default cmap."""
import pyvista as pv
import underworld3 as uw
import underworld3.visualisation as vis

pv.OFF_SCREEN = True
print("pyvista", pv.__version__)
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.25)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=1)
V = uw.discretisation.MeshVariable("V", mesh, 2, degree=1)
for name, fn, arg in (("plot_scalar", vis.plot_scalar, T.sym[0]), ("plot_vector", vis.plot_vector, V.sym)):
    for kw in ({}, {"cmap": "viridis"}):
        try:
            fn(mesh, arg, **kw)
            print(name, kw or "default", "OK")
        except Exception as e:
            print(name, kw or "default", "raised", type(e).__name__, e)
