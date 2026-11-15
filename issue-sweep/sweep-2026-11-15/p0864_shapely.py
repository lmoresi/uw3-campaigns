"""#864: the shapely half (import), and whether the coverage check sees a skip for a missing import."""
import importlib, pathlib
for mod in ("mcp", "shapely"):
    try:
        importlib.import_module(mod)
        print(mod, "importable")
    except ImportError as e:
        print(mod, "missing:", e)
src = pathlib.Path("scripts/check_test_coverage.py").read_text()
print("coverage check mentions 'could not import' / importorskip:",
      "could not import" in src or "importorskip" in src)
