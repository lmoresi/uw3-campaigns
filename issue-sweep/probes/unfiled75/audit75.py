import subprocess, re, json
rev = "fbef72fa"
files = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "src/"], capture_output=True, text=True).stdout.split()
files = [f for f in files if f.endswith((".py", ".pyx"))]
out = []
for f in files:
    src = subprocess.run(["git", "show", f"{rev}:{f}"], capture_output=True, text=True).stdout
    for m in re.finditer(r"\.(allreduce|reduce)\(", src):
        i = m.end(); depth = 1; j = i
        while j < len(src) and depth:
            depth += {"(": 1, ")": -1}.get(src[j], 0); j += 1
        args = src[i:j - 1]
        line = src.count("\n", 0, m.start()) + 1
        opm = re.search(r"op\s*=\s*([\w\.]+)", args)
        op = opm.group(1).split(".")[-1] if opm else ("<positional>" if "," in args else "SUM(default)")
        first = args.split(",")[0].strip() if opm or "," in args else args.strip()
        if op in ("SUM", "SUM(default)", "LAND", "LOR", "BOR", "LXOR", "BAND"): continue
        out.append(dict(file=f[len("src/underworld3/"):], line=line, op=op, arg=" ".join(first.split())[:90]))
for r in out: print(f"{r['file']}:{r['line']} | {r['op']} | {r['arg']}")
print(len(out), "sites")
