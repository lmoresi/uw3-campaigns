"""Create the Project items described by manifest.json. Dry run unless --apply.
Draft items for everything except bugs; bugs become issues (or link an existing one).
Skips titles listed one per line in skip.txt; 'draft:' prefix in skip.txt forces a draft instead of an issue.
Usage: python migrate.py [--apply]"""
import json, subprocess, sys, os, re, time
APPLY = "--apply" in sys.argv
N, O, REPO = "10", "underworldcode", "underworldcode/underworld3"
m = json.load(open("manifest.json"))
skip, force_draft = set(), set()
if os.path.exists("skip.txt"):
    for l in open("skip.txt"):
        l = l.strip()
        if l.startswith("draft:"): force_draft.add(l[6:].strip())
        elif l: skip.add(l)
def sh(*a, inp=None):
    if not APPLY:
        print("  $", " ".join(x if len(x) < 60 else x[:57] + "..." for x in a)); return "{}"
    r = subprocess.run(a, capture_output=True, text=True, input=inp)
    if r.returncode: print("ERR", r.stderr.strip()[:300]); return "{}"
    return r.stdout
fields = json.loads(subprocess.run(["gh", "project", "field-list", N, "--owner", O, "--format", "json"], capture_output=True, text=True).stdout)["fields"]
F = {f["name"]: f for f in fields}
def opt(field, name):
    for o in F[field].get("options", []):
        if o["name"].lower() == name.lower(): return o["id"]
    return None
PID = json.loads(open("project.json").read())["id"]
done = json.load(open("done.json")) if os.path.exists("done.json") else {}
def body_of(it):
    src = f"\n\n---\nMigrated from the planning hub (`underworld.md`, section *{it['section']}*) on 2026-10-05."
    b = it["body"].strip()
    if it["body_issues"]: src += " Mentions " + ", ".join("#" + x for x in it["body_issues"]) + "."
    return (b or "(no body in the planning file)") + src
created = []
for it in m["items"]:
    t = it["title"]
    if t in skip or t in done: continue
    kind, status, area = it["type"], it["status"], it["area"]
    make_issue = False      # Louis (2026-10-05): load everything as drafts; bugs become issues after review
    label_title = t if len(t) <= 240 else t[:237] + "..."
    print(f"{'ISSUE' if make_issue else ('LINK #'+it['issues'][0] if (kind=='bug' and it['issues']) else 'DRAFT'):>10} | {kind:8} | {area:14} | {status:7} | {t[:90]}")
    if make_issue:
        out = sh("gh", "issue", "create", "-R", REPO, "--title", label_title, "--body", body_of(it), "--label", "bug")
        url = out.strip() if APPLY else "https://github.com/x/y/issues/0"
        item = sh("gh", "project", "item-add", N, "--owner", O, "--url", url, "--format", "json")
    elif kind == "bug" and it["issues"]:
        url = f"https://github.com/{REPO}/issues/{it['issues'][0]}"
        item = sh("gh", "project", "item-add", N, "--owner", O, "--url", url, "--format", "json")
        pass   # no public comment on the linked issue; the hub text stays in the Project item body
    else:
        item = sh("gh", "project", "item-create", N, "--owner", O, "--title", label_title, "--body", body_of(it), "--format", "json")
    iid = json.loads(item).get("id", "ITEM") if APPLY else "ITEM"
    for field, value in (("Status", status), ("Kind", kind.capitalize()), ("Area", area)):
        oid = opt(field, value)
        if oid: sh("gh", "project", "item-edit", "--project-id", PID, "--id", iid, "--field-id", F[field]["id"], "--single-select-option-id", oid)
    if it["added"]:
        sh("gh", "project", "item-edit", "--project-id", PID, "--id", iid, "--field-id", F["Added"]["id"], "--date", it["added"])
    if APPLY:
        done[t] = iid; json.dump(done, open("done.json", "w"), indent=1); time.sleep(0.5)
    created.append(t)
print(f"\n{len(created)} items {'created' if APPLY else 'would be created'}; {len(skip)} skipped")
