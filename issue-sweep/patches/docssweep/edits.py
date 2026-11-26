"""H7 docs/ sweep, clear cases only (C1's interim rule, 2026-11-26): session codes, and
workstation host names used as where a measurement was made. Cluster and platform
mentions (Kaiju, Gadi) are left as they are, pending Louis. (file, line, old, new)."""
import sys
WS = "a 96-thread Linux workstation"
P = "docs/developer/design/CONVERGENCE_REFERENCE_POLICY_2026-11.md"
E = [
(P, 3, "The inventory it rests on is hyperion's, posted on #911", "The inventory it rests on was posted on #911"),
(P, 39, "(hyperion's review, M3)", "(review, M3)"),
(P, 43, "read by value it did not: hyperion's review, M1)", "read by value it did not: review, M1)"),
(P, 49, "(hyperion's review, M2)", "(review, M2)"),
(P, 51, "(hyperion's review, H1)", "(review)"),
(P, 51, "758 s to 13.6 s on wombat,", "758 s to 13.6 s on a workstation,"),
(P, 51, "(hyperion's review records and wombat)", "(review records from two machines)"),
(P, 51, "where development is 1e-8 (hyperion's review)", "where development is 1e-8 (review)"),
(P, 100, "(laptop, plus hyperion with Nehalem and Zen forced)", "(laptop, plus " + WS + " with Nehalem and Zen forced)"),
("docs/developer/CHANGELOG.md", 163, "takes 13.6 s on wombat against 758 s", "takes 13.6 s on a workstation against 758 s"),
("docs/developer/subsystems/rotated-freeslip.md", 352, "(#964, round 4, hyperion)", "(#964, round 4, " + WS + ")"),
("docs/developer/design/parallel-addon-distribution-2026-10.md", 40, "## Measured (hyperion, f21f3d85, under a 16-rank study)", "## Measured (" + WS + ", f21f3d85, under a 16-rank study)"),
("docs/developer/guides/fault-multigrid.md", 199, "4 on hyperion's fixture,", "4 on the review's fixture,"),
]
root = sys.argv[1]; bad = 0; files = {}
for f, ln, old, new in E:
    lines = files.setdefault(f, open(f"{root}/{f}").read().split("\n"))
    if lines[ln - 1].count(old) != 1:
        print(f"NO MATCH {f}:{ln}: {old!r}"); bad += 1; continue
    lines[ln - 1] = lines[ln - 1].replace(old, new)
if bad: sys.exit(f"{bad} edits did not match; nothing written")
for f, lines in files.items():
    open(f"{root}/{f}", "w").write("\n".join(lines))
print(f"{len(E)} edits in {len(files)} files")
# applied after the list above (found by the second search):
# docs/reviews/2026-10/stress-snapshot-order-adversarial-review.md:10 "probes on hyperion." -> "probes on a 96-thread Linux workstation."
# docs/reviews/2026-10/stress-snapshot-order-adversarial-review.md:98 "(a campaign, not a hyperion job)" -> "(a campaign, not a single-workstation job)"
