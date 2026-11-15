"""#944, runtime half: the API drift the issue and its comments name, counted on development.

Run from the repository root. Reads files only.
"""
import pathlib, re
import underworld3 as uw

print("uw.function has evalf:", hasattr(uw.function, "evalf"))
roots = [pathlib.Path("docs/examples"), pathlib.Path("docs/beginner")]
files = [p for r in roots for p in r.rglob("*") if p.suffix in (".py", ".ipynb")]
evalf = sorted(str(p) for p in files if re.search(r"function\.evalf\b", p.read_text(errors="ignore")))
stats5 = sorted(str(p) for p in files if "stats()[5]" in p.read_text(errors="ignore"))
print(f"files calling uw.function.evalf: {len(evalf)} ({sum('/WIP/' in f for f in evalf)} under WIP/)")
for f in evalf:
    print("  ", f)
print(f"files indexing stats()[5]: {len(stats5)}")
for f in stats5:
    print("  ", f)
