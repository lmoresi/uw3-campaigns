"""Bulk review of underworld3 branches and open PRs against development.

Usage: python3 tools/bulk_review.py <underworld3 clone with all origin branches fetched> <open_prs.json> <out.json>
open_prs.json is the REST list of open PRs (repos/underworldcode/underworld3/pulls?state=open, all pages).
For every open PR head and every branch not merged into development with a commit since SINCE:
ahead/behind, unique commits (by patch-id; squash merges show as unique), files since the merge
base, conflicts with development (merge-tree), issues named in its commits, and pairwise src overlap.
"""
import json, re, subprocess, sys, collections

GIT = ["git", "-C", sys.argv[1]]
PRS = json.load(open(sys.argv[2]))
OUT = sys.argv[3]
SINCE = "2026-10-01"
DEV = "origin/development"


def git(*a, check=True):
    r = subprocess.run(GIT + list(a), capture_output=True, text=True)
    if check and r.returncode not in (0, 1):
        raise RuntimeError(f"{a}: {r.stderr[:300]}")
    return r


pr_by_head = {p["head"]["ref"]: p for p in PRS}
refs = [l.split(" ", 1) for l in git("for-each-ref", "--format=%(committerdate:short) %(refname:short)",
                                      "refs/remotes/origin").stdout.split("\n") if l]
unmerged = set(git("branch", "-r", "--no-merged", DEV).stdout.split())
cands = []
for date, ref in refs:
    name = ref[len("origin/"):]
    if name in ("HEAD", "development", "main") or ref == "origin":
        continue
    if name in pr_by_head or (ref in unmerged and date >= SINCE):
        cands.append((date, name))

rows = {}
for date, name in cands:
    ref = "origin/" + name
    ahead, behind = map(int, git("rev-list", "--left-right", "--count", f"{ref}...{DEV}").stdout.split())
    cherry = git("cherry", DEV, ref).stdout.split("\n")
    unique = sum(1 for l in cherry if l.startswith("+"))
    mb = git("merge-base", DEV, ref).stdout.strip()
    files = [f for f in git("diff", "--name-only", mb, ref).stdout.split("\n") if f]
    mt = git("merge-tree", "--write-tree", "--name-only", DEV, ref)
    conflicts = []
    if mt.returncode == 1:
        lines = mt.stdout.split("\n")
        # after the tree id: conflicted file names, then a blank line, then messages
        for l in lines[1:]:
            if not l:
                break
            conflicts.append(l)
    msgs = git("log", "--format=%s%n%b", f"{DEV}..{ref}").stdout
    issues = sorted({int(n) for n in re.findall(r"#(\d{3,4})\b", msgs)})
    p = pr_by_head.get(name)
    rows[name] = dict(date=date, ahead=ahead, behind=behind, unique=unique, files=files,
                      src=[f for f in files if f.startswith("src/")], conflicts=conflicts,
                      issues=issues, pr=p["number"] if p else None,
                      pr_title=p["title"] if p else None, pr_user=p["user"]["login"] if p else None)
    print(f"{name}: +{ahead}/-{behind} unique={unique} files={len(files)} conflicts={len(conflicts)}",
          file=sys.stderr)

# pairwise overlap on src files among live entries (unique > 0)
live = {n: r for n, r in rows.items() if r["unique"] > 0}
overlap = collections.defaultdict(list)
names = sorted(live)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        shared = sorted(set(live[a]["src"]) & set(live[b]["src"]))
        if shared:
            overlap[a].append((b, shared))
            overlap[b].append((a, shared))
json.dump(dict(rows=rows, overlap=overlap), open(OUT, "w"), indent=1)
print(f"{len(rows)} entries, {len(live)} with unique commits", file=sys.stderr)
