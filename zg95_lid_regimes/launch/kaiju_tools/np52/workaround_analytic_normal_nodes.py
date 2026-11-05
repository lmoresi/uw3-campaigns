# kaiju_tools: UW_WANN=1: the integration session's analytic-normal node workaround (before #938)
"""Driver-side workaround: an analytic wall normal on every owned wall node, at any
rank count (development af6f19b3 and earlier).

rotated_bc._boundary_velocity_nodes takes a rank's wall nodes from the closures of
the labelled facets it holds. Each facet is labelled on one rank, so a rank can own
a wall vertex all of whose labelled facets sit on a neighbour. The geometric path
(normal=None) finds that vertex: it sums the facet normals over the point SF and
walks every support-1 facet's closure (_local_boundary_candidates, #560). The
analytic path does neither, so that vertex gets no constraint row. Kaiju saw it on
the zg95 annulus at np 24-52 with the radial normal; np 16 happened to have no such
vertex.

The wrapper keeps the analytic path's nodes and normals as they are and adds the
nodes that only the geometric path finds, each with the analytic normal at its
coordinate. It needs a build whose geometric path has the cross-rank sum (#560):
if the geometric normal is clean at the rank count, it has. Import it once in the
driver, before the first solve:

    import workaround_analytic_normal_nodes as wann
    wann.install(("Upper", "Lower"))

Only the named boundaries change. Leave out an internal boundary (a fault): the
geometric facet normal is not defined on a facet with two cells. The geometric
call is collective, so every rank must reach it for each boundary in the same
order; build_rotation already does. ``wann.ADDED`` counts the nodes added on this
rank, per boundary.
"""
import numpy as np
import sympy

from underworld3.utilities import rotated_bc as _rbc

_original = _rbc._boundary_velocity_nodes
ADDED = {}


def _analytic(solver, normal, boundary):
    """The library's (sym_fn, const_normal) for an analytic or constant normal."""
    source = getattr(_rbc, "_normal_source", None)
    if source is not None:
        return source(solver, normal, boundary)
    if isinstance(normal, sympy.Matrix):
        from underworld3.function.expressions import unwrap
        comps = [sympy.sympify(unwrap(normal[0, k], keep_constants=False, return_self=False))
                 for k in range(solver.mesh.cdim)]
        return sympy.lambdify(list(solver.mesh.X), comps, "numpy"), None
    return None, np.asarray(normal, dtype=float).ravel()


def install(boundaries):
    walls = set(boundaries)

    def nodes(solver, boundary, normal=None):
        if normal is None or boundary not in walls:
            return _original(solver, boundary, normal=normal)
        found = dict(_original(solver, boundary, normal=normal))
        complete = _original(solver, boundary, normal=None)
        missing = [q for q, _n in complete if q not in found]
        ADDED[boundary] = len(missing)
        if missing:
            sym_fn, const_normal = _analytic(solver, normal, boundary)
            dm = solver.dm
            dim = solver.mesh.cdim
            csec = dm.getCoordinateSection()
            cvec = np.asarray(dm.getCoordinatesLocal().array).reshape(-1, dim)
            v0, v1 = dm.getDepthStratum(0)
            for q in missing:
                if sym_fn is not None:
                    ne = np.asarray(sym_fn(*_rbc._point_coord(dm, dim, cvec, csec, v0, v1, q)),
                                    dtype=float).ravel()
                else:
                    ne = const_normal.copy()
                found[q] = ne / (np.linalg.norm(ne) + 1e-30)
        return sorted(found.items())

    _rbc._boundary_velocity_nodes = nodes
    return nodes
