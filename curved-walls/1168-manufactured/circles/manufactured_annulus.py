"""Exact Stokes solutions on the annulus 1/2 < r < 1 with exact free slip on both walls.

The construction of ../manufactured.py ("both") with the ellipse replaced by the
unit circle: phi_o = r^2 - 1, phi_i = r^2 - 1/4, Phi = phi_o phi_i, and

    psi = Phi h + Phi^2 K,   u = (psi_y, -psi_x),   p = x y,   viscosity 1.

psi = 0 on both walls, so u.n = 0 there and div u = 0 everywhere; K is blended so
that the Phi^2 K term cancels the tangential traction of Phi h on each wall (see
../manufactured.py for the derivation). On each wall the slip is u.t = h |grad Phi|,
and |grad Phi| is constant on a circle (3/2 on r = 1, 3/4 on r = 1/2), so the slip
has the angular shape of h:

  "s2"      h = 2 x y            slip ~ sin 2 theta (no net circulation)
  "c3"      h = x^3 - 3 x y^2    slip ~ cos 3 theta (no net circulation)
  "circ"    h = 1                uniform slip (a pure circulation)
  "s2circ"  h = 1 + 2 x y        sin 2 theta plus a circulation

    python manufactured_annulus.py s2 c3    # checks both free-slip conditions
"""
import sympy as sp

x, y = sp.symbols("x y", real=True)

H = {"s2": 2 * x * y, "c3": x**3 - 3 * x * y**2, "circ": sp.Integer(1),
     "s2circ": 1 + 2 * x * y}


def fields(kind):
    h = H[kind]
    phi = x**2 + y**2 - 1
    phi_i = x**2 + y**2 - sp.Rational(1, 4)
    Phi = phi * phi_i

    def velocity(psi):
        return sp.Matrix([psi.diff(y), -psi.diff(x)])

    uh = velocity(Phi * h)
    grad = uh.jacobian([x, y])
    S = grad + grad.T

    def traction_with(level):
        g = sp.Matrix([level.diff(x), level.diff(y)])
        tg = sp.Matrix([-g[1], g[0]])
        return (tg.T * S * g)[0], g.dot(g)

    T_o, g2_o = traction_with(phi)
    T_i, g2_i = traction_with(phi_i)
    K = (phi_i * T_o / (2 * g2_o**2) - phi * T_i / (2 * g2_i**2)) / (phi_i**3 - phi**3)
    psi = Phi * h + Phi**2 * K
    u = velocity(psi)
    p = x * y
    lap = sp.Matrix([u[0].diff(x, 2) + u[0].diff(y, 2), u[1].diff(x, 2) + u[1].diff(y, 2)])
    f = -lap + sp.Matrix([p.diff(x), p.diff(y)])
    return dict(u=u, p=p, f=f, psi=psi)


def check(kind):
    import mpmath
    import numpy as np
    mpmath.mp.dps = 50
    u = fields(kind)["u"]
    s = sp.Symbol("s", real=True)
    print(f"kind {kind}: div u = {sp.simplify(u[0].diff(x) + u[1].diff(y))}")
    grad = u.jacobian([x, y])
    for name, radius in (("outer r=1", 1), ("inner r=1/2", sp.Rational(1, 2))):
        on = {x: radius * sp.cos(s), y: radius * sp.sin(s)}
        n = sp.Matrix([sp.cos(s), sp.sin(s)])
        t = sp.Matrix([-n[1], n[0]])
        un = (u.T * n)[0].subs(on)
        tt = (t.T * (grad + grad.T).subs(on) * n)[0]
        fu, ft, fs = (sp.lambdify(s, e, modules="mpmath") for e in (un, tt, (u.T * t)[0].subs(on)))
        pts = [mpmath.mpf(j) / 40 * 2 * mpmath.pi for j in range(40)]
        worst = max(abs(g(q)) for g in (fu, ft) for q in pts)
        slip = [float(fs(q)) for q in pts]
        print(f"  {name}: largest |u.n|, |tangential traction| at 40 points (50 digits) "
              f"{mpmath.nstr(worst, 3)}; slip {min(slip):+.3f} to {max(slip):+.3f}")


if __name__ == "__main__":
    import sys
    for kind in sys.argv[1:] or list(H):
        check(kind)
