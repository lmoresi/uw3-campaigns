"""#824: uw.unwrap forwards keep_constants and return_self positionally."""
import sympy
import underworld3 as uw

x = sympy.Symbol("x")
inner = uw.expression(r"a_{in}", 2 * x, "inner")
outer = uw.expression(r"a_{out}", 3 * inner, "outer")
print("uw.unwrap(outer):                       ", uw.unwrap(outer))
print("uw.unwrap(outer, keep_constants=False): ", uw.unwrap(outer, keep_constants=False))
print("expressions.unwrap(outer):              ", uw.function.expressions.unwrap(outer))
