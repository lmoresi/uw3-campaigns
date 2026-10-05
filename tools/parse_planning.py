"""Parse Planning/underworld.md into items and write a migration manifest (dry run).
Usage: python parse_planning.py <underworld.md> <outdir>"""
import json, re, sys, os
src, out = sys.argv[1], sys.argv[2]
lines = open(src).read().split("\n")
TAG = re.compile(r"<!--\s*([^>]*?)\s*-->")
ITEM_SECTIONS = {"Active": "active", "Bugs": "bugs", "Nice to Have": "nice"}
items, prelude, section, cur = [], [], None, None
def close():
    global cur
    if cur: items.append(cur); cur = None
for ln in lines:
    h2 = re.match(r"^## (.+?)\s*(<!--.*-->)?\s*$", ln)
    if h2:
        close()
        name = h2.group(1).strip(); tags = TAG.findall(ln)
        section = {"name": name, "kind": ITEM_SECTIONS.get(name, "other"), "tags": tags}
        if section["kind"] == "other" and name not in ("Code Quality Guidelines", "Periodic Reviews"):
            # a project sub-section is itself one design item
            cur = {"section": name, "kind": "other", "title": name, "tags": tags, "lines": []}
        continue
    if section is None:
        prelude.append(ln); continue
    start = re.match(r"^- \*\*(.+?)\*\*(.*)$", ln) if section["kind"] in ("active", "bugs") else re.match(r"^### (.+?)\s*$", ln) if section["kind"] == "nice" else None
    if start:
        close()
        title_raw = start.group(1) + (start.group(2) if section["kind"] != "nice" else "")
        tags = TAG.findall(title_raw) + section["tags"]
        title = TAG.sub("", title_raw).strip().rstrip(":").strip()
        cur = {"section": section["name"], "kind": section["kind"], "title": title, "tags": tags, "lines": []}
        continue
    if cur is not None:
        cur["lines"].append(ln)
    elif section["kind"] in ("other",) and section["name"] in ("Code Quality Guidelines", "Periodic Reviews"):
        prelude.append(ln)
close()

def area_of(tags):
    for t in tags:
        m = re.search(r"project:underworld3/([\w-]+)", t)
        if m: return m.group(1)
    for t in tags:
        if "batbot" in t: return "batbot"
    return "general"
def kind_of(it):
    t = it["title"].lower()
    if it["kind"] == "bugs": return "bug"
    if t.startswith("decision"): return "decision"
    if t.startswith(("design direction", "priority", "liaison")) or it["kind"] == "other": return "design"
    if it["kind"] == "nice": return "idea"
    return "task"
STATUS = {"active": "Active", "bugs": "Active", "nice": "Someday", "other": "Active"}
for it in items:
    body = "\n".join(it["lines"]).strip("\n")
    it["body"] = body
    it["annotations"] = [l.strip() for l in it["lines"] if l.strip().startswith(">")]
    m = re.search(r"(?:added|Louis,?)\s*(\d{4}-\d{2}-\d{2})", it["title"]) or re.search(r"(\d{4}-\d{2}-\d{2})", it["title"])
    it["added"] = m.group(1) if m else None
    it["issues"] = sorted(set(re.findall(r"#(\d{3,4})\b", it["title"])))
    it["body_issues"] = sorted(set(re.findall(r"#(\d{3,4})\b", body)) - set(it["issues"]))
    it["area"] = area_of(it["tags"]); it["type"] = kind_of(it); it["status"] = STATUS[it["kind"]]
    it["target"] = ("link existing issue #" + it["issues"][0]) if (it["type"] == "bug" and it["issues"]) else ("new issue" if it["type"] == "bug" else "draft item")
    it["words"] = len(body.split()); del it["lines"]
os.makedirs(out, exist_ok=True)
json.dump({"prelude": "\n".join(prelude), "items": items}, open(f"{out}/manifest.json", "w"), indent=1)
with open(f"{out}/MIGRATION_DRY_RUN.md", "w") as f:
    f.write("# underworld.md -> GitHub Project: dry run\n\n")
    f.write(f"{len(items)} items. Nothing has been created. Columns: what would be created, Project fields, size of the body carried over, annotations found, and issue numbers the body mentions (a bug whose body cites an issue may already be tracked or fixed: those rows need a human eye before a new issue is opened).\n\n")
    f.write("Rules applied: Active and Nice to Have items and the project sub-sections become DRAFT items (no issue); Bugs become issues unless the title names one, which is linked instead. Type from the title (Decision, Design, Task, Bug, Idea); Area from the project tag; Status Active or Someday; Added from the date in the title. Body text and annotations carry over verbatim into the item.\n\n")
    for kind, head in (("active", "Active"), ("bugs", "Bugs"), ("nice", "Nice to Have"), ("other", "Project sub-sections")):
        sel = [i for i in items if i["kind"] == kind]
        f.write(f"## {head} ({len(sel)})\n\n| # | title | creates | type | area | status | added | body words | annotations | issues in body |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for n, i in enumerate(sel, 1):
            f.write(f"| {n} | {i['title'][:110]} | {i['target']} | {i['type']} | {i['area']} | {i['status']} | {i['added'] or ''} | {i['words']} | {len(i['annotations'])} | {' '.join('#'+x for x in i['body_issues'][:6])} |\n")
        f.write("\n")
    f.write("## Not migrated as items\n\nThe sections before Active (Code Quality Guidelines, Periodic Reviews, Issue Triage SLA) are standing rules and review cadences: they go to the wiki as Working Practices pages, not to the Project.\n")
print(len(items), "items;", sum(1 for i in items if i["target"]=="new issue"), "new issues;", sum(1 for i in items if i["target"].startswith("link")), "linked issues;", sum(1 for i in items if i["target"]=="draft item"), "draft items")
