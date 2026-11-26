"""H7 src/ sweep: session codes and host names out of comments and docstrings (rule 9).
Each edit is (file, line, old, new); nothing is written unless every edit matches."""
import sys
WS = "a 96-thread Linux workstation"
S = "src/underworld3/"
E = [
(S + "model.py", 435, "until it was killed (kaiju, 2026-10).", "until it was killed (a Linux cluster, 2026-10)."),
(S + "mpi.py", 101, "(#874, H1's review of #1218).", "(#874, the #1218 review)."),
(S + "utilities/agreed_build.py", 58, "next agreement (H1's", "next agreement (the"),
(S + "utilities/agreed_build.py", 59, "    review of #1218). Call", "    #1218 review). Call"),
(S + "utilities/agreed_build.py", 94, "before degrading (H1, round 3)", "before degrading (review round 3)"),
(S + "utilities/custom_mg.py", 971, "on one rank (H1's review).", "on one rank (measured in review)."),
(S + "utilities/custom_mg.py", 1646, "and stays (hyperion's review, M1).", "and stays (review, M1)."),
(S + "utilities/custom_mg.py", 1747, "(kaiju, #895; rcm was", "(a Linux cluster, #895; rcm was"),
(S + "utilities/custom_mg.py", 1749, "every block measured (hyperion's review).", "every block measured (in review)."),
(S + "utilities/custom_mg.py", 1833, "from the database (hyperion", "from the database (review"),
(S + "utilities/custom_mg.py", 2647, "the solution. Hyperion measured 2-3 velocity", "the solution. Review measured 2-3 velocity"),
(S + "utilities/custom_mg.py", 2661, "applies again (hyperion measured 3 iterations kept", "applies again (review measured 3 iterations kept"),
(S + "utilities/fault_contact.py", 80, "(#874, W1's review of #1218).", "(#874, the #1218 review)."),
(S + "utilities/fault_mg.py", 462, "neighbours' (W1's rule):", "neighbours' (the rule):"),
(S + "utilities/fault_mg.py", 579, "gain (W1's decision on #1120).", "gain (decided on #1120)."),
(S + "utilities/rotated_bc.py", 150, "at two scales (H7's review).", "at two scales (measured in review)."),
(S + "utilities/rotated_bc.py", 3034, "1e-6 (hyperion's review, H1).", "1e-6 (measured in review)."),
(S + "utilities/rotated_bc.py", 2780, "(hyperion's review records and wombat, 833 decisions):", "(review records from two machines, 833 decisions):"),
(S + "utilities/rotated_bc.py", 2884, "(#964, round 4, hyperion, walls slid", "(#964, round 4, " + WS + ", walls slid"),
(S + "cython/petsc_generic_snes_solvers.pyx", 4693, "\"no datum\": hyperion's review, M1)", "\"no datum\": review, M1)"),
(S + "cython/petsc_generic_snes_solvers.pyx", 4861, "nonlinear Poisson: hyperion's review,", "nonlinear Poisson: review,"),
(S + "cython/petsc_generic_snes_solvers.pyx", 13457, "u = 0 (hyperion's review: a power-law", "u = 0 (review: a power-law"),
(S + "systems/free_surface.py", 864, "rebound (H1's review of #1205).", "rebound (the #1205 review)."),
(S + "systems/free_surface.py", 1808, "100 times too large (H1's", "100 times too large (the"),
(S + "systems/free_surface.py", 1809, "# review of #1205); ddt.py", "# #1205 review); ddt.py"),
(S + "discretisation/discretisation_mesh.py", 8600, "(measured by H1 on #1175:", "(measured in the #1175 review:"),
(S + "discretisation/remesh.py", 343, "(H4's review of #960).", "(the #960 review)."),
]
root = sys.argv[1]; bad = 0; files = {}
for f, ln, old, new in E:
    lines = files.setdefault(f, open(f"{root}/{f}").read().split("\n"))
    if lines[ln - 1].count(old) != 1:
        print(f"NO MATCH {f}:{ln}: {old!r} | {lines[ln - 1]!r}"); bad += 1; continue
    lines[ln - 1] = lines[ln - 1].replace(old, new)
if bad: sys.exit(f"{bad} edits did not match; nothing written")
for f, lines in files.items():
    open(f"{root}/{f}", "w").write("\n".join(lines))
print(f"{len(E)} edits in {len(files)} files")
