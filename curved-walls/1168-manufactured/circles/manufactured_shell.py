"""Exact Stokes solutions in the spherical shell 1/2 < r < 1 with exact free slip on both walls.

Viscosity 1, p = x y z, f = -lap u + grad p (div u = 0). P = x y, a harmonic of
degree 2. Two velocity fields, each with u.n = 0 and zero tangential traction on
both spheres (checked below to 50 digits):

  "tor"  toroidal, u = q(r) grad P x X with q(r) r = 1 + 4 (r - 1/2)^2 (r - 1)^2.
         Tangential everywhere; for a toroidal field the tangential traction is
         r d/dr(u_t / r), which vanishes where d/dr(q r) = 0, i.e. on both walls.
         Its slip is surface-divergence-free (a circulation on each sphere).
  "pol"  poloidal, u = curl curl (X chi), chi = F(r) P, F = (r - 1/2)(r - 1)(c0 + c1 r + c2 r^2).
         u.n vanishes with F on both walls; c is the one direction (up to scale)
         that also zeroes the tangential traction on both walls (two linear
         conditions on three coefficients). Its slip is a surface gradient,
         the analogue of the annulus's sin 2 theta slip.

    python manufactured_shell.py tor pol
"""
import sympy as sp

x, y, z = sp.symbols("x y z", real=True)
X = sp.Matrix([x, y, z])
r = sp.sqrt(x**2 + y**2 + z**2)
a, b = sp.Rational(1, 2), sp.Integer(1)
P = x * y


def grad(f):
    return sp.Matrix([f.diff(v) for v in (x, y, z)])


def curl(A):
    return sp.Matrix([A[2].diff(y) - A[1].diff(z), A[0].diff(z) - A[2].diff(x),
                      A[1].diff(x) - A[0].diff(y)])


def tangential_traction(u, point, tangent):
    """t . (grad u + grad u^T) . n at a point on a sphere (n radial there)."""
    J = u.jacobian([x, y, z])
    S = (J + J.T).subs(point)
    n = sp.Matrix([point[x], point[y], point[z]])
    n = n / sp.sqrt(n.dot(n))
    return (tangent.T * S * n)[0]


def fields(kind):
    if kind == "tor":
        q = (1 + 4 * (r - a)**2 * (r - b)**2) / r
        u = q * grad(P).cross(X)
    else:
        c0, c1, c2 = sp.symbols("c0 c1 c2")
        F = (r - a) * (r - b) * (c0 + c1 * r + c2 * r**2)
        u_c = curl(curl(X * F * P))
        # a point on each wall where P's surface gradient is not radial, with a
        # tangent along which the traction does not vanish by symmetry
        s3 = 1 / sp.sqrt(3)
        eqs = []
        for R in (a, b):
            pt = {x: R * s3, y: R * s3, z: R * s3}
            t = sp.Matrix([1, -1, 0]) / sp.sqrt(2)
            t2 = sp.Matrix([1, 1, -2]) / sp.sqrt(6)
            for tt in (t, t2):
                eqs.append(sp.nsimplify(sp.simplify(tangential_traction(u_c, pt, tt))))
        sol = sp.solve([e for e in eqs if e != 0] + [c0 - 1], [c0, c1, c2], dict=True)
        assert len(sol) == 1, (eqs, sol)
        u = u_c.subs(sol[0])
    p = x * y * z
    lap = sp.Matrix([sum(ui.diff(v, 2) for v in (x, y, z)) for ui in u])
    f = -lap + grad(p)
    return dict(u=u, p=p, f=f)


def check(kind):
    import mpmath
    import random
    mpmath.mp.dps = 50
    u = fields(kind)["u"]
    div = sum(u[i].diff(v) for i, v in enumerate((x, y, z)))
    fdiv = sp.lambdify((x, y, z), div, "mpmath")
    J = u.jacobian([x, y, z])
    fu, fJ = sp.lambdify((x, y, z), u, "mpmath"), sp.lambdify((x, y, z), J, "mpmath")
    random.seed(1)
    worst_div = worst_un = worst_tt = 0
    slip = []
    for R in (a, b):
        for _ in range(30):
            v = [mpmath.mpf(random.gauss(0, 1)) for _ in range(3)]
            nv = mpmath.sqrt(sum(c * c for c in v))
            n = [c / nv for c in v]
            pt = [mpmath.mpf(R) * c for c in n]
            uu = fu(*pt)
            JJ = fJ(*pt)
            un = sum(uu[i] * n[i] for i in range(3))
            Sn = [sum((JJ[i, j] + JJ[j, i]) * n[j] for j in range(3)) for i in range(3)]
            nSn = sum(Sn[i] * n[i] for i in range(3))
            tt = mpmath.sqrt(sum((Sn[i] - nSn * n[i])**2 for i in range(3)))
            worst_un, worst_tt = max(worst_un, abs(un)), max(worst_tt, tt)
            worst_div = max(worst_div, abs(fdiv(*[c * mpmath.mpf(3) / 4 / R for c in pt])))
            slip.append(float(mpmath.sqrt(sum(c * c for c in uu))))
    print(f"kind {kind}: at 30 random points per wall (50 digits): max |u.n| {mpmath.nstr(worst_un, 3)}, "
          f"max |tangential traction| {mpmath.nstr(worst_tt, 3)}, max |div u| inside "
          f"{mpmath.nstr(worst_div, 3)}; wall speed {min(slip):.3f} to {max(slip):.3f}")


if __name__ == "__main__":
    import sys
    for kind in sys.argv[1:] or ["tor", "pol"]:
        check(kind)
