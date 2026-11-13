"""Scan a tree for BC calls that pass components (positionally or by keyword).

Classifies each by reading literals: REFUSED (a named component has no entry in
the value), OK (every named component has an entry), UNKNOWN (not literal).
.py files by AST; notebooks by their code cells; .md/.rst/.pyx/.qmd by regex.
"""
import ast, json, re, sys, pathlib

root = pathlib.Path(sys.argv[1])
METHODS = {"add_dirichlet_bc", "add_essential_bc", "add_natural_bc", "add_condition", "add_bc"}


def length(node):
    """Number of entries a literal value has as add_condition counts them."""
    if isinstance(node, (ast.Tuple, ast.List)):
        return len(node.elts)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return 1
    if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
        return 1
    return None


def comps(node):
    if isinstance(node, (ast.Tuple, ast.List)):
        out = []
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, int):
                out.append(e.value)
            else:
                return None
        return out
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "none"
        if isinstance(node.value, int):
            return [node.value]
    return None


def scan_source(src, where, hits):
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        hits.append((where, 0, "PARSE-ERROR", str(e)[:60]))
        return
    lines = src.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
        if name not in METHODS:
            continue
        args = list(node.args)
        kws = {k.arg: k.value for k in node.keywords if k.arg}
        if name == "add_condition":
            names = ["f_id", "c_type", "conds", "label", "components"]
        else:
            names = ["conds", "boundary", "components"]
        bound = dict(zip(names, args))
        bound.update({k: v for k, v in kws.items()})
        if "components" not in bound:
            continue
        c = comps(bound["components"])
        if c == "none":
            continue
        cond = bound.get("conds", bound.get("g"))
        n = length(cond) if cond is not None else None
        # legacy boundary-first order: first arg a string
        if cond is not None and isinstance(cond, ast.Constant) and isinstance(cond.value, str):
            other = bound.get("boundary")
            n = length(other) if other is not None else None
        text = " ".join(l.strip() for l in lines[node.lineno - 1:node.end_lineno])[:110]
        if c is None or n is None:
            verdict = "UNKNOWN"
        elif any(k >= n for k in c):
            verdict = "REFUSED"
        else:
            verdict = "OK"
        hits.append((where, node.lineno, verdict, text))


hits = []
for path in sorted(root.rglob("*")):
    if not path.is_file():
        continue
    rel = str(path.relative_to(root))
    if path.suffix == ".py":
        scan_source(path.read_text(errors="replace"), rel, hits)
    elif path.suffix == ".ipynb":
        try:
            nb = json.loads(path.read_text())
        except Exception as e:
            hits.append((rel, 0, "PARSE-ERROR", str(e)[:60])); continue
        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            src = "".join(cell.get("source", []))
            src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("%", "!")))
            before = len(hits)
            scan_source(src, f"{rel}[cell {i}]", hits)
            hits[before:] = [h for h in hits[before:] if h[2] != "PARSE-ERROR"]
    elif path.suffix in (".md", ".rst", ".pyx", ".qmd", ".txt"):
        text = path.read_text(errors="replace").splitlines()
        for ln, line in enumerate(text, 1):
            m = re.search(r"\b(add_dirichlet_bc|add_essential_bc|add_natural_bc|add_condition)\s*\((.*)", line)
            if not m:
                continue
            call = m.group(0)
            # balance to the closing bracket on this line only
            depth = 0; end = None
            for i, ch in enumerate(call):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end = i; break
            snippet = call[:end + 1] if end else call
            before = len(hits)
            scan_source("x." + snippet if not snippet.startswith("x.") else snippet, rel, hits)
            for j in range(before, len(hits)):
                w, _, v, t = hits[j]
                hits[j] = (w, ln, v if v != "PARSE-ERROR" else "UNPARSED-LINE", line.strip()[:110] if v == "PARSE-ERROR" else t)

only = sys.argv[2:] or ["REFUSED", "UNKNOWN", "OK", "PARSE-ERROR", "UNPARSED-LINE"]
for w, ln, v, t in hits:
    if v in only:
        print(f"{v:8s} {w}:{ln}: {t}")
from collections import Counter
print(Counter(h[2] for h in hits), file=sys.stderr)
