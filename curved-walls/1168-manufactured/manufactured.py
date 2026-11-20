"""An exact Stokes solution on an elliptical annulus with exact free slip on the ellipse.

Outer wall: the ellipse phi = x^2/A^2 + y^2 - 1 = 0 (A = 1.5, semi-axes 1.5 and 1).
Inner wall: the circle of radius 0.5, where the exact velocity is given as data.
Viscosity 1. Stokes: -div(2 eps(u)) + grad p = f, div u = 0.

Velocity from a stream function, u = (psi_y, -psi_x), so div u = 0 exactly:

    psi = phi * h + phi^2 * k,     h = 1 + x/4.

On phi = 0, u.n = 0 because psi is constant there. The phi^2 k term leaves the
velocity on the wall unchanged and adds -2 k |grad phi|^2 (sign checked below)
to the wall's tangential traction t.(grad u + grad u^T).n, so k is chosen as the
traction of phi*h alone divided by that factor: the total tangential traction on
the ellipse is then zero. The slip velocity on the wall is u.t = h |grad phi|,
which varies around the wall. Pressure p = x y (any smooth field; its mean is
removed when comparing).

Both free-slip conditions on phi = 0 (u.n = 0, n.sigma.t = 0) are checked
exactly below on the parametrised ellipse x = A cos s, y = sin s.

Variant "both" (free slip on the inner circle as well, as in issue #1168's
fixture): Phi = phi_o * phi_i with phi_o the ellipse's level function above and
phi_i = x^2 + y^2 - 1/4, so psi = Phi h + Phi^2 K is constant (zero) on both
walls. On each wall Phi^2 K adds -2 K |grad Phi|^2 to the tangential traction,
so K must equal T_o / (2 |grad Phi|^2) on the ellipse and T_i / (2 |grad Phi|^2)
on the circle, where T is the tangential traction of Phi h computed with that
wall's own normal. |grad Phi|^2 is phi_i^2 |grad phi_o|^2 on the ellipse and
phi_o^2 |grad phi_i|^2 on the circle, so

    K = [phi_i T_o / (2 |grad phi_o|^2) - phi_o T_i / (2 |grad phi_i|^2)]
        / (phi_i^3 - phi_o^3)

takes each value on its own wall (phi_o = 0 on the ellipse, phi_i = 0 on the
circle). In the fluid phi_o < 0 < phi_i, so the denominator is positive and of
order one, and K is smooth. (A first attempt that divided by |grad Phi|^4 + Phi^2
was exact too but had sharp features where grad Phi nearly vanishes between the
walls: the essential-data control was 9 % off at cell size 0.1.)
"""
import sympy as sp

A = sp.Rational(3, 2)
x, y = sp.symbols("x y", real=True)


