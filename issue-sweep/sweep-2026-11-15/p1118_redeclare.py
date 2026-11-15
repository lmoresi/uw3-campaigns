"""#1118: a MeshVariable re-declared under an existing name returns the old one."""
import underworld3 as uw

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=0.5)
a = uw.discretisation.MeshVariable("f", mesh, 1, degree=2)
try:
    b = uw.discretisation.MeshVariable("f", mesh, 2, degree=1, varsymbol=r"\bar{f}")
    print("returned:", b.num_components, b.degree, b.sym[0], "same object:", a is b)
except Exception as e:
    print("raised", type(e).__name__, e)
