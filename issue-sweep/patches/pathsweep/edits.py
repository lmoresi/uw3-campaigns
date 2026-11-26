"""H7 local-paths sweep (rule 9): a developer's home-directory paths in docs/ become neutral
placeholders, most specific prefix first. The saved PETSc traceback in the stderr output of
docs/beginner/tutorials/17-Richards-Transient-Wetting-Front.ipynb (cell 11) is quoted output
and is left as it is."""
import re, subprocess, sys
root = sys.argv[1]
SKIP = {"docs/beginner/tutorials/17-Richards-Transient-Wetting-Front.ipynb"}
MAP = [
    ("/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/", "~/path/to/worktrees/"),
    ("/Users/lmoresi/+Underworld/underworld3-pixi/", "~/path/to/underworld3/"),
    ("/Users/lmoresi/+Underworld/underworld-pixi-2/underworld3", "~/path/to/underworld3"),
    ("/Users/lmoresi/+Underworld/underworld-pixi-2/petsc/", "~/path/to/petsc/"),
    ("/Users/lmoresi/+Underworld/underworld3/", "~/path/to/underworld3/"),
    ("/Users/lmoresi/+Simulations/", "~/path/to/simulations/"),
    ("/Users/lmoresi/Downloads/", "~/path/to/"),
    ("/Users/jgra0019/Documents/codes/", "~/path/to/"),
]
files = subprocess.check_output(["grep", "-rlE", "/Users/[a-z]", "docs"], cwd=root, text=True).split()
n = 0
for f in files:
    if f in SKIP: continue
    p = f"{root}/{f}"
    try:
        s = open(p, encoding="utf-8").read()
    except UnicodeDecodeError:
        print(f"BINARY, left: {f}"); continue
    t = s
    for a, b in MAP: t = t.replace(a, b)
    left = re.findall(r"/Users/[a-z][^\s`\"']*", t)
    if left: sys.exit(f"unmapped path in {f}: {left[:3]}")
    if t != s:
        n += sum(1 for x, y in zip(s.split("\n"), t.split("\n")) if x != y)
        open(p, "w").write(t)
print(f"{n} lines changed in {len(files) - len(SKIP & set(files))} files")