def fields(variant="outer"):
    """psi, u (2-vector), p, f (2-vector) as sympy expressions in x, y.

    variant "outer": free slip on the ellipse only. "both": also on the circle
    r = 1/2. "both-xy": as "both" with h = 2 x y, so the slip on each wall is odd
    in x and odd in y (the symmetry of issue #1168's flow); "outer" and "both"
    use h = 1 + x/4, whose slip is a one-signed circulation. ``n`` is the ellipse's outward unit normal; ``n_inner`` the circle's
    unit normal pointing out of the fluid (towards the origin)."""
    phi = x**2 / A**2 + y**2 - 1
    gphi = sp.Matrix([phi.diff(x), phi.diff(y)])
    g2 = gphi.dot(gphi)
    n = gphi / sp.sqrt(g2)
    t = sp.Matrix([-n[1], n[0]])
    n_inner = -sp.Matrix([x, y]) / sp.sqrt(x**2 + y**2)

    def velocity(psi):
        return sp.Matrix([psi.diff(y), -psi.diff(x)])

    def tangential_traction(u):
        grad = u.jacobian([x, y])
        return (t.T * (grad + grad.T) * n)[0]

    h = 2 * x * y if variant == "both-xy" else 1 + x / 4
    if variant == "outer":
        traction_h = sp.simplify(tangential_traction(velocity(phi * h)))
        # The factor the phi^2 k term contributes on phi = 0, found symbolically:
        kk = sp.Symbol("kk")
        factor = sp.simplify(tangential_traction(velocity(phi**2 * kk)).subs(phi, 0))
        k = sp.cancel(-traction_h / (factor / kk))
        psi = phi * h + phi**2 * k
    else:
        phi_i = x**2 + y**2 - sp.Rational(1, 4)
        Phi = phi * phi_i
        uh = velocity(Phi * h)
        grad = uh.jacobian([x, y])
        S = grad + grad.T

        def traction_with(level):
            g = sp.Matrix([level.diff(x), level.diff(y)])
            tg = sp.Matrix([-g[1], g[0]])
            # unit normal and tangent: (tg.S.g) / |g|^2
            return (tg.T * S * g)[0], g.dot(g)

        T_o, g2_o = traction_with(phi)
        T_i, g2_i = traction_with(phi_i)
        # T_o / g2_o is the traction with the ellipse's unit normal; it is to be
        # divided by 2 |grad Phi|^2 = 2 phi_i^2 g2_o on the ellipse, and so on.
        K = (phi_i * T_o / (2 * g2_o**2) - phi * T_i / (2 * g2_i**2)) / (phi_i**3 - phi**3)
        k = K
        psi = Phi * h + Phi**2 * K
        factor = None
    u = velocity(psi)
    p = x * y
    lap = sp.Matrix([u[0].diff(x, 2) + u[0].diff(y, 2), u[1].diff(x, 2) + u[1].diff(y, 2)])
    f = -lap + sp.Matrix([p.diff(x), p.diff(y)])
    return dict(phi=phi, n=n, t=t, n_inner=n_inner, psi=psi, u=u, p=p, f=f, k=k,
                factor=factor, tangential_traction=tangential_traction)


def check(variant):
    import numpy as np
    F = fields(variant)
    s = sp.Symbol("s", real=True)
    u = F["u"]
    print(f"variant {variant}")
    print("  div u:", sp.simplify(u[0].diff(x) + u[1].diff(y)))
    walls = [("ellipse", {x: A * sp.cos(s), y: sp.sin(s)}, F["n"])]
    if variant != "outer":
        walls.append(("circle", {x: sp.cos(s) / 2, y: sp.sin(s) / 2}, F["n_inner"]))
    ss = np.linspace(0, 2 * np.pi, 721)
    for name, on_wall, n in walls:
        t = sp.Matrix([-n[1], n[0]])
        grad = u.jacobian([x, y])
        un = (u.T * n)[0].subs(on_wall)
        tt = (t.T * (grad + grad.T) * n)[0].subs(on_wall)
        if variant == "outer":
            print(f"  u.n on the {name} (exact):", sp.simplify(un))
            print(f"  tangential traction on the {name} (exact):", sp.simplify(tt))
        else:
            # Exact simplification of this variant takes too long; evaluate to 50
            # digits at 40 points instead (each value is 0 to ~1e-45 if exact).
            import mpmath
            mpmath.mp.dps = 50
            fu50, ft50 = (sp.lambdify(s, e, modules="mpmath") for e in (un, tt))
            worst = max(abs(g(mpmath.mpf(j) / 40 * 2 * mpmath.pi)) for g in (fu50, ft50)
                        for j in range(40))
            print(f"  largest |u.n|, |traction| on the {name} at 40 points, 50 digits: "
                  f"{mpmath.nstr(worst, 3)}")
        fu, ft = sp.lambdify(s, un), sp.lambdify(s, tt)
        ut = sp.lambdify(s, (u.T * t)[0].subs(on_wall))(ss)
        print(f"  {name}: numerical max |u.n| {np.max(np.abs(fu(ss))):.2e}, max |traction| "
              f"{np.max(np.abs(ft(ss))):.2e} on 721 points; slip speed {np.abs(ut).min():.3f} to "
              f"{np.abs(ut).max():.3f}")
    print("  expression length: u %d, f %d characters" % (len(str(u)), len(str(F["f"]))))


if __name__ == "__main__":
    import sys
    for variant in sys.argv[1:] or ["outer", "both", "both-xy"]:
        check(variant)
