**THE PROBE PASS (Louis, 2026-11-13: "All the recommendations 1-6 seem reasonable. Let's get to work.")**

Why: 143 issues are live and the count has not moved in three days (174, 145, 143), because we raise about as many as we fix. About 80 of them were filed between July and early November against code that has since been rewritten. Louis has one more usage reset this week and wants the pile knocked down so he can return to science and writing. There is no early release: the goal is every issue labelled `fixed-in-development`, on a probe.

**For each issue on your list, in order, at most 20 minutes each:**
1. Read the issue. Run its reproduction (or the smallest one you can write from it) against the newest `development` build you have; say which commit. Development is 01dec8d2. If you need a build and your session needs Louis's go-ahead for it, ask him in your session; he has been told to expect it.
2. Return ONE verdict:
   - **FIXED**: the probe passes on development. Paste the probe and its output as a comment on the issue, name the PR that fixed it if you can tell, and add the label `fixed-in-development` (leave the issue open; it closes at release).
   - **LIVE**: one line saying which part still fails, with the number. Then a size: S (under about 40 lines of library change plus a test), M (a day), L (design or more), and whether it touches solver defaults or `petsc_generic_snes_solvers`.
   - **DUPLICATE of #N**: say which is the better record.
   - **NOT A DEFECT**: a feature request, design thread or tracking note; it goes to the roadmap.
   - **UNPROBED**: 20 minutes was not enough; say what it needs.
3. Posting: verdict comments and the label go on GitHub only if Louis has approved posting in YOUR session and your permission check allows it. If not, keep the probe in your verdict file; do not ask another session to post it for you. Rule 9 applies to anything public: name machines by what they are, no session codes without a gloss, no local paths.

**Fixing:** an S fix that does not touch solver defaults, `petsc_generic_snes_solvers`, `rotated_bc.py` or the custom multigrid may be done at once: regression test first, shown failing on development; start it at tier B; reachable from `scripts/test.sh`. Batch fixes into ONE PR per desk (at most one a day), on a side branch, so CI and review are paid once. Everything else is a verdict only; the hub assigns it.

**The week rule holds:** close, don't open. A side finding that does not corrupt results is one line in your verdict file, not a new issue.

**Report:** a table, one row per issue (number, verdict, one line, size), in the campaigns repo as `probe-pass/<your code>.md`, committed as you go, with a dated "for the hub" line at the top when you pass the halfway mark and when you finish. The hub pulls the repo whenever it wakes. Sessions that cannot message the hub also drop a one-line "done" note in `mail/H1/` marked "relay to C1".

## Lists (C1, 2026-11-13; sorted from titles, so say if one is not yours)

- **H1** (parallel): #873 #874 #888 #956 #962 #893 #885 #900 #923 #960 #975 #976 #999 #994 #974
- **H3** (evaluate and general; after the #1121 table): #551 #604 #641 #799 #1004 #824 #844 #957 #864 #587 #1083 #842 #922 #944
- **H4** (adjoint, thin sheet, swarm, transport API): #781 #787 #804 #879 #872 #870 #554 #866 #867 #868 #984 #966 #995 #1000 #1034 #1029 #810
- **H5** (faults, placement, multigrid, restart; until #1119 is on development, then #1120 first): #429 #449 #494 #559 #595 #621 #623 #670 #718 #940 #880 #1064 #540 #610 #408 #157
- **H6** (rotated BC, spherical, benchmarks; verdicts only, the territory is W1's): #98 #949 #953 #608 #939 #941 #883 #884 #887 #348 #826 #817 #821 #473 #410 #1011

Not in the pass: in flight (#1093 #1103 #1120 #1122 #1089 #1090 #1069 #1072 #969 #1118 #1115); units, waiting on Louis's ruling (#771 #881 #904 #979 #990 #991 #992 #993 #998 #1001 #1080 #1081 #786); stress history (#735 #738 #742 #749 #797 #811 #871 #1009 #685 #1025 #712); extreme-viscosity conditioning (#1058 #1059 #625 #755); roadmap candidates (labelled `roadmap`).
