"""#966: after a mover, is a swarm proxy (and the domain kd-tree) refreshed?

Annulus, s = x of each particle, proxy_degree=1. Read the proxy once, move the
interior nodes with spring smoothing, rewrite s, read the proxy again and compare
it with x at the moved nodes and at the pre-move nodes.
"""
import numpy as np
import underworld3 as uw

mesh = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=1 / 8)
swarm = uw.swarm.Swarm(mesh)
s = uw.swarm.SwarmVariable("s", swarm, 1, proxy_degree=1)
swarm.populate(fill_param=3)
s.data[:, 0] = swarm.data[:, 0]
proxy = s._meshVar


def proxy_x_error(X):
    uw.function.evaluate(s.sym[0], X[:1])        # touch the proxy so a stale one refreshes
    return np.abs(np.asarray(proxy.array).ravel() - X[:, 0]).max()


X0 = np.asarray(proxy.coords).copy()
print(f"before the move: proxy error against the nodes {proxy_x_error(X0):.2e}")
v0, mv0 = mesh._mesh_version, getattr(mesh, "_move_version", None)
uw.meshing.smoothing.smooth_mesh_interior(mesh, method="spring")
X1 = np.asarray(proxy.coords).copy()
s.data[:, 0] = swarm.data[:, 0]
print(f"largest node move {np.linalg.norm(X1 - X0, axis=1).max():.3e}")
print(f"after the move and rewrite: proxy error against moved nodes {proxy_x_error(X1):.2e}, "
      f"against pre-move nodes {proxy_x_error(X0):.2e}")
print(f"_mesh_version {v0} -> {mesh._mesh_version}; _move_version {mv0} -> {getattr(mesh, '_move_version', None)}")
