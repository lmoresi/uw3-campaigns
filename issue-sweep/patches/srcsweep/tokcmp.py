"""Token streams of base and head, with COMMENT and STRING contents blanked, for every
changed file (.py and .pyx: Python's tokenizer reads Cython's syntax as names and
operators). Identical streams mean only comment and string text changed."""
import io, subprocess, sys, tokenize
base, head, repo = sys.argv[1:4]
files = subprocess.check_output(["git", "-C", repo, "diff", "--name-only", base, head], text=True).split()
def toks(src):
    out = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.COMMENT, tokenize.STRING):
            out.append((t.type, "<blank>"))
        elif t.type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            out.append((t.type, ""))
        else:
            out.append((t.type, t.string))
    return out
bad = 0
for f in files:
    a = subprocess.check_output(["git", "-C", repo, "show", f"{base}:{f}"], text=True)
    b = subprocess.check_output(["git", "-C", repo, "show", f"{head}:{f}"], text=True)
    same = toks(a) == toks(b); bad += not same
    print("SAME" if same else "DIFF", f)
print("code changes:", bad)
