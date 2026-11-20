"""The elliptical annulus of issue #1168: outer ellipse with semi-axes 1.5 and 1,
inner circle of radius 0.5, cell size `cell` outside and half that inside."""
from enum import Enum

import underworld3 as uw

A = 1.5


class boundaries(Enum):
    Inner = 1
    Outer = 2


def write_mesh(filename, cell):
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 1)
    gmsh.model.add("EllipticalAnnulus")
    geo = gmsh.model.geo
    centre = geo.add_point(0.0, 0.0, 0.0, meshSize=cell / 2)
    curves = {}
    for name, a, b, size in (("Inner", 0.5, 0.5, cell / 2), ("Outer", A, 1.0, cell)):
        east = geo.add_point(a, 0.0, 0.0, meshSize=size)
        north = geo.add_point(0.0, b, 0.0, meshSize=size)
        west = geo.add_point(-a, 0.0, 0.0, meshSize=size)
        south = geo.add_point(0.0, -b, 0.0, meshSize=size)
        curves[name] = [geo.add_ellipse_arc(east, centre, east, north),
                        geo.add_ellipse_arc(north, centre, west, west),
                        geo.add_ellipse_arc(west, centre, west, south),
                        geo.add_ellipse_arc(south, centre, east, east)]
    inner = geo.add_curve_loop(curves["Inner"])
    outer = geo.add_curve_loop(curves["Outer"])
    surface = geo.add_plane_surface([outer, inner])
    geo.synchronize()
    gmsh.model.addPhysicalGroup(1, curves["Inner"], boundaries.Inner.value, name="Inner")
    gmsh.model.addPhysicalGroup(1, curves["Outer"], boundaries.Outer.value, name="Outer")
    gmsh.model.addPhysicalGroup(2, [surface], 666666, "Elements")
    gmsh.model.mesh.generate(2)
    gmsh.write(filename)
    gmsh.finalize()


def ellipse_mesh(cell, qdegree=4):
    filename = f"ellipse_{cell}.msh"
    if uw.mpi.rank == 0:
        write_mesh(filename, cell)
    uw.mpi.barrier()
    return uw.discretisation.Mesh(filename, degree=1, qdegree=qdegree, useMultipleTags=True,
                                  useRegions=True, markVertices=True, boundaries=boundaries)
