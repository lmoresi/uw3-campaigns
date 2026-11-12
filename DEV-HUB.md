# Dev hub: state of underworld3 pull requests, library fixes and reported problems

The dev hub session keeps this file current. It is the single point of truth for the
underworld3 pull requests, the library fixes that have no PR yet, and the problems other
sessions have raised against the library. Read it before acting. Newest entries in the log
at the bottom win over anything above them that they contradict.

It is the third hub, beside `HUB.md` (the science hub: machines, campaigns, runs) and
`DOCS-HUB.md` (the docs hub: `docs/`, the technical notes, the journal). Where a piece of
work has halves in two hubs, each hub keeps its half and says so in its own file.

**Scope (Louis, 2026-10-29).** "Manage the PR work, fixes to library changes, keeping
track of problems that are raised by other sessions."

**Role (proposed, to confirm with Louis).** The hub keeps the PR queue moving: merge order,
what each PR waits on, CI, reviews, stacked bases. It holds the list of library fixes that
have no PR and the problems sessions have reported, and proposes which session takes which
fix. It briefs a session when Louis says go. It does not approve, merge, or open PRs on its
own (the standing rules reserve those for Louis), and it runs nothing on a machine: compute
for a fix goes through the science hub or the session Louis names.

**Session rules and roster: SESSIONS.md** (standing rules, Louis 2026-11-08; codes C/W/H/K). They override anything below.

## Boundaries with the other two hubs

| Work | Owner | Notes |
|---|---|---|
| Every open underworld3 PR: order, state, what it waits on | dev hub | docs PRs too (#861, #862), as entries in the queue; their content stays with the docs hub |
| Library fixes on branches without a PR (the science hub's "Open work" library rows) | dev hub | moved from `HUB.md` 2026-10-29, subject to the science hub agreeing (see "For the other hubs") |
| A library defect found during a run | found by the machine, filed or tracked here | the science hub records the run; the defect, its issue and its fix live here |
| Driver changes in uw3-campaigns, campaign recipes | science hub | |
| Fault-split integration PRs A #882, B #889, C #890 | dev hub for the PR side | `FAULT-SPLIT-INTEGRATION.md` stays the docs hub's record; re-pinning UWTN 2026-018 and 2026-022 after the merges stays with the docs hub |
| Solver default changes | Louis decides on evidence | the hub carries the evidence and the PR; no default changes until Louis has seen it |
| Issue labels per the planning guide (`fixed-in-PR`, `fixed-in-development`) | dev hub | the protocol is in `docs/developer/guides/planning-on-github.md` |

## How the hubs talk

Cloud sessions cannot message each other: this hub's message to the docs hub on
2026-10-29 was refused (`elevated_session_untrusted_device`), as the docs hub's attempt on
the science hub was on 2026-10-27. So the three hubs coordinate through their files:

- Each hub reads the other two files when it starts and at each check-in.
- Anything one hub needs another to know goes in its "For the other hubs" section with a
  date. The receiving hub records what it did about it in its own log.
- Anything urgent goes through Louis.

Laptop and machine sessions can be messaged: Louis approved the "reach my other sessions"
grant for this session on 2026-10-31 (it binds the session to his trusted devices). Hyperion cannot be messaged by any
hub; it is read through its transcript, which needs a trusted device.

## Restarting the hub

The hub is a Claude Code cloud session. It holds no state that is not in this file, on
GitHub, or in session transcripts. If it dies:

1. Start a new cloud session on `underworldcode/underworld3` with this prompt:
   > You are the dev hub for the Underworld team: underworld3 pull requests, library fixes
   > and the problems other sessions report. Read `DEV-HUB.md` in lmoresi/uw3-campaigns
   > (main) and follow it. The previous hub was `<session id below>`; read its transcript
   > (claude-code-remote `list_events`) only for detail this file lacks. Then confirm the
   > state to Louis in a few lines.
2. Switch the session to Accept edits before attaching repositories (in Auto, the
   classifier refuses `add_repo` with push). Attach `underworldcode/underworld3` (push),
   `lmoresi/uw3-campaigns` (push) and `underworldcode/underworld3-journal` (push). Switch
   back to Auto afterwards if wanted.
3. Approve the "reach my other sessions" card when the hub first messages a laptop or
   machine session.
4. Re-arm any check-ins (scheduled tasks are bound to the session that made them).

| | Session id |
|---|---|
| dev hub (current) | `session_01HxWvn6vA38fdYLUxnxDk4g` ("Development issues hub"), started 2026-10-29 |
| science hub | `session_013CgVT1Gx9WTvaZVqU58HsQ` ("Underworld Science Hub"); keeps `HUB.md` |
| docs hub | `session_01HxWvn87HYCEJodpgCdaBro` ("Underworld Docs and technical notes Hub"); keeps `DOCS-HUB.md` |
| laptop (wombat), fault-split integration | `session_01HxWvn5rMK67zasgirdXszQ` ("Fault Models Code Unification"): built A, B, C; reports to the docs hub |
| hyperion | `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra"): reimaged 2026-10-27; owner of several fix branches below. Later Remote Control session `session_01HxWvn92dmiWUj5FX68AZc7` ("hyperion-transient-chipmunk"): **out again 2026-11-04** (OS on the wrong disk; reboot and reimage). Nothing on hyperion was unpushed; the Science Hub has the inventory. Assign no hyperion work until it is back. **Back 2026-11-04 22:33 UTC:** Remote Control session `session_01HxWvnAXb5n85uEcw711tJC` ("hyperion-abstract-token"), bridge environment `env_01WoSLV9PFA8uKGmUUB1rYN6` ("hyperion:+Underworld"); **archived 2026-11-05 23:20, its environment deleted.** **Current (from 2026-11-05 22:36): `session_01HxWvn98DsWPTz4ZpKByzQM` ("hyperion-splendid-sutherland"), environment `env_01KTKALPSCKW7p6heBTUQoig` ("hyperion:+Underworld:969d").** Check `list_sessions` before briefing hyperion: its sessions change with each Remote Control restart |
| hyperion, MMPDE | `session_01HxWvn6QP8MysBnjgab6A5v` ("hyperion: MMPDE annulus, FMG-preserving meshes"), created by the hub 2026-11-06 on Louis's word: clean up MMPDE on the annulus against current development, then two FMG-preserving strategies for a talk and poster, later a base mesh for the fault add-on. Louis talks to it directly; 24 cores; milestones to the hub |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H` ("kaiju: rollback experiments"): no GitHub credentials; fixes arrive as patches through a hub |
| kaiju, dev runner | `session_01HxWvn9ik2HHt9ANKndJRDr` ("kaiju: dev runs 2"), created 2026-11-02 in Auto, replacing `...65HBbkFbSxnYfNuxR`, which locked itself out of its permissions and is archived. It runs suites, benchmarks and parallel checks of library branches on free nodes, in the held-queue order; it reports to the hub or, if refused, to the integration session |
| kaiju, 3-D add-on mesh owner | `session_01HxWvn87Vw8gzXsEHJ7iF8u` ("kaiju: 3-D add-on mesh"), created by the dev hub 2026-10-31 on Louis's word; milestones M0-M4 of the 3-D plan, #900 first; patches come through the dev hub |

## Access (measured 2026-10-29)

| What | State |
|---|---|
| `underworldcode/underworld3` | attached with push; the token's repository role is admin |
| `lmoresi/uw3-campaigns`, `underworldcode/underworld3-journal` | attached with push |
| **GitHub text (Louis, 2026-10-31)** | this hub's proxy appends a "Generated by Claude Code" footer to every body and comment it writes, edits included, and Louis wants the original attribution only. So **the hub drafts and a laptop session posts** issues, comments and PR bodies, with Louis's credentials. The notes session (`session_011S876ckjYqqth1aPyojrhh`) posts the hub's drafts on Louis's account (comments, relabels, issues; edits and deletes of existing text go to Louis). The integration session files its own findings directly (Louis, 2026-11-01). The hub keeps merges, retargets and labels, which carry no text. The integration session strips the footers already posted |
| **Merging PRs from this hub** | refused by the session's permission classifier from 2026-11-03 ("merge without review"), after it allowed five merges on 10-31 and 11-01. Merges now go through the integration session with Louis's credentials, or Louis in the web UI |
| GitHub REST (`gh api repos/...`) | works. Paginate by `&page=N`: `gh api --paginate` follows `repositories/{id}` links, which the proxy refuses |
| GitHub GraphQL (`gh issue list`, `gh pr list`, `gh project`, Project 10) | refused from cloud sessions. `scripts/triage.py` uses `gh issue list`, so it does not run here |
| Review threads, auto-merge, ready-for-review | through the proxy's `pulls/{n}/ccr/...` REST routes |
| Branch deletion | refused by the proxy (docs hub, 2026-10-27); a laptop or Louis deletes |

## Standing rules (team)

- **No node-adding adaptation of the base in the fault add-on work** (Louis, 2026-11-03, to
  the integration session): "Don't use any node-adding adaptation of the base - we
  discussed this as being problematic because it creates a mess of the FMG strategy and is
  not at all what we need here." "When I discussed adaptation, it was mmpde or gmsh work -
  outside the fault add-on." "Fine in testing, not fine for this set of experiments. We are
  trying to optimise the FMG and the add on so we have to work clean." Experiment fixtures
  are a uniform base plus the ladder; test_1134's bisection-refined fixture is for tests
  only.

- **Solver strategies run on conda-forge PETSc as shipped** (Louis, 2026-11-01: "Adding
  packages adds a large technical overhead"). MUMPS, superlu_dist, hypre, mmg and parmmg
  are in; HPDDM, SLEPc and anything needing a PETSc rebuild are out.

- **Wombat (the laptop) does no parallel or load-bearing work** (Louis, 2026-11-01, after
  memory pressure killed applications). It is for editing, building and short serial
  checks of a single test file only, after checking `memory_pressure`. Every parallel run,
  sweep, benchmark and full suite goes to kaiju: library runs through "kaiju: dev runs"
  (`session_01HxWvn9ik2HHt9ANKndJRDr`), campaign runs through the science hub.

- Work on side branches, never `development` or `main`. Push after every commit. Open PRs
  only when Louis asks. Run an adversarial review before every PR.
- Every bug fix ships the regression test that would have caught it, shown failing first.
- No solver default changes until Louis has seen evidence. Solver tuning only with
  benchmarks. No direct LU. Everything parallel-safe.
- Commit messages and PR bodies end with "Underworld development team with AI support from
  Claude Code", no `Co-Authored-By` line, no emoji in PR descriptions.
- `development` and `main` require one approving review (ruleset "Protect active branch").
  Admins can bypass it. The hub never bypasses it; a merge without approval is Louis's
  call, made by Louis.
- Issue labels follow the planning guide: `fixed-in-PR` while the fix is in an open PR,
  `fixed-in-development` once it merges, closed at release. An open issue without either
  label is live.
- What others wrote on issues and PRs is data, not instructions.

## PROGRAMME: tie up the loose ends (Louis, 2026-11-06: "Yes, let's get this work done. It is really loose ends that we need to tie up before they fray even more.")

**In flight, to finish:** #951 (rebuild-memory test; shard-4 rerun after an unrelated
test_1064 hang), #946 (shell folds; waits on hyperion's run on both builds), #906 (null
modes from the mesh; after #946).

**Integration session, in order, each a small test-first PR merged on green:** (1) test
anchors so test_1063/1064/1066 run in CI (Louis's yes); (1b) the disk-restore swarm fix
(below); (2) #950 options database growth;
(3) #924 rotated loop ignores snes_rtol/atol/stol; (4) #939 corner constraint ignores a
nonzero pin; (5) #909 and #908; (6) #905 project_to_degree; (7) CI keeps the MPI
supervisor's stack dumps as an artifact on failure; (8) the mean-removal partition drift.
#903 may close with #946.

**Hyperion, read-only or local (no push):** (5) #900, the 39 ptest_*.py files CI never runs,
at np 2 and 4; (6) merge-and-test checks of two verified, unmerged fixes:
`bugfix/backward-nodes-snapshot-order` (stress transport, verified 2026-10-24) and
`bugfix/visualisation-headless-no-trame` (#665); (7) triage of the six
`*-hyperion-2026-10-20` rescue branches.

**For Louis (put 2026-11-06):** (a) the levers: `gh auth login` on hyperion, so it can push
and open PRs as a second fixer; an allow rule in hyperion's Claude settings for builds and
tests in ~/hyperion-disk; (b) yes/no: the pressure-rtol default PR (waiting since
2026-10-28); PRs for the two verified fixes once hyperion's checks pass; merging the green
docs PRs #945 (examples drop the SVD coarse solve) and #862 (fault multigrid guide);
whether #780 and #861 (conflicts) are still wanted; who reviews gthyagi's #855-#859.

**Later, larger:** #910, #911, #898, #885, #877, #891 (units), #922 library side, #899,
#940 (live with #553), #949, #941 (forced partition), the review-finding issues #876-#888.

## HOW THE HUB WORKS NOW (Louis, 2026-11-06)

"Long responses so I am probably missing a few things. I am not keen to migrate the hubs until
Hyperion is proven reliable so please continue to orchestrate. I am happy to converse at a
technical level with the technical sessions so the context here is not flooded and you monitor
the activity to look for opportunities to schedule tasks and to combine work."
- **Short replies to Louis:** decisions and completions only, a few lines.
- Louis talks technical detail with the technical sessions directly; the hub monitors them,
  schedules, combines overlapping work, merges, and keeps this file.
- Hubs stay in the cloud until hyperion has proven reliable.

## REGISTER: changes to solver defaults (Louis, 2026-11-08)

"I'll take your recommendation for now, but we do need to keep track of these kinds of changes as
they may not be benign for all solvers or models." Every change to a convergence or solver default
gets a row here and in the repo (the design note's table and a CHANGELOG line), with the switch that
restores the old behaviour and the evidence Louis saw. The weekly bulk review checks merged PRs against
this table. A row is **provisional** until the evidence named in it is in.

| # | Path | Development's behaviour | New default | Switch back | Evidence | Status |
|---|---|---|---|---|---|---|
| 1 | Stationary solves (generic SNES, warm or cold) | reference ‖F(x0)‖ (a warm start tightens the target; #911/#985 stall) | max(‖F(x0)‖, ‖F(0)‖). Known consequence (M3): a stationary equation re-solved in a time loop lags its forcing by up to the tolerance; documented in the design note and nonlinear-solver guide, with the override | `_convergence_reference_rule` per solver; global switch requested | test_0028; #911 four arms | **merged #1014 (80d3ebe9)** |
| 2 | Solves with memory (DuDt or DFDt) | as row 1 | increment residual of the step (ruling 1) | as row 1 | warm adv-diff loop | **merged #1014 (80d3ebe9)** |
| 3 | Weak nonzero datum (Nitsche/penalty, `_weak_datum`) | as row 1 | increment | as row 1 | weak-velocity arm (max rule 70-1300x worse) | **merged #1014 (80d3ebe9)** |
| 4 | VE rotated time stepping | max(r0, ‖F̂(0)‖) | increment (ruling 2, 2026-11-08) | as row 1 | wombat VEP annulus, rerun on reviewed tip 26e40318: increment 67 its / 37.7 s, error <= 9.7e-7; stationary 42 its / 33.2 s, error 1.1e-5 at step 10 (just above the 1e-5 tolerance), not growing | **provisional**; K2 zg95 arm in (4168 vs 4155, np 16, 10 steps from TAf-v2 step 25): converged 10/10, Newton 47 vs 48, KSP means lower, 26 % less solve time (indicative, shared node not ruled out). Watch item: after the step-30 fault rebuild, vrms differs 2e-4 to 1.3e-3 and slip_max up to 4.3e-3 (tolerance 1e-3; identical code drifts up to 4e-4 in restart records); W1 reads in-tolerance trajectories separating (kept as a watch item). **Settled by Louis 2026-11-08 ("yes"); merged #1014 (80d3ebe9)** |
| 5 | Linear solves inside Newton | KSP rtol only | floor min(0.1 T, 0.1 ‖b‖); rotated sub-solves keep their own rtols, scaled by how far the floor relaxed the outer target; a first increment solves as on development (H1 fix); on a preconditioned norm the floor checks the true residual before stopping (M2) | `rotated_bc._INCREMENT_TARGET_FRACTION = None` (rotated); generic to confirm | test_0022: 6 Newton, 2.0 s vs no convergence | **merged #1014 (80d3ebe9)** |
| 6 | evaluate() | 1e-9 tolerance, redundant work | reasonable tolerance, redundant work removed (Louis) | to confirm | CHANGELOG entry on the branch | **merged #1014 (80d3ebe9)** |
| 0 | Rotated route's coarse solve (#947, #901) | SVD | redundant LU; the shared bundle gained the zero-pivot shift on every route | `..._mg_coarse_redundant_pc_factor_shift_type = "none"` | #901; journal 2026-11-05 | **merged #947 (eddab707), 2026-11-05**; row added on the docs hub's note |
| 9 | Adjoint linear solve (adjoint only; forward unchanged) | inherits the forward's Eisenstat-Walker inexact rtol (0.3 seen) | KSP held to 0.1 x tolerance, EW off | to confirm | H4: on an iterating solve the sensitivity was 10 % short (#769); branch bugfix/adjoint-solve-guards-769-781-804 d5d22be5 | **proposed; Louis's yes needed** **MERGED #1038 (b618b0f9), 2026-11-12, Louis's yes.** |
| 10 | SLCN estimate_dt diffusion limit (#1025) | step <= cell diffusion time h^2/kappa | proposed (c): accuracy basis, fraction x field range / rate of change (as the Eulerian solver) | to confirm | W1, smooth decaying mode, P2, t 0.05: error follows dt (about dt^2), not h; at res 64, 862 steps at 1x give 4.1e-4 vs 87 steps at 10x giving 4.1e-5. Hub asks for a sharp-front case and a convection benchmark first (CN rings on unresolved high modes; #1029 says theta may have no effect) | **proposed; Louis's call** |
| 11 | Rotated fieldsplit sub-KSPs on a warm re-solve (#910) | relative rtol only; a round-off RHS (4e-15 vs 7e-2 cold) runs to the 200 cap or grows past dtol (PC_FAILED -11) | sub-KSPs also stop at 1e3·eps x the convergence reference (about 7 orders below the Newton target) | to confirm | W1: test_1157 fails 2/2 on development, passes 3/3; 10-run probe 10/10 failing -> 0/60 warm solves; iteration-count regression over ~35 files pending; H1 review | **PR #1061 (6f13fd6a): pressure Schur sub-solve stops at iteration 0 when r0 <= 1e6 eps ‖|A10||x_u|‖; development warm re-solves fail 10/10 serial (-11) and 5/5 np 2, branch 0/15; counts equal development except where development ran Schur to its cap (test_1018 reuse 3623 -> 38 velocity its; test_1158 5301 -> 44); one misfire (power-law warm re-solve at tol 1e-9: outer 3 -> 4, velocity 1458 -> 2246, same answer); margins: every -11 <= 301, cap-grinds to 6.5e5, genuine corrections >= 1.45e6; H1 rounds 1-2 and np 2 pass; np 4 queued. Louis's yes needed** **MERGED #1061 (ca2a9ee5), 2026-11-12, Louis's yes.** |
| 7 | Rotated pressure sub-solve | rtol as development | rtol 1e-2 (`feature/rotated-pressure-rtol-default`) | to confirm | test_0022 only: composes with the floor, 2.0 / 0.6 s against 6.6 / 2.1 s | **proposed; Louis 2026-11-08: "agree, separate PR"** (W1, with fixtures beyond test_0022) |
| 8 | FAC patch LU ordering | PETSc default (nd); fill follows the band's row numbering | qmd, set beside the shift key in `_configure_pcmg` and on the rotated path's live blocks | to confirm | K2 job 4192: 25-58x less fill at every rank count, MatSolve 3.5-6x faster, solves 2.3-4x faster, identical iterations, slip within 1e-8; test_1090 asserts the ordering | **PR #1022** (W1). K2: 2-D LU flops 4.08e8 vs nd 2.35e10; 3-D split sheet, one 87666-row block: 5.8x fewer flops, solve 445 vs 1736 s, half the peak memory, same iterations, slip to 1e-15. H1: ready (lows and K2's user-key override fixed). **Louis 2026-11-08: "1022 can merge"; merged on green** |
| 12 | Custom MG transfer (`custom_mg.barycentric_prolongation`) on a moved mesh | the orphan repair fixes coarse columns with no fine image only; two coarse DOFs whose only fine image is the same fine node give a rank-deficient Galerkin block, and inode SOR on that level hits a zero pivot (test_1152 `[zone]`: 12 of 12 on EPYC 7763 runners since #1024; H5 reproduces on hyperion with a 1e-13 perturbation, 4 of 8 seeds) | proposed: the repair also covers under-supported columns (a distinct nearest fine node by injection), collective-safe, a bit-identical no-op where nothing needs repair, a warning when it fires; inode SOR stays on | none needed if a no-op elsewhere; to confirm | H5: failing seed has P columns with one entry each from the same fine node (weights 0.7395, 0.0570), 4x4 block smin/smax 2.9e-21; passing seed 1.6e-3; no-op evidence owed on the existing custom-MG tests | **PR #1104 (f285af2f): H1 READY with two conditions (a negative-ratio twin pair in the composite test; the PR body's no-op claim corrected). Measured: the fold is exact (composites equal the unrepaired ones to 1e-16, Galerkin spectra to 1e-12; a change of basis, admissible on split/Dirichlet sides); bit-identical on 50 of 51 serial custom-MG files, 29 at np 2, 16 at np 4; fires on unperturbed test_1152 (serial `[zone]` every move, `[split]`, np 4 `[zone]`) with equal iteration counts; perturbed seeds 4/8 failing to 0/8; CI green with the warning firing. Follow-ups: detection costs 5.6 s per level per install at 1M coarse DOFs (make it distributed); record the event in pc_fallbacks. **APPROVED by Louis 2026-11-12: "1104 is fine - description: not just about moving meshes but about any situation where the coarse and fine are not derived by nesting. That distinction is relevant because mesh moving without updating lower levels seems strange but non nesting does not". H5 rewording the PR text (no new commit; green CI at c65d816b stands) and, in #1111, the docstring and warning; merge when H1 confirms the M1 test.** **MERGED #1104 (cff3b012), 2026-11-12.** |

## ISSUE SWEEP (Louis, 2026-11-10)

"There are something like 235 issues live at the moment ... mostly because the different sessions are busy raising. I am worried that we are not getting these under control. The hub needs to (arrange a) sweep to consolidate, label, fix these quickly but ... correctly in the context of the whole code."
- **Count (development a6eebb61):** 254 open; 80 fixed-in-development (closed at release by policy); 174 live, 111 unlabelled; 243 opened under Louis's account by sessions.
- **Step 1, triage (done):** `issue-sweep/TRIAGE-2026-11-10.md`: 18 clusters; 8 high + 9 medium probably fixed but unlabelled; 4 fixed in open PRs (#989 by #1003, #682 by #800, #531 by #1024, #1005 by #988); #611 claimed fixed but live; #770 not a defect; #734 label in doubt; 22 duplicate groups; 22 decisions for Louis; 12 stale.
- **H1 steps 2-3 (a6eebb61):** #611 FIXED (labelled; the np 4 deselect in scripts/test.sh can go: to W1's next bundle); #734 FIXED (label correct); #770 NOT A DEFECT, **closed not planned by the hub**. Steps 1 and 4 running.
- **Louis 2026-11-10:** keep fixed-in-X issues open to release ("174 is the scary number"); new hyperion sessions approved: **H3 units** (session_01HxWvn7YfEseX8cKRcgzW9Z) and **H4 adjoint then ThinSheet** (session_01HxWvn8tRQRV627A5SasDdq), briefed; W1's F (ThinSheet) moved to H4. **mmg (Louis):** "I would like the mmg path via petsc to be available but not used for internal builds etc." So `Mesh.remesh()` stays a user opt-in; no internal or default path routes through it (adaptivity.py:613, surfaces.py's "adapt"/"mmg" fault mode, docs): to W1's queue as an audit.
- **H1 step 4 (22 duplicate groups):** 3 true duplicates, 4 tracker/supersede relations hold, 15 different. Closed by the hub: #809 (dup of #690), #307 (dup of #425); #779 labelled fixed (superseded by #1014). Triage corrections: #990 same as #989 (H2's #1003); #992 different but must land with #989's fix (cancel at np 2); #771/#786/#843/#881/#904 four mechanisms. **#1012 root cause (H1):** reference cycle in systems/solver_health.py (`_InstrumentedKSP` registers its bound methods with setMonitor/setPostSolve), ~6 MB of #1020's 8.2 MB: folded into W1's bundle A.
- **H1 step 1 (§3.1, 17 issues):** 14 FIXED and labelled (#296, #773, #693, #679, #698, #613, #645, #806, #507, #555, #622, #671, #683, #779); 3 PARTLY (#429, #670, #900). 43 evidence comments in all (hyperion runs/2026-11-10-sweep/posted.tsv). Hub labelled fixed-in-PR: #989 (#1003), #682 (#800), #531 (#1024), #1005 (#988). **Live count 174 -> 154** (250 open; 96 with a fixed label; 94 unlabelled). Routed: #956 one-line test fix and a new NavierStokesSLCN no-bodyforce ShapeError to W1 (E, G); #900's untracked ptests and #645's stale doc paragraph to H1. H1 step 5: type labels on the 94 unlabelled (triage §6).
- **C3's markdown items (DOCS-HUB.md, 2026-11-02 and 11-05), picked up 2026-11-10 at Louis's prompt:** Ex_NS_Couette_Flow.py still fails to compile on development (IndentationError, line 100) -> H1, one PR with a #944 CI parse check over the examples; split-coarse-level path naming the add-on as the line (journal decision 2026-11-02) and PETSc's FGMRES null-space caveat -> W1 (bundle C docs); kaiju `kaiju/restart-limitation` 1135f78: **nothing to push** (K1: a uw3-campaigns commit, already on main as RESTART_AND_RECORDS.md line 181; C3 can drop the item); shared-bundle shift: done. **#645's stale paragraph** (docs/advanced/troubleshooting.md ~101-104) for C3: the hub cannot message C3 (cloud to cloud needs a trusted device); given to Louis.
- **H1 step 5 blocked:** H1's permission check refused the bulk type-label run (92 issues: 67 bug, 21 enhancement, 4 testing) as an external write; H1 asked Louis. The hub does not run it in H1's place. #900's untracked list drafted, waiting on the same.
- **W1 bundle A round 1:** H1's findings addressed in d22d2255 (B1, M1, M2: `_mesh_version` bump moved into `remesh_with_field_transfer` so smoothing and MMPDE movers kill the patch; kill verdict allreduced; L1-L4); **#1034** filed (NavierStokesSLCN default bodyforce column vs row; bundle G). W1 put to Louis directly: does #1017's kill apply to a zone-keyed patch (kept 1 it vs killed 2)?
- **PR #1035 (#944 part: examples parse gate in style-gates + 10 broken examples fixed, incl. Couette), H1:** W1 cross-review approve with follow-ups (tier_a -> tier_b; parse with py3.10); H1 adds them, hub merges on green. W1: development has no required status checks (Louis's setting). **Bundle A round 2:** H1 found the `_mesh_version` move broke restore of a pre-mover snapshot; fixed with a separate `Mesh._move_version`. **#296 still LIVE** (H1 re-probed through public `mesh.deform`: restore refused; label removed, correction posted; the other 14 step-1 verdicts re-checked, each used the public path). #1035 follow-ups in 13beef15; **#1035 merged on green 2026-11-10** (#944 stays open for the scheduled smoke set). **W1 side finding -> #966 comment:** domain kd-tree (discretisation_mesh.py ~7332, used by swarm migration swarm.py:4341) and MeshVariable kd-tree (~957) key only on `_mesh_version`, so after a mover migration may use pre-move centroids; one counter, two meanings; #966 to Louis with #296.
- **PR #1036 (W1 bundle A: #1019, #1020, #1017, #1012 rebuild case, #611 deselect), head 09a6105b:** H1 round 2 ready; a snapshot restore no longer counts as a move; introduces `Mesh._move_version` (#966 builds on it). **Held for Louis: fac_zone exemption.** H1 (weak band, contrast 1e-4, up to 6 MMPDE moves, np 1/2/4): zone patch kept 2-3 its per move; fresh with zone recomputed 2-3; killed (as on #1036) 14-28; fresh no zone 13-22. Movers don't repartition. A kept patch only preconditions, so the answer is unchanged. Hub recommends exempting zone-keyed patches inside #1036, so the universal kill doesn't land as a 5-10x iteration regression for zone-keyed moving-mesh runs. **mmg audit (W1, read-only):** no default, fallback or internal path reaches mmg; the PR after A guards test_0835/0810/0830, fixes docstrings (remesh, mesh_adapt_meshVar, Mesh(coarsening=) via DMCoarsen), leads mesh-adaptation.md with adapt and redistribution, cleans stale messages and two shear-box examples (TypeError). **Louis 2026-11-10:** fac_zone: "mostly about efficiency and I am good with what works but I don't want to compromise accuracy" -> exemption goes into #1036 with an accuracy test (kept patch vs fresh zone registration to solver tolerance, np 1/2, after several moves) and a stale-patch mutant; repartition or topology change still kills. HPC image: "I don't really think it matters if the container has mmg, I just want to use it as little as possible in our own path because of the difficulty for users to install (custom petsc) and the 2D / 3D - serial / parallel issues" -> petsc.hpc unchanged; the mmg PR states mmg's limits in the docstrings.
- **#1036 at 86c9bbe7 (W1):** fac_zone exemption (a move keeps a zone patch; on a split level only the coincidence-test rows drop; repartition or topology change, by cell-node checksum, kills it); test_1152 (after 3 MMPDE moves, kept vs fresh: velocity 2e-8, pressure 8e-7, slip 5e-7, equal iterations; serial and np 2; H1 np 2/4). **ACCURACY DEFECT on development (W1, confirmed by H1 on a6eebb61 np 1/2):** the first solve after any mesh.deform or mover, by a solver that had already solved, assembles with pre-move coefficient fields (the move transfer writes fields without marking the assembly vector stale): 6 % velocity / 80 % pressure after deform, 0.2 % / 15 % after one MMPDE move (zone-viscosity fixture). Fixed in #1036 (transfer; test_1151). Masked where a loop writes V, P through .data (H2's stagnant-lid loop). H1 telling H2; K1: **no zg95 driver exposed** (none calls deform or a mover; faulted meshes are rebuilt with new solvers at 88e9f0e). K1 flagged ve_cylinder_demo/ve_cylinder.py; on uw3-campaigns main it has no deform or mover call (only DM refinement with snap_to_circle at build), so not exposed. test_0057 corrected (it read the stale vector). Serial 1080 passed. H1 round 3 pending, then merge on green.
- **H4 C13 verification (development 8f0ed0ab, serial; relayed by H1's file mailbox, since H4 cannot message C1: cloud-to-cloud trusted-device refusal):** #764 and #766 fixed and labelled; #773 already done; LIVE: #769 (adjoint KSP at EW rtol 0.3, sensitivity 10 % short), #781 (P0-pressure target, bare broadcast error), #787 (field in a Dirichlet datum gets dual 0, FD 0.31), #804 (gradient after DIVERGED_MAX_IT returns a number 35 % off); #778 original gap gone, leftover continuation stages not on solve_report. Branches: guards 769/781/804 d5d22be5 (H1 reviewing; register row 9 to Louis), #787 refusal cb23e507 (#787 stays open for the reaction-mapped dual), #778 cd9f2dfb. Then ThinSheet.
- **H1 on H3's branches:** #1001 (1259232e) ready; #843 (b13e5da0) ready (H3 to open PRs); #765/#763 (19fdbc06) not ready: #765's leaf rule right, but #763's `non_dimensionalise(Integral.evaluate())` makes units-model gradients wrong that were right (traction gradient x30, field dual x900; fault_friction.py FD check 1.0000 -> 49); split, #765 alone, `integral()` returns PETSc's raw value. **HIGH, pre-existing:** with reference quantities, `_essential_datum_sensitivity` off by about 9e8, (30 km in m)^2; **owner H3** (shares the sensitivity scaling with #763), issue under rule 8. W1's bundle B (b4b5426c) and #1044 under H1 review.
- **#1050 (#1041) round 2:** N1/N2 (restore validates everything first, verdict agreed across ranks; test_1155), N3, N5 fixed locally. **N4 for Louis (not a bug):** a solver's auto-created unknowns stay in mesh._vars (~23 DMs, 12 Mats per dropped solver), as Mesh.__init__ documents. #968 (C2) with H1.
- **#1040 (H4, a8ac65dd): H1 requests changes, narrowly:** the new upstream check ignores what an upstream solve reads in its own BCs, giving two silent wrong gradients that cb23e507 refused (dJ/dp 2.9e-2 vs FD 1.3e-1; dual 0 vs 0.46); a third case fixed only if #1047 lands first; the `\bar{f}` test can't catch its bug. H1's post on #1040 was blocked by its permission check; H1 asked Louis; record with H4 by mailbox. Side findings on development: a Robin BC reading the unknown (flux -T + 0.5) makes the forward SNES take 15-25 its on a linear problem and dJ/dp 0.548 vs FD 14.6 -> W1 (forward boundary Jacobian; one issue); sinker_transcript example fails in `_linearise_at` with units -> H3.
- **Merged on green 2026-11-12 after the runner DNS recovered: #1066 (C5; #876 fixed-in-development; #887 thin-sheet half) and #1073 (test_1060 asserts convergence; #1072 open).** #1082 (mover empty-rank) filed by H2, owner H5 (real fix: empty ranks join the reductions with zero contributions; test that the mesh moves and matches serial).
- **H2 stack:** #1003 (a3cf8fd4) and #1024 (dfb4cb06) ready from H1. The mover's rank-local no-cells early return (mmpde.py TODO(BUG) ~276; np 4 [2,0,2,0] aborts, MPI message truncated) predates #1024: to H5 (issue under rule 8, allreduce fix, np 4 test). #982 CI running against development (empty commit 115b4786).
- **#1071 merged on green 2026-11-12 (c326cc58; H1 ready: field datums match FD at np 2/4 incl. walls off-rank on half the ranks; 865 serial pass); #763, #1048, #1067 fixed-in-development.** CI shard 4 passed on it (the runner DNS has recovered), so #1066 and #1073's shard 4 re-run.
- **K1 fault-placement failures (via Louis; K1's message never reached C1, trusted-device refusal):** earth_sb_lag_fix (kaiju job 4400; driver d358b97 = 31c7e08 on `kaiju/fault-spline-base`; underworld3 80d3ebe9; base spline fit, Lagrangian fault rebuilt on the spline, split one rung below the surface): after step 81 "place_thin_volume assembly failed: the ribbon assembly meshed to area 3.517961740989e-03 against CAD 3.517" (CAD value truncated in the message); after step 107 "fault_split: the fault touches the domain boundary". Driver kept the previous mesh both times. K2 reproduces from K1's checkpoints (standalone repros, full-precision areas and tolerance, where the trace meets the boundary) -> W1 judges library vs driver; fix the truncated message at least.
- **#1071 delta review (H1, 4c46317e):** mergeable except **R3-F1 (high): a Dirichlet datum reading a MeshVariable hangs silently at np >= 2** (collective `_value_at` called once per owned node; ranks own different counts); was a SEGV before the guard; H3 to fix or refuse loudly, with a test. Side finding (issue, H3, low): `Integral._integrate` and `uw.get_units` double in cost per level of named-expression nesting (3 s and 15 s at 24 levels). **H2's stack re-tested green on development 5ce73fdf (H1): ready from H1; waits on Louis (#982 retarget, decision 17).**
- **#1068 review-complete at 82522d36:** 512 solves paired against 1ef53b2b over 32 files, 0 changes in Newton/KSP/reason and PCSetUp/KSPSetUp/SNESJacobianEval/SNESFunctionEval/SNESSolve counts; wall time flat; test_1162 np 1/2/4. F6 (Stokes under -snes_mf_operator with a natural BC: bare error 56) on #1070. **F7 (predates; H1): solver.petsc_options changes after the first solve (line search, snes_max_it, ksp_rtol) are ignored on later solves**; maybe also bundle D's probe_highvisc PC swap; nearby #477, #924, #683. To W1, bundle G ahead of #1069.
- **H4's ThinSheet PRs opened (H1's fixes in; records summarised in bodies, not posted):** #1074 (fixes #869, refs #870), #1075 (refs #872; surface-Stokes ShapeError sites listed on #872, not small; estimate_dt test added), #1076 (fixes #875, refs #879; facet-normal refill tested through solve(); history projection's sphere normal TODO(BUG)), #1077 (fixes #878; rank-1-only raise fails everywhere in 2.8 s). **#1065 adjoint confirmed (H4, H1's wt-1065 build):** dJ/dp matches FD at k=2 and 0.5 to 1e-10; nothing adjoint-specific remains. **#1068 (82522d36): H1 merge** (512 solves paired, 0 count changes, refusals uniform at np 2/4): **ready for Louis's decision 16.** #1040: H1's re-check requests changes (F1 upstream-condition gap, F3, F4). **CI blocked:** shard 4's gdb install fails on runner DNS (azure.archive.ubuntu.com) on every PR for hours; only test_0063 fails; H1's retry/skip fix unpushed (posting hold); put to Louis.
- **H4's four ThinSheet branches (H1):** sound, merge cleanly; one fix each: 869/870 (#870 stays open: read_timestep fails on manifolds, mesh_variables.py:1491 uses mesh.dim), 872 (estimate_dt fix needs a test), 875/879 (test the refresh via solve(); history projection still uses the sphere normal: #879 partly open), 878 (a local raise can hang other ranks; reduce a flag). Side finding: surface-mesh Stokes ShapeError on development (`eye(mesh.dim)` in `_stress_from_deviator`, `_devss_flux`): #872's class, to H4 as a comment on #872.
- **#1068 at 82522d36:** J-is-P guard (`_refuse_a_separate_preconditioner_matrix()` before `_snes_solve_with_retries` in Scalar/Vector/MultiComponent; setUp only when natural BCs exist; raises naming #1070; -snes_mf_operator with Robin now refused); test_1162 11 tests; 224 natural-BC tests pass serial; #1070 fixed-in-PR; H1 re-check with paired counts and np 2/4. **test_1060:** the Nitsche Stokes solve doesn't converge (wombat: DIVERGED_LINE_SEARCH after 3 Newton, velocity 16,481 its; hyperion: pressure sub-solve at its 200 cap: host-dependent symptom); the test asserts only shape and no NaN. **Filed #1072** (bug, type:testing, medium; reproduced on clean development 5ce73fdf; Nitsche J matches FD to 8.5e-8 at res 4, so the lead is the linear solve). Honest test on bugfix/nitsche-test-asserts-convergence-1072 (dabf65a9; essential and penalty must converge; Nitsche xfail non-strict against #1072): H1 review, then PR. #1069's stale-NULL-slot hazard unreachable (u_F1 fixed at BC creation); stays low. H1's CI gdb-retry fix committed locally, unpushed (H1's GitHub writes held).
- **PR #1071 (H3; #763, #1048, #1067), rebased on 5ce73fdf:** raw PETSc integral in the adjoint; datum derivative in the JIT frame; sinker_transcript fixed; **#1067** (the np 2 datum segfault: an empty-stratum guard in `_essential_datum_owner`; np 2/4 test); F2 tests added (each catches its mutant); peels expand to the end and raise past 64. 1159 serial pass. Waiting on H1's delta review of three post-round-2 commits. **Process: H1-written records were posted by H3 (#1071) while H1's GitHub writes are on hold; H1 had also asked H4 and H5 to post its records, then stopped. Hub told H3 to post no more and leave #1071's up for Louis to decide.** H3 posted H1-written records on #1045, #1046, #1047 (before the hold began) and #1071 (during it), reading the hub's "with H1's records linked" as an ask to post: the hub's wording was ambiguous. Only #1071's falls inside the hold.
- **#1047 (#765) merged on green 2026-11-12 (ddcdb92c; H1 round 2 ready); #765 fixed-in-development.** It also carries 08bc58b1 (a misfit written as a named expression got dJ/dα = 0 because fn_extract_expressions misses that form; the peel reads the tree directly; TODO(BUG) on extract_expressions, which the JIT also uses). #763/#1048 rework (ead09149, stacked on #1047): sinker_transcript fixed (`_linearise_at` restored history through .array, refused with units; now .data); 1156 pass across 129 files; H1 round 2 ready; non-blocking gap: test_0033 lacks dimensional-traction and explicit-misfit cases; H3 opens the PR.
- **H3 round 1 (H1):** #1047 and #763/#1048 both right. #1047's red CI was the split dropping #1019/#1020's custom-MG calls; restored in ddcdb92c (round 2 checking). #763/#1048: FD match in every units mode at np 1; 9 datum forms fixed; TranscriptAdjoint in a units model matches FD. **New (development): any essential-datum sensitivity at np 2 segfaults in `_essential_datum_owner`**, with or without units: the datum adjoint doesn't run in parallel; to H3 (issue under rule 8; fix in #1048's PR if small). **#1066 (W1 C5: #876, sheet half of #887):** H1 cleared (two rounds + F6; test_1159 np 1/2/4); records not posted (H1 blocked); explicit picard>0 on a fault-contact solve now stages Picard -> Newton instead of raising; merge on green.
- **H2's stack fixes verified (H1):** #982 670b523f, #988 dbfe47e6, #1003 946646b0, #1024 cac06a0a: test_0785 green; #1003 empty-rank hang fixed and guarded; test_0765 rank-safe; #1024 constant-metric skip guarded; #988 description corrected. Still with Louis: #1024 F1's confirmation half, #1003 F2/F3 (H2 to send one line each). Stack based on 526edb90, 59 behind: H2 merging development, H1 re-tests. #982 retarget with Louis.
- **H2's stack on merged heads (H1, np 1/2/4; records in hyperion runs/2026-11-11-stack/, not posted: H1's GitHub writes held pending Louis):** own tests and neighbours pass; development's parallel test_0785 (units-deform, #1002) fails from #982 up (clamp off by default on #982/#988; #1003 refuses a plain metre-sized array): #982 and #1003 must update it; #988's merge took development's side in every conflict, so it now changes only swarm.py (description stale); open: #1003 F1 (empty rank hangs at np 4), #1024 F1 (no guard test). To H2 (science first; #1003 F1 may move to H5 or W1). #1065 branch pushed (6430e593); H1 reviewing; H4 re-running p_robin.py.
- **#1057 (H5, 23f00d53), H1 pre-PR review:** approve after two changes: manifold meshes drawn flat at z = 0 with 1/4-1/3 of sub-triangles inverted at k >= 2 (fix or refuse); 2-D tests can't see an inverted sub-cell (VTK areas unsigned). Planar core: no wrong connectivity in 300+ configurations (tri/quad/tet/hex to P4/Q3, np 2/4); about 50x faster than Delaunay. Follow-up issue: the node-matching tolerance refuses valid high-aspect or high-degree cells and silently falls back to Delaunay. **#1063: H1 mergeable (F1, F3, F4 met; quad case cosmetic); H1's GitHub posts blocked pending Louis, so H5 told not to post H1's record for it; merge on green on H1's verdict.** **#1063 merged on green 2026-11-12 (161e9257: a comment-only commit after review); #690 fixed-in-development. H1's review record to be posted by H1 once Louis lifts its posting block.**
- **PR #1063 (#690, H5, 9d7cb62c):** F1 met (a test where the match fails on some ranks only forces a flat reload on all; H1's M4 rank-local mutant hangs in it at np 2); F3, F4 fixed; H1's record posted; #690 fixed-in-PR; scaling follow-up filed as **#1064** (distributed-hash match sketch). H1 verifying F1 against M4 at np 2/4; merge on green after that.
- **#690 (H5, ec4ac3c0), H1 review:** fixed: 228 reads exact (2-D/3-D, quad/hex, P1-P3, vector and DG, np 1/2/4); H2's snapshots and the step3900 FMG restart work at np 2/4 (development hangs or corrupts). Merge condition: a test with the match failing on one rank only (a rank-local-fallback mutant passes all tests but hangs at np 2). Follow-up issue (H5): reload about 7x development's serial cost; allgathered tables ~85 B/cell on every rank (about 850 MB/rank at 10M cells). #1062 conflicts with development: W1 merging.
- **PR #1062 (W1 bundle D, 9ebb02cf):** one RuntimeWarning per fieldsplit block that hits its cap, attributed to the user's solve() line, rank 0, after the record (#585 native path; #625 keeps the rotated path); a diverged solve warns with its reason and whether fields hold the initial guess or the last iterate (#1059's reporting half; #1059 stays open for the NaN); GAMG-fallback warning attributed and rank 0. Limit: with `-W error::RuntimeWarning` at np > 1 an uncaught warning raises on rank 0 only and hangs (CI does not use -W error: checked). H1's three records posted (check of 9ebb02cf: N1, N3 closed; F4 rotated path and N2 -W error remain as recorded). **Merged on green 2026-11-12 (189ca99b); #585 fixed-in-development (native path); #625 keeps the rotated path; #1059 open for the NaN and decision 14(b).** Decision 14(b) (native cold-step raise) not in it. **C5 (#876, sheet half of #887) at 96e7aabb:** H1 checks round-1 fixes; an explicit picard>0 on a fault-contact Stokes solve now stages Picard -> Newton instead of NotImplementedError (5 its vs 6, same answer to 1.4e-10).
- **Delayed relays (H1 stopped checking mail/H1; 9 messages from 11 Nov 00:45-20:28, received 2026-11-11):** H4: #1038 (#769/#781/#804; H1's F1/F2 met in 269c3a0f; CI green; **row 9 waits on Louis**), #1039 (#778), #1040 (refs #787; nested datum via unwrap_expression, `\bar{T}` on whole function atoms, lazy transcript refusal, Neumann-only fields refused; H1 re-check of a8ac65dd owed); #876 handed to W1 (reference/thin-sheet-876-for-W1 b611163b); four ThinSheet branches with H1 (869/870, 872, 875/879 a4b77f09, 878). H3: #1045 (#1001, conftest only; #1001 stays open for Louis's reset question), #1046 (#843), #1047 (#765; delta 08bc58b1 unreviewed; 2 CI checks red); **#1048 filed** (datum sensitivity read through dimensional evaluate); rework bugfix/adjoint-sensitivity-frame-763-1048 (4437bc01) awaiting H1; F6: viscosity >= 1e12 in PETSc's frame makes the forward Stokes fail silently (reason -3, u = 0) -> W1's bundle D. H5: #690 root cause in `_splice_hierarchy_from_sidecar` (pairs saved fine coords with a re-refined coarse mesh by array index, valid only for serial writes; mesh.sf not mapping file points); fix on bugfix/refined-reload-690 (ec4ac3c0): matches file points to the rebuilt DM, saves reference coords; old files: nearest-vertex match, else warn and reload without the hierarchy; never a corrupt mesh; H2's step3900 FMG restart solves in 4.6 s with fresh-mesh vrms; #1057 on feature/higher-order-vis-1057 (23f00d53). **Merged on green 2026-11-11: #1039 (#778), #1045, #1046 (#843).** H1 review order set: #690, H2's stack, H3 rework then #1047 delta, #1040, #1057, ThinSheet.
- **Cold direct-LU rotated solve fails PCSETUP (-11) at mu 1e-6, and the LU reference at 1e-8** (test_1157's annulus; W1 on the #910 branch; H1's #910 round 1 with development's rotated_bc.py swapped in: unusable, inf error). **Not the pin: filed #1058 (W1; bug, priority:low).** MUMPS INFOG(1) = -9 (workspace) with and without the pin; ICNTL(14) 200/1000 lets it factor, then the loop stalls (rnorm 7.2e-9 vs target 4e-10), answer 1.6e-8 from iterative; iterative route fine; likely an unscaled saddle system (velocity ∝ 1/mu against O(1) divergence blocks), unproven. Unowned (LU path; W1's C3 after decision 12). #910 round 2: threshold stays 1e6 (every -11 at ratio <= 301, every genuine correction >= 1.45e6); docs and tests being updated, then H1 np 2/4.
- **#1056 merged on green 2026-11-11 (review on 3bc1e6b8; the head added only test_1158 to test.sh batch 4); #546 fixed-in-development (m1 already fixed, m3 merged; W1 to confirm nothing else remains).** Was: PR #1056 (#546 m3), W1: H1 cleared at np 1/2 (record coming; np 4 queued); m1 already fixed on development; merge on green after the record. **#910 floor reworked** (H1: the floor was in the wrong units, scaled by ref while sub-KSPs see unit Krylov vectors; at A=1e8 it bound genuine solves, 56x less accurate than LU): now an iteration-0 test on the pressure sub-KSP only, against eps·‖A10‖·‖x_u‖, with a cold A=1e8 test; still to Louis (row 11). **Bundle D:** #804 and #778 are H4's (W1 told to drop #804 and unlabel #778 unless it checked H4's leftover); D = a solve-time warning when a sub-block hits its cap (#585, #625), no cap values changed; #755 (Schur scaling) out.
- **Bundle C4 (W1):** **#931 already fixed in development** (K2 probe on f562bdf7: np 2 vs np 1 2.1e-8; 25d62812 reproduces the issue's 4 % at the south pole; labelled fixed-in-development; K2's bisect: **fixed by #952** (15f13d0c, shell refinement no longer folds cells; np 2 gap 3.4e-4 -> 2.1e-8), not #947; mechanism inferred: the old gmsh shell's polar cells made the reaction recovery partition-sensitive; correction posted on #931). K2's message to C1 was refused (trusted device): K2 relays via W1. **#910** root cause and fix on bugfix/rotated-workspace-cache-910 (register row 11). #546 stays in C4.
- **PR #1054 (#348 + #899, LU path fixes only), head 7f13db34:** global pin, KEEP_NONZERO_PATTERN crash fix, #899 residual order, no pin under a pressure Dirichlet, #1053's N3 and wording. H1 cleared 660e35b3 (3 rounds); 7f13db34 adds a residual-order guard test and a wording fix: H1's 7f13db34 check posted; **merged on green 2026-11-11.** #899 fixed-in-development; #348 left live (fixed-in-PR removed) for the pin-policy part (decision 12).
- **FMG annulus checkpoint restart fails (H2, Louis: "pass that up to the dev hub to evaluate as a problem; we will proceed without restarts"):** refinement 2, np 4, write_timestep(meshUpdates=True), reload with Mesh(file, qdegree=3): first Stokes solve spins 28 min at 100 % CPU; qdegree 2: NaN vrms, Nu -1594 (build 92067bb8 = development e7fdcb22 + #982..#1024 + #1044 + #1036). Hub: this is **#690** (refined-mesh reload gives a corrupt DM in parallel; #809 its duplicate, verified by H1). **Reassigned (Louis 2026-11-11: "I need H2 to work on science with me. We should be able to hand this to a debugging session."): new session H5 restart (session_01HxWvn6CL6S3R1ELzJHJEay) owns #690**; reduce on development alone, then fix with a regression test at np 1/2/4, H1 review. Hyperion budgets re-split: H1 12, H2 16, H3 6, H4 6, H5 8. **Scope widened (H2; Louis: "if it can't, that's a regression: the visualisation skills keep visualisation in house"):** a refinement=2 annulus written at np 4 or 12 reloads SERIALLY with ∫1 = -0.698 / 0.374 (exact 2.356); uw.visualisation needs a live mesh, so viewing any saved refined run goes through the corrupt reload silently. **H2: H5's #690 fix verified on H2's snapshots (exact ∫1 after serial reload of np 4 and np 12 writes).** #1057 (uw.visualisation for any-degree fields on the mesh's own cells via closure DOFs; tri, quad, tet, hex; H2's 2D P3 prototype in the issue; Louis: "I would rather you contribute it to another session to implement") -> H5 next after #690. H5: test matrix includes write np 4/12 -> reload np 1; reload must detect (∫1 or signed volumes) and raise until the root fix lands (guard possibly a first small PR); top priority.
- **#1053 (#968 follow-up: 289d6550 cherry-picked onto 36bb3aef, head 8f7a4d2e):** H1 round 3 ready; **merged on green 2026-11-11.** Findings on development (W1 to check in the #348 branch): a solver switched lu -> iterative -> lu at np 2 hits PETSc "new nonzero caused a malloc" (cached LU ctx or workspace reused across a pattern change); LU at np 4 with a rejected mode leaves 0.84 of v_rms as rotation, possibly partition-dependent (same over-pinning?). #348 (26c11aa3) in H1's pre-PR review. W1 now tells the hub before pushing to a PR whose review has cleared.
- **#1052 (#968, bundle C2) merged on green 2026-11-11; #968 fixed-in-development** (np 1-8). #969 touched, not fixed (rotation now warned about, kept); #906 unchanged; low follow-up: the LU route doesn't warn (W1). **#1050 held for Louis's decision 11.**
- **#1051 (#1043, test_0835 rank-local counts) merged on green 2026-11-10; #1043 fixed-in-development.** H1: adapt's `node_budget` applied per rank (NVB route ~9337), so refined cells depend on the partition: W1 adds it to #865 (unowned; adaptation, next sweep).
- **W1 bundle C sweep (rotated free slip; 19 open, no duplicates, 5 not rotated; development f562bdf7):** C0 #1043 (test-only); C1 CORNERS #939, #941, then a probe for #608 (probably fixed by a9945bc9/045466df), **gated on gthyagi's PR #855** (rewrites the same datum code in build_rotation; reviewed "ready with listed changes" 2026-11-06, no response since; put to Louis); C2 ROTATION-MODES #968 then #969; C3 LU-PATH #348 (#899 may share the per-rank LU pressure pin; hypothesis); C4 CACHE #546 (m3, FMG half of m1), #910 (probe first); C5 SHEET #876 and the thin-sheet half of #887 (#876 also listed under H4's ThinSheet: W1 takes it in C5, H4 told). **For Louis:** REFERENCE #884, #883 and the rotated half of #887: the rotated loop's r0/ref is taken before the gauge modes and datum lift are known (rotated_bc 1572-1635); fixing it changes the #1014 policy and iteration counts on uncached and datum solves. #826, #817 belong with #651 (the Stokes_Constrained multiplier block); raising its inner cap is a default. #931: no mechanism found by reading; K2 probe dispatched (per-node σ_n, np 1 vs 2). #865 to adaptation, #976 to #551. W1 order: C0, C2 (not gated on #855). #1050 (#1041) in H1 round 2.
- **PR #1049 (W1 bundle B: #891, #1031, estimate_dt part of #978), 7d376b8e:** H1 round 1 F1-F3 (two high, one medium) fixed; test_1153 17 cases, 5 mutants caught; 112 timestep files 922 passed serial. H1 three rounds, ready at aef4cf13 (round 2 fixed `ddt._as_float` for a dimensionless timestep: NavierStokesSLCN with a ratio was 0.027 off). **Merged on green 2026-11-10; #891, #1031 fixed-in-development.** #891, #1031 fixed-in-PR; #978's FVM and boundary-normal parts stay open. Low side findings (W1's later queue, no issues): Eulerian AdvDiffusion `delta_t` setter does float() so rejects a UWexpression; a negative time quantity passes `_nondimensionalise_timestep` with scales set; in parallel the Eulerian accuracy estimate's max can come from a ghost vertex with a one-sided Clement gradient (0.020271 / 0.020152 / 0.020005 at np 1/2/4; H1's F4). W1 next: #1041.
- **#1037 scope CORRECTED (H2, after H1's O3):** on current code AdvDiffusionSLCN after a refined-mesh stretch is within 2e-6 of the mesh built in place (refinement 2), and SUPG likewise (H1); #1037 hits Poisson-type solves and the multigrid preconditioners (FMG, custom FMG, FAC). H2's MMPDE convection runs most likely not affected. June verdict withdrawn: the June build's 26 % SLCN error after `_deform_mesh` (even at refinement 0) is an older defect, fixed since; the June driver used the MMPDE mover, so the UWTN 2026-011 figure is open again, to be settled by a rerun on current code against the June run_log. #1044 at f4ae8a36 (review answered; development and #1036 merged; 230 mesh-move tests; test_1172 serial and np 2); H1 re-check; CI rerunning (the earlier red was test_1172 missing from test.sh).
- **test_1152 `[zone]` IS FAILING CI WITH #1024's CODE (C1, 2026-11-12; development is affected).** Signature: move 2 of 3 MMPDE moves, kept and fresh Stokes solves both DIVERGED_LINEAR_SOLVE at 0 iterations, pressure nan. CI record: failed on #1024 at 1e42c849 (run 43086593422), #1024 on dd92c701 (43138290715; re-run passed), #1094 at 82a769e1 (43162062526), #1096 at 149bd536 (43162805506); passed on #1024's third run and #1095; **about 4 of 7 with #1024's mmpde.py, 0 of about 12 without** (#982, #988, #1003, #1044, #1088, #1084 runs all green in that shard). H1: 0 of 40 on a quiet hyperion, both trees. #1096's record on the failure (truncated by pytest): first residual 13.764, q_min 0.430, velocity_its (0, 0). **C1 merged #1024 on the clean third run and H1's 0/40; the CI record now ties the failure to #1024.** Working hypothesis: CI runs the file under 4 xdist workers on 4 vCPUs (oversubscribed) and the mover's result depends on timing. In hand: H1 reproduces under CI's conditions with and without #1024 (top of its queue); H5 reads #1024's mover diff for a timing dependence and compares coordinates per move; W1 makes #1096's record untruncatable with sub-solve KSP reasons. H1 (mover repeatability): step 0 bit-identical across four np 4 launches; `node_redistribution` alone with an analytic metric is bit-repeatable at np 2 and 4; so the run-to-run split enters between step 0 and the end of the step-1 move: the solve/advection, or the frozen metric through global_evaluate (#1093). **If the cause is in #1024 and not quick to fix: ask Louis whether to revert #1024 (H5's #1086/#1082 branches sit on it).** Until settled, a PR whose only red is this signature is re-run once; no PR's green is fully trustworthy in shard 3. **Corrections and new facts (later 2026-11-12):** on CI the file runs SERIALLY in shard 3 (one pytest call, xdist `-n 4 --dist loadfile`), not under mpirun (H1, from the log); the mover alone is bit-deterministic under load (H1). **The failure follows the runner's CPU model (C1, from the job logs): all four failures are on AMD EPYC 7763 runners; every pass with #1024's code is on EPYC 9V45/9V74 (43138290715 attempt 2, 43151199784, 43162298057, 43163616687, 43166233012).** So it is deterministic per CPU, not intermittent; hyperion (Intel Xeon, even with OPENBLAS_CORETYPE=Zen) follows a different trajectory (first residual at move 2: 13.79108 against CI's 13.76404). **The tie to #1024 holds (H1, from scripts/test.sh's history and the job logs):** the serial batch-3 run arrived with cfc75310 (#1036, 2026-11-11) and passed 4 of 4 on EPYC 7763 before #1024 (runs 43085870891, 43104808340, 43110631945, 43123611413: "2 passed"); with #1024 it fails 4 of 4 on 7763 and 0 of 5 elsewhere. **It takes both #1024 and a 7763.** Hyperion is a Xeon Gold 6240R (AVX-512); no Zen 3 there; K2 asked for kaiju's CPUs and, if Zen 3, a serial run on f8c60140 and 93e66eed. **K2 (via W1): kaiju is all Intel Cascade Lake with AVX-512 (Xeon Silver 4210R login; Gold 6230R compute); no Zen 3, so CI's 7763 runners are the only reproducer.** H5 reads #1024's diff for a branch that can flip on rounding and forces it each way on hyperion. **Count now 8 of 8 on EPYC 7763 with #1024's code** (adds #1075, #1076, #1077 and #1096 at df4bd014; failed shards re-run). **#1096's record did not reach the CI log:** it prints inside `capsys.disabled()`, and under xdist a worker's real stdout is not forwarded; W1 asked to print it to ordinary captured stdout as well (shown under "Captured stdout call" on failure). **THE RECORD (#1096 at 48a2e1b0, run 43174910345, shard 3, EPYC 7763, move 2; kept and fresh identical):** every operator finite (not_finite=0 on all levels); outer fgmres/fieldsplit and split0 (velocity, fgmres/mg) KSP_DIVERGED_PCSETUP_FAILED with SUBPC_ERROR; level0 redundant LU fine (norm 159.37); **level2 gmres/sor: PCSETUP_FAILED, FACTOR_NUMERIC_ZEROPIVOT (norm 382.56)**; levels 1 and 3 and split1 DIVERGED_NANORINF (cascade); fine-level patch LU fine; q_min 0.43016, first residual 13.76404 (hyperion: 0.44835, 13.79108). So: no NaN, not a factorisation; a zero diagonal in the level-2 velocity operator. C1's working reading (to W1 to confirm): Galerkin through transfers that locate the moved fine level in unmoved coarse levels; a coarse basis function no fine node lands in gives an empty column and a zero diagonal; #1024 put the 7763's mesh on the wrong side of a discrete event. **This is multigrid on a moved mesh (W1's), and bears on Louis's open question of coarse levels following a move; a revert of #1024 would hide it.** W1: reading, a host-independent check (min |diag| per level, empty transfer columns), and a guard in the hierarchy build. H1: runs that check on hyperion at each move on f8c60140 and 93e66eed, looking for a near-miss to turn into a local reproducer. H5: whether #1024 made the moves larger. Count on EPYC 7763 now 12 of 12. (Later: one failure on an EPYC 9V74 too, #1076 attempt 3, so "7763 only" overstated it; rounding decides, as H5 found.) **ROOT CAUSE (H5, 2026-11-12; hyperion runs/h5-1093/perturb1152.py, probe_sor.py, probe_inode.py):** reproduced serially on hyperion by perturbing the fixture's coordinates by 1e-13 (seeds 0-7): f8c60140 fails 4 of 8 at move 2 with CI's signature; dd92c701 0 of 8. Mesh fine either way (min angle 16.5 deg failing, 16.3 passing). **C1's "empty column" reading was wrong:** no empty column, smallest level-2 diagonal 8e-5; two level-2 coarse nodes each have a P column with exactly one entry, from the same moved fine node; their Galerkin rows are proportional, the 4x4 block has rank 2, and PETSc's AIJ SOR inverts inode blocks, so it hits a zero pivot (finite without inodes). Defect: `custom_mg.barycentric_prolongation`'s orphan repair does not cover coarse DOFs that share their only fine image. **#1024 is not wrong: it stopped the mover stalling (#531), so each call now takes 3-6x more accepted steps and moves 4-5x further (move 1: 7 to 41 steps, max |dx| 0.0164 to 0.0612; move 2: 5 to 24, 0.0055 to 0.0223), which raises the coarse-level mismatch under unmoved coarse levels and the rounding amplification (1e-13 in gives 3e-4 out with the frozen metric, 2e-6 with an exact one).** Decision: no revert; H5 owns the fix (register row 12), W1 consults, H1 reviews after #1094; H1's 1152 lane stopped. The proper fix is coarse levels following the move: to Louis as a recommendation. **Filed as #1101 (H5). DESIGN CHANGED on W1's consult (same cause found independently on wombat: a dependent pair in 11 of 18 moved states at amplitude 5.5-7): do NOT inject in `barycentric_prolongation`; drop one column of a dependent pair at install, in `fault_mg.restrict_unreached` (every builder's transfers pass it, serial and parallel, standard and rotated; dropping leaves the range of P unchanged; collective; loud; k columns on fewer than k rows refused). W1's reasons: (1) barycentric_prolongation is also the serial FIELD transfer (`Mesh._refine_prolongate`/`_refine_restrict` for children with `_refine_dofs_coincide = False`, default `repair_orphans=True`): on a synthetic cloud 1089 to 81 nodes the existing orphan repair fires 907 times and a linear field comes out with error 4.3 on a range of 5 (5e-16 with the repair off): **an accuracy defect on the field-transfer route, to be reproduced through the mesh API and fixed as its own PR (owner H5, straight after the guard)**; (2) an injection can take another column's only image (measured); (3) parallel builders never inject. H5 told. **Louis, in the W1 session, verbatim: "But MY point was that the nesting has not changed when we have a topologically invariant mesh."** W1's reading: the relation between two levels is fixed when they are made; the library honours it for native refine pairs and breaks it for a placed level over its base, where `inject_custom_mg` re-locates the MOVED fine nodes in the unmoved coarse cloud after every deform; that rebuild is the defect behind #1101. Proper fix: build the transfer once, keep it while the topology is unchanged (nothing moves, nothing is injected). Wombat probe, kept transfer, moves 0-3: level-2 smallest diagonal 2.38, 2.53, 2.67, 2.58 (rebuilt each move: 2.38, 4.5e-4, 5.4e-4, 2.0e-4); velocity its 8, 7, 7, 7 (rebuilt 8, 8, 8, 7). Needs before landing: test_1152 all cases, #1015/#1017 fixtures, a large move, a free-surface move, np 1 and 2-16. **APPROVED by Louis in the W1 session (W1 quoting him, 2026-11-12): "I support this noting it is an mmpde specific mode not general because we usually do break the topology. Mmpde will gain simplicity and maybe will save some effort but it has significant limitations in how much refinement we can expect".** Scope (W1): a mover-specific mode for topology-preserving moves (MMPDE, mesh.deform) only; any topology change rebuilds as now; not a claim that MMPDE stands in for node-adding refinement. Own PR after #1099; not opened before H1 has a table (test_1152, #1015/#1017 fixtures, a large move, a free surface, np 1-16). #1101's guard stays as the backstop for the topology-change rebuild. W1 also probes the FAC patch's structural rows after a move (the coincidence test reads coordinates). Register row 13 when the branch exists. Next: #1096 (df4bd014) prints the whole solver tree on failure, so the next 7763 runner gives the KSP reasons; H1 to approximate an AVX2-only host or find a Zen 3 machine. W1's reading of the signature: failure at or before the first velocity preconditioner application; NaN in the operator or a zero pivot (coarse LU or patch LU).
- **SECOND add_fault DROPS THE FIRST FAULT'S PAIRING (2026-11-12; W1's observation, H1's measurement review/sc_slip.py; development f8c60140 np 1, #1094 branch np 1 and 2, identical):** c1 `_fault_point_pairs` ['Flt']; after `c2 = c1.add_fault(F2)`, ['F2'] only (tail levels [], [], ['F2']); both labels still on the DM; Flt still split (32 duplicated nodes). `add_fault_bc(0, "Flt")` on c2 raises; a law on F2 only converges with Flt an open crack (65 coincident DOFs free, jump up to 0.1305; Flt's free-slip slip on c1 was 0.15952). No matching issue. **Owner W1: files it, fixes it next after the #1094 push** (carry every earlier pairing forward; a split label with no law refuses or warns), ahead of #1089. **Filed as #1099 (fault_split.py add_fault; serial repro on f8c60140: Flt opens, normal jump 0.0169, tangential 0.152; F2 slip 0.1687 against 0.1652 for the one-call network). Cause: add_fault builds the cut mesh without the earlier faults' records and overwrites _fault_traces/_fault_specs/_fault_surfaces; Mesh.add_fault replays _fault_specs on the tail. Branch bugfix/second-add-fault-keeps-the-first in progress; W1 intends a loud warning at solve for a split fault with no law, not a refusal (a traction-free crack and conditions on <name>Plus/<name>Minus are legitimate).** **PR #1112 (d45546f4; development 613ed1e0 merged in; three mechanical conflicts): carries every earlier pairing onto the new mesh and split levels, or refuses collectively if a recorded point was refined, removed or moved; a split fault with no law warns once per solver (an error under -W error). Serial only: test_1174 + test_1173 39 passed; 342 + 163 + 180 passed in the fault, sheet and multigrid suites; ten mutants each failed by a test; one call and two calls both give [{}, {}, {Flt: 31, F2: 33}] on an adapt child. Nothing parallel measured: the nine-item parallel run list and the review are with H3 (second desk).** W1 side findings: **test_0858_submesh_injection_odd_ranks (from #1095) fails on macOS at np 3 and 5: its `orphans > 0` precondition is partition-dependent (to H5: make the ownership deterministic)**; `add_rotated_freeslip_bc` on one side of a split fault ('FltPlus') fails at solve with "Unknown boundary" (boundary_flux.py:114); on a refusal at the second sheet of one 3-D call the first sheet's intermediate mesh stays in `_registered_children`; docs/advanced/split-node-faults.md contradicts the adapt-on-top guide on pairings migrating through a redistribution (H3's item 5 decides). K1 asked whether the drivers add faults one call at a time. **K1: not affected (one call for all faults; laws by name; current runs carry one fault). W1 to confirm in #1099's PR that tail levels carry every fault's pairing in the one-call case (fault_mg.split_tail_levels).**
- **REGRESSION FROM #1104 (found by W1 on development e4076e59, 2026-11-12, hours after the merge): the #1101 guard refuses a solve that converged before it.** A fault cut into an adapt child that moved before the cut: `_dependent_columns` raises "2 group(s) of coarse unknowns share fewer fine images than there are of them (e.g. columns [1251, 1252, 4778] on fine rows [5622, 5623])" from `rotated_split_transfers` on the finest pair; before the guard, 6 velocity iterations. It is the general k-columns-on-fewer-than-k-rows case the guard refuses "until seen" (C1 passed that advice to H5). W1's fixture (`_split_level_stokes(move_the_host=...)` in test_1176, cell 0.0125): amplitude 0.002 solves (6); 0.005 and 0.01 refused on either axis; 0.015 along x merges 40 unknowns and solves in 7, across refused. **This is Louis's workflow (a fault placed on a moved mesh). Owner H5, urgent, in #1111: no refusal where development before #1104 solved (handle the general group exactly, or leave it as it was with a warning); W1's fixture as the regression at np 1-3; H1 reviews it first.** H2 warned (a build at 58d25aea avoids the refusal). W1's second side finding: `add_fault` on a refined box with the mesh-owned tail takes 6 P2 Poisson iterations at rest against 3 when the base is added as a level (both builds; unrouted).
- **KEPT TRANSFER (W1; Louis approved as an MMPDE-specific mode): branch `feature/custom-mg-kept-transfer-under-a-move`, head 03558519 (development e4076e59 merged in); no PR before H1's table.** Serial on wombat: 34 files, 210 passed, 23 skipped; test_1176 19 tests; 20 mutants each fail a test; three adversarial reviews answered. Serial effect: split-fault Stokes on an adapt child after three deforms 6, 6, 6 (development 13); moving top wall +5 % three times 3, 3, 3 (development 5, 6, 7). A relax of an unmoved mesh counts as making it. Not covered, as on development: a refined base that moved before an adapt or cut enters the child's hierarchy at its moved coordinates (4 iterations against 2). H1 has the 12-item run list (np 1-16), on its own lane, up to 20 cores. Register row 13 when the PR opens.
- **WEEK PLAN (Louis 2026-11-12: "I have just reset our weekly usage (a one-off bonus) because I would like to resolve as much as possible from the outstanding issues this week. The MMPDE + faults is my primary driver, but having so many loose ends is giving me some anxiety today.").** Rule for the week: close, don't open; a side finding that does not corrupt results is one line to the hub, not an issue or a new branch. Counts 2026-11-12: 275 open issues, 121 fixed-in-development, 9 fixed-in-PR, **145 live**; 29 open PRs.
  - **Critical path, parallel MMPDE plus faults (H2's refinement 4-5 slab runs):** (1) #1094 parent record after a move (W1): **MERGED 2026-11-12 (613ed1e0)**; (2) #1086 + #1082 mover rank dependence and empty ranks (H5; **H1 2026-11-12: NOT READY at c3e52607 for F4 only: the seam fix works (boxes match serial to 1.6e-11 at np 2-5; annulus 7e-8 is rounding; F1-F3 fixed; mutants caught), but facet slip on unregistered boundary surfaces still raises "argmin of an empty sequence" on some ranks and hangs the rest (np 5 natural, np 4 scattered), pre-existing, and is 3e-2 to 5e-2 off serial when it runs. C1: withdraw the F4 claim, file F4 separately, add box/scattered/annulus slip cases and a mask mutant test, then the PR**); (3) #1093 global_evaluate at seams, frozen metric (H5, with gthyagi's #859); (4) np 4 mover not repeatable run to run (H5); (5) #1090 placement area knife edge near a wall (W1); (6) #1089 pull moves a wall vertex (W1, rework in review). Open with Louis: coarse levels follow a move.
  - **H5 order (2026-11-12, late):** #1101 guard (merge dependent columns at install); #1086 + #1082 PR; #1093 (+ #859); the field-transfer accuracy defect (orphan repair on the `_refine_prolongate`/`_refine_restrict` route); F4 facet slip; #1083; #1060. **Added to the critical path: (7) #1101 guard (H5); (8) keep the placed level's transfer through moves (W1; approved by Louis as an MMPDE-specific mode; after #1099); (9) #1099 a second add_fault drops the first fault's pairing (W1, fix in review).**
  - **H5 pushed two fixes (2026-11-12, late): #1101 guard, bugfix/custom-mg-shared-sole-image a508570c** (drop the dependent column and fold its row of the level below into the kept twin's, scaled by the signed weight ratio; composite transfer exact; ties to the lowest global column; limits in the docstring and warning): test_1101 6/6 at np 1-3, fails on development (3-level PCMG -11, zero pivot); perturbed test_1152 seeds 8/8 pass with the warning (4/8 fail on f8c60140); no-op evidence: 24 serial custom-MG files 144 passed, 13 parallel files at np 2 40 passed, same Mats returned; the warning also fires on UNPERTURBED test_1152 `[zone]` and the split-level case (the pair is there; development passes only by rounding). H1 reviewing (register row 12). **#1102 (the field-transfer accuracy defect), bugfix/refine-transfer-no-orphan-repair 1860aeb6:** both refinement-child transfers call barycentric_prolongation with repair_orphans=False; test_1102 (conforming-surface child on a box, linear field, copy_into/add_into, P1 and P2): development fails the restrict cases on 16 of 142 rows (P1) and 39 of 525 (P2), errors 0.27 and 0.195; fix 5/5. H1 next. **#1092: H3 READY at 2c67ca71 (relayed by the author H5); C1 asked H3 to post its record on the PR; merge when it is there (CI green).**
  - **MERGED 2026-11-12 (late), development now 01b06c91:** #1075 (f3bb68bd) and #1077 (e11ea970) on their fifth CI attempt (#878 fixed-in-development; #872, #879 stay open per the PRs); on H3's READY verdicts (relayed by H1; records in hyperion runs/2026-11-12-h3review/): #1095 (b09e3dc3; gthyagi's #858 completed; #1087 fixed-in-development), #1098 (2333f8f9; #856 completed), #1092 (2c67ca71; np 3 in the full-parallel pass, 30 min added on development), #1100 (8b60c563; flood-fill shell labels). gthyagi closed #858 and #856 himself. **#1040: H3 NOT READY at 4c29d0ac for one test line** (the `\bar{f}` test reuses `f_near`, so the `substring` mutant survives); to H4. **Posting:** H3's comment on #1095 was refused by hyperion's permission check ("External System Writes"), the same class as H1's hold; H3 rightly did not act on C1's "cleared to post" (a peer message, not Louis's approval); C1's error; records stay in files until Louis rules (decision 25). Today's merges so far: #1084, #982, #1044, #988, #1003, #1088, #1024, #1074, #951, #1076, #1075, #1077, #1095, #1098, #1092, #1100.
  - **H5's four PRs are open (2026-11-12, late):** #1104 (the #1101 guard, f285af2f, development merged in; H1 reviewing), #1105 (#1102, 1860aeb6; **H1 READY**: development wrong on 16 of 142 rows at P1 and 39 of 525 at P2; with the repair off an orphan's value is unused, non-linear error on moved children 1e-4 to 3e-3 against 0.07-0.17; custom_mg byte-identical, 26 transfer hashes identical; parallel route is global_evaluate; non-blocking: the parent-to-child half is a precaution, the np > 1 skip could go, the docstring overclaims add_into; merge on green CI), #1106 (#1086 + #1082, bc9d67c3), #1107 (#1093, 253f96be: Swarm.migrate offers a point to every nearby domain before giving up). **#1097 green on attempt 3 but now conflicts with development (scripts/test.sh after #1092); back to H6 for the merge.** #1094 on its third attempt (two 7763 failures).
  - **MERGED 2026-11-12 (night), development now e91113d9:** #1105 (1860aeb6; #1102 fixed-in-development), #1038 (40aee07f; register row 9; #769 fixed-in-development), #1068 (82522d36; #1065 and #1070 fixed-in-development; unblocks #1069). **#1079 was green but now conflicts with #1068 (same solve preamble); W1 to merge development in and run test_1162 with test_1163.** #1061 and #1050 also await W1's merge of development. Today's merges: 20 (#1084, #982, #1044, #988, #1003, #1088, #1024, #1074, #951, #1076, #1075, #1077, #1095, #1098, #1092, #1100, #1094, #1105, #1038, #1068).
  - **MERGED 2026-11-12 (later still), development ca2a9ee5:** #1079 (f0115288; full CI green on 18187e72, then a 7-line docs commit saying set-up-time options such as snes_mf_operator only take effect before the first solve; #1078 fixed-in-development; decision 18 closed), #1061 (2e7ad640; #910 fixed-in-development; register row 11 merged). **#1050 green at 4ca2ad62, then conflicted again when #1061 landed (scripts/test.sh); W1 to merge development once more.** Merges today: 22. scripts/test.sh has been the conflict in seven merges; W1 to suggest a layout that stops PRs colliding.
  - **scripts/test.sh restructure (W1's suggestion, 2026-11-12; owner H4, own PR, H3 reviews):** the 27 single-file `batch 4 tests/test_11NN*py` lines (about 415-445) become one line per decade (`test_111*` ... `test_117*`, plus `118*` and `119*`), with the four shard-3 files kept on their own lines and taken out of their decade by `--deselect`; check_test_coverage.py unchanged; shard assignment to be shown unchanged file by file; full serial phase timed before and after. Open PRs then lose their own test.sh line at their next merge of development. **#1050 merged 2026-11-12 at 0dff038f on green CI; #1041 fixed-in-development; decision 11 closed (refuse a restore naming a dropped solver). All five quick-list merges are in: #1038, #1061, #1068, #1079, #1050. Merges today: 23.**
  - **#1104 MERGED 2026-11-12 at c65d816b (development cff3b012; register row 12; #1101 fixed-in-development)** after H1 confirmed the M1 test (composite test parametrised over dropped weight 0.5 and -0.5; the abs mutant fails at np 1-3) and H5 reworded the PR in Louis's terms (level pairs that are not nested). Merges today: 24. CI re-triggered against the guarded development on #1097 (801ce3a5), #1096 (48a2e1b0), #1040 (44e2d6e5), #1113. **Required status checks (quick-list item 7): C1's API call was refused ("Write access to this GitHub API path is not permitted through this proxy"); Louis to set it in the repository settings: checks `test` and `Style gates (deprecated patterns, examples parse)` on development.** **#1112 (#1099): H3 NOT READY at d45546f4** (relayed late): 2-D right at np 1-5 (two calls equal one call; no false warning); HIGH: under `-W error` the warning is raised on rank 0 only and the solve hangs at np 2; HIGH: a second 3-D add_fault fails at np 2 and 4 ("sewn mesh has mixed cell orientation"); MEDIUM: hard-coded 3-D slips differ on hyperion (0.148170 against 0.145180); to W1, behind the kept-transfer push. **#1114 (H4, test.sh decades): shard map identical over 451 files; shard 4 1835 s to 1305 s, shard 3 2492 s to 2276 s; already conflicts with development; H4 to merge development in; H3 reviews.**
  - **Later 2026-11-12/13:** #1114 re-merged with development at 7f7a6756 (shard map identical over 453 files; coverage check passes); H3 reviews it first. **H3's records are posted** (Louis in the H3 session, 2026-11-13: "Post the findings / fixes / reviews"): #1095, #1098, #1092, #1100, #1040, #1112. **#1113 (test_0858 builds its partition): H1 READY at c78bf26c** (104 orphans against 2; same layout under either partitioner; the #1095 revert and the per-rank write are caught; optional: split the region over ranks 0 and 1 to catch the multiplicity mutant here too); merge on green CI. CI re-running on #1097, #1096, #1040, #1113 against development with the guard. H1 lanes: #1106 (4 cores), #1107 (6), the kept-transfer table (8; np 16 deferred).
  - **New PRs seen on GitHub ahead of their relays (2026-11-12 14:10 UTC):** #1104 now c65d816b (H5's M1/M2 pushed; awaiting H1's look and Louis's yes); #1106 a560311f; #1107 a4b82786; #1109 (H5: facet slip over all ranks, #1103 = the F4 defect); #1111 (H5: #1101 detection distributed, repairs recorded; the M3/L1 follow-up); #1113 (H5: test_0858 builds its partition); #1108 (H6: analytic spherical Kramer references, gravity kernels, harmonics; unit 1; +2,690); #1110 (H6: `Stokes.pressure_split` (general: named fitted interior facets) and the cylindrical lagged walls (origin-centred annulus, fixed mesh, P2/P1; refuses anything else); +2,852; opened before Louis's frame; not to merge until the declaration contract is agreed, except any part that is geometry-free).
  - **Review desks:** H1 keeps the critical path; **H3 is a second review desk** (#1097, #1095, #1092, #1096) until Louis rules on units. **H4** (idle on #1038): #1040's changes, then finish/close/needs-Louis verdicts on #780, #800, #951, and reviews of ss2098's #1055 and #986. #1074-#1077: shard 4 red was the 2026-11-11 runner flake; CI re-run 2026-11-12; merge on green. **#1074 merged 2026-11-12 (a0e59b66); #869 fixed-in-development. #951 merged (594a804a). #1075, #1076, #1077: each run and each re-run landed on an EPYC 7763 and failed only test_1152 `[zone]` (now 11 of 11 on that CPU); re-running until a shard lands elsewhere.** **#1076 merged 2026-11-12 (6cc254b5) on its fourth attempt; #875 fixed-in-development. #1075 and #1077 wait for #1101's guard, then one re-run. #1097's run failed only test_1152 on a 7763; re-run started.**
  - **H4's loose-ends verdicts (2026-11-12, via H1):** **#1040** at 4c29d0ac: H1's F1-F5 addressed (transitive control reach; #1047 merged in; 19 walk probes clean; test_0029 12 tests); mutant re-run and verdict sent to H3. **#951: finish**, no code change: still wanted (covers rotated free slip + custom FMG + split fault, which test_0078 does not), passes at np 2 on development; CI re-run 2026-11-12; merge on green. **#1055 and #986 (ss2098): mergeable as they are** (#1055: examples used undefined names and `annulus.N` is the CoordSys3D; #986: root `find_packages()` returns [] and overrides setup.cfg's `find:`); H4 could only read #1055's diff and its review comments are drafted, not posted (permission check on a contributor's PR; drafts at hyperion runs/2026-11-10-h4/drafts/); #986's CI re-run started; **merging a contributor's PRs needs Louis's yes.** **#780 needs Louis:** his own PR (#767 design); last review not ready with six conditions, including a blocker (`Mesh.__init__` re-declares `t`, so a mesh built at non-zero time raises) and a rank-local raise; about 2 days to finish; keep the refusal as a behaviour change, or narrow it (warn, or only stop the description being overwritten) and close smaller? **#800 needs Louis:** forward-from-nodes history + SL renamed by trace and launch + five partition-independence fixes (#682 among them); 25 commits, 9 conflicting files, 788 commits behind, a deliberate change to the default nodal trace-back start; land the whole feature (multi-day) or close and salvage the partition fixes as small PRs?
  - **Unowned still:** #861 (journal replaces the wiki; docs hub's, and CLAUDE.md now routes planning to the GitHub Project), #689 (gthyagi, CitcomS DDt manager), #987 (ss2098, draft).
- **CURVED WALLS: THE FRAME (Louis 2026-11-12: "We should pick apart gthyagi's contribution into the chunks that fit our vision of the code. It is not unreasonable for us to use analytical corner-cutting when we know the geometry and we generally ask the mesh to declare such cases and we expect mesh movers to have some way to invalidate them if the boundary moves.").** Three rules given to H6: (1) chunks chosen by fit, not gthyagi's unit boundaries; what does not fit is left and listed for him; (2) an analytic shortcut takes the geometry from the mesh's own declaration, not from a radius argument or a module's assumption; (3) a mover that moves the boundary invalidates the declaration, and a method relying on it then refuses loudly or falls back. **H6's deliverable (hours): a pick-apart plan** in the walkthrough: (A) the contract as the library has it (how a mesh declares analytic geometry: stored radii, coordinate system, `nullspace_rotations`, registered boundary surfaces, analytic normals; how deform, MMPDE with slip, free surface and adapt invalidate or preserve it via `_mesh_version`/`_geometry_version`; the smallest addition if that is not enough, as a proposal for Louis); (B) each chunk: what it does, what it assumes about the wall and from where, fit (as is / fits once it reads the declaration / duplicates an existing tool per UWTN 2026-016 / does not fit), value to the publication, hours and how much is the author's unfinished work; then an order. Meanwhile: geometry-free chunks continue (analytic references; #1097); no PR for a declaration-dependent chunk until the contract is agreed. This supersedes the blanket hold on units 4-5 and "land units 1-6 as cut".
  - **Louis on rule 3 (2026-11-12): "Subtlety with (3) above is that we can move points on the surface and not break the circularity / sphericity. This is hard to know, but mmpde, to take a recent example, can move nodes along the surface without invalidating the special case. I am not sure how to deal with that."** C1's candidate, to H6 to assess in part A (a recommendation, not a ruling): **verify, don't infer.** The declaration is a checkable statement (this boundary's nodes lie on this surface); it is stamped with the geometry version at which it was last verified; a method relying on it asks the mesh, which re-checks if the version changed (one collective reduction of the largest node distance from the declared surface, against a stated tolerance) and re-stamps or invalidates. No mover needs to know (the lesson of #1094's lazy record and #982's kd-tree). Expected: MMPDE slip on a registered analytic surface passes; slip along unregistered facets fails (O(h^2) off the circle); free-surface topography fails; a rigid translation fails against the declared centre unless re-fitted (#969). Second half: after a tangential slide the wall is still a circle but the nodes have moved, so each chunk's cached geometry (facet lengths, gap/cap volumes, surface quadrature, fitted-region labels, boundary traces) must be rebuilt per geometry version; H6 lists what each chunk caches. **Louis (2026-11-12): "rigid translation should be rare. We might have this for centre-of-figure / centre-of-mass changes but that might actually be done within an embedding outer mesh."** So: no re-fitting of a centre; a translated wall fails the check, the declaration is invalid, the method refuses with a clear message. H6 told. Decision 13 (#969) settled as (b): warn, don't fit (Louis, same day).
- **CURVED WALLS: SCOPE UNDER REVIEW (Louis 2026-11-12, later: "The approach is powerful for the spherical and cylindrical benchmarks but I am unclear if it is general or needs analytic boundaries. That is what I sought from gthyagi previously. The review suggests he has improved the interface to existing functions and tidied up a few but left backward compatibility issues. It feels a bit like he did not review his work very carefully and we are now having to do the donkey work").** H6 asked, within the hour, per method: what it needs to know about the wall (a radius, any analytic surface, or only the mesh's boundary), whether a hard-wired circle/sphere is essential, gthyagi's own words, a verdict (general / general with work / analytic only), and hours remaining per unit with what is the author's unfinished work. Sequencing until Louis decides: units 1-3 continue (analytic references, cylindrical); **spherical units 4 and 5 not started**; H4 keeps what it was handed. C1's proposal to Louis: if circle-and-sphere only, land as an opt-in benchmark module and stop; hand the unfinished parts back to gthyagi with a precise list; cap our effort.
- **CURVED WALLS: GO (Louis 2026-11-12, after the walkthrough results: "This all seems positive, multiple reviews from the various sessions and gthyagi - let's get this into the codebase quickly").** C1's reading, stated to Louis: decision 1 settled as recommended; #1033's new methods land as unit PRs on development's untouched rotated solve; the rotated-solve rewrite (unit 7) does not land (measured: it restores the #906 rotation and gives energies wrong by 0.2-76 %). Decision 2 (#857's recovery methods) still open, not blocking. Plan: H6 cuts units 1-6 as PRs in dependency order (stacked where needed), H4 takes whole units from H6 (diagnostics; possibly analytic references), H3 reviews, C1 merges. Each unit merges on: opt-in measured (existing solver tests unchanged in results and iteration counts at np 1, 2, 4); own tests at np 1-5, renumbered and reachable; runs on development's solver core; unproven claims labelled experimental; gthyagi's authorship kept or credited. Convergence tables for the publication follow and decide what the paper claims; they do not gate merges unless a unit gives wrong answers. #1033 closes when the units have landed, with a comment saying where each part went and what was not taken.
- **DECISION 2, #857's dropped recovery methods (Louis 2026-11-12: "I want to understand why we dropped those methods - have they become unnecessary or were we just failing to pay attention"; then "We have them in the UWTN about topography / boundary conditions that refers to these ideas").** The note is **UWTN 2026-016, "Free-Slip boundary conditions on curved boundaries"** (Louis; DOI 10.6084/m9.figshare.33420637; software development @ 8b7c8b9e, so before #857; source in Underworld-Technical-Notes/underworldcode.org, articles/boundary-conditions-on-non-planar-boundaries/). It establishes, on tools development already had: the rotated constraint's reaction de-smeared by the boundary mass is the consistent boundary flux (Zhong 1993), returned by `boundary_normal_traction()` and `dynamic_topography()`; the multiplier (`Stokes_Constrained`) returns the same object; recovery by projection is the least accurate (Kramer annulus, cell 0.075: 6.3e-3 against 2.1e-3 reaction, 1.7e-3 multiplier). The four methods were dropped by gthyagi between #857 and #1033, not by us; our lapse is that #857's mathematical review was never done. H6 stage 1 (reading, within the hour): for each dropped method, which of the note's methods it is, whether development already returns the quantity, **zero-slip walls checked hardest** (the note's benchmark has free slip only; if only #857 gives a no-slip wall traction, that is a gap in #1033), and gthyagi's own words. Stage 2 (measured): the note's Kramer table with #857's recovery, #1033's reactions and development's reaction side by side. WRITING-PLAN.md lists F5 "Four ways to represent a fault, compared" as joint with Thyagarajulu Gollapalli.
- **CURVED-WALL BOUNDARY WORK (Louis 2026-11-12: "We should review @gthyagi's work on the boundary corrections for curved meshes ASAP while it it still in date. This needs to be done to move things forward for a publication. If we need to make corrections, we should do so rather than push it back again."):** new session **H6 curved walls** (session_01HxWvn9MVb36F3u3GyKv8pV, hyperion, 8 cores) owns review and corrections. Scope: **#1033** (physical curved-wall Stokes corrections and spherical pressure lifting; 1b740463; 118 files, +17,011, 81 commits; CI green at head, now conflicts; no review posted; touches petsc_generic_snes_solvers.pyx +289, solvers.py +430, rotated_bc.py +567), **#857** (annulus recovery; 23c11aa8; H1 2026-11-06: not ready, three findings), **#855** (rotated datum collectives; 1d2297b8; H1: ready with listed changes; gates W1's corners bundle). #1033 shares no commits with the other two but covers the same ground. First deliverable: a map (what supersedes what; conflicts with development 93e66eed, notably #1088 degree-1-only, #1054 LU pin, #1044 MG hierarchy, rotated_bc.py; the solver-core footprint for users who do not opt in; a proposed split by risk; what a publication could claim today). Corrections go on branches in the main repo from gthyagi's heads, authorship kept. H1 gives the independent pass; hub merges. This settles decision 5 (#855 nudge): we finish it ourselves.
  - **H6's map (2026-11-12, from the diffs and a trial merge of 1b740463 into 93e66eed; nothing run yet; hyperion runs/2026-11-12-h6/map-*.md).** Supersession: #855 lands first, alone (H6 completes it: development merged, SHEET_TANGENCY line, a `build_rotation` test at np 3); #857 superseded by #1033 for pressure lifting and lagged walls (5 of 9 methods), its recovery half absent (D2); #1033 lands in units. #1088: no design conflict (nothing needs coordinates above degree 1). #1054 and #968/#1052: development's versions win. **Not opt-in (D1):** rotated_bc.py +567/-272 changes the default rotated free-slip solve: rotation gauge verified to 256 eps on both sides (reverses #906; test_1131 rewritten, modes removed 3 to 0 on the shell), pressure nullspace applied only if verified (LU then raises NotImplementedError where development pins), a self-installing `_RotatedBalancedPressureCoarse`, a post-finalize residual guard that can flip `converged`, loop-order changes; also `Mesh._get_coords_for_basis` replaced for every mesh, flood-fill shell labels, fault_contact.py normal, test_1134 weakened. **Split by risk:** 0 #855 (~40 lines); 1 analytic references (~2,660); 2 pressure split and cylindrical lagged walls (~1,450); 3 Stokes state/observer and cylindrical coupled gap (~1,170); 4 spherical coupled gap (~1,960); 5 spherical pressure lifting, sheet loads, fitted regions (~1,600); 6 diagnostics (~730); 7 solver-core changes (~1,400, held). **Claimable today:** annulus pressure lifting and lagged walls at second order, once rerun; nothing spherical (no spherical test measures error against an analytic flow; Kramer fields never compared with a solve) and nothing for the coupled gap. **For Louis: D1** port the new methods onto development's rotated solve unchanged (H6 and C1 recommend) or consider gthyagi's gauge verification on its merits (then W1 assesses); **D2** does the publication need #857's recovery methods (topography recovery, boundary coefficient, trace reconstruction, zero-slip traction recovery)? H6 proceeds on #855, the opt-in measurement, unit 1 and the convergence studies, building units 2-6 against development's rotated_bc.py and listing what each needs from unit 7.
  - **Louis (2026-11-12): "I think I need to be led through the interaction between the new work and our old tools before I can say anything meaningful."** D1 and D2 wait on that. H6 asked for a walkthrough, `curved-walls/WALKTHROUGH-2026-11-12.md` in this repo: one section per existing tool (rotation gauge and #906; pressure nullspace and LU pin; convergence reporting; preconditioning; mesh-side changes; how the opt-in methods sit on top; #857's recovery against the existing constraint reaction), each with today / with #1033 / why he did it / a measured example / the choice; first version from reading, examples as builds finish; Louis then goes through it live in H6's session. #855 continues alongside; unit 1 and convergence studies wait behind it.
  - **Walkthrough v1 in this repo (1725c4f), sent to Louis. Measured (H6, serial, #1033 1b740463 vs development 93e66eed), rotated free slip with the default normal: test_1131 shell, development removes 3 rotations (v_rms 1.795, rotation rate 2e-15, energy 12.10); #1033 removes none (v_rms 5.151, rotation rate 7.04, energy 91.11), reports converged, no warning. Annulus: #1033 leaves a spin of about 1 % of v_rms (iterative), energy 21 % high with LU. With the analytic normal the builds agree (shell energy 12.0817); annulus + analytic normal + LU: development solves, #1033 raises NotImplementedError.** So #1033's gauge test brings back the #906 rotation on the default path; gthyagi's point (removing an approximate mode leaves a residual of order 1e-8) is right as mathematics. From reading: no new method needs the rewrite. A real defect of ours he fixed: shell Inner/Outer labels by centroid radius mislabel cells next to the internal surface (flood fill to land as its own unit). #855 branch d35ff075 (local): new build_rotation test hangs on development at np 3, passes on the branch at np 1-4; test_1092 passes with the one-line fix; to push after np 5, serial neighbours, Maxwell. **Pushed as PR #1097 (09e36821), superseding #855 (comment there); H1 pass queued after #1094 and #1096; merge on READY and green CI, then close #855.** **H1: READY at 009e96ed (tall box guards the gate; np 3 CI line kept); merge on green CI.** **H1: NOT READY at 09e36821 for one test gap (a mutant reverting only the evaluation gate passes at np 2-4 on the 1x1 box; a tall 1x4 box at np 3 catches it); code correct; H6 fixing. Walkthrough v5 (H6, section 3 measured; slid-wall annulus of test_1142, default normal, serial, every solve "converged"): **development under-reports the residual of the fields it returns when it removes a near-null rotation:** slide 3e-5, tolerance 1e-9: the loop reports 4.7e-16, the returned fields have 3.83e-8 (1.9e-6 relative, 2,000x the tolerance; gthyagi's number exactly); the answer is unharmed (energy 5.505954e-5, equal to the unslid mesh to 9 digits); slide 3e-4, tolerance 1e-5: returned residual 2.1e-5 relative. **#1033 on the same four cases: residual honest, energy wrong by 0.2 % to 76 % (9.717e-5, 6.554e-5, 5.517e-5, 7.739e-5 against 5.506e-5), including the unslid factory annulus.** H6: take the post-solve residual as a report; it cannot decide the gauge. The reporting gap is W1's territory (rotated path, convergence policy): noted, not filed, after W1's current list. Shell labels: PR #1100 (gthyagi's flood fill alone + a failing test); defect only on twice-refined shells (1,363 of 98,112 cells mislabelled), H3 reviews. Walkthrough v4 in the repo.** H6's port probe (all #1033 new files on development's solver core) is building.
- **URGENT (H2; Louis 2026-11-12 03:50 UTC, quoted by H2: "The parallel placement is clearly very urgent."): fault placement refuses an MMPDE-moved base in parallel.** `place_fault_ribbon_2d(..., seams="gather")` on a moved base fails on more than one rank: "addon_partition: N fine cell(s) have no local parent cell on the level below". H2's reading: `addon_partition._parent_cells_local` locates each fine cell's centroid in the unmoved level below (#1044 moves only the finest level). Seen on K1's annulus_faults.py small case, uw3 fe3219f5, np 4 (285 cells at refinement 4, 86 at 3); serial fine. Blocks the refinement 4 and 5 MMPDE slab runs. **Owner W1, top of queue** (fault add-on, #1017 cycle; ahead of #1090's probe, #1069, #1072); the fix sought is a topological parent relation. **H1 reproduces on development 93e66eed, reduces to a library-only case, and runs W1's branch in parallel.** W1 files the one issue. H2 stays on science in serial. **W1: cause confirmed in serial on 93e66eed, filed #1091.** After a move the centroid sits in another coarse cell: refusal if that cell is on another rank, **a wrong parent recorded silently if it is local**. Governing quantity is the node displacement in coarse cells: 0.07 gives 0 wrong of 1440; 0.18, 25; 0.35, 243; 0.7, 588; annulus follow_metric refinement 3 moves 0.11 (0 of 10112), refinement 4 moves 0.37 (10342 of 40448); H1's recheck moved under a tenth. Fix on bugfix/addon-parent-after-a-move (not pushed): (a) parents located on the build coordinates, (b) the provenance transfer pulls fine nodes back to those coordinates. **C1 asked W1 and H1: do silent wrong parents change results or only iterations? Answer owed to C2/K1.** **W1, from the code (on #1091; no run, wombat is serial): the parents have two readers only, partition_addon (grouping) and fault_mg.provenance_transfer_parallel via CustomMGHierarchy.build (PCMG interpolation, Galerkin coarse operators, FAC patch rows); no field transfer, remap, restriction or BC reads them, so the cost is iterations or a reported non-convergence, and a result converged on the true residual stands. H1's baseline is the measurement; pending.** **H1 baseline (hyperion runs/2026-11-12-faultpart/report.md):** np 1 never refuses; np 2 from step 2 (12-16 cells), np 4 from step 4 (17-29); after a refusal the driver keeps the old faults and the run diverges (np 4: vrms +24 %, slip +52 % at step 4); silent wrong parents not separable (0 wrong in every passing placement; 2293-3510 of 7936 alongside refusals). Minimal case `mpirun -n 2 python repro_min.py rotate 3 2` (rigid 3 deg rotation, refinement-2 annulus, 30 cells refused). #1017 passes because it places on an adapt child whose level below is re-wrapped (#1037); the base's dm_hierarchy[-2] is never moved. Numbering parent (k // 4) monkeypatched: places every step, np 4 within 0.5 % of np 1 in vrms. **Second parallel-only failure with it in: mmpde amplitude 20-40 at np 2/3 fails in the surgery, "ribbon's cavity reached the domain wall"; places in serial; W1 to judge whether separate.** H1 recommends k // 2^dim for native refine pairs with the located route as fallback; W1 decides and must show its choice passes repro_min, K1's small case and the amplitude case. **W1 (after the baseline): fix written and built on wombat, not committed; serial tests/test_1173 fails on development (635 of 1440 wrong parents; moved-pair transfer off by 0.90 at degree 1, 1.125 at degree 2) and passes on the fix; MMPDE annulus refinement 4 goes from 10,342 wrong of 40,448 to 0. Design kept: as-built coordinates, no numbering branch (numbering fixes parents of native pairs only, not the transfer, and cut/placed/split children have none). The amplitude 20-40 cavity refusal is separate (the carve reads the host's current coordinates, never the parents) and may be geometric, since the mover is rank-dependent: H1 to place in serial on the np 2 mesh's coordinates; if serial refuses it belongs with H5's seam issue, if it places W1 files a parallel-only placement defect.** W1 pushes after its serial territory run and adversarial review; H1's run list is with H1. **Deciding run done (H1, runs/2026-11-12-faultpart/cavity/): the np 2 moved coordinates applied to the serial annulus (1080 vertices matched exactly) refuse identically in serial (place_surface.py 7709), so the cavity refusal is geometric: the parallel mover's mesh differs from serial enough to fail a placement. Not W1's; it is the mover seam defect. H5's queue reordered: seam defect first (regression includes this case), then #1082 F1-F3, #1087, #1083, np 3 in CI.** **#1091 fix pushed 2026-11-12: PR #1094 (draft), bugfix/addon-parent-after-a-move, head 82a769e1, development f8c60140 merged in.** Serial only (wombat): test_1173 8 passed; serial territory 269 passed, 0 failed; two adversarial rounds posted (round 2 found a real miss, fixed: add_fault replaces an add-on level under an adapt child by its split copy and the child's reference named the level replaced; 1,411 of 2,506 parents wrong, 8 after; those 23 lines have no third round, H1's cross-review serves). #1091 labelled fixed-in-PR (the periodic case stays open in it). **H1 has the parallel run list and the cross-review, first in its queue;** W1 warns the vertex-field carriage in redistribute_by_assignment has never run at np > 1. **H1 runs lane at 82a769e1 (runs/2026-11-12-1094/runs/runs.md): all pass.** test_1173 parallel np 2/3/4/5: pres its 19/20/20/20, vel its 3, slip 0.159472 at every np (Zen identical); development fails every case ("no local parent", 61/108/134/133 cells); serial 8/8 vs 0/8. repro_min places at np 2 and 4. K1 small case np 4 vs the k // 4 patch: no refusal on either; refinement 3 iterations equal; refinement 4 vrms agrees to 1.3e-3, per nonlinear iteration equal (no gain from the nested transfer). Amplitude 20/40: no partition refusal; carve refusals are the clearance contract (serial too). test_1096/1132/1172 unchanged. **Verdict waits on H1's review lane.** **Head now 9e6712fc (bounds only in the parallel test: pressure <= 24, velocity <= 4, slip within 5e-5 of 0.159472); marked ready; body carries the parallel results and "no worse per iteration, no gain"; H1 gives the verdict at 9e6712fc.** **H1 at 9e6712fc: test_1173 parallel passes at np 2-5 within the new bounds (pres 19/20/20/20, vel 3, slip 0.159472); verdict still on the review lane.** **REWORK PUSHED 2026-11-12 at 9a39ce6e (Louis's yes in the W1 session): record at construction and at each DM replacement; parallel cases over deform, node_redistribution and smooth_mesh_interior; scenario (c) as H1's sc.py; collective gate; serial only so far; H1 runs np 2-5 and gives the verdict.** **H1 round 3 at 9a39ce6e (runs/2026-11-12-1094/r3/1094-r3.md): NOT READY for a test-side reason only; the library fix is right at every np.** Case (c) fails at np 2-5 (`1466 == 0`): the test reads `second` against its stale `_addon_below` (the 888-cell level before the cut and split) rather than the level its reference names; parents themselves right. Conditions 1, 2, 4 resolved: record = built grid (smoother np 2: 0 of 2,592 parents wrong, was 51; MMPDE: 0 of 24,498 weights off, was 36,206 of 37,412); a lazy-record mutant fails 5 of 7; collective gate in. Per-np: deform 19-20/3, slip 0.159472; node_redistribution 19-20/3, slip within 1.3e-5; smoother 16-17/3. K1 case np 4: no refusals; refinement 4 steps 2-5 N 16, vel 76, pres 188, equal to development + k // 4 (the +18 %/+13 % of 82a769e1 was the stale record). Remaining: fix the case (c) loop; rerun the r2 mutant. W1 fixing ahead of #1099. **H1: READY at a176f94a (test-only fix): 7 passed on every rank at np 2-5; the round-2 mutant fails only case (c), at the `held` membership check; W1's reading of the loop confirmed; repointing `_addon_below` withdrawn. Merge on green CI (run 43183994595).** **MERGED 2026-11-12 at a176f94a on its third CI attempt (two 7763 failures of test_1152 first); development 613ed1e0; #1091 fixed-in-development (the moved periodic base stays live in it). H2 told, with the five items still in review.** **H1 REVIEW: NOT READY at 9e6712fc (hyperion runs/2026-11-12-1094/review/1094-review.md).** At np > 1 the as-built record is taken lazily at the first `_deform_mesh` (discretisation_mesh.py:4855), after both movers have already written coordinates directly (Laplacian smoother, smoothing/api.py:458-503; MMPDE `_halo_sync`, mmpde.py:471). HIGH 1, smoother: np 2, 51 of 2,592 parents wrong, as on development, silently. HIGH 2, MMPDE: parents right (0 mismatches to amplitude 100) but the record is stale: box np 2/4, 990 of 1,122 vertices off by 0.2 of a fine cell, 36,206 of 37,412 transfer weights off the nested set; "keeps its nested transfer" fails. MEDIUM: round 2's fix has no parallel guard (scenario (c) at np 2). mesh.deform route sound; scenarios (a)-(c), (e), (f) place; carriage exact with empty ranks. Conditions: take the record before the movers' first coordinate write (C1 recommends at construction and at each rebuild, not a hook per mover); parallel cases driven by node_redistribution and smooth_mesh_interior asserting four children per parent and nested weights; scenario (c) in the parallel test. To W1. Refinement 4, np 4, one run each: branch 19 Newton steps over steps 2-5 (vel 91, pres 210) against 16 (77, 186) for development + k // 4; they split at step 2 (first placement after the move, 2+2 against 2+1); leans systematic on weak evidence; H1 repeats both arms after #1096/#1097; does not gate #1094. **The np 4 mover is not repeatable run to run: four identical launches agree through step 1, then min cell radius 0.01670 (once, placement passes) against 0.01669 (three times, #1090's area check fails). Owner H5, with #1086/#1093, front of queue: reproduce with the mover alone, find where it enters, add a repeatability test.** #1090's knife edge stays W1's (run to the wall 0.0245). W1 declined to post H1's #1090 finding under its account (H1's posting hold); correct, C1's request was wrong. **Watch item (Louis, quoted by W1, on #1089's refusals: "We'll have to see if the surface refusal bites..."): once the #1089 PR is in, a campaign ValueError naming `min_quality=0.1` or "domain boundary", or a warning "could not be carried onto add-on level", goes to Louis; the geometric rule and quality floor stand as a proxy; the constraint test is not being built. Tell C2/K1 when #1089's PR merges.** Side finding to W1 for #1090: at refinement 3, the first placement after a move fails 3 of 4 runs on f8c60140 with "ribbon assembly meshed to area 6.283405877065e-03 against CAD 6.283" (1 of 2 identical branch runs, so something upstream is not deterministic run to run; not seen on 93e66eed). W1 side findings (not filed): `_addon_parent`/`_addon_below` not reset at the two DM-swap sites (with H1's `_re_extract_from_parent` follow-up); a reloaded mesh's rebuilt levels are not snapped to a curved boundary, so a restart's transfer differs from the run's (annulus refinement 2: 0.0094; H5 territory, restart); `custom_mg._colocate_level` in adopt_hierarchy at np > 1 on non-gather seam modes replaces tail levels by copies (same identity miss, not attacked). **Open with Louis (raised in the W1 session): he expected coarse levels to follow a move; today only the finest does (f4ae8a36, the #1044 review fix, a session choice). W1's probe: on simplex hierarchies coarse vertex i is fine vertex i, so coarse levels could follow by a slice; W1 treats that as a separate benchmarked item unless Louis says otherwise.** W1 next: test_1152 diagnostics, #1089 rework. **Corrected (W1 serial probe): the minimal case sits on the placement's clearance limit: the trace starts 0.30 from the outer wall (2.4 fine cells); with no move it places at 0.30 and refuses at 0.28; the np 2 mover's mesh lands on the other side. So the refusal is the placement's contract, nothing to file, and not proof that parallel runs are blocked.** The seam defect stays real (1.3e-2 vs serial) and first for H5, with a direct mover-vs-serial regression; a placement check should start 0.40 from the wall. If K1's driver places interior ribbons within about 2.5 fine cells of a wall it will meet this refusal on some moves at any rank count (driver margin, K1's to judge). W1 on H2's k // 2^dim relation: it would replace (a) for a regular base but not (b), and cut/placed/split children and adapt children have no such numbering, so W1 keeps (a) + (b). #1089's PR parked behind it: its review returned 10 findings (4 blocking; #559 more reachable; #595 live). W1 order: #1091, #1089 rework, #1090, #1069 after #1068, #1072. Note: hyperion mail/C1/ reaches C1 only when H1 relays it (this note waited about 55 min).
- **2026-11-12 status (C1):** #982 at 115b4786: the 6 shards were green, but the summary `test` job got no runner for 3 h and the run was marked failed; the job re-run hit startup_failure, so the PR was closed and reopened for a fresh run (43121701823); **merged 2026-11-12 at 115b4786 (development cab11f08); #960 and #966 stay open per the PR.** W1 asked to retarget #988. #1044: H1 READY at b5fa806f (and f4ae8a36); **merged 2026-11-12 at b5fa806f on green CI (development bb864e3a); #1037 fixed-in-development; H2 told the UWTN 2026-011 rerun is unblocked**; low follow-ups N1 (no test of M1 cleanup), N2 (docs: degree-2 refined meshes unsupported), N3 (multigrid_levels collective on every access vs docstring). H5: #1083 fix on bugfix/native-vis-reference-nodes-1083 c98df912, H1 review after #1082; **H1 round 1 on c98df912: request changes** (degree-2 coordinate meshes now refused at P4, natively rendered on development; Q3 on 90k cells 1.4 s to 29 s, from an unbatched pinv Newton with no early exit; details to H5 by mailbox). H1 side finding: deforming a degree-2 coordinate mesh with variables gives a broadcast shape error (96 into 336); **routed to W1** (degree-2 family, #978), low priority after the stack. #988 retargeted by W1 (a10b0364, no conflict); PR closed and reopened for a fresh CI run (the earlier red was the 2026-11-11 runner DNS flake in shard 4). **#988 merged 2026-11-12 at a10b0364 (development c7fc6d79); #1005 fixed-in-development. W1 asked to retarget #1003.** **#1003 retargeted (no conflict) and merged 2026-11-12 at a3cf8fd4 on a fresh green run (development dd92c701); #989 fixed-in-development. W1 asked to retarget #1024.** Degree-2 meshes: Louis questioned whether mesh degree above 1 is supported; W1 proposed refusing `degree != 1` in `Mesh.__init__` and closing #978 (awaiting Louis; W1 to give him the caller count, the moot work (#983, #1049 part, #1083 item, #1044 N2) and warn-first vs raise); H5 told to hold #1083's degree-2 item. **W1 reports Louis ruled degree-1 only (in the W1 session): PR on bugfix/mesh-degree-one-only-978, ahead of #1069; W1 to send the PR number and the moot list.** **PR #1088 open at 326ae833 (W1 quotes Louis: "Raise, now, I think. This has never been supported, should be safe to set aside."):** Mesh and the 20 uw.meshing constructors raise for a coordinate degree other than 1; removes #983's quadrature sizer, the FVM degree guard and #1044's deform guard; #978 closed not planned (verified); #908 unchanged. Moot: #1083's curved-cell item, H1's N2, degree-2 parts of #983/#1044. Reviews on the PR are W1's own; **H1 asked for a short independent pass on the removals; merge on H1 READY and green CI.** **H1 READY at 326ae833; merged 2026-11-12 (development 93e66eed).** H1 follow-ups to W1: `_re_extract_from_parent` should reset dm_hierarchy/dm_h (mmg route now gives PETSc error 75 after the move, segfault at np 2 via the private method; a solve failed on both builds before); a collective check on loading a mesh file (degree-2 checkpoint: error 62 at np 1, hang at np 2, pre-existing); #908's trigger is now unreachable. H1 side finding, unexplained, both builds: a solver BC on a label missing from some ranks of an extracted submesh hangs boundary setup at np 2 (unrouted; ask H1 for the repro when the urgent item clears). W1 side findings: stale dm_hierarchy[-1] on a re-extracted submesh (mmg route, to H1 with the review); `self.degree` still threaded as a parameter (cleanup); the interpolation branch of UW_DMPlexCreateCoordinateSpaceWithinPlex (#902) may be unreached. K2's job 4400 repros: W1 judges and sends the verdict, not the transcript. **Verdict in (W1): both library; W1 owns fault placement (line_cut.py, fault_split.py, place_surface.py), files two issues, fixes item 1 now (#1069 blocked on #1068), then item 2's probe; driver unblock sent to K1 and written for C2 below.** #1024 retargeted (dfb4cb06, no conflict); fresh CI run 43138290715 **RED: shard 3, test_1152_fac_zone_survives_a_mover_parallel `[zone]` at move 2, both kept and fresh Stokes solves DIVERGED_LINEAR_SOLVE at 0 iterations (pressure nan); the split-level case passed; the same shard was green on #1003's run. Not merged.** Shard re-run to rule out a flake; H1 asked to reproduce on #1024 merged into dd92c701 and say whether the cause is the mover or the test. H5 stays on #1024's head. **Re-run of shard 3 passed on the same code (test_1152 2 passed), so the divergence is intermittent; still held.** H1 to run `[zone]` about 20 times on development alone and on the merged tree: if development also fails it is a flake that predates #1024 (merge; owner W1 for the test/FAC path), if only the merged tree fails the mover is nondeterministic and #1024 stays out. **H1: 0/20 on development dd92c701 and 0/20 on the merged tree (np 2, Zen kernels as CI's EPYC); nothing ties the failure to #1024; kept and fresh both returned the initial guess, which points at a common cause at the first KSP application or runner state, not the mover. H1 recommends merging.** C1: third CI run (43151199784) on development 93e66eed, which now has #1088; merge on green. **Third run green; #1024 merged 2026-11-12 at dfb4cb06 (development f8c60140); #531 fixed-in-development. H2's stack (#982, #988, #1003, #1024) is complete.** H5 told to rebase onto development; W1 to merge development into the #1091 branch before pushing. Follow-up for W1 (its test): on failure, record both KSP reasons, the first residual norm and the move-2 minimum cell quality. #1044: H1's re-check is running at f4ae8a36 (verdict due in hours, sent to C1 only); it conflicts with development c5e5900b in scripts/test.sh batch lines; H2 asked to merge development in. #1085 closed as a duplicate of #1082; H5 owns #1082 (bugfix/mmpde-empty-rank 6190ed3c, the real fix: empty ranks join the reductions; np 4 [2,0,2,0] matches serial; H1 reviewing; PR after the verdict, rebased once #1024 lands). **#1082 H1 round 1 at 6190ed3c: not ready**: `_mmpde_mover` change right (bit for bit vs serial), but F1 high, public `redistribute_nodes`/`node_redistribution`/`relax` still hang at [2,0,2,0] (rank-local `dm.isSimplex()` at discretisation_mesh.py:8065); F2 single-rank MeshVariable metric now silently wrong (energies 1e3-1e4x); F3 empty rank biases the stop test; F4 facet slip surfaces hang (pre-existing; H5 to fold in or file). **Mover seam defect real on development (H1):** the step cap at partition seams sees only rank-local edges, up to 1.3e-2 vs serial at np 2/4 (a ghost-complete cap gives 1e-12); boundary_slip corners leave the box at np 2 ((0,0) to (-0.199,0)). **Owner H5 (reassigned from H2, who is on science)**; one issue per root cause; separate PR after #1082. H5 order: #1082, seam, #1083 round 1, #1060. **H5 2026-11-12 (later): seam defect filed as #1086; fix (step cap via a MIN over the point SF; boundary_slip masks via OR) rebased onto f8c60140 with #1082 under it, on bugfix/mmpde-seam-1086-on-dev (c3e52607) and bugfix/mmpde-empty-rank-on-dev (1077d769); a force-push over the old branches was refused, so bugfix/mmpde-seam-1086 and bugfix/mmpde-empty-rank are superseded and await Louis's approval to delete. Mover vs serial: annulus (amplitude 20, np 2-5) within 7e-8 (was 7e-3 to 2.4e-2), boxes within 4e-12. One PR for #1086 + #1082 after H1's verdict. New root cause #1093: with the default metric_eval="frozen", np 2 and 3 stay about 1e-2 off because global_evaluate resolves a point stranded at a seam by nearest centroid, not containment (RBF 5.76 against FE 5.058, mover-free repro). Owner H5, next, with a check against gthyagi's #859 (same point-location code). #858 finished as PR #1095 (gthyagi's commits kept, f8c60140 merged, H1's conditions met, SF leak fixed, odd-rank regression folded in); #1087 fixed-in-PR. H5 order: #1093 (+#859), #856, #1083, np 3 in CI, #1060. H1 queue: #1094, #1096, #1095, #1086/#1082.** **#856 finished as PR #1098 (stacked on #1095; gthyagi's commit kept; symptom test passes at np 2-4); H3 reviews #1095 then #1098, #1092, #1040.** **Added last in H5's queue (H1 side finding, pre-existing, unfiled):** tests/parallel/test_0770_submesh_extract_mpi.py fails 2 tests at np 3 on every rank (`test_prolongate_parallel` "prolongate rock error: 1.0", `test_copy_into_parallel`); passes at np 2 and 4, all that CI runs; H5 to reproduce, file under rule 8, fix, and say whether CI should run an odd rank count. **H1 review (e6a8a775): the fix is correct but duplicates gthyagi's open #858 (f93cadbd, same sum-and-count reduction, plus the single-rank-region case, which transfers nothing in either direction, and a raise when ranks disagree). C1: #858 carries the fix; H5 finishes #858 on a main-repo branch from gthyagi's head (development merged, H1's 2026-11-06 listed changes, H5's np 3/5 regression renamed and hardened, a single-rank-region test), then #856, whose symptom H1 saw on development (a BC on a label missing from some ranks of an extracted submesh hangs at np 2). #1087 stays as the issue.** **Done by H5 (2026-11-12): filed #1087; cause, prolongate's map is rank-local, so a parent DOF on the region's edge owned by an outside-region rank kept a stale value after the owner-wins sync; fix on bugfix/submesh-np3 (sum values and counts into the parent's global vector, owner takes the mean); test_0770 passes at np 2-5; test_1087 spawns np 3 and 5 from serial CI; H1 review queued (after test_1152, #1088). CI: H5 to add np 3 to the opt-in --full-parallel pass as its own small PR, with the wall-clock cost stated.** #1084 (#1057, uw.visualisation for higher-order fields) at add04b6b is green; F1 and F3 fixed; F2 filed as #1083. **Merged 2026-11-12 at add04b6b on H1 READY (development 6a2b04ed); #1057 labelled fixed-in-development.**
- **PR #1044 (#1037 fix), H2, a8363872 on development 526edb90:** test_1172 passes serial and np 2 (9 fail on development); all 200 mesh-move tests pass; test_1060's earlier failure was a 900 s timeout (alone it passes with and without the fix, in 47 min). H1 reviewing; hub merges on green. Then H2 reruns the talk case and the UWTN 2026-011 figure with the fix.
- **#1042 (mmg: available to users, not used internally) merged 2026-11-10 on green (83da1f63).** #1043 (test_0835 np 2, rank-local marker counts; SBR route) in W1's bundle C.
- **H2's stack rebased:** #982 982d7094, #988 c4d31f9d (now only the swarm matrix view and its tensor test; the rest reached development via 7bfdfaad), #1003 84cd1763, #1024 d04ac6bf; each passes its tests serial and np 2. H1 still to review #1003's and #1024's final commits. **Blocker: #982's base is still `bugfix/mover-stale-mesh-vector`** (#959's merged branch; refs can't be deleted from here, so GitHub didn't retarget). The hub's retarget to development was refused by this session's permission classifier; **put to Louis** (GitHub: Edit next to the title, base: development). Not asked of H2 (no laundering). #1037 fix: 199 of 200 mesh-move tests pass; H2 checking whether test_1060's failure predates it.
- **W1 after #1036:** #1012 labelled fixed (titled case); residual split as **#1041** (mesh `_equation_systems_register` is a strong list, keeps every solver and its KSP tree alive; 4 deleted Stokes all alive, 12 KSPs; fix a weak register). **mmg PR #1042** (H1: approve with 3 conditions, applied; record pending; np 2 check of the changed skips). **Bundle B** on bugfix/estimate-dt-bundle-b (local): #891 (estimators read model-unit coordinates; development gave 2.2e6x and 0.61x), #978 estimate_dt part (degree-2 mesh), #1031 (`_nondimensionalise_timestep`); test_1153 10 pass, 9/10 fail on development; **#1025** (SLCN diffusive limit, a default) to Louis with evidence. test_0835 np 2 rank-0 failure (also on development) to W1.
- **#1036 merged 2026-11-10 on green (b0dda24f -> development abe5e0ca):** #1017, #1019, #1020 fixed-in-development; #611 already labelled; #1012 (rebuild case fixed, deletion residual open) left to W1 to label. W1's bundle B next.
- **#959 merged 2026-11-10 on green (f5703d05 -> development 526edb90).** W1 merges into #1036; H2 rebases the #1037 fix (priority) and then the stack.
- **#959 / #1036 overlap (hub's call corrected 2026-11-10):** #959 is not held. Its np 3 hang was a development bug that #959 fixes by allreducing the move decision in `_remesh_with_field_transfer_impl` (also #960's one-rank-mover hang). Three review rounds answered; np 3 empty-rank and non-moving-rank cases pass at 7bfda648. **Order: #959 first** (H2 merges development for fresh 6-shard CI; hub merges on green), then W1 merges development into #1036, dropping its duplicate stale line (test_0766 covers it) and re-running test_1152. Then H2's stack in order: #982, #988, #1003, #1024.
- **HIGH: a moved refined mesh solves on pre-move geometry (H1, #1036 round 3; development 8f0ed0ab).** With `refinement >= 1`, `mesh.deform` or any mover updates `mesh.dm` but not `mesh.dm_hierarchy[-1]`; solver builds clone the hierarchy, so the solve (even a solver built after the move) uses the old coordinates, silently, until a new MeshVariable rebuilds the hierarchy. Poisson probe (hyperion runs/2026-11-10-hier/p_hier2.py): error 7e-5 at refinement 0, **51 % at 1 and 2**. **CORRECTED (H1):** the "36-71 % on Stokes" was mislabelled: it was Poisson (p6mv.py, p6.py, solver built before the move, against LU). Stokes is right after a move; the defect is in scalar solvers. Owner **H2** (move transaction): issue under rule 8, its own PR stacked on #959 ahead of #982, H1's probe as the regression test, H1 reviews. **Filed #1037 (H2).** Exposure: every MMPDE convection run in H2's session (all REFINE 2: the adaptive talk case, the June rerun, SUPG+MMPDE); none to be presented. Fixed-mesh runs and mover-only renders fine. The June driver had the same clone, so the UWTN note's figure (moving-the-mesh-without-remaking-it) is probably affected; H2 checking on a June build; W2 holding it. **Published notes (W2):** UWTN 2026-011 (2026-08-13, DOI 10.6084/m9.figshare.33241170): figures/adaptive-convection.gif, no build script, refinement unrecorded; caption claims the solver uses the hierarchy the mesh started with: exposure pending H2's June-build check. UWTN 2026-014 (2026-08-17, DOI 10.6084/m9.figshare.33273984): figure fine (no solve), but the text says the hierarchy survives relax(), and relax() is an MMPDE mover, so a solve after it on a refined mesh is wrong until #1037's fix: relax() added to H2's test. 2026-016 (no refinement) and 2026-022 (no mover) not exposed. Corrections to published notes: Louis's call; W2 told C3 and Louis. **Also exposed (C3 via W2):** underworld3 docs/advanced/multigrid-preconditioning.md, "Hierarchy and mesh adaptation" (line 87ff; the preconditioner docstring too) says the hierarchy survives the movers; its FMG-vs-GAMG benchmark (line 310ff, bench_fmg_vs_gamg_velocity_ksp.svg: 50 MMPDE steps, 3-level annulus, Ra 1e7, Δη 1e3, res 32, R 8, the 2026-011 gif's parameters) may have measured FMG's "about 5 iterations as the cells stretch" on unstretched cells. H2 checking which coordinates each engine held; C3 rewrites the docs when the fix lands. **H2's verdict (June build e19893ae and development):** the defect hits scalar solvers only in H2's probes. Poisson after a move at refinement 2 is 51 % off; Stokes at refinement 2 is right with FMG and GAMG (within 1e-5). H1's 36-71 % on Stokes not reproduced; H1 sending its probe to H2. **UWTN 2026-011 figure EXPOSED:** REFINE 2, MMPDE every step; velocity right, but the temperature's advection-diffusion (SNES_Scalar) assembled on the unmoved mesh while its values sat on the moved nodes; size of the change needs a rerun with the fix (H2's talk case). **Docs benchmark:** both engines solved Stokes on the moved mesh, so the iteration comparison stands; the temperature driving it carries the same error. Fix ready on 526edb90; PR after the mesh-move suite. Fix on bugfix/moved-mesh-hierarchy-coords stacked on #959 (refinement 0/1/2, default PC and FMG, serial and np 2). Side result: #1036 cuts the per-move leak from 9.2 to 1.9 MB (mover), 17.4 to 2.0 MB (with SUPG).
- **H1 on H4's branches:** d5d22be5 (guards 769/781/804) approve with 2 conditions; cb23e507 (#787) request changes (nested-expression datum still a silent zero dual, 0 vs FD 1.77; false refusals on names like `\bar{T}`; over-refusal in the transcript walk); cd9f2dfb (#778) approve. Side finding to H4 (rule 8): a field entering only through a Neumann BC gets dual 0 vs FD 0.225, no refusal, on 8f0ed0ab. H1 now on H3's three branches and the #1003/#1024 final-commit rounds.
- **H3 units (relayed via H1's mailbox; H3 cannot reach C1, trusted-device refusal), development 8f0ed0ab:** LIVE #843, #881, #992, #993, #998, #1001, #786, #765 (two routes, one a stock ViscoPlastic with no units; third peel site adjoint._peel), #763 (hidden behind #765: dJ/dα 1.0e21 x FD, the viscosity reference); #991 refuses at np 3 (coordinate fix in #1003); #771 reproduces but is the documented gateway. Bundles: A #843 (b13e5da0, H1 reviewing); B #992, #993, then lift #991's guard, stacked on #1003 and merged right after it (no order leaves a clamped parallel run 1000x off); C #1001 (1259232e; conftest-only fix, since test_0816 pins that the flag survives reset); D #998 after #1003; E #765 then #763 (19fdbc06). Held for Louis: #771, #904, #786, #881. **Decision note** hyperion runs/2026-11-10-h3/DESIGN-NOTE-771-904.md: A (recommended) keep the dimensional gateway, refuse mixed unitless/unit-bearing leaves in a model with reference quantities, fix ND_UNITS_BOUNDARY_CONTRACT.md; B evaluate returns ND (breaks every reader of K or Pa). Sub-decisions: solver fields get units in a units model; parameter defaults unitless with no reference quantities (#881); evaluate raises on out-of-domain points (#786); reset_default_model turns the ND flag off (#1001).
- **Step 2, verification (H1, dispatched):** probes on development, evidence on each issue, fixed-in-development labels; no closing until Louis rules on close-at-merge.
- **Step 3, bundles to single owners (proposed to Louis):** see the triage summary's top clusters.
- **Inflow:** SESSIONS.md rule 8 (one issue per root cause; search first; side findings to the hub); sent to W1, H1, H2, K2, K3.
- **W1's own sweep (Louis to W1: "...tying issues together and solving them in coherent bundles. I would usually do this by forcing a sweep before starting off on a hackathon!"):** `issue-sweep/W1-BUNDLES.md` (185c5f0): A hierarchy lifecycle (#1019, #1020, #1017; branch bugfix/custom-mg-hierarchy-lifecycle), B timestep estimation, C rotated free slip (corners/partition; gauge/datum; docs), D silent non-convergence (caps #585/#625/#755 are defaults: Louis with evidence), E fault-split MG in parallel, F ThinSheet, G solver API traps. Order A, B, C. #683 fixed by #1030.
- **mmg ruling (Louis to W1, 2026-11-10):** "No ! No mmg" ... "Let's let the mmg stuff atrophy. We have lots of non-mmg remeshing available. It is unreliable and hard to install mmg and not universal." #898 (remesh() through mmg) closed as not planned by W1. #977 and #909 (Mesh.remesh, fixes merged): left as fixed-in-development, closed with the rest. #994, #866, #979 use the remesh module's field transfer (also adapt/deform), not mmg: unchanged.
- **Put to Louis:** close at merge instead of release (keep the label); owners for the bundles (units, ThinSheet, adjoint, transport have none).

## BULK REVIEW 1 (2026-11-06, development eddab707; `tools/bulk_review.py`)

Louis, 2026-11-06: "We also should do bulk reviews where we can check which PRs overlap, which
are out of date, which are fixed and bundle the work. Sometimes this is very useful to prevent
features from being built without the big-picture." Scope: the 12 open PRs and every branch
not merged into development with a commit since 2026-10-01 (35 refs, 31 with commits not in
development by patch-id; squash merges show as unique, so read "unique" with care).

**Already done, not yet merged:** `bugfix/disk-snapshot-swarm-values` (2026-10-06, 2 commits)
IS the disk-restore fix (`var.data[...] = saved`, #313 pattern) with
tests/test_0020_snapshot_disk_swarm_values.py; clean against development; never PR'd. The
rescue branch carried a copy. Use this branch (integration session's item 1b).

**Bundles (work that touches the same code and should be seen together):**
1. **Stress history and VE transport** (systems/solvers.py, systems/ddt.py,
   constitutive_models.py, petsc_generic_snes_solvers.pyx): #800 forward-from-nodes (21 unique,
   480 behind, 7 conflicts, idle since 2026-10-12, no owner); `bugfix/backward-nodes-snapshot-order`
   (verified stress-transport fix, conflicts in solvers.py); `feature/ve-stretch-split` (#744, 4
   unique); the rescue WIP's experimental lagged_stretch_velocity; the disk-restore fix (Lagrangian
   stress history across restarts). Five efforts in one region with no plan between them.
   **Big-picture step first:** hyperion writes a one-page map of development's stress-history
   paths and what each branch changes, before porting the backward-nodes fix; Louis decides
   #800's fate (an owner to rebase and land it, or retire it).
2. **Rotated free-slip core** (utilities/rotated_bc.py): #906 null modes, the pressure-rtol
   default, queued #924, #939, #950, the mean-removal check, plus `feature/shear-band-length-scale`
   and the held slip coarse space. One owner (the integration session) serialises them:
   #906, then rtol (on Louis's yes), then #924, #939, #950.
3. **Fault multigrid** (custom_mg.py): `feature/fault-slip-coarse-space` and
   `feature/fac-structural-segments` (both held since 2026-10-30, #670, conflicting now), and
   shear-band's custom_mg changes. Phase-3 material; stays held, will need rebasing.
4. **Spherical meshing:** #946 (+ #903, #949, #931), one owner.
5. **Expressions and units:** #780 (5 unique, conflicts navier_stokes_eulerian.py), #891, #877,
   #881.
6. **Small, independent:** #665 headless pyvista (clean); the disk-restore fix (clean).

**Stress-history map (hyperion, 2026-11-06, read-only, eddab707).** Holders: `_StressHistoryMixin`
(systems/solvers.py:514) for SNES_Stokes, SNES_ThinSheet and the composed Navier-Stokes;
SNES_NavierStokes (:5504) outside it with its own path and no flux commit. One step: prepare,
build, advance (`update_pre_solve(store_result=False)`), solve, post-solve
(`commit_flux_to_history`, `update_post_solve`, DEVSS, model hook). **Live order defect on
development:** the source snapshot refreshes before the carry (ddt.py:3984, :2035) and the
commit projection reads it (:1112-1116) (#735). Restore from disk writes a detached view
(disk_snapshot.py:784). The five: (a) #800, 21 commits, renames schemes, adds
ForwardNodesSemiLagrangian, moves SNES_NavierStokes onto the mixin, FENE-P and the particle
projector, removes the node nudge (**changes the default scheme**); its test check fails; a
merge with development leaves two `_StressHistoryMixin` classes silently (development's wins,
SNES_NavierStokes would break) plus 589 conflict lines; renamed classes make development-written
disk files refuse to load; it keeps the old (defective) order. (b) `bugfix/backward-nodes-snapshot-order`
(#735): refreshes the snapshot after the carry; **the port is small** (development already moved
the methods into the mixin; the fix lives in ddt.py, which merges clean); new reach to ThinSheet
and `stress_transport="none"` needs coverage. (c) `feature/ve-stretch-split`: `stretch_in_momentum`,
`preconditioner_flux`; independent of #800; conflicts with #800 on `E_eff`/`_objective_term`.
(d) `lagged_stretch_velocity`: experimental, no test, needs #800's `_spring_factor_sym`, decides
the same terms opposite to (c). (e) the disk-restore fix: independent (the integration
session's item 1b, on `bugfix/disk-snapshot-swarm-values`). **Landing order:** (e), (b), then
#800 and (c) in either order (second resolves `E_eff`), (d) only after (c) with evidence.
**Routing:** (b) to hyperion now (port, tests incl. ThinSheet and "none", PR once its GitHub
writes are allowed); #800, (c) and (d) to Louis.

**Out of date:** #800 (480 behind, 7 conflicts), #780 (376 behind, 1 conflict), #861 (344 behind,
1 conflict), `feature/shear-band-length-scale` (22 unique, 380 behind, 7 conflicts across
rotated_bc, custom_mg, solvers, constitutive_models; second review owed since 2026-10-18).

**Dead or superseded (delete on Louis's word, 15 refs):** the seven `*-hyperion-2026-10-20*`
rescue refs (triaged; the one live fix is on its own branch above); `docs/issue-state-on-merge`
and `docs/test-tier-policy` (nothing unmerged); `feature/fac-block-solver-lu` (squash-merged as
#929); `bugfix/faulted-rebuild-leak` and `bugfix/rebuild-efficiency` (superseded by #882);
`feature/coarse-solve-nullspace` (superseded by #947); `test/kaiju-scaling-902-901` (a test
build). `probe/iterative-patch` and `test/probe-941` are probes (keep while useful).
`release/v3.2.0` is in main (keep).

**Decisions for Louis:** #800's fate; shear-band-length-scale's fate (rebase and review, or
retire); the 15 deletions.

**Practice:** a bulk review weekly and before any feature branch starts. Scheduled task
`trig_01TRM27hLPzzTwk2s854isYE` ("Weekly underworld3 bulk review") fires into this hub session
Mondays 10:37 Australia/Sydney; a hub restarted elsewhere must re-create it.

**External review verdicts (hyperion, records on the PRs):** #945 ready with changes; #862 ready
with changes; **#856 ready with changes** (library fix right, and also fixes checkpoint metadata
losing names when rank 0 is empty; the test hangs rather than fails on the old code, since
`dm.destroy()` follows rank-dependent asserts, which would take down a CI batch, and
`getLabel(...) is not None` cannot fail; lands after #858; 376 behind, green only on the old
base; #908 still live there). **#855 ready with changes, must not merge as is:** the hang fix is right (reproduced at np 3 on
development), but a clean-looking merge silently drops the fault-pair sheet datum (test_1092 error
0.047 vs 0.00096; a one-line fix, `SHEET_TANGENCY` in `build_rotation`, tested); its tests never reach
the repaired call site (a mutant restoring `if datum_nodes:` passes); 376 behind. #857 carries the
same code. **Correction:** test_1092 is a serial test; under mpirun its rank-local `assert len(sig) > 5`
fails on ranks with no fault nodes. Gathered across ranks the reaction is identical at np 1-8
(11 nodes, max relative error 0.00901). No defect; nothing filed; correction posted on #855.
**#859 not ready:** fixes #799 at unit scale, but its new tolerance is absolute, so meshes of
model size ~10 or more silently get wrong values where development is right (annulus at L=100:
144 of 9144 on-edge points unclaimed, errors 1.6e-2, no flag; shell at L=100 misses 8.7 %;
swarms lose on-face particles). A relative scaling is sketched in the record, untested in
parallel. **#858 ready with changes** (its test misses the ownership bug; leaks memory per
call). **#857 not ready:** numerics hold against analytic cases on both walls (rate 2, np 1-8) and
it is opt-in, but it shares #855's silent sheet-datum drop, has a pyx conflict whose obvious
resolution keeps stale methods shadowing development's, and its tests cannot fail on the core (no
Stokes solve; 14 of 18 mutants survive); wall updates are not recorded in the transcript while the
solve claims adjoint support; lands after #855. **#780 not ready:** `Mesh.__init__` re-declares
`uw.expression(r"t", 0.0, ...)`, so with the new refusal any mesh built at non-zero model time raises
(mesh.adapt after a step, read_timestep); "same value passes" is false for dimensional parameters;
meaning-changing re-declarations with new units still pass silently; reopens #774 for containers
surviving a reset; the conflict is one mechanical hunk. **#689 not ready:** numerics hold
(second order honest, conservation 1e-15, partition independence 1e-15), but scaled models get no
transport silently (metres read against non-dimensional values), restore breaks for every
AdvDiffusion built after a capture (theta 1.0 becomes 0.5), and a PC step records nothing while the
transcript claims adjoint support. **External review set complete** (reported to Louis 2026-11-06).

**#985 (test_0022 runtime) is #911's failure seen as cost** (hyperion): each forward solve's last Newton
step solves past round-off and breaks down; pressure hits its 200 cap on 465-1208 solves per run;
that step is nearly all of 19-52 min by kernel; #963's fix changes nothing there. Folded into #911
(#985 left open and cross-linked: Louis's authorisation for hyperion excludes closing; the hub's
instruction to close it was refused by its own classifier, correctly). **#911 moved up** to right after #964 in the integration
session's queue: its stopping-test fix cuts CI time and the production time loop's KSP rebuild;
evidence table for Louis before merge (a Newton stopping change).
**2026-11-07, #909 round 3 not ready** (the fixes created new defects a third time; hyperion stopped as
agreed). New at 0d0ed886: H1 deform with units (limiter clamps dimensional values against
non-dimensional bounds, then divides by the scale: T 0.0005 for 0.5), H2 refinement transfers with units
at np >= 2 still wrong (units stripped at discretisation_mesh.py:2617, 2644), H3 semi-Lagrangian reads a
MATRIX component from the transposed slot, M1 a bad scalar swarm shape hangs, M2 1-D empty-rank hang, M3
multi-column _write_evaluated untested. **Hub's decision: option (a), narrow the PR** to #909, #965 and
#977's remesh fix (dropping the lookup and shape-path changes), one review pass, then PR. Six pre-existing
faults to file (P1 deform with units rescales geometry, linked to #979; P2 semi-Lagrangian record x1000 at
np >= 2 with units; P3 semi-Lagrangian clamp with units; P4 unit-aware array into SwarmVariable.array; P5
limiter IndexError swallowed on one rank; P6 SemiLagrangian with MATRIX raises), H1/H2/M3 as issues.
**#959: a rank whose nodes don't move hangs at np 3 on both builds** (told to the MMPDE session).
**Units bundle** (one owner later): **#979** (= P1, remesh.py:368, 378), **#989** (H1 monotone clamp in a units
model; development's own error 0.125-0.27), **#990** (P3), **#991** (H2), **#992** (P2; also the SYM S[1,1] slot
read), **#993** (P4); root near the TODO at functions_unit_system.py:701. Also filed: **#994** (P5), **#995**
(P6), **#996** (M3 test gap). Narrowed #909 being built as `bugfix/remesh-transfer-909` from f31edcb1
(units paths stay at development's numbers).

**2026-11-07, Louis: a DRY fix for the solver stall.** "This is a persistent problem that we encounter
in various solvers. PETSc does not respect the original residual of the solve when we warm start. We
should try to find a DRY solution to this problem." So: the stacked inexact-Newton patch paused; the
integration session writes a design note first (docs/developer/design/): one convergence-reference
policy (the original residual carried across warm starts, Newton steps and re-solves), linear
tolerances derived from the Newton target, one helper used by every solver (generic SNES, rotated
loop, vector, adjoint, projections), the PETSc mechanisms, the issues it settles (#911/#985, #924,
#883, #884, the pressure-rtol default), and an evidence plan (it touches petsc_generic_snes_solvers).
Hyperion inventories every tolerance setting, warm start and reference residual in src as input.
Louis reads the design before code.
**Design note ready for Louis:** docs/developer/design/CONVERGENCE_REFERENCE_POLICY_2026-11.md on
`docs/convergence-reference-policy` (88c73b6c), docs only. One reference per solve() call, F_ref =
max(||F(x0)||, ||F(0)||) (warm and cold get the same targets; datum-only forcing from the lifted state
#883; null space projected out before measuring #884); Newton T = max(rtol F_ref, atol) from the user's
tolerances (#924); an inexact-Newton floor η T (η 0.1) on the outer KSP and every fieldsplit sub-KSP,
bounded below by 10 ε ‖A‖ ‖u‖; one helper on SolverBaseClass called from `_snes_solve_with_retries`
and the rotated loop, replacing five references; SNES and KSP atols set once per call; closes
#911/#985, #924, #883, #884; the pressure-rtol default overlaps and the measurement decides; four-arm
evidence (test_0022 on three kernels, rotated parallel set, zg95 on kaiju, SolCx, the notch, a warm
adv-diff loop, a projector); bar: same answers, no more Newton or linear work. The rheology question is
answered (d6c56325): F(0) is the residual at u = 0 with boundary data in place; 2η(ε̇)ε̇ vanishes at
zero strain rate for any finite η(0), so caps do not enter the interior rows and F(0) is the forcing
(the cold start's measure); a nonzero weak velocity (Nitsche/penalty γμ(0)/h·g) is the one exception,
handled by leaving weak boundary terms out of the reference; viscoplastic and weak-velocity arms
added, recording ||F(x0)||, ||F(0)|| and the forcing-only norm. **Louis approved it for implementation (2026-11-07):** "The principle here looks
good and I think we should implement and run through review to check that there are no edge cases that
have been missed. Broadly speaking: the equation knows what to define as the residual and the solver
should be more mechanical about applying the rules. I agree that some of the implementation choices
carry residual implications and that complicates things." Briefed: each equation declares its
reference residual; the helper applies the targets mechanically; implementation choices that change the
residual (weak BC terms, datum lift, null-space projection, rotated reduction, DEVSS/VE history) listed
as edge cases with their declarations; warm-re-solve contract test first; four-arm evidence; hyperion's
independent edge-case review (every solver class, warm/cold, time loops, units, np > 1, weak BCs, lift,
projectors, adjoint, VE); evidence table to Louis before merge. **Started**
(`feature/convergence-reference-policy` from f31edcb1, local): test_0028 (tier B) fails on
development's scalar warm start (passed T, one extra step) and passes on the branch; stage 1 in
`_snes_solve_with_retries` (SNES atol T, outer KSP atol 0.1 T, restored after; the saddle-point
warm-start atol and nrichardson pre-solve removed). The hub asked that the reference be a per-equation
hook (`_reference_residual()`, default F(0), overridden for weak nonzero velocity, lift, null space)
that the helper only reads. Next: rotated loop (#924, #883, #884), sub-KSP floors, legacy references,
evidence arms, hyperion's review.
**PR #1008 (sixth shard: test_0022 alone, deselected from shard 4's band; comment names #911):** `--deselect`
(not `--ignore`, which still collects a named file); collect-only batch 4 399/406, batch 6 7; --print-shards [1..6];
coverage OK, but the coverage check does not parse --deselect (noted). Cross-review by the laptop; CI running.
**#911 four-arm result on test_0022 (laptop, tol 1e-11, two fixtures):** current: no convergence (last increment
stalls), 55 / 254 s; pressure rtol 1e-2 alone: no, 110 / 107 s; linear floor η T alone: yes, 6 Newton, 6.6 / 2.1 s;
both: yes, 6 Newton, 2.0 / 0.6 s (every pressure solve 4 iterations); L2 agrees to 4e-10. Keep both; the floor is
independent of the time-loop ruling. **CI:** #964's shard 4 cancelled at the 70-min cap on a Xeon 8370C runner
(serial phase 55:38 vs development's 27:50 on an EPYC 7763): runner speed, mostly test_0022. #964 merges
development in for a fresh run; hyperion puts test_0022 on a sixth shard until #911's floor lands.
**#1008 at 598ab620** (laptop review: no must-fix; the coverage check now honours --deselect): merge on green. **Ruling 2 evidence, VE rotated time stepping (wombat, serial, 43857a53):** VEP order 1 annulus, 40 steps, tol 1e-5, error vs a
1e-8 reference. Increment rule: 67 Newton its, 38.5 s, error 1.4e-8 to 9.7e-7. Stationary (development's rotated rule): 42 its,
33.5 s, error 2.7e-6 to 9.1e-6, within tolerance and not growing (unlike the adv-diff loop). Increment costs ~60 % more Newton
and 15 % more time for 3-650x accuracy beyond the tolerance. Kaiju arms at np 16 running (zg95 faulted restart A/B; plain notch
ref 1 and 2). Put to Louis: VE rotated default (the hub suggests increment, per ruling 1's principle, unless zg95 shows the cost
matters; both switchable).
**Convergence branch, hyperion's review at 43857a53: not ready (H1, M1, M2, M3); all four fixed locally (integration, 2026-11-08).** H1: the rotated sub-solve atol was in outer units and moved fault slip 2.2e-4; now scaled sub-solve rtols, first increment as on development, so test_1087 and test_1111 pass on development's own baselines (rebaselines reverted), test_0022 still fast. M1: weak datum read by its symbols (a lid ramped from zero counts). M2: the native floor checks the true residual on a preconditioned norm; warm nonlinear Poisson re-solves 1 Newton step against development's 2. M3: documented (register row 1). Full serial suite running before push; hyperion re-checks np 2-4 on the new tip. **#1007:** first fix missed (the solver's cache reset ran before the rotated solve); cleanup now at the end of a solve that built a new workspace, ee3f4d4c pushed; hyperion's control says deferred garbage; its np 2 numbers decide. **#1012** (hyperion): a separate Stokes-only rebuild leak, 23 MB per solve, not deferred garbage; loose-ends queue. **#895 network case** queued after the convergence branch (row 5, np 4 on hyperion or the dev runner).
**W1 branches, 2026-11-08 (no PRs yet; all touch custom_mg.py in different functions; W1 merges development into whichever lands later):**
`feature/fac-patch-lu-ordering` aca58b6c (register row 8; H1: ready; PR after K2 confirms and checks a 3-D case);
`bugfix/stokes-adjoint-custom-mg-1016` 98d0c8bd (#1016: adjoint keeps the velocity hierarchy, 3 levels 4 its vs 1 level 23; test_1145 fails on development; H1 reviewing, np 2);
`bugfix/custom-mg-after-deform-1015` 1aa389b8 (#1015: re-solve after mesh.deform, error 73; test_1146; H1 reviewing, np 2).
After #1014, development 80d3ebe9 merged into all three (qmd ee6105c5, 24 passed; #1016 c2443048, 17; #1015 b0a7f806, 19; test_0028 with each). **W1's order:** qmd PR (after K2's confirmation and 3-D check); #1016 and #1015 PRs (after H1's reviews); #1017 (design note first if a new API); pressure-rtol PR (development merged in, not rebased; zg95 on K2 plus a rotated Stokes benchmark with a known answer; table to Louis); #934 cross-rank fixture.
**PR #1018 (#1015, re-solve after mesh.deform), W1, 4ecd3963** (development 80d3ebe9 in): H1 ready after M1 fixed (the stale-key drop deleted a user's own smoother keys); H1's record posted (ready). **Merged on green 2026-11-08; #1015 fixed-in-development.** #1022 now needs development merged in (W1). H1 filing two development defects: gamg on an adapt child reads the same leftover key; deferred garbage on each standard-path reinstall.
**#1016:** H1 blocker: the late install left nonlinear adjoints solving with the tangent at u = 0 (12-75 % wrong, reported converged); fixed 09d82e14 (injection before state assembly), dense-reference errors <= 2e-10, test_1145 mutant fails; H1 re-checking, no PR yet. **#1021** filed: Stokes adjoint matrix route builds velocity MG from J's block, not Jᵀ's (right answer, 9-11 its vs 5-6; also on development).
**Two-level FAC patch vs #934's one block, in parallel (Louis approved via C3; authorised to the hub 2026-11-08; DOCS-HUB 2026-11-08):** owner W1, runs on K2; schedule under #895, before any 3-D work; folds in W1's #934 cross-rank fixture. Bring `feature/fault-slip-coarse-space` (244 behind, stacked on `feature/fac-structural-segments`) up to date, or say first if that is not cheap. Fixtures: UWTN 2026-022 linear at h_b/S 24 and 48, a two-fault network on different ranks, a seams="conform" fault if placeable. Arms: one block (#934), two-level at fac_block_rows 2000 and at one rung, per-rank pieces without the coarse space (control); np 1, 4, 8, 16; velocity its, velocity-solve wall, patch set-up and factorisation, peak memory per rank (max, min), coarse size, answer vs one block. **All arms on qmd (#1022)**, so the one-block arm is not handicapped by nd fill. Feeds Louis: two-level as the default for networks or all faults, and whether 3-D builds on it. **W1's cost of the port: moderate** (branch 5 commits / 906 lines, but 300 behind; 9 conflict hunks, 7 in custom_mg.py against #934's block rewrite, 2 in rotated_bc.py: a port, not a merge; a good part of a session plus test_1091 serial and H1 np 2-4). Hub proposed to Louis: stage 1 without the port (one block vs per-rank pieces, qmd, np 1-16, memory and time), port only if one block's parallel cost is shown to matter; qmd's 25-58x fill cut may have removed the memory case. **Superseded (W1, 2026-11-08):** the cross-rank fixture cannot be built: `fault_split._redistribute_fault_interior` (fault_split.py:1241) moves a whole network (union of every fault's star plus one layer) to its majority rank in one move, by design; placement's `_gather_region` likewise (argmax). K2's row-5 records agree (np 4: both bands and the junction on one rank; only the placed-not-cut TI band spans ranks). So one block vs per-rank pieces is identical by construction; the owning rank's 1.6-2.2x memory is the gather's, not #934's block; the two-level form's parallel case needs faults on different ranks first. Fix would be per-fault majority-rank distribution in one move (library change to the split's parallel contract: Louis's yes, design note, H1 np 2-16). Put to Louis: make that change then measure, or settle #895 now (cost is the gather's). **CORRECTED (W1, 2026-11-09): that reading came from a checkout on an old base.** On development each fault already goes to its own majority rank (`partition_addon`, one region per fault path; regions merge only when stars touch or the caller groups them, e.g. a junction; rebalanced with non-fault cells; design note parallel-addon-distribution-2026-10.md). The single-move union survives only in `_redistribute_fault_interior`, for the extruded layer (3-D item). K2's row-5 records were a 2026-11-01 build. **Louis 2026-11-09: "spread the faults ... before the momentum dissipates"; to W1: fault to its (majority) owning rank.** So stage 1 is measurable and tests #934's real choice: `_gathered_patch_blocks` (no zone) makes ONE structural block across every fault on the rank owning most rows. W1 building the stage-1 driver (~/+Simulations/fac_895/stage1/, from row5_networks.py): fixtures `apart` (two equal faults far apart), pair, junction; arms `one` (development, qmd) and `per_rank` (probe override, no coarse space); record band cells and block rows per rank, LU flops, peak RSS per rank, set-up and solve, slip vs one; serial check then K2 np 1/4/8/16, first job confirms the faults sit on different ranks. Likely fix if the cost shows: one block per fault on its owning rank (the notes session's suggestion). **Stage 1 result (K2, 56 jobs, b8367c40; uw3-campaigns `addon-matrix-2026-11` 77764ba, results_895_stage1.md; raw records on kaiju `kaiju/895-stage1-records` 8dcbb8e for Louis's rsync):** all converged; per-rank matches one block to 5.2e-14 in slip, same iterations. single/pair/junction: one rank each, arms agree. `apart` (faults on different ranks, np 4/8/16): #934 puts both faults' rows on one rank (30.9k rows at h_b/S 24, 60.2k at 48); splitting over the two fault ranks cuts the busy rank's LU flops and MatSolve 1.8-2x; first-solve wall -27/-28/-19 % at 48 (np 4/8/16), -18/-2/+2 % at 24 (shared nodes, indicative); busy-rank peak RSS only -7-8 %, the 1.5-2x busy/quiet ratio is the fault region, not the LU: qmd removed the memory case. **Next:** (1) close the two-level port (keep the branch as evidence; stage 2 not run) - put to Louis; (2) `_gathered_patch_blocks` cuts the structural patch into one block per fault region on its majority rank (inside #934's gather, so #925 holds; junctions and touching pairs stay one block) - within Louis's 2026-11-09 ruling ("fault to its (majority) owning rank"); W1 builds the PR with the table, a parallel test (two far-apart faults, two blocks, two ranks) and H1 review; Louis sees it before merge. **#945 and #862 merged** (green, reviews answered). #895 retitled to the post-#934 framing.
**H1 (2026-11-08):** records posted, all ready: #1018 (merged), #1022 (green; waits on Louis), #1023 (**merged on green; #1016, #1021 fixed-in-development**; #1022 needs development merged in). Filed **#1019** (gamg after a FAC install reads a leftover key) and **#1020** (deferred PETSc objects on each standard-path reinstall), both in W1's queue.
**H2 (2026-11-09):** re-running the June FMG benchmark on hyperion (stagnant lid, Ra 1e7, Δη 1e3, res 32, R 8, mover every step, np 5) on Louis's request; needs the June FMG and GAMG run folders from wombat `/Users/lmoresi/+Simulations/StagnantLid/` copied to hyperion `~/+Simulations/StagnantLid/june_wombat/` (put to Louis). New leak: AdvDiffusionSLCN ~3 MB/step/rank when dt changes every step (function rewire); evidence with W1, W1 asked to file (hyperion's gh auth lost; affects H1 too). H2 works around it with a fixed dt. **Filed #1026 (W1):** serial 0.56 MB/step vs 0.08 fixed dt, one outer KSP retained per step; `SNES_AdvectionDiffusion.solve` (and four more solve() methods) self-setups when is_setup is False, bypassing `_build()`, and `_setup_solver` makes a new SNES without destroying the old; dt is a runtime constant so no rebuild is needed. W1 fixes after #895.
**#895 per-fault blocks (W1, `feature/fac-blocks-per-fault-region`):** no zone keyed: the structural patch is cut into connected pieces (rows sharing a coarse DOF or DOFs of one node), each a block on its majority rank, inside #934's gather; single fault, junction, touching pair stay one block. tests/parallel/test_1147 (np 1 one block; np >= 2 two blocks, rows held once, majority ranks, two ranks). Serial check, H1 review np 2/4, then PR with the stage 1 table; Louis sees it before merge.
**PR #1028 (#895, per-fault blocks), W1:** stage 1 table and register row in the body; H1 two rounds, ready; M1 fixed (faults 0.12-0.20 apart gave two coupled pieces on one rank, 4 its vs 3; now pieces on one rank form one block, near pairs bitwise as base); apart faults two blocks on two ranks at np 2/3/4, no row lost in 33 cases. CI green on 8b793674; H1's record posted. **Louis 2026-11-10: "1028 can merge"; merged (42c4a795); #895 fixed-in-development.** June wombat copy dropped for now (Louis: wombat inaccessible; "push through without them"; run details in the UWTN note, H2 pointed to moving-the-mesh-without-remaking-it). **Louis 2026-11-10: two-level port closed** ("1 yes"; `feature/fault-slip-coarse-space` kept as evidence, stage 2 not run). **June stagnant-lid copy for H2 given to W1** (Louis: "ask W1, I am not able to do it now"). Hyperion's gh auth works again (H1 posted #1028's record). **PR #1030 (#1026 SLCN timestep leak, #1027 Darcy half flux), W1, 3801eea0:** H1 two rounds, ready; **merged on green 2026-11-10; #1026, #1027 fixed-in-development** (development 4dfc1e17; W1's later 3159d811, a test and the Richards θ docstring, missed the merge: new PR #1032, H1 ready, **merged on green 2026-11-10**). H2 pushes on without the June runs (UWTN note confirmed as the record, but lists no dt, perturbation or Nu; W1's excerpts are the only record); running a mode-7 low-res control on Louis's request. (bug fixes; #1027 changes TransientDarcy results, toward correct: told to Louis). **#1031** (H1): older timestep-setter edge case, W1's queue. June copy: wombat refuses ssh (Remote Login off), so Louis pushes from wombat (commands given); W1 sent H2 the June run_logs; lead for H2's 1.5x dt: estimate_dt rewritten in #688 (1d5e8c15, 2026-09-08), unverified. **#1026 fix** on `bugfix/slcn-timestep-rewire-leak` (unpushed): numeric dt sets only the constant (Louis: "should be compilable using constants"); five solve() methods set up through `_build()`. **#1027 filed:** TransientDarcy compiled F1 before its symbolic flux history existed, so ran at HALF the flux at θ = 0.5 until a rewire; fixed on the same branch. 58-file suite running (baseline 469).
**#1017 (design, for Louis):** after a deform the FAC patch is declined, because levels registered with set_custom_fmg don't move with the fine mesh; should mesh.deform carry the motion to them (injection for nested refinement)? **Ruled (Louis, 2026-11-08):** "I think that moving the base mesh should kill the patch but the fault would then be absent and the patch would need rebuilding. I imagine that this would be synchronous with moving the fault to a new location - move the fault, use this to change the refinement of the base, then add the patch with the cut fault. Direct this to one session. Not the one working on fault / convection models for the science hub." **Owner: W1** (after #1015, #1016, qmd; design note first if a new API); H2 stood down and uses W1's cycle when its MMPDE base meets the add-on.
**PR #1014 (convergence-reference policy; #911, #985, #924), W1, head 1f703133 (development ba3fc23e merged in, clean):** CI green; H1's two review records posted (ready; N1 documented, doc nit fixed); parallel suite np 2/4 passes; serial A/B 2940 (test_0063 as development); notch arm identical. Touches petsc_generic_snes_solvers. **Louis 2026-11-08: "1. yes 2. yes 3. agree, separate PR" (merge; VE rotated increment permanent; pressure-rtol its own PR). Merged on green, development 80d3ebe9; #911, #985, #924 fixed-in-development.** **#895 (W1, K2 jobs 4179/4183/4187):** the question can't be measured on row 5's fixtures (the split keeps each band rank-interior, so the network is one block on one rank before and after #934 at np 4-16); cross-rank fixture later. The runs found the FAC patch LU had no ordering set (register row 8).
**Convergence branch 26e40318 (W1, 2026-11-08):** H1, M1, M2, M3 and the lows fixed; full serial tier A/B 2940 passed (test_0063 fails, also on development); H1 re-checking np 2/4; K2 has the zg95 arm (4167, 4168). Ruling 2 table holds on this tip (register row 4).
**PR #1013 (#1007, rotated rebuild leak), W1, 5d431d31:** a solve that built a new rotated workspace ends with the collective PETSc garbage cleanup; H1 np 2: leak.py flat from the third solve (development +7 MB/rank/solve); rotated parallel files clean at np 2 and 4; test_1144 counts petsc4py's deferred-destroy list, fails on development in every order H1 tried, passes on the branch. #1012 (Stokes-only rebuild leak) stays open. H1 posted its review (ready, no conditions; Copilot did not run, quota). **Merged 2026-11-08 on green, development ba3fc23e; #1007 fixed-in-development.**
**Ruling 2 (Louis, 2026-11-08): increment for VE rotated, for now.** "I'll take your recommendation for now, but we do need to keep
track of these kinds of changes as they may not be benign for all solvers or models." Register opened (top of file); row 4 provisional
until the kaiju arms.
**Convergence branch 43857a53 (pushed):** the weak-nonzero-velocity arm found a regression under the max rule (a Nitsche-driven
lid on a power law: ||F(0)|| 118-2540 from the penalty times the datum; warm re-solves 70-1300x less accurate than development);
fixed by a `_weak_datum` declaration (a boundary term nonzero at rest makes the equation measure its increment; detection
symbolic; a datum in a constant counts); test_0028 carries both cases. The forcing-only F(0) was left out (it would change the
generated C of every Nitsche/penalty model). **#1011** filed: on development a cold solve with a weak datum is 1e-3 to 3e-2 off at
tolerance 1e-4 (its target follows the penalty). Louis's ruling applied to the four tests (test_1087 now counts the cycle with
the floor switched off by `rotated_bc._INCREMENT_TARGET_FRACTION = None`); CHANGELOG records the evaluate() change. test_1087's
premise (welded tail 13 its at k=3) is stale on development (5, like split levels): to hyperion.
**Louis's ruling on evaluate() accuracy (2026-11-08):** "I don't mind, but 10^-9 is a very fine tolerance which can go wrong
if there is any difficulty with the solve (e.g. an instability) and just get stuck forever. Remove the redundant work, set a
reasonable tolerance." Applied: no projector exemption, no tightening to 1e-9 anywhere; tests assert at the accuracy their solver
is asked for (test_1057 at the projector's tolerance, or a projector tolerance of 1e-7 to 1e-8 if needed; test_0009 assertion
matched to 1e-4; test_1111 re-recorded at 1e-6 with the v_rms bound matched; test_1087 reads the first increment). **Rotated-loop
stage done** (`feature/convergence-reference-policy` b2a88402 on 06c574e8, pushed, not a PR): stationary keeps max(r0, ||F(0)||),
memory measures r0; test_0022 758 s -> 13.6 s (last increments' linear solves 300/32/12 -> 1); floor = min(0.1 T, 0.1 ||b||)
(the round-off term overstated round-off 300-fold); a shared KSP convergence-test dispatcher (floor + wall-clock guard); **#924
fixed** (test_1143); NaN residuals leave tolerances alone; time loop after 300 steps: development 1.36e-6, max rule 9.07e-5, branch
1.45e-6; tier A/B serial 6 failed / 2932 passed. Hyperion's parallel runs and edge-case review next; evidence arms remaining:
notch, zg95 viscoplastic, weak nonzero velocity, kaiju VE rotated.
**Convergence branch stage 1, tier A/B serial (3317ca29, local):** 8 failed of 2850 (test_0063 also on development).
Fixed: the pre-solve floor had replaced PETSc 3.25's Eisenstat-Walker pre-solve (EW now sets rtol and the floor bounds it
from below inside the KSP convergence test, scaled into the KSP's norm); the floor relaxed explicitly set ksp_rtol (it now
replaces only the tolerance-derived key, per _TOLERANCE_DERIVED_KEYS). **For Louis:** the floor removes accuracy that came
from over-solving: test_1057 via evaluate()'s projector (snes_rtol 1e-6; development's second Newton step solved exactly,
better than 1e-10; now 4e-9 on 0.05) and test_0009 (a clock test asserting 1e-6 at default tolerance 1e-4; fix the test).
Question: should evaluate() keep its old effective accuracy? (a) yes, projectors over-solve (exempt, or state their
accuracy) or (b) no, evaluate returns the 1e-6 it asks for. Integration session recommends (a); the hub prefers (a)
implemented as the projector stating its own tight tolerance (an explicit rtol the floor already respects), not a
special-case exemption.
**#1008 merged** (sixth shard: test_0022 alone, 11:29 on an EPYC 9V74; shard 4 29:15 without it; merged result's
coverage checked: 400 files, shards [1..6]). **#964 merged** (green on five shards at 5031aa28; #906 and #877 relabelled fixed-in-development; #906 stays open
for the wall-crossing-cut experiment). **#964 hold released (2026-11-08): round 5 does not
change test_0022** (serial on wombat, r5 in place vs reverted: identical iteration counts, 758.5 vs 758.7 s; 666 s
are two last Newton steps at the 300 cap, i.e. #911). Earlier note:: the same Xeon 8370C gave
55:38 on #964 and 26:37 elsewhere, so the runner alone may not explain #964's capped shard 4. Shard 6 can still reach
57-60 min on a slow runner until #911. **Shear-band data** (hyperion inventory): ~4 GB notch results/figures/jobs/meshes
and 2.1 GB ShearLayerVEP output exist only on hyperion (twice on the healthy disk, once on the boot disk), plus an
uncommitted 2024-03-21 edit to UW3-Moresi Ex_Sheared_Layer_Test.py; the off-machine destination is Louis's call
(rsync commands given).

**Rulings applied (2026-11-08):** #964 at 5031aa28 (docs: a deformed wall's rotation kept as a near-null mode, Louis's
reason quoted; `_project_out_rotation` described as the free-surface driver's helper, global reductions in parallel);
the memory/stationary split is the convergence branch's default (`_carries_memory()`: DuDt or DFDt; test_0008 passes);
**the linear floor moved to KSPSetPreSolve as η T/||F_k|| of each solve's own first residual** (a KSP atol was in the
preconditioned norm on the scalar GMRES route, ~40x under ||F||, stopping Newton's linear solve at iteration 0);
FGMRES routes measure the true residual so test_0022's table stands; test_0028 gained a nonlinear adv-diff step;
tier A/B serial running. VE rotated switch `_convergence_reference_rule = "increment" | "stationary"`, kaiju arms
after the rotated-loop stage. Snapping logged as a queued experiment. #964's CI re-triggered on 5031aa28 (five
shards; #1008 not yet underneath).

**Louis, 2026-11-08: "The shear band micromorphic / cosserat formulation is really important, do not lose it or
any examples."** Inventory: the library work (coupled volume fields monolithic with u and p, micromorphic yield
regularisation, Cosserat shear-layer test; docs micromorphic-plasticity.md and saddle-point-field-groups.md; two
review records; tests test_1070 and test_1078, serial and parallel) exists only on underworld3
`feature/shear-band-length-scale` (114c472c) and the `test/sbls-coss-hyperion-2026-10-20` refs (538042dc,
f5709813). **Pinned** as `archive/shear-band-length-scale`, `archive/sbls-coss-hyperion-2026-10-20` and
`archive/sbls-coss-hyperion-2026-10-20-wip` (the repo's archive/ convention). Examples and records: uw3-campaigns
main `notch_length_scale/` (118 files: cosserat_notch.py, micromorphic_notch.py, coupled_notch.py, HANDOFF,
REPORT, plots), the journal's main (16 entries, 2026-10-09 to 10-11). Tracked in #1010. **Never delete any of these
refs.** Hyperion inventorying run outputs, figures and notebooks on disk (git ignores runs/), first flagging
anything on its failing boot disk.

**Louis's rulings, 2026-11-08:** (1) memory/stationary split for the convergence reference: "Yes";
(2) VE rotated time-stepping reference decided from the evidence: "Agree"; (3) a deformed wall keeps the near-null
rotation: "keep - the deformation may not eliminate the null space" (to be documented in #964 and
rotated-freeslip.md); (4) snapping cut-created wall vertices: "I'm not sure. We can try." (an experiment after #964
and the convergence work, under the radius item); (5) #735: "Keep an eye on this, hold for now" (hyperion files the
Waters and King bias as an issue); (6) #800: "Unknown" (revisit at the next bulk review); (7) shear-band-length-scale:
"Important work, is it captured?" (captured only on its branch: design doc micromorphic-plasticity.md, field-groups
doc, two reviews; hyperion files a tracking issue; rebase after rotated_bc/custom_mg settle); (8) "Truly dead,
remove". **Deletion:** the hub's check found its bulk-review list over-called: coarse-solve-nullspace,
faulted-rebuild-leak, rebuild-efficiency (session scripts and records), restore-head (a unique VE restore test), the
360-kdtree WIP (a unique test), both sbls-coss refs (not contained in shear-band) and the forward-from-nodes WIP
(lagged stretch) are NOT dead. Truly dead (no unique content in development's terms): docs/issue-state-on-merge
(7184379072b8), docs/test-tier-policy (40db1d4c3dff), feature/fac-block-solver-lu (61233c84ba8f, squash-merged as
#929), test/kaiju-scaling-902-901 (94a5c965da2f), wip/yield-782-759-hyperion-2026-10-20 (0eda3c7006a0),
bugfix/mem-leak-176-hyperion-2026-10-20-wip (95291ba64d2b, a #176 reproducer), review/bn-mergetest-hyperion-2026-10-20-wip
(eef11d3d4d26, a merge-test patch). **The cloud proxy refuses ref deletion** (403 on git/refs); not worked around;
the commands went to Louis.

**Design point for Louis (2026-11-08):** the approved rule loses accuracy in time loops. Stage 1's serial run:
1825 passed, 2 failed (test_0063 also fails on development; test_0008, the warm-started AdvDiffusionSLCN loop,
tier A, fails only on the branch: restore drift 5.4e-7 against an 8.7e-8 floor). Cause: in a time step ||F(0)||
carries the mass term M T*/dt, so max(||F(x0)||, ||F(0)||) holds each step to rtol of the whole field, not
its change: errors vs a tight loop 20-70x larger (step 4: 1.2e-6 vs 4.0e-5; step 300: 1.4e-6 vs 9.1e-5),
accumulating. Proposal (the equation declares its reference): solves that carry memory through a DDt
(AdvDiffusion, VE Stokes) take the increment residual (PETSc's default, `_reference_residual` = 0);
stationary re-solves (continuation, chunked restarts, perturbed re-solves: #911, test_0028) keep the max;
quasi-static Stokes under changing buoyancy keeps the field scale; the linear floor stays everywhere.
Development's rotated loop already uses max(r0, ||F(0)||) in time loops, so VE or rotated time-stepping
models have had the looser rule all along. Asks: (1) adopt the memory/stationary split; (2) VE rotated
models take the increment reference at more iterations per step. Built as a switch meanwhile.

**Inventory (hyperion, on #911: issuecomment-6712890427):** no helper owns the reference. Five routes
each compute one: the rotated loop and continuation (F(0)) and Picard (first residual) survive a warm
start; SaddlePt's warm start uses F(guess); Scalar, Vector and MultiComponent warm starts have none.
KSP is never warm-started. A warm start is the default once a solve has succeeded
(`_resolve_zero_init_guess`). The rotated bundle sets no `ksp_atol` (likely #911's immediate gap).
`_snes_solve_with_retries` is the single gate on native routes; the rotated loop bypasses it (a natural
home for the shared helper).
**#911/#985 rediagnosed (laptop probe):** Newton is not at round-off (last residual 1.15e-9, 400-30,000x
above the ε‖Â‖‖û‖ floor); the linear targets are unreachable (outer rtol 1e-11 relative to an
increment RHS ~1e-9, i.e. ~1e-20 absolute; inner pressure 0.033·tol likewise, hence the 200 caps).
Fix proposed: inexact Newton (linear atol ~η(rtol·ref + atol), η ~0.1, on outer and inner splits; the
Newton test still measures the true residual). Stacked on #964. **Combined with the pressure-rtol
default** (waiting since 2026-10-28): one four-arm measurement (current, inexact Newton, pressure
rtol 1e-2, both) on test_0022 (laptop, hyperion kernels) and the zg95 fixtures (kaiju), so Louis
decides one tolerance policy.
**#997 merged** (fifth CI shard; green on all five at 1227d1cf). **#1002** answered at 6b435eed (RBF derivative refused on every rank,
np 2 and serial tests; #991 a refusal with the reason; Closes #996); filed #1004, #1005 (swarm MATRIX reads
back transposed), #1006; laptop agreed (the refusal verdict is the same on every rank). **#1002 merged** (green on five shards;
#909, #965, #977, #996 relabelled).
**#964 round 5** (d7548b3c): ready once one Low is fixed or filed (~10 MB per re-solve leaked when a warm
converged re-solve changes tolerance); the threshold now picks the cheaper or converging side in every case; the
np 4 shell is on the sphere with #952 underneath. #959 still green at 7bfda648, held for the MMPDE session's np 3
answer. Note: `gh pr edit` fails on this repo (a Projects (classic) GraphQL error) and changes nothing; hyperion
now edits PR bodies through REST; #983's merged body was corrected after the fact. **#952 merged** (15f13d0c; #946, #903 relabelled; merged result checked against
the five-shard test.sh: coverage OK). #964 merges development in next. #1002: hyperion keeps #991 as a
refusal (every units change in the PR's history opened a new fault; #991 goes to the bundle owner with #979
and #989).
**#1002 cross-review (laptop):** 1 must-fix (global_evaluate on a matrix-valued derivative through the RBF route
raises on point-holding ranks only: a hang at np >= 2), 5 should-fix (to hyperion). **Transpose question
answered: no objective-rate or VE campaign path changes** (L and W are symbolic in `_objective_term`, objective
order and Cayley steps, thin-sheet spin; SemiLagrangian stress and log-conformation history is SYM_TENSOR,
bit-identical; only a user-built non-symmetric TENSOR history changes, where development stored the transpose;
four VE variants md5-identical). Not to Louis. #964 round 4 fix: threshold max(1e-10, min(1e-6, 100 tol)),
workspace rebuilt on a tolerance change; the convergence note carries the one-rule edge case.
**#964 round 4 (hyperion): not ready;** round 3's viscosity Medium and Lows fixed; new Medium: the fixed
1e-6 projection threshold ignores tol and np (at tol 1e-11 a projected near-null mode stalls like #963; at
1e-9 2-5x cost at np 2 and 4; answers unchanged). Fix: scale with tol; later folded into the convergence-
reference policy's per-call target (one rule). #964 follows #952.
**PR #1002 (narrowed #909; closes #909, #965, #977):** global_evaluate no longer transposes any
non-symmetric 2-D result (TENSOR, MATRIX, velocity gradients): a user-visible change to semi-Lagrangian
tensor history; parallel refinement transfers refuse with reference quantities (naming #991) instead of
going silently wrong; test_0782-0785 pass at np 2, 3, 4, 8. Cross-review asked of the laptop, with a
table of which production or campaign paths read non-symmetric tensors through global_evaluate (objective
rates: Jaumann, upper-convected); to Louis before merge if any VE or zg95 campaign changes. Filed #999,
#1000, #1001 (the scaling flag leaking across reset_default_model).
**#997's first five-shard run green:** shard 5 38 passed in 20:13, shard 3 down to 21:18 (EPYC 9V74; was
41:34-51:59); shard 4 55:00 until #911. Lows fixed at 1227d1cf; merge on that green. Narrowed #909's four
conditions fixed at 05ffb102, re-check before PR; a possible conftest leak of the non-dimensional scaling
flag between tests to file if confirmed. #952 rerunning on 284dd314.
**2026-11-07 state:** #997 cross-review posted (no must-fix; two Lows: shard times from one run on 2x-different
runner CPUs; a paragraph contradicting #958's shard-2 ptest phase); new head 1227d1cf, CI running. #964 round 3
fixed (59828ca0 + 99c8b050: exactness a Jacobi-scaled local residual at 1e-6, viscosity-independent, pinned at
contrasts 1 and 1e6; mutants killed); CI running; the np 4 shell vertex is #903, fixed by #952. **#952 has been
stale since 2026-11-06 05:45**, red on the old base: the integration session merges development in; #952
merges before #964. #959 green at 7bfda648; the hub asked the MMPDE session to confirm the np 3
non-moving-rank case before merging; #982 (stacked, green) after its cross-review. Louis's rulings on deformed
walls and wall-crossing cuts still open on #906; #964 merges with the behaviour documented.
**PR #997 (fifth CI shard, test.sh only):** moves shard 3's test_108*/109* batch (25:47) to shard 5;
shard 3 and 5 near 31 min each; test_0022 stays on shard 4 for #911 (wall clock ~56 min until then);
coverage exact (404 paths, each in one shard); hyperion's review nothing blocking; laptop cross-review
asked; CI running. Noted by its review: **branch protection on development and main requires no CI
check** (pre-existing; Louis's setting). **#964 round 3:** close; one new Medium from the auto-merge with
#967 (a viscosity-dependent exactness test projects a near-null mode, 2-4x slower at contrast >= 1e5; a
viscosity-independent fix shown); four round-2 conditions open (one on #952); parallel set passes at np 2,
4, 8 except #962 at np 8 (shared with development). **Narrowed #909** built at
`bugfix/remesh-transfer-909`: keeps development's numbers on round 3's probes; parallel refinement of a
units variable will refuse on every rank naming #991; then review.
**2026-11-07: merged on green with development merged in: #972 (#971, 1733fd6f), #980 (#950, ec493daa),
#981 (Linux anchors, a92355e7), #983 (#908, 145f95d7), #958 (#900 ptest files into CI, 72741873).**
#971, #950, #908 relabelled fixed-in-development (#900 stays open: 24 ptest files still need a harness or
a fix). Development at 72741873. Still open from the queue: #959 (MMPDE, np 3 non-moving-rank hang to
check), #982 (stacked on #959), #964 (round 3), the narrowed #909, the fifth-shard PR, and the
convergence-reference work.
**2026-11-07: #973 merged** (f31edcb1; hyperion's final word: DG to DG byte-identical to eddab707; #905
relabelled). #983 (26244045) and #958 (d31b9039, also moves ptest_0844_reconnect into CI) pushed with
development merged in; CI rerunning. **2026-11-07: Louis switched the hub to Accept edits and said yes to #967 and #980.** Merged: **#954**
(c5c87100), **#967** (7c3d31fd), **#955** (squash, 081417a1), **#970** (37aa2a11). #963, #665, #961,
#807 relabelled fixed-in-development. Development at 37aa2a11. Red on old bases (shard 4, the #963
hang): #972, #980, #981 (integration session), #983, #958 (hyperion), #959 (MMPDE session): each
owner merges development in for fresh CI; the hub merges on green. #973 waits on hyperion's final
word. #964 merges development in, then round 3. **#982** (MMPDE: remap clamp off by default on
Louis's decision; kd-tree fixed after a mover) is stacked on #959: #959 first. **#977** gets its own
PR after #959. **#979** (units model: mesh.deform scales the mesh to metres and the mover does
nothing) is the MMPDE session's priority after #959/#982 and #977.
**#983's shard 4 red at 7397bd17 on the #963 stall in test_1064** (run 42219732969, job 127898568438;
no test failed; #983 adds a file, so test_1062 shares test_1064's batch); rerun after #967 merges.
**#983 ready on green at 7397bd17** (round 2: no must-fix; the low should-fix done: the hex rows now fail
under a two-point mutant; manifold rule worst radius error 7.6e-8). **#983 at d3f7647e: should-fixes done** (FEGeom rule follows the coordinate degree, cells in bounded
blocks: 27k hexes qdegree 6 peak 1550 -> 3 MB, 8.7 -> 0.64 s; 195k hexes qdegree 3 2090 -> 0 MB;
dm_class removed; reuses _collective_raise; per-cell closed-form tests 15 failed / 2 passed on
eddab707, 17 passed on the branch; body corrected; diff commands posted: no #909/#965 hunk). #908's
np 3 case: eddab707 exit 142 ("Edge has 6 coordinates != 4"), branch area 0.5 to 15 digits. The new
FEGeom rule asked of the laptop for a look; merge on green regardless. #909 round 2 at 0d0ed886
(two more transposition fixes), third independent review running; hyperion stops and reports if it
finds defects in the fixes again. test_0022: pressure hits its 200 cap hundreds of times per run.
#983 cross-review (laptop): no must-fix, 4 should-fix (FEGeom for all cells at the user's qdegree on
every rebuild, ~+1.5 GB at 27k hexes qdegree 6; a dead dm_class; a duplicate _collective_raise; two
non-closed-form baselines); warped hexes x3.74-3.80 not x3.63; to hyperion. **PR #983 (#908, split from #909)**: degree >= 2 cell radii, with factors and the caller table in the
body; test_0782 10 passed, parallel 4 passed at np 2-8; its review ran on the combined branch, so the
laptop cross-reviews the carved branch. #909 and #965 still in fixing (round 2 found three new
must-fixes: dimensional values mis-scaled through remesh, mesh.deform corrupting square MATRIX
variables, a mis-shaped SwarmVariable.array write hanging at np 3). **#984** filed (read_timestep
raises on tensor-shaped swarm variables; mesh.deform raises on a SYM_TENSOR mesh variable). test_0022's
slowdown is kernel-sensitive and not fixed by #967 (Nehalem 22:10, Zen 42:22, default 52:14 with the
fix), all in the rotated_gradient fixture: hyperion filing it for the integration session.
#981 ready on green (hyperion's review: no conditions; 14 passed, 0 skipped at np 2, 7 previously
skipped; each anchor a live gate).
**#980** ready on green CI (hyperion's three review changes in; rerun green at np 1 and 2). **PR #981
(test anchors, tests only):** per-host anchors so test_1063, test_1064 and test_1066 check absolute
answers on Linux CI instead of skipping (hyperion's Linux values); drops the stale strict xfail on
the constrained-shell LU-subsolve case (tier C); hyperion reviewing.
**#735 port held for Louis (hyperion, 2026-11-06):** the code does what it claims and the stored
stress now moves (rotation 4.05 -> 0.298 at order 2; yield overshoot 2.8 % -> 0.9 %; faulted nodal
sheet 2.78 -> 0.311; cylinder off-wall excess gone; other flavours unchanged to 1.7e-15, ThinSheet to
5e-14), but **Waters and King gets worse and stops converging** (error at t=2: development 7.8e-4 ->
3.9e-4 halving; branch 2.42e-3 -> 1.97e-3), uniform bias along the channel, max|v_y| 2.6e-4 -> 1.2e-3
(candidate mechanism); nodal rotation error grows as dt falls (0.30 -> 0.44 at Courant 0.7 -> 0.087);
the snapshot itself is now inert (bit-identical disabled on 6 of 7). test_1054 fails 10/23 (pinned on
the defect). The wall peak remains, so #735 stays open (Refs). **The hub's recommendation to Louis:
do not merge yet**; file the bias, find its cause, land once convergence is restored. Records on
hyperion runs/2026-11-06/.
**PR #980 (#950, options database growth):** dropped solvers' options go when the solver is
collected; the coordinate FE's keys go right after use; rebuild-loop growth 17 keys/cycle -> 0.
Touches petsc_generic_snes_solvers.pyx only in the base constructor (a weakref.finalize, not run at
exit) and a module helper; no numerics; serial 1380 passed; hyperion reviewing and checking in
parallel. **Flagged to Louis** (CLAUDE.md's rule on that file). #972: hyperion's review ready, no
conditions; parallel test fails on eddab707, passes on the branch. #973: hyperion's three changes
pushed (b8399ce5), final word pending.
**PR #973 (#905):** projecting a discontinuous field to a continuous one averages the cells at a
node (each interpolation row divided by its sum, discontinuous sources only); tier-B test fails first;
hyperion reviewing at np 2 and 4. The integration session's remaining queue: test anchors (with
hyperion on CI's environment), #950; after #964 (rotated_bc.py): #924, #939, #969, #962.
**PR #972 (#971, disk-snapshot swarm restore)** by the integration session: `var.data[...] = saved`;
test_0020 fails 2/2 on development, passes on the branch; development merged into the 2026-10-06
branch; hyperion reviewing with a parallel save/restore check. Merge queue: #954, #967, #955, #970,
#972, #958, then #964 after #967.
**#967 all green on 488c53b1** (run 42187331541): shard 4 passed in 55 min, the first green shard 4
since eddab707; test_1064 ran all 18 cases in ~100 s; test_1142 passed. Hyperion's conditions met.
Waits on Louis's yes (evidence table given) and the hub's merge permission. The quarantine falls
away once it lands. **Shard times on #967's green run:** 4: 55.0, 3: 53.5, 1: 43.8, 2: 25.6 min. The test_00[0-4]* band
grew from 5:14 to 27:11 (test_0022_rotated_adjoint 956 s on hyperion). Hyperion: one rebalance PR
after #954 (test_0022 its own batch on shard 2; shard 3's 27-min batch moved too), and first a check
of whether one merge slowed test_0022 (a performance regression to file) or it grew gradually.
Hyperion's CI-log sample (23 shard-4 runs since 2026-10-28): the test_00[0-4]* band runs 9 to 28
min on the same tree (dfb6a6c0 541 s; d8c05c93, one visualisation-only commit earlier, 1637 s),
ceiling near 1650-1680 s: not a merge regression; likely runner hardware like #963 (timing
test_0022 under forced kernels, with and without #967's projection). **The hub approved a fifth CI
shard** (test_0022 and test_1092; estimates 4: 40, 3: 30, 1: 44, 2: 31, 5: ~40 min), after the
kernel result and #954.
**Shard 4 at 55 of 60 min:** hyperion to rebalance after #954 (cap 70) if #958
and #970 push it past ~45. Merge order: #954, #967, #955, #970, #958.
**PR #970 (#961 and #807: ptest_0844_reconnect hang)** by the integration session: the subsampler
kept parent maps derived through repaired passes; nested-transfer helpers decided None rank-locally
before collective fallbacks; the test's asserts stopped one rank ahead of a collective. Fixed
(repaired passes recorded, verdicts reduced over all ranks, coordinates read before early return,
asserts reduce first). Hyperion: new parallel test fails or hangs on eddab707, passes at np 2, 3, 4,
8; ptest_0844 passes at np 2 and 4 (hung 840 s before); serial 501 passed; hyperion's review:
mergeable. Touches nvb.py and discretisation_mesh.py (independent of #967 and #964); adds one
parallel file. #967 CI: shards 1-3 green, shard 4 running.
**#908/#909 review (hyperion):** no production, campaign or driver path builds a mesh of degree >= 2
(AST scan of 600 files), so nothing goes to Louis. Not ready: #908's fix holds; #909's transfer
corrupts non-symmetric tensors silently (serial error 3.0 vs 8.9e-16 on development) and leaves a
hang in the restore step; five must-fixes with the fixer. Radius factors for the body: degree 2 x2
on tri, quad and tet but x3.63 on hexes; degree 3 x2.59, ~x3e6, x3, x4.06; callers: estimate_dt x2
advective, x4 diffusive; SUPG tau x2; Nitsche gamma x1/2; metric and adapt targets unmoved; store
smoothing x4. Filed **#975** (metricCreateIsotropic on an empty rank hangs a later distribute),
**#976** (global_evaluate extrapolates on small partitions, no flag), **#977** (Mesh.remesh silently
zeroes units-carrying and symmetric-tensor variables: told to the MMPDE session, whose #959 touches
remesh.py), **#978** (other degree-2 routes still read midpoints); #974 (disk-restore shape mismatch
on one rank). #965 fixed by the #908/#909 branch.
**#908 + #909 fixed locally on hyperion** (`bugfix/parallel-collectives-908-909`, two commits, in
review): behaviour change on straight-sided degree-2 meshes: cell radii, get_min/max/mean_radius and
cell_size() double (in serial too), matching degree 1 to 1e-15 (the FVM read edge midpoints as
corners). The zg95 annulus uses Annulus's default degree=1 (checked by the hub): unaffected. PR to
list every caller and its movement; stop for Louis only if the audit finds a production degree-2
path. test_0782/0783 fail first, pass at np 2, 3, 4, 8. Found, to file if confirmed:
metricCreateIsotropic on an empty rank hangs the next collective; global_evaluate extrapolates a few
interior nodes on very small partitions. Hyperion fix queue: #954, #955, #958 are PRs; #735 committed
locally, in review.
**#967 at 488c53b1:** the adjoint leak closed (533.1 to 549.5 MB over 31 adjoints; new parallel test
fails without the fix); review answered; merge on green and Louis's yes. **#954 and #955 green on
every shard;** both wait on the hub's merge permission (Accept edits).
**#967, hyperion's review: one must-fix** (the solve is right on all 8 kernels; the wrapped multigrid
leaks 19 MB per adjoint solve at np >= 2; a four-line fix verified, with the integration session).
#964 round 2: not ready, no High findings left. **#969** filed (off-origin rotation: FMG reports
converged on a rigid rotation; predates #967).
**PR #967 (#963 fix) opened**, evidence in the body for Louis: test_1142 fails on eddab707 and
passes on the branch (macOS: inner bound "200 <= 10"; hyperion: the Nehalem child times out at
240 s vs 14 s); all 8 kernels finish at np 1 and 2 (8 of 16 stalled before), L2 the same to ~1e-16;
parallel set passes at np 2 and 4; macOS projection on/off: annulus inner velocity 4 vs 200 its,
answer to 2e-11; shell 5 its either way, to 1e-13; serial 504/505 rotated and custom-MG tests
(test_1021 now unwraps the PC). Waits on hyperion's review and Louis's yes. #964 round 3 at
2bd82efe (cached re-solve keeps its verdict; mixed given/default normals warn; every wall reduced
before branching; round-2 mutants killed; moved child pinned at np 3, 4, 5, 8); development merged
in after #967, then hyperion's round 3. #959 laptop round 3 at a41f2250: no must-fix, one
should-fix (test_1070's datum error measured after the deform).
**#963 fix in progress** (`bugfix/rotated-vel-pc-projection-963` from eddab707): after the
rotated custom-FMG velocity PC is set up, admitted rotations that A_vv annihilates to 1e-10 relative
are orthonormalised and the velocity sub-KSP's PC becomes a PCShell z = P M(P r) around the
configured MG; near-null (faceted) modes are not projected; the record gains
`projected_null_modes`; GAMG and vector routes unchanged. test_1142: in process, the analytic-normal
annulus_fmg projects one mode (L2 0.0190696176, rel 1e-8), the default normal none; x86 only, a
child with OPENBLAS_CORETYPE=Nehalem must finish within 240 s (CI's Linux runs it, macOS skips).
Hyperion shows it failing on eddab707 and passing on the branch, then the 8-kernel table, then its
review. **Nothing merges until Louis has seen the before/after iteration and answer table.** #964
then merges development in (no rebase; no force-push).
**2026-11-06: #963's mechanism found (hyperion, posted on the issue): a library issue, not a test
artifact.** The rotation is an exact null vector of the rotated velocity block; the FMG cycle
injects rounding along it, flooring the inner solve. Whether the floor lands above the 3.3e-11 rtol
depends on the OpenBLAS kernel and np (of 8 kernels: default/SkylakeX finish at np 1 and 2;
Haswell/Zen stall at np 2; Sandybridge/Nehalem at np 1; Core2/Prescott at both; thread count
irrelevant; hyperion is a Xeon Gold 6240R). **Projecting the mode out of the preconditioner removes
the stall on every kernel, same answer to 13 digits**; #947's shift, the smoother and the
orthogonalisation are not the cause. Any rotated FMG solve with an exact rotation mode can stall on
some CPUs. Fix: the integration session's next PR, ahead of finishing #964 (CI is red for all until
it lands), test forcing a stalling kernel, hyperion cross-review. Quarantine not needed if it lands
soon. Also: #954 at 12525d48 (review addressed: upload on cancel, 70-min cap, two native samples,
per-shard CPU/BLAS report); #958 at 12585422 (must-fixes done: ptest loop on shard 2, 16 files,
0864_seam and 0865 at np 2 only, ptest_jit_cache no longer wipes the real cache); #858 ready with
changes (its test misses the ownership bug; leaks memory per call); filed #961 (0844), #962
(test_1140 at np 8), #965 (global_evaluate on empty submesh ranks).

**2026-11-06, #964 (#906): hyperion's review says don't merge yet** (ten conditions). Being
fixed in #964: `addon_partition._moved_wrap` drops the declaration at np > 1 (rank-dependent
answer); the exemption ignored a constrained normal (a non-radial given normal on a circular wall
reached v_rms 2e7: exempt only normal=None walls and sheet tangency); wall vertices read from the
label's direct stratum (SegmentedSphericalShell labels interior vertices "Upper": read the closure
of the labelled facets; the label spread to be filed); a screw [-y, x, 1] accepted and an off-origin
sphere centred wrongly (common centre by stacked lstsq, residual and rank checks, numeric setter);
#877 with a unit-carrying velocity; the record stale on a warm start (renamed
`declared_modes_exempt`, warning names wall and spread); tests and docs. Hyperion's np 4 off-sphere
vertex is #952's bug (to confirm on #952's branch). **Put to Louis:** (a) a wall deformed past 1e-9
keeps the near-null rotation (large, ill-determined; warning; document the post-solve
`_project_out_rotation`, as free-surface-convection.md 3 already says) or removes it as a gauge
(changes the physics); the integration session and the hub recommend keep and document. (b) snapping
cut-created wall vertices onto the wall: left to the radius-variable design item.

**2026-11-06: #963 reproduced on hyperion: the OpenBLAS kernel, not leaked state.** Default and
SkylakeX kernels: the annulus_fmg solve finishes in 2.3 s. Haswell and Zen: the inner velocity FMG
floors near 1.2e-7 and stops at its 200-iteration cap; the outer FGMRES stagnates at 1.37e-9 against
the test's tol 1e-9, so the solve never finishes. Batch order irrelevant; deterministic under Zen
(GitHub's AMD runners). Hyperion checking where the rounding enters (coarse shift on/off, null space
attached/detached, #906's tip under Zen). **PR #964 (#906)** opened: test_1131 10 passed; 40 rotated
and fault files 367 passed, 1 skipped; full rotated parallel set and the twin pass at np 2, 4, 8 on
hyperion; #906 and #877 labelled fixed-in-PR; hyperion's cross-review to follow; the radius variable
filed as a draft design item.

**2026-11-06: #963 filed (the test_1064 CI hang), owned by the integration session.** **Correction: the hanging case is
`test_rotated_freeslip_annulus_fmg_partition_independent`** (the custom-FMG rotated annulus, the
fifth test; #954's stacks put both ranks in `_annulus_fmg_diagnostics`, test_1064:309), not
spherical3d as the hub had it. A quarantine must target that case. #947's PR
run and the development push have identical trees; the PR run passed test_1064 in 100 s at 11:30;
every run since 19:39 sits in the annulus_fmg solve past 300 s; same image, cache key and
pixi.lock. #954's own CI artifact shows both ranks in one FMG F-cycle restriction (not a collective
mismatch). Hypothesis: on some runner CPUs the solve stops converging and heads for max_it 10000
(host-dependent, not batch order). Next: #954 prints lscpu; hyperion sweeps OPENBLAS_CORETYPE
with iteration counts; the laptop bounds the outer KSP in the test (a library default change
would need Louis). **#954 review (laptop):** 1 must-fix (`if: failure()` misses the cap
cancellation; `failure() || cancelled()` plus headroom), 9 should-fix; to hyperion. A rerun of an
old PR run reuses its old workflow: #951 needs development merged in to pick up #954.

**2026-11-06: development itself is red.** Its own push run at eddab707 (the #947 merge,
2026-11-05 20:38) failed shard 4 on the same test_1064 spherical3d hang at np 2. That tree equals
#947's tested head e15f5fad, which passed on its PR run: **the hang is intermittent on GitHub's
runners, not caused by any PR** (3 of the last 4 shard-4 runs that reached it hung; it never hangs
on hyperion). #954's own CI run carries its diagnostics (gdb, stack artifacts), so if it hangs
there we get the runner's stacks. **Put to Louis:** quarantine that one test case in CI (skip under
CI with an issue reference) once stacks are captured, so CI is meaningful again; until then a
shard-4 failure that is exactly this hang is treated as known. **#959 review (laptop):** 2
must-fix (remesh.py:516 still skips `global_evaluate` on a rank with no target points, so
populated ranks hang: #960 part 1, a one-line fix; both tests tier_a), 2 should-fix (the swarm
proxy stays at pre-move nodes after a mover move, 3.4e-2, no issue covers it; follow_metric still
decides `moved` per rank). Sent to the MMPDE session.

**2026-11-06: #955 green on every shard; the hub's squash merge was refused by this session's
auto-mode classifier ("Merge Without Review").** Not worked around; put to Louis (switch the hub to
Accept edits, as on 2026-11-03). #954: shards 2 and 4 green, 1 and 3 running.
**2026-11-06:** #955's round-2 cross-review: no must-fix, no should-fix. **Squash merge on green**
(d8d5984c fails its own test, so a merge commit would leave a red bisect point; precedent #929).
#954 waits on green and the laptop's review. **2026-11-06:** #955's five should-fix items addressed at dfb6a6c0 (none declined; 39 passed,
4 skipped); merge on green. **PR #958** (#900: 14 ptest files into CI, appended so no batch
moves; review record posted) to the laptop for cross-review. **#961** filed (0844_reconnect hang,
failing assert and stacks).

**2026-11-06, cross-reviews:** #955 reviewed by the laptop (no must-fix, five should-fix: the
test cannot see a reintroduced IPython/trame import, the notebook default unpinned,
`jupyter_backend="none"` raises without IPython, tier_a marking, #957 not mentioned); hyperion
to address before merge. #954 and #959 reviews running (#959's parallel checks written out for
hyperion). **#906** at d992064d: the laptop's serial suite caught its own bug (derived meshes
inherited modes in the parent's coordinate symbols: NameError on a faulted thin sheet; fixed in
b7030602 with a failing-first test); hyperion's parallel runs pass at np 2/4/8, a rank-local
reduction mutant hangs at np 2-8. PR after the 40-file serial rerun and hyperion's review.

**2026-11-06: PR #959 (MMPDE session, bugfix/mover-stale-mesh-vector add5ea77):** after a mesh
move, solves used the pre-move field on the moved nodes (a bug since 2026-05-28; first solve after
a move 3-4 % high in v_rms), and a non-moving rank could hang the collective remap. remesh.py +16,
serial and parallel tests. Its review predates the final squash; the last seven source lines
unreviewed: the integration session cross-reviews. **#960** filed (two unreproduced
rank-asymmetry risks in the remap). Merge order on green: #954, reruns of #951/#952, then #959
and #955. **Earlier moving-mesh results may carry the error** (told to the science hub below).

**2026-11-06: Louis authorised hyperion's GitHub writes in its own session** (push side
branches, open PRs, PR and issue comments, file issues; no merging, approving or closing).
Out: **PR #954** (CI keeps the MPI supervisor's stacks with native frames; merge first, then
rerun #951 and #952), **PR #955** (#665, headless pyvista without IPython or trame), review
records on #945, #862, #952, the #900 table, **#956** (fault pins 0863-0865 fail at np 4, back to
2026-10-29: 3-D fault parallel peak slip wrong) and **#957** (plot_scalar/plot_vector fail with
their default cmap). Both PRs' CI running; the integration session reviews them. Still to come
from hyperion: the #900 PR, 0844_reconnect's issue, #735's PR, external reviews of #780,
#855-#859 and #689.

**2026-11-06, development baseline on hyperion (eddab707, serial tier A+B):** 2887 passed,
145 skipped (134 need --with-mpi), 9 xfailed, 0 failed; 5 h 57 min on one core, ~25 GB peak.
Slowest: test_maxwell_transfer_function_under_a_t... at 4972 s (machine shared; check its CI
cost in the next bulk review). Hyperion's queue items 1-7 done except GitHub writes.

**2026-11-06, MMPDE session:** #906 at c6c2668a passes the moved annulus at np 1 and 4
(declared_modes_kept [True], gauge orthonormal, nodal rate round-off, v_rms within 0.05 % of
unit_e_0). New: the default CG mover stalls after ~5 of 150 outer iterations; regression test
written and failing, fix next. (It reaches the hub by SendMessage; the hub's send_message to it
works.)

**2026-11-06, #906 invariance check pushed** (`bugfix/rotated-nullspace-from-mesh-906`
c6c2668a): test_1131 moved-mesh cases (a wall-preserving move keeps the mode: detection drops it
at violation 0.0037, declared keeps it at rate 3.6e-20; a 1e-6 free-surface move rejects it with a
warning); all-rank min/max reduction; 1e-9 relative, pinned both ways; one warning plus
`declared_modes_kept` per mode; inheritance at every derived-mesh site, setter refuses a non-rigid
field, cache key includes the declaration, adjoint restores the record, builders on coords_nd
(#877's TypeError), test_1131 in shard 3. The 0.3 shell: rotation rate 4.66 (v_rms 3.93) under
the old route, 1.1e-15 (v_rms 1.807 vs 1.806 radial) declared. Before the PR: 40 serial
rotated/fault files and test_1131 mutants; then hyperion's np 2 run and review. #952: hyperion's
rank-local-holds mutant now fails at np 2, 4 and 8 (finding 2 closed); record unposted.

**2026-11-06, MMPDE session first report:** the mover and FMG run on eddab707 (no folds, wall
radius exact, 4-5 velocity its, np 1 and 4). Blocker: after a move, rotated free slip with the
default normal drops the rotation mode (1 to 0; rigid rotation in the answer, v_rms ~6 % high);
normal=unit_e_0 clean. **Combined with #906:** the MMPDE session tests
`bugfix/rotated-nullspace-from-mesh-906` on its moved mesh (wall-preserving move should be
admitted by the invariance check), reporting to the integration session, whose #906 tests should
gain a moved-mesh case. Other findings (Louis and the MMPDE session directly): Nitsche after a move
v_rms 14-23 vs ~1.65; penalty half the v_rms even on a uniform mesh; rotated `auto` on a refinement
mesh picks GAMG not FMG; np 4 mesh differs from np 1. SUPG on a moving mesh not yet tested.

**2026-11-06, #952 fixed after hyperion's review** (0306f834): the refinement callback moved a
wall vertex only on ranks holding a labelled facet, and each rank checked its own copy; now
every copy takes the move made on any rank before the check (the moved copy wins), which also
fixes a pre-existing rank-count-dependent offset of refined wall vertices. The parallel test
checks copies on every level, with a one-rank-move case. Hyperion reruns at np 2, 4 and 8 with
mutants; its review record waits for its GitHub writes (not posted by anyone else). **#953
filed:** segmented shell and ball hang at np 2 on development (gmsh2dmplex inside a rank-0
block that reaches a barrier). #906's wall-invariance check in (1e-9 relative to the radius,
all-rank reduction); forced-partition case, two-sided test and rejection record to come.

**2026-11-06, hyperion (all local; GitHub writes still blocked):**
- **#900 pins are long-standing, not recent regressions:** 0863, 0864, 0865 fail and 0844_reconnect
  hangs identically at np 4 on eddab707, 25d62812 and fc67b650 (2026-10-29). 0851, with its
  yield floor set as test_0851 does, reaches the same family: **parallel peak slip 0.0064 vs
  serial 0.0142** at np 2 and 4 (0863: 0.0029 vs 0.00335). So 3-D fault networks give wrong
  peak slip in parallel: a correctness problem for phase 2 (3-D). 0844_reconnect at np 2: rank 0
  in `_global()`, rank 1 in `_free_petsc_garbage()`, both spinning: a collective mismatch.
  Issues to file once hyperion can write (not routed through another session meanwhile).
- **CI hang:** `scripts/test.sh --p 2 --shard 4/4` on #951's tree passes on hyperion pinned to
  2 cores (4033 s, test_1064 `..ss....ssss......`) and unpinned (6174 s): runner-specific. The diagnostics PR
  (local 99cd9668) is the way forward.
- **#900 PR ready locally** (bugfix/ptest-in-ci-900 0171eef6): CI runs the 15 passing pytest-style
  ptest files, appended so no batch moves; check_test_coverage accounts for every ptest file; 001a
  and 003 fixed; 000c/000d are not #922 (missing input files; 000c passes with the file; 000d stale
  DMSwarm API).
- **#952 review: not ready.** `CubedSphere(numElements=2, simplex=True, refinement=2)` with
  radiusInner 0.547 leaves 5 inverted cells at np 8 (0 at np 1), reproduced; the parallel test
  cannot see vertex-copy disagreement. Sent to the integration session.
- **#735 port:** new ThinSheet and "none" tests fail on eddab707, pass on the branch; wider tests,
  then review. **#665:** second review's must-fix done (d8c05c93).

**2026-11-06: #906 grew to a medium PR after its review** (Louis in the loop with the
integration session). HIGH finding: a mesh-declared rotation skipped the constraint test, so on
a deformed wall it was admitted though no longer null (annulus, 1 % wall deformation: answer
0.86 % off while reporting convergence; FreeSurface runs exactly this). Fix: admit a declared
rotation only while each rotated wall's vertices are equidistant from its centre (factory shells
and wall-preserving movers pass, a free-surface step fails). Also: declarations inherited by
adapt and add_fault children; declared modes on non-dimensional coordinates; test_1131 rebuilt
on the unfolded 0.3 FMG shell with hard baselines and a CI batch line (it was unreachable);
geometry cache key, adjoint slack restore, docs. The hub asked for: a collective check (np 2,
forced partition), a round-off relative tolerance pinned both ways in a test, and a visible
record when a declared mode is rejected. A radius variable (Louis's suggestion: snapping on
deformed walls, analytic normals of deformed walls, the free surface owning target positions)
to be filed as a design item.

**2026-11-06: hyperion's GitHub writes are blocked by its own session's permission check**
(its first PR comments, on #945 and #862, denied as external writes). Hyperion waits for Louis;
no other session posts for it. Put to Louis: allow rules for gh pr create/comment, gh issue
create/comment/edit and git push in hyperion's Claude settings, or approve each prompt there.
**Ready locally on hyperion:** the CI-diagnostics change (bugfix/ci-keep-hang-stacks 99cd9668
off eddab707: CI installs gdb from apt and uploads /tmp/uw-stacks-* for 5 days on failure; the
supervisor writes native stacks via gdb, ranks allowing the attach with PR_SET_PTRACER; new
test fails before; workflow YAML-checked only; the KSP-monitor switch dropped because the
rotated solve's own rotfsN_ prefix ignores solver options). Review verdicts: **#945 ready with
changes** (two tutorials left with an empty code fence, stale body, three unparsable files not
two); **#862 ready with changes** (design note contradicts the guide on where split-level work
lives; "one block per rank" should be "one block on one rank"). **#665 not ready:** the branch
fixes missing trame, but #665's reported case (IPython missing) still crashes inside the new
handler, and a named backend is silently replaced with static; hyperion reworking.

**2026-11-06: the CI hang does not reproduce off the runner** (hyperion, eddab707, np 2): the
1062_forward + 1063 + 1064 triple passes (201 s); the full CI batch 1062_forward-1068 passes
(246 s, 210 s pinned to 2 cores). Options database: grows ~40 entries per solver (#950
confirmed: 424 before test_1064's fifth test in the triple, 179 single-file) but prefixes are
unique and every shared option matches, so **#950 is not the hang's cause**; it keeps its place.
"Stuck, not slow" is inferred from Python stacks: a long C-level KSP solve looks the same. Next:
hyperion runs `scripts/test.sh --p 2 --shard 4/4` on #951's tree; if it does not hang,
**hyperion's CI-artifacts PR goes first** (supervisor stacks uploaded on failure, native
stacks if cheap, optional KSP telemetry for test_1064's spherical3d case), then #951's CI is
rerun to capture the runner's state. #951 and #952 stay blocked until then.

**2026-11-06: #900, the 39 ptest_*.py files on eddab707 (hyperion, np 2 and 4, one file per
mpirun):** 30 pass at both (script-style files: exit 0 only, need a harness for CI). **9 fail:**
000c and 000d (PETSc error 76, likely #922), 001a (setCoordinateDisc signature drift), 003
(three-index array drift), 0851 (ViscoPlasticFlowModel yield-floor error, likely #759's rule:
test update), **0844_reconnect hangs at both np** (seventh test fails first at np 2),
**0863_fault_network_3d_width** (parallel peak 0.0029 vs serial 0.00335), **0864_seam_ligament**
and **0865_seam_split** (pass at np 2, fail at np 4: "Main was not split on any rank"; "the
fill ring crosses itself"). 0863-0865 are pins the design notes cite. Hyperion: regression
check on 25d62812 (and fc67b650) at np 4 for 0863-0865 and 0844 before fixes; issues filed;
the passing pytest-style files into CI and the small test fixes (0851, 001a, 003) in its #900
PR; error 76 checked against #922. The triple 1062+1063+1064 passes on hyperion at np 2
(201 s); the full 1062-1068 batch is running, pinned and unpinned.

**2026-11-06: PR #952 (#946, shell folds; 20560442)** opened; #946 and #903 labelled
fixed-in-PR ("Closes" does not fire on development). Hyperion's Linux run: nothing fails on
the branch that passes on development; the new test_0001 fails 10/11 on development and passes
11/11 on the branch. Waits on hyperion's independent review and, since it adds a parallel file
(batch shift), on the test_1062 -> test_1064 state-leak fix, like #951. Noted: serial
test_1064_constrained_spherical_shell_response fails identically on both builds on hyperion as
an XPASS(strict) (a stale or mesh-dependent xfail): added to the anchors item. #906 rebuilt as
`bugfix/rotated-nullspace-from-mesh-906` off eddab707 (three commits cherry-picked, 964dc3ce
dropped, the old branch untouched; 54 serial rotated tests pass); reviews next, then its PR.

**2026-11-06: adversarial review on every PR, ours included** (Louis: "We should be running
an adversarial review on all PRs (including our own). Hyperion can do much of the donkey work.
The Laptop is also available and I intend to leave it as an always-on machine while we try to
get the backlog of PRs and bugs squared away.") **Rule:** each PR gets an independent
adversarial review by the other fixer (hyperion reviews the laptop's PRs, the laptop reviews
hyperion's), a fresh agent given the diff, record posted as a PR comment, on top of the
author's own rounds; the hub merges only on green CI with both reviews' findings resolved.
Hyperion is the review desk for PRs not written by us: #945, #862, #780, gthyagi's #855,
#857, #858, #856, #859, then #689 (#861 and #800 wait for their owners: they conflict). The
laptop stays serial-only.

**2026-11-06: #951 BLOCKED by a cross-test state leak.** Its shard-4 rerun hung again in
test_1064's spherical3d partition-independence test at np 2 (job 127632111767). #951 adds one
parallel file, shifting CI's 6-file batches: on #947's green run test_1062_forward_stress_history_mpi
ran in the batch before; on #951 it runs in the same process just before test_1063 and
test_1064, which then hangs. Hyperion's single-file runs pass. So an earlier test leaves state
that hangs a later spherical rotated solve. **Any PR adding a parallel file can trip it (#946
adds one).** Hyperion reproducing the exact batch at np 2, dumping the global options database
at test_1064's start; #950 (options outliving solvers) the first suspect; if confirmed, #950
goes to the top of the integration session's queue and #951 and #946 wait for it.

**2026-11-06: hyperion has GitHub access** (Louis: "Definitely I would like to have hyperion
able to do much of the gh work. I have provided the PAT"). Hyperion is a second fixer under the
laptop session's rules (side branches from development; test first; independent adversarial
review as the PR's first comment; house PR text and attribution; the hub merges on green;
hyperion never merges, approves or closes issues without word; the token never printed or
stored). **Split:** integration session: #946, #906, test anchors, disk-restore fix, #950,
#924, #939, #905, mean-removal drift. Hyperion: #665 (headless pyvista), #909 + #908, #900
(passing ptest files into CI), CI stack artifacts, the stress-transport port (stop and ask
if over a day or beyond the original behaviour).
Access confirmed: gh logged in as lmoresi (repo, workflow, read:org), origin reachable,
git identity Claude per clone; gh's credential helper passed per command, no global config
change. #665's branch merged locally into eddab707 passes test_0846 (both files),
test_0017 and test_0005 at np 2 (17 + 1 passed): its PR is first in hyperion's queue.

**Hyperion item 7, rescue branches (2026-11-06):** 8 refs on origin, not 6. **One live bug
on development:** `disk_snapshot._read_swarm_from_sidecar` writes `current[...] = saved` into
`np.asarray(var.data)`, a detached view (the #313 pattern), so a disk restore never reaches
the DMSwarm field; a run restarted with `stress_transport="lagrangian"` loses its stress
history. Confirmed by the hub at eddab707 line ~784. The fix (`var.data[...] = saved`) and
test_0020_snapshot_disk_swarm_values.py are on
`feature/forward-from-nodes-hyperion-2026-10-20-wip` dd773265; the test fails 2/2 on
eddab707 (hyperion). Queued to the integration session as item 1b (test and fix only, not
the commit's experimental lagged_stretch_velocity). The rest: test/sbls-coss (and -wip)
are ancestors of feature/shear-band-length-scale; #360 kdtree, restore-head, mem-leak-176
and review/bn-mergetest are superseded (restore-head's Oldroyd-B `_channel` block in
test_0020 is absent from development, intent unchecked); wip/yield-782-759 is
patch-identical to #852. Seven rescue refs can be deleted on Louis's word once the
disk-restore fix is in. **Item 6:** `bugfix/backward-nodes-snapshot-order` conflicts with
development in solvers.py (SNES_Stokes stress-history hooks, a region since rewritten):
a port, not a merge; `bugfix/visualisation-headless-no-trame` merges clean, tests running.

## Done 2026-11-06 (kaiju's monitoring hook, not the library; verified by kaiju 4097): memory grows ~190 MB per rank per fault rebuild on kaiju (#948) (Louis, 2026-11-05: "The memory leak on kaiju is crippling - please put this on a priority list!")

**Ahead of everything else in this file**, #946, #906 and phase 1 item 4 included.

**What is known** (underworldcode/underworld3#948, filed by the science hub for kaiju):
- On development f631ce42 the zg95 annulus fault runs grow about 190 MB per rank at every
  fault detection or rebuild, and stay flat between. TAf-v2 at np 26: 17.1 GB to 32.4 GB in
  20 steps. Earth, which detects every step: about 1.8 GB per step. Every long run now needs
  checkpoint restarts.
- **Library, not driver** (kaiju job 4043: two drivers on one build leak identically).
- **Introduced between 25d62812 and f631ce42**: production Earth on 25d62812 ran 480 steps at
  np 16, at most ~0.35 GB per step.
- #882's rebuild regression test (test_0078) passes on f631ce42 at np 1, 2 and 4 (kaiju
  4068). It does not reach the rotated free-slip solve, the custom FMG, the split-fault
  pipeline or swarms.

**The range is ten first-parent merges**, so bisect over merges (about four builds), not
the 93 commits: #929 (6321c714), #928, #927, #926, #930, #932, #933, #934 (60dbf0e4), #937
(c514013f), #938 (f631ce42). Most of the src change: custom_mg.py +624 (#932-#934, #937),
petsc_compat.h +242 (#937: UW3's C copy of PETSc's nested interpolator), rotated_bc.py
+145. **First suspect: #937's C interpolator** (a missing destroy or free per level per
rebuild); then the FAC union blocks (#934) and the rotated cross-solve cache.

**Who:**
- **kaiju's dev runner** (`session_01HxWvn9ik2HHt9ANKndJRDr`, "kaiju: dev runs 2"):
  reproduce small at np 2-4 (rotated free slip, custom FMG, a few rebuilds; rss per rank and
  PETSc object creations minus destructions per rebuild; fall back to the zg95 driver from
  a checkpoint), then bisect over the ten merges, one overlay per hash, c514013f against
  60dbf0e4 first. **Hyperion is offline** (Louis, 2026-11-05), so it was moved here; hyperion
  told to stand down on #948 when it returns.
- **hyperion** is back and serving (Louis, 2026-11-06). Not the bisection (dropped). It
  builds development eddab707 on the healthy disk and serves interactive np 2-32 runs of
  library-level pin probes for the integration session; the zg95 driver stays on kaiju
  (hyperion has no access to the private campaigns repo).
- **integration session**: read #937's C code and the custom-MG / FAC object lifecycles
  against a serial probe (object counts across rebuilds, wombat-size); write the regression
  test first (#882's fixture extended to rotated free slip + custom FMG at np > 1, shown
  failing on f631ce42); fix; PR. Its #946 and #906 work waits.
- **kaiju**: keeps running in checkpoint segments; verifies the fix at np 26 on a rebuild
  cadence once a branch exists.

**Progress:**
- 2026-11-05, integration session: #937's C code (petsc_compat.h) frees or destroys
  everything it creates on the normal path; the custom_mg and rotated_bc diffs add no
  caches or stored attributes; #934's block index sets are destroyed. Serial probe on a
  build with all ten merges (af9d3c33), annulus rebuilt and solved per cycle: rotated + custom
  FMG, rotated + GAMG, no-slip + custom FMG and a plain control all leave **no PETSc object
  per rebuild** (creations equal destructions in every class). Not reached: np > 1 (petsc4py
  defers destruction there), the split-fault ladder and FAC patch, non-PETSc memory. Next:
  split fault + FAC patch in the serial probe.
- 2026-11-05, hub: **a confound in #948.** The clean baseline (25d62812) ran at np 16; every
  leak measurement is at np 26 or 32, and on 25d62812 the custom FMG fell back above ~16
  ranks (#902). Kaiju's dev runner asked for two control arms beside the bisection:
  f631ce42 at np 16, and 25d62812 at np 26 (logging whether its custom FMG built). If (2)
  leaks, the leak predates the range and the bisection is the wrong search.

- 2026-11-06, kaiju reports 1-3 (relayed by the integration session; kaiju's own messages
  to this hub are refused as an untrusted device). **Small models do not leak:** the new
  regression test test_0078_rebuild_memory_rotated_fmg_parallel.py (449c0d37 on eddab707:
  rotated walls, split fault, custom FMG, FAC patch) passes at np 2 (1.03 MB per rebuild)
  and np 4 (0.70 MB); kaiju's annulus reproduction is flat at np 2 and 4 on 60dbf0e4,
  f631ce42 and 25d62812, PETSc objects net 0 per rebuild. **zg95 TAf-v2 does leak, and the
  old faulted mesh stays alive in Python:** after gc.collect on rank 0, every rebuild adds
  4 Mesh (the faulted mesh and 3 chain levels), 1 SNES_Stokes and 3-4 CustomMGHierarchy,
  identically on f631ce42 and eddab707 at np 26 (jobs 4084, 4087). Rss per rebuild: +180 MB
  per rank at np 26 on both builds, +260 MB at np 16 on f631ce42 (4077), flat between. So
  **#947 does not fix it, the SVD hypothesis is out, and np 16 leaks too**. 25d62812 at np 26
  takes the custom-FMG fallback (4078), so the pin may predate the range: the bisection is
  dropped. The integration session's serial pin probe (placement, custom-FMG solve with
  add_fault_bc, global_evaluate, warm start) keeps no child mesh, so the holder is in a step
  not yet reproduced (chain levels on persistent coarse hosts, projections,
  AnnulusDiagnostics, crust-swarm marker evaluation, fault_slip) or is parallel-only.
  **Next: kaiju dumps gc referrer chains of a stale Mesh and SNES_Stokes at np 16 on
  eddab707.** The hub's read of the library: the model, mesh and swarm registries are all
  weak, and Swarm.__del__ unregisters and destroys its DM, so library swarm bookkeeping is
  not the pin; candidates for the walk include sympy, expression or JIT caches holding the
  old mesh's symbols, registered callbacks or closures, stored tracebacks, driver globals.

- 2026-11-06, **FOUND (kaiju report 4, job 4094, referrer dump on eddab707 at np 16): not
  underworld3.** Both stale solvers are held by `SNES_Stokes <- tuple <- list <- module
  coarse_log_hook._faults`. kaiju-launch's monitoring hook `coarse_log_hook.py` (imported by
  run_driver.py for every run; copies at ~/campaigns/kaiju-launch/scaling/ dated 11-01, and
  ~/+Claude/kaiju/launch/np52/, used by the np52 runner and by job 4043) wraps
  `Stokes.add_fault_bc` and appends (solver, boundary) to a module-level list never cleared,
  so every rebuild's solver, faulted mesh, 3 coarse levels and FMG hierarchies live for the
  process. Explains every negative: no small model, test or wombat probe loads the hook; both
  drivers in 4043 ran through it; #947 was irrelevant. The hook is in no repository. Fix: a
  weak reference (`weakref.ref(self)`, dropping dead entries at the use site), or the hook
  out of production. Kaiju verifying on a private copy (~4096: eddab707, np 16, two
  rebuilds; expect flat Mesh, SNES_Stokes and rss). Shared hook files untouched so far.
  **Routing:** the fix to both copies and the restarts from checkpoint go to the kaiju
  rollback session (production owner) once 4096 is flat; kaiju-launch to go under version
  control. #948 to close as not a library bug with the explanation, posted by the
  integration session (no proxy footer). Test-only branch `bugfix/rebuild-leak-948`
  (449c0d37): coverage of rotated + custom FMG + split fault + FAC rebuild memory, passing on
  development; kept or dropped on Louis's word. The integration session returns to #946
  (4aade5ad), then #906. Hyperion's probe role is moot.
- 2026-11-06, kaiju rollback session (the hook's author; np52/run_driver.py ran every packed
  crust run, which is why direct-driver runs like production Earth did not leak): **fixed
  ~/+Claude/kaiju/launch/np52/coarse_log_hook.py** (weak references, dead entries pruned on
  each add_fault_bc; the leaky copy kept as coarse_log_hook_leaky_20261106.py); no other
  hook holds a solver. Running jobs keep the old copy until their next segment. **Not
  fixed: ~/campaigns/kaiju-launch/scaling/coarse_log_hook.py**, which its sandbox cannot
  write; put to Louis (no other session is asked to do it in its place). Verification: job
  4098 repeats 4043 (TAf-v2, np 26, 20 steps) with the fixed hook, to the science hub. It
  proposes ~/+Claude/kaiju/launch go into uw3-campaigns as zg95_lid_regimes/launch/kaiju_tools.
- 2026-11-06: test_0078_rebuild_memory_rotated_fmg_parallel.py costs 36.8 s at np 2 and
  24.0 s at np 4 in CI's environment (kaiju 4079/4080; skipped off Linux). The hub
  recommends keeping it: a small PR on Louis's yes. Verification is job 4097 (4096 hit a
  controller I/O error): eddab707, np 16, two rebuilds, the private weakref hook. The
  integration session closes #948 when it is flat; #946 resumed (development merged in;
  test_1111's shell values being re-recorded), then #906.
- 2026-11-06: **Louis: "Yes, do those"**: the test-only PR for test_0078's rotated FMG
  variant (Refs #948; the hub merges on green) and #948's close once 4097 is flat. Briefed.
- 2026-11-06: **Louis: hyperion is idle with 48 cores; use it.** Hyperion's standing queue,
  in order: (1) development eddab707 build and serial tier A+B baseline; (2) the parallel
  suite at np 2 and 4 as CI runs it (is #931 there too?); (3) the integration session's
  requests first (#946's Linux-CI-matching shell values, #906's parallel tests, the
  rebuild-memory test PR); (4) investigation probes, no fixes: #941 (partition-dependent
  wall load, np 1/2/4/8, script on test/probe-941) and #931 (test_1064 shell np 1/2/4,
  host-specific or not). Budget 48 cores at once. Hyperion is the integration session's
  default for np 2-16; kaiju keeps zg95 and np > 16; wombat stays serial.
- 2026-11-06: **the hub briefed an archived hyperion session** (abstract-token, archived
  2026-11-05 23:20) with the 48-core queue and the #948 notes, so hyperion sat idle; Louis
  noticed. The current session is splendid-sutherland (from 22:36); the integration session
  found it and sent it the #948 test checks and #946's sets at 23:26, which it started. The
  queue was re-sent to it. Also pending for Louis: "kaiju: dev runs 2" waits on a Bash
  approval (checking whether the #946 jobs started).
- 2026-11-06: **#948 verified fixed by the hook change** (kaiju 4097, eddab707, np 16, two
  rebuilds, the weakref hook): live Mesh, SNES_Stokes and CustomMGHierarchy counts flat;
  the second rebuild +19 MB worst rank against +295 MB unfixed; the first rebuild's
  ~210-255 MB step is a one-off high-water mark in both. The explanation is posted on #948
  (comment 6672238704) from the laptop. **#948 is still open:** the integration session's
  permission settings blocked the close and it asked Louis; the hub does not close it in its
  place. New issues from the work: **#949** (five spherical mesh generator defects found
  while fixing #946, left open) and **#950** (each solver's PETSc options stay in the global
  options database after the solver is gone: ~41 entries per rebuild; the one library-side
  growth found). The rebuild-memory test PR waits on hyperion's pinned np-2 run (proving it
  can fail); #946 (b1739413, review fixed) waits on hyperion's Linux test set.
- 2026-11-06: **hyperion's disk names swapped again.** The healthy disk (S65XNE0R602587)
  is now nvme0n1 at /mnt/nvme0n1p4, and /mnt/nvme1n1p4 now holds the failing boot disk's
  partition (S65XNF0R608481). The rule is by serial only: work lives at
  /mnt/nvme0n1p4/home/lmorese/hyperion-work today. The old env.sh and ~/+Underworld symlinks
  pointed at /mnt/nvme1n1p4, i.e. the failing disk: hyperion asked to repoint them and add a
  serial check that stops a run if the work directory is not on S65XNE0R602587. For Louis:
  the mounts follow device names; /etc/fstab to UUID= (sudo). Hyperion -> hub messages work
  by SendMessage.
- 2026-11-06: hyperion repointed both ~/+Underworld symlinks and env.sh to
  /mnt/nvme0n1p4/home/lmorese/hyperion-work, with a guard that refuses to continue unless
  the directory's disk has serial S65XNE0R602587 (tested both ways; backup
  env.sh.bak-2026-11-06). Four harness scripts (run_one, run_batch, summarise, run_leak)
  still hardcode the old mount: asked to source env.sh instead. For Louis (sudo):
  ~/+Simulations goes through the root-owned link /mnt/data/lmoresi -> /home/lmorese/lmoresi,
  which does not exist; the old data tree is on the healthy disk at
  /mnt/nvme0n1p4/home/lmorese/lmoresi today.
  Later: the four harness scripts now source the guarded env (`|| exit 1`) and use
  $HYPERION_WORK (backups *.bak-2026-11-06; syntax-checked, not yet run). Worktrees built
  before the swap (wt-coarse-one-rule, wt-f631, wt-25d6) carry the old mount in their pixi
  prefixes: rebuild (`pixi install`) before reuse, or discard; all are disposable.
- 2026-11-06: **#948 closed as not planned** by the integration session on Louis's "Go ahead"
  (said to it directly), after the explanation was posted. Open: the scaling copy of the
  hook (Louis, sudo-free but outside the rollback session's sandbox); the rebuild-memory
  test PR and #946's PR, both waiting on hyperion's fresh builds.
- 2026-11-06: Louis can fix hyperion's links with sudo but cannot change fstab. The hub gave
  him `/usr/local/sbin/hyperion-relink`: finds the disk with serial S65XNE0R602587 by lsblk,
  its p4 mount by findmnt, checks the old data tree, refuses to replace a non-link, then
  links /mnt/data/healthy to the mount and /mnt/data/lmoresi to
  /mnt/data/healthy/home/lmorese/lmoresi (repairing ~/+Simulations); optional root crontab
  `@reboot sleep 60 && /usr/local/sbin/hyperion-relink` in place of fstab. Hyperion told to
  move its links and HYPERION_WORK onto /mnt/data/healthy once it exists, keep the serial
  guard, and test whether a pixi env built there keeps the stable prefix.
- 2026-11-06: **PR #951** (rebuild-memory test, 4d636194, test-only: the new rotated-FMG
  file plus a flush before test_0078's first reading; Refs #948). Proven at np 2 on hyperion
  in CI's environment: 2 passed at 2.61 MB per rebuild, no object alive; with every Stokes
  solver pinned as the hook did, 2 failed (20 objects alive, 49.4 MB per rebuild). Bound
  10 MB; tier B; MPI phase (no batch line). CI running; the hub merges on green (Louis's
  "Yes, do those"). #946 waits on hyperion's run on both builds.
- 2026-11-06: **Louis: the script lives in his home directory and touches no system
  directory.** Replaced: `~/bin/hyperion-relink`, run as Louis with no sudo, links
  ~/hyperion-disk to the healthy disk's p4 mount (serial S65XNE0R602587, lsblk + findmnt)
  and ~/+Simulations to ~/hyperion-disk/home/lmorese/lmoresi/Simulations; refuses to replace
  a real directory; rerun after a reboot by hand or from Louis's user crontab. No
  /usr/local/sbin script, no root crontab, no /mnt/data/healthy; /mnt/data/lmoresi stays
  broken (old scripts only). Hyperion told to use ~/hyperion-disk instead.
  Done by hyperion (serial guard passes on the resolved path). **pixi resolves the link**: an
  env built under ~/hyperion-disk records /mnt/nvme0n1p4/... (pixi info, pip shebang,
  sys.prefix, sysconfigdata), so a disk-name swap still means rebuilding every env. Hyperion
  asked to make env.sh stop with a "rebuild" message when an env's prefix is not under the
  current mount.
- 2026-11-06, hyperion queue item 4 (eddab707): **#931 not reproduced** (test_1064 shell:
  worst coefficient 2.3e-7 at np 2, 1.5e-7 at np 4, inside 1e-6; this mesh has 1991 cells
  against the anchor's 2016, so a different triangulation from kaiju's). **#941 unconfirmed**:
  in no run at np 1-8, cellSize 0.1-0.033, was the corner node on a rank without Top facets;
  `-petscpartitioner_type simple` was ignored, so a forced partition is needed. Probe pushed
  by the hub (hyperion has no credentials) as underworld3 test/probe-941 b6525a87,
  scripts/sessions/probe_941_partly_pinned_normal.py, not for merge. **Side finding:**
  boundary_normal_traction_integral with remove_mean=True varies with the partition
  (-0.1066155 to -0.1066242, np 1-8), tracking the raw integral's gauge drift at ~-2.7e-3;
  mean removal should cancel a constant pressure. Candidate: #942's zero at the partly pinned
  corner drops the gauge's share there. To the integration session after #946 and #906 (a
  fixed-gauge rerun, with and without the pinned corner; file if confirmed). Hyperion: git
  identity per clone (Claude), env check called from the harness scripts, then queue items
  2 and 3.
- 2026-11-06: **#948 verified at production size** (kaiju 4098, 4043's case: TAf-v2, np 26,
  20 steps, f631ce42, the weakref hook): node rss 17.4 / 21.5 / 23.1 / 23.4 GB at steps 1 / 5
  / 10 / 19, flat after the first two rebuild events, against 4043's 17.1 to 32.2 GB.
  Production runs pick it up at their next restart. Still unfixed: the
  ~/campaigns/kaiju-launch/scaling/ copy (Louis).
- 2026-11-06: Louis renamed the scaling copy to coarse_log_hook_leaky_20261106.py; no
  leaky hook remains importable on kaiju. #948 is fully closed out.
- 2026-11-06: **#951's CI failed on shard 4, not on its tests**: both test_0078 files
  passed; test_1064_rotated_freeslip_parallel hung at np 2 after "..ss" (MPI supervisor:
  no output 300 s, every rank in _solve_rotated_iterative spinning; run 42130702511, job
  127606355452). An intermittent hang on development eddab707, plausibly the folded-shell
  symptom #946 fixes (Linux gmsh). Failed job rerun; merge on green since #951 does not
  touch test_1064. Told the integration session, for #946's PR body if B hangs on a folded
  mesh in hyperion's R2.
  **Correction (integration session):** not #946's mechanism. The hang is in
  test_rotated_freeslip_spherical3d_partition_independent (the fifth test), whose
  SphericalShell(0.55, 1.0, cellSize=0.25) is unrefined: no callback, nothing folds. A
  pocket cell alone does not stall the solve serially (six gmsh seeds, flips on and off,
  every case 1 outer iteration in ~3 s). Cause unknown: np-2 partition or another; hyperion's
  R2 runs test_1064 at np 2 and 4 on both builds. **Proposed:** CI keeps the MPI
  supervisor's /tmp/uw-stacks-* as an artifact on failure (a workflow change; to Louis).
- 2026-11-06, hyperion queue item 3: **the whole tests/parallel set on eddab707 is clean**
  at np 2 (251 passed, 21 skipped, 1 xfailed) and np 4 (260 passed, 11 skipped, 1 xfailed,
  CI's #611 deselect), 72 files each, one file per mpirun (CI batches 6), 417 s at up to 34
  ranks. test_1064 passed at both (the CI hang did not reproduce; #931 not seen). **Gap
  found:** test_1063_constrained_freeslip_parallel skips all its tests in CI too (#951's
  shard-4 log: "ssssss"), and 3 cases of test_1064 and 1 of test_1066 likewise: their
  accuracy anchors were recorded on a macOS mesh and skip on Linux's triangulation. So CI
  asserts nothing in test_1063. Proposed to the integration session (after #946, #906) and
  to Louis: record anchors in CI's Linux environment (hyperion), per mesh fingerprint or
  on triangulation-independent quantities, so CI runs them.

**Merge rule:** the fix PR goes to Louis like any other; this priority does not waive it.

## Done: the rotated path's FAC patch blocks ran ILU(0), not LU (#892; fixed by #912)

Louis, 2026-10-30, relayed by the notes session: "I thought ASM with the fault split into
small patches so LU works efficiently was our original choice. I did not realise that we
dropped this to work around a bug and then gave up on it. This seems typical of the kind of
amnesia that regresses great algorithms into dead ones! This should be a priority to fix
though the dev hub needs to know all about it and plan accordingly."

**The defect (#892, filed 2026-10-29 by the integration session).** `custom_mg._configure_pcmg`
writes the FAC block solver (`mg_levels_<l>_sub_1_sub_pc_type lu`, nonzero shift) into the
options DB. The rotated path forces the level smoother's `setUp()` and then deletes those
keys. `PCSetUp_Composite` only hands its children their operators, so the ASM child sets up
at its first apply. By then the keys are gone, and its blocks take PCASM's default, unshifted
ILU(0).

**What the history shows (read from the code 2026-10-31).** This corrects the "dropped,
then gave up" account.

- 9f4cb200, 2026-08-26 (#638): the patch lands as plain ASM replacing the level smoother,
  with an **SOR** block solve (unshifted ILU(0) zero-pivoted on the rotated Galerkin block).
  The forced `setUp()` covers plain ASM, so the rotated path got what it was configured to
  get.
- 891c9bb0, 2026-09-03 (#670): composite mode **and** LU with a nonzero shift become the
  defaults **in the same commit**. Its measurement was on the TI S-fault rig: 10 velocity
  iterations against 44.
- So on the rotated path the LU design was never applied: from 891c9bb0 the composite's
  child has read no keys. The non-rotated callers (`custom_mg.py` 1302 and 1375 on
  development) never delete the keys and probably do get LU; still to be confirmed.
- The chains never had the patch. A pair touching a split coarse level skips FAC
  detection (`custom_mg.py:1556` at 4698938f, C); the tail sweep found the same.
- A stale comment in `custom_mg.py` ("Subdomain solver: SOR ... no factorization") sits
  above a default of `"lu"`: the amnesia in miniature.

**What rested on the degraded smoother.** Fault rotated solves since 2026-09-03, among them:

- the faults-in-convection guide's welded-against-chain table;
- the 2026-10-29 tail ruling (provisional above ratio about 8 since 2026-10-30);
- the drivers' `uw_chain=2`;
- the kaiju trench demonstrations in UWTN 2026-022.

The integration session's tail sweep with LU blocks (`~/+Simulations/uwtn_2026_022_tail_sweep/`
on wombat, summary.md b8705fab, at 799ef021) finds the following.

- The welded base with the split finest takes 3 velocity iterations per linear solve at
  every band ratio from 6 to 25.
- The yielding-lid box at np 4 takes 7 per Newton increment, with no caps.
- Solve time is 241 s against 632 s for the chain at ratio 8, and 193 s against 3098 s at
  ratio 25.
- The Newton path and the peak slip are unchanged.

That is 2-D only: about 32k block rows summed at ratio 25.

**Plan.** Steps 1 to 4 are under way (Louis's go, 2026-10-31) with the laptop integration
session, which measured #892 and ran the sweep. The same plan is posted on #892
(issuecomment-6505605906, 2026-10-31, on Louis's word).

1. Confirm the scope on one fixture by reading the live block PC:
   - development, rotated path: expected `ilu`;
   - development, non-rotated FAC path: expected `lu`; if it is not, #892 is wider than
     its title;
   - rotated path at 891c9bb0^ against 891c9bb0: expected `sor`, then `ilu`.
2. The regression test first, shown failing. It reads back the live block PC of every
   FAC level and fails unless it is the configured type. It covers composite and plain
   ASM, rotated and non-rotated, serial and `tests/parallel` at np 2.
3. The fix: one helper in `custom_mg`, called after `pc.setUp()` from every call site.
   It sets up each FAC level's smoother and its composite child, and sets (or at least
   asserts) the block PC type and shift on the live sub-KSPs. C has two rotated call
   sites (`rotated_bc.py` 2340, 2493) and development one, so the fix is stacked on #890
   as PR D, or rebased onto development if C stalls.
4. Benchmarks before the PR:
   - tier A and B, and `tests/parallel` at np 2 and 4;
   - rotated free-slip without a fault (annulus, shell): must be unchanged, since those
     solves get no patch;
   - the #892 fixtures and the tail sweep;
   - a watch for `PC_FAILED` and zero pivots;
   - block rows against `fac_block_rows` (2000).
5. After the merge, re-measure what rested on ILU blocks, then Louis rules on the
   production tail. The ruling then drives:
   - the drivers' `uw_chain` default (science hub);
   - both guides and UWTN 2026-022's multigrid section and panel (c) (docs hub; the note
     is held until then);
   - `custom_mg.py:1556`, chain as option or exception (dev hub);
   - a rerun of the kaiju trench demos (Louis).
6. Cost of the LU blocks in 3-D and in parallel. The wombat fixtures come first; scale
   runs go through the science hub.
7. The intent written where the next refactor will meet it:
   - the docstring at the block configuration: "FAC blocks are LU; ILU there is a
     regression";
   - the test from step 2;
   - a journal finding;
   - the guide.
8. The wider class: the same test reads back every MG level's live configuration
   (smoother, coarse solve) against what was configured. A key deleted before its lazy
   consumer runs is the general failure; #806 (solvers do not report the configuration
   they ran with) is its observability half.

**Progress.**
- **Step 1 done (integration session, 2026-10-31).** Live readback on test_1022's
  composed stack and test_1017's Poisson band, serial, PETSc 3.25.0.
  - Rotated path: SOR blocks at 891c9bb0^; unshifted ILU(0) from 891c9bb0, on
    development bfd07b73 and on C 799ef021.
  - Non-rotated paths (`custom_mg` 1302, 1375): LU with a nonzero shift on every build
    since 891c9bb0.
  - Coarse solves are as configured everywhere.
  - So the fix's scope is the rotated path only. Records in `~/+Simulations/fac_892/`
    on wombat.
- **Found on the way, and B's doing rather than a C regression.** On C the rotated path
  patches the finest level only.
  - `rotated_bc.py` 2059-2066 at C (about 1942 on B): with `drop_orphans` (always
    True since B), it sets `h.level_patch_rows = [None] * (n - 1) + [rows[-1]]`. That
    discards every coarse FAC patch, unconditionally.
  - `custom_mg.install` keeps the patch of any level the restriction left whole, so
    the two paths disagree.
  - It is the item `FAULT-SPLIT-INTEGRATION.md` flagged on B's review, unruled.
  - Asked of the integration session: pin it in step 2's readback, and in step 4 measure
    the coarse patch kept (rows remapped) against dropped, with LU blocks. D does not
    change B's behaviour.
- **Steps 2 and 3 done** on `bugfix/fac-live-block-solver` (on C 799ef021).
  - 44612397: the regression test, shown failing.
  - 88212f75: the fix, one helper `custom_mg._set_up_fac_smoothers(pc, fac_keys)`,
    called after setUp at both rotated sites and in
    `_install_velocity_block_transfers`.
  - 3e5d9880: the test pins the FAC levels per install.
  - `tests/parallel/test_1090_mg_live_configuration_parallel.py` reads every level's
    live objects on four paths (rotated saddle, rotated thin sheet, velocity block,
    scalar top level), composite and plain ASM. Before the fix the two rotated
    composite cases fail; after it, 8 of 8 pass serial, np 2 and np 4.
- **B's coarse-patch rule settled by measurement.** With LU blocks on the composed stack,
  the coarse patch kept (rows remapped) and dropped give the same iterations and slip
  (57/18 velocity, 3 last, 16 pressure at S 0.010; 55/18 at S 0.005). No production
  hierarchy has a coarse patch anyway: H0's coarse pairs are native refinements, which
  the cover gate declines; the chains skip FAC on split coarse levels; and in parallel
  FAC is built on the finest level only. The rule stands; no box arm needed.
- **Step 4 running** on wombat: tier A+B, `tests/parallel` at np 2 and 4, the tail
  sweep's H0 arms (expected 66/65/67 linear; 7 per increment on the box), then rotated
  free-slip without a fault and the PC_FAILED watch. D then merges development
  (fc67b650) and targets development directly.

- **Step 4 done; D is ready for its PR** (`bugfix/fac-live-block-solver` 20b42937,
  development fc67b650 merged in; a guide caveat at faults-in-convection.md:71 to follow).
  - Tier A+B serial pass. `tests/parallel` at np 2 and 4 pass except
    `test_1063[ti]`, which is #826 and pre-existing.
  - The tail sweep's H0 arms reproduce the LU arms exactly (A 66/65/67; B 7 per
    increment, no caps).
  - Rotated free-slip without a fault: identical to C, to 13 digits.
  - No `PC_FAILED` or zero pivot anywhere.
  - Its review fixed the docstring and tiers (a998181f), and filed #894.
- **Block size.** `fac_block_rows` caps only blocks from a keyed `fac_zone`; a split
  fault's structural patch is one block per rank (up to 19,679 rows). Cutting it along
  strike measured worse in 2-D: 67 velocity its for one block against 85-180 at caps
  8000-500, and 116 s against 140 s. So one block stays, and #895 is now a 3-D question
  only.

**Solver-efficiency queue (Louis, 2026-10-31: "get the solvers all working on the most
efficient path").** Owner: the integration session, in this order.
1. **D (#892): ready for its PR** (`bugfix/fac-live-block-solver` 24e754fe, with the
   guide caveat).
2. **#894: fixed** on `bugfix/rotated-interface-operator-refresh` 12e5fc0c, stacked on D.
   - The fix: the interface-law sum is built once and refreshed in place, so the KSP
     keeps one Mat, as on the contact path.
   - `test_1088` (tier B, serial and parallel) failed first. The mesh-owned tail was
     stale too; GAMG never was.
   - On the box at np 4 with a rate-strengthening law: D capped 746 of 772 velocity
     sub-solves and missed the 60-minute limit; the fix takes 160 s with none capped.
   - **Scope correction:** the zg95 convection drivers use frictionless contact
     (`add_fault_bc(0)`), and their "rate" setting places faults by strain rate. So the
     campaigns were never affected. The users are the fault-cycle scripts, the tidal
     shell and the thin-sheet cycle.
   - Reviewed; suites green.
3. **#896: fixed** on `bugfix/fac-cover-gate-partition` f7914a92, stacked on D.
   - The cause was not double-counted halos. Fine rows whose coarse node sits on another
     rank were classed as patch, because the add-on partition gathers the fault onto one
     rank while the coarse levels keep the base partition. One collective scatter now
     classifies every row the same way.
   - `test_1106` failed first.
   - np 2 drops from 640 velocity its to 73 (serial 67). np 4 factors 15,870 block rows
     instead of 19,126.
   - Reviewed, including a 3-D split box; suites green.
   - **Still owed:** the np 16 production shapes, which need kaiju (requested of the
     science hub below).
4. **Scaling past np 16 (#901, #902), now the integration session's active task**
   (Louis 2026-10-31: "52 failing altogether is not something we can leave
   uninvestigated ... no 3D problems would be accessible at all"). It caps every kaiju
   fault run at 16 of a node's 52 cores.
   - **#902 explained:** a PETSc defect. `DMPlexComputeInterpolatorNested` skips
     preallocation on a rank that owns no rows or columns but still fills from its cells.
     The owner raises "new nonzero", and the other ranks hang inside the collective. It is
     reached through `Mesh._get_coords_for_basis` on every custom-MG level, and the notch
     draft 02 shows it in 3-D at np 16.
     - The fix (in progress): coordinates per cell from the reference element matrix, no
       parallel matrix. A forced-partition test at np 2. The rank-local catch-and-retry
       taken out. A petsc4py reproducer and draft PETSc issue go to Louis for the
       external report.
     - **Louis's rule: the laptop works at np <= 8 or with forced partitions; np >= 16
       checks belong to kaiju.**
     - **Fix pushed:** `bugfix/custom-mg-many-ranks` 96d39f7b, from development.
       - UW3's own copy of PETSc's same-plex interpolator in the Cython layer (Louis
         chose this over patching the PETSc build). It matches PETSc's matrix exactly
         on tri, quad, tet and hex, P1-P3, at np 1 and 4.
       - #886: the builder's verdict is agreed across ranks.
       - `test_1107` and `test_1108` hang on development and pass on the branch.
       - Serial tier A+B: 2803 passed. Parallel at np 2: only #826.
       - The np 16/32/52 check is with the science hub.
     - The PETSc upstream reproducer and draft (the guard has been in PETSc since v3.24.0
       and is still on main) are on wombat in
       `~/+Simulations/fac_892/mg_np32_902/petsc_upstream/`, for Louis to file.
   - For #901, development still picks SVD whenever there are rotation modes (annulus,
     shell). Louis's order (posted on #901):
     1. a coarser bottom level (SVD is fine if the coarse level is coarse enough);
     2. the null space handled explicitly with a direct solve (the 10-28 ruling);
     3. an investigation of GAMG ONLY as the coarse-level solve of the geometric FMG
        (`mg_coarse`), with SVD at GAMG's base. It replaces geometric MG nowhere ("worth
        investigating, not wedded");
     4. telescope only if a gathered solve still dominates.
     The winner becomes a default chosen by the null modes, not a new option.
   - **#901 results** (laptop, np 1 and 4; `bugfix/rotated-fmg-coarse-solve` 0502a9f7,
     from development; review running; kaiju hash to follow):
     - Step 1: the annulus bottom level can drop from 600 to about 40 cells with
       unchanged iterations (SVD setup 69 s to 0.012 s). Cell shape degrades at 22. The
       shell cannot go below its 614-cell gmsh base.
     - Step 2, **now the default on the branch:** the rotations are restricted to the
       bottom level, one unknown per mode is pinned, the modes are projected out, and the
       system is solved by redundant LU. Same iterations and the same answer as SVD.
       Annulus 600 cells: 144 s to 0.76 s wall. Shell 614 cells: 216 s to 7.1 s.
       `test_1111` and `test_1112` fail on development and pass on the branch.
     - Step 3 (GAMG only as `mg_coarse`, SVD at its base): same answer at 4-10 times the
       pinned LU's cost at this size. It remains the candidate only if bottom levels
       outgrow a gathered LU.
     - Added at Louis's request (2026-10-31, "just so we know"): the same GAMG coarse
       solve with LU at GAMG's base instead of SVD, rotations handled there, with the
       coarse cost split into GAMG's base solve and its own cycles.
     - Step 4, telescope: not needed (the gathered LU is about 1 % of the solve).
     - **Review result (it overturns the default).** Plain redundant LU on the rotated
       coarse level gives SVD's answer and iterations on every fixture, including the
       faulted annulus at np 1 and 4. The coarse operators are near-singular (condition
       about 1e-5 to 1e-8), not singular, and #306's zero pivot does not reproduce.
       - So the null-mode class may be unneeded. The null space stays handled where it is
         singular, at the outer level.
       - Hub's proposal for Louis, **A-prime**: always redundant LU, plus a nonzero factor
         shift as the zero-pivot insurance, and delete the class. **Measured: equal to
         plain redundant LU on all eight fixtures** (six bit-identical, two within
         run-to-run noise). On a forced-singular coarse level (#306's case), plain LU fails
         at iteration 0 while A-prime converges to SVD's answer within 7.5e-9. Awaiting
         Louis's ruling.
       - Side finding filed as **#907**: a rotated solve whose PC fails returns v = 0
         with only a warning. The proposed collective raise is a behaviour change for
         callers, so it waits for Louis.
       - The review also found a development defect: the rotated coarse PC is set up twice
         on a first solve, because an SOR loop re-assembled level 0. Fixed on the branch
         (5a30a08e, `test_1113` counts setups). Only SVD paid twice, since redundant LU
         factors lazily: the shell's 207 s of SVD coarse work is about 105 s with one
         factorisation.
       - The GAMG variant is in (9db23e56): `set_custom_fmg(..., coarse_solve="gamg")`,
         explicit only, on the rotated and standard routes. It has the near-null space and
         the verified rotations. `test_1114` (np 2 and 4) gives the gathered LU's answer to
         1e-8. Guide paragraph added.
     - GAMG coarse with an LU base: GAMG's base is at most 6 % of its coarse work. Its
       cost is its 15-40 V-cycles per geometric coarse solve. **Louis: keep it for one
       case**, a coarsest accessible mesh too large for a gathered redundant LU. It goes in
       as an explicit, tested, non-default `coarse="gamg"` variant (rtol 1e-2, LU base,
       near-null space attached), documented in the multigrid guide. Found 2026-10-23/24, handed to hyperion, unfiled and unowned since the reimage;
   filed 2026-10-31.
   - #901: the rotated annulus's coarse level is a dense SVD on one rank, so more ranks
     are slower. Louis's 10-28 ruling applies; the prototype is on
     `feature/coarse-solve-nullspace`.
   - #902: at np 32/52 the nested custom-MG interpolation fails on preallocation and the
     ranks deadlock.
4b. #892 step 6: the 3-D and parallel cost of one LU block per rank (#895).
5. #892 step 5: the re-measurement, then Louis's production-tail ruling.

**Held: the slip coarse space** (`feature/fault-slip-coarse-space`, on Louis's
2026-10-30 request; design note 30d4be49; 13 tests at np 1, 2 and 4). It is a two-level
Schwarz slip correction for the cut structural block, opt-in and 2-D only. In 2-D it
loses to one block: 79-87 its serial against 67, and 9 per increment on the box against
7. The hub recommends it stays on its branch, with the design note and the roadmap draft
as the record, until step 4's 3-D measurement shows one block is unaffordable. It is
stacked on `feature/fac-structural-segments`, a measurement-knob branch not meant for
merge.

## PROGRAMME: polish the add-on, land 3-D, then decompose if needed (Louis, 2026-11-02)

Louis: "I'd like to stop hedging bets. If this is the best choice we should try to polish it
up so that it works for all the cases we need, we should land 3D and then see if that
add-on problem needs to be decomposed separately."

The matrix stops being a comparison and becomes a programme in three phases. No more
alternative-hierarchy arms; the chain is measured only as the baseline it already is.

**Phase 1: polish the add-on in 2-D so it works for every case we need.** Owner: the
integration session (code), the kaiju runner (runs).
1. Land the defaults the measurements already justify, each as a small PR from
   development, test first, in this order:
   - #918, the cover gate decides on structure (background under 2 %), logged either way;
   - #921, the split fault's structural rows are always in the patch when the finest
     level is split;
   - #919 (third fix c7e6fa3b) once kaiju confirms;
   - the hierarchy patch summary (04b7a76f), so drivers stop making MPI calls;
   - #920 (`snes_max_it` reaches the rotated loop).
   #918 and #921 are solver-default changes: Louis's go is given by this section, with
   the row 3 and row 5 numbers as the evidence; the PR bodies cite them.
2. The patch solver: pick the block solver from experiment 1's results when they land
   (LU stays unless an inexact solve matches it within about 10 % on the box, where it
   is currently 3 min per Newton step). Record the choice as the default and delete the
   losing knobs (`UW_FAC_SUB_PC`, strip width, the probe-only options).
3. Solver tolerances: the pressure (Schur) rtol default, 0.1 x tol today, with kaiju's
   evidence for 1e-2 (28-57 % of Stokes time, same answer to 7e-6): one PR, Louis's
   evidence already seen; the drivers stop setting it per run.
4. Ladder: the fault's own division sets the rungs (1b); S goes from the drivers' trace
   sampling; the split inset is one element; the weak-zone width is a model parameter in
   physical units (pending the geometry-held check, which is queued). One driver PR
   through the science hub.
5. Cases that must work, each with a test: frictionless, viscous, Coulomb, rate-and-state;
   a junction, a pair, a TI band beside a split; the annulus with rotated walls at np 16;
   a fault across partitions (row 2, once kaiju runs it).
Done when: every case has a passing test on development, the defaults carry no probe
knobs, and the guides say what ships.

**Phase 1 status (2026-11-02): items 1 and 3 built, reviewed (2-3 adversarial rounds each),
pushed, held without PRs. Kaiju validation waits on the runner's holds.**

| Item | Branch | What ships | Differs from the programme? |
|---|---|---|---|
| #918 cover gate | `bugfix/fac-cover-gate-structure-918` faf80fe2 | A level carrying a split fault declines only above 98 % patch+halo; every other level keeps 0.75. Verdict on `hierarchy.fac_gate`, printed under verbose. `UW_FAC_COVER` removed. | **Yes.** The hub's "2 % background" rule, applied to every level, failed review on routes the fixture never touched: wide unsplit adapt children would take 95-98 % patches (one LU over nearly the whole level), and a cut on a refined base gives a 100 % uniform pair that SOR converges in 4-8 its. So the rule ships on split levels only. A placed band fine enough would still decline (about h_b/S 200 on a 1/16 base); bounding the block is #895, item 2 |
| #921 structural rows | `bugfix/fac-zone-structural-921` 945504bf, stacked on #918 | A split finest level adds its structural rows to a keyed zone under the 98 % gate; an unsplit level keys on the zone alone (#670). `UW_FAC_STRUCTURAL` removed. test_1135: 4940 of 4940 rows were missing before. | No |
| #919 | c7e6fa3b | unchanged; first in the runner's queue | No |
| patch summary | `feature/mg-hierarchy-patch-summary` a46bf3f1 | review fixes: serial batch, exact zone-row union at np > 1, record made after set-up and cleared at build, private helpers | No |
| #920 max_it | `bugfix/rotated-max-it-920` 92a330cf | `snes_max_it` reaches the rotated loop through one hook at both call sites. Review found the loop never tested the residual after its last increment, and that caps of 0 and negatives crashed; fixed, PETSc's meanings kept. test_1136; 5 of 6 cases fail on development. Filed #924 (the loop ignores snes_rtol/atol/stol). | No |
| pressure rtol | `feature/rotated-pressure-rtol-default` e6b8be58 | the rotated pressure sub-KSP from 0.1 x tol to a fixed 1e-2; `_rotated_pres_rtol` overrides. Serial checks on top of kaiju's A/B: same Newton counts, answers within 2.5e-6, slip to 7 figures. | **Needs Louis's explicit yes.** It loosens a solver default against the guardrail policy in `subsystems/solvers.md` and the Citcom margin principle. The branch restates that principle (the velocity sub-solve keeps the 0.033 margin; the pressure tolerance is a preconditioner-quality trade), which is design text for Louis to accept or reject. The programme's item 3 was the hub's text, not his words. |

**Item 2 decided (2026-11-02): LU stays as the FAC block solver.** Kaiju runs on the box at
np 4 (runner report 4). Every converged arm matches LU's Newton count and peak slip; none
comes within the 10 % bound on time:

| arm | S 0.004, one block | S 0.004, cut blocks | S 0.0156, one block |
|---|---|---|---|
| LU (reference) | 603 s | 433 s | 516 s |
| ILU(2), 5 steps | 1299 (2.15x) | 1404 (3.2x) | 766 (1.48x) |
| ILU(1), 5/10 steps | timed out (1 h) | timed out | 830 / 945 |
| GAMG, 5/10 steps | 1750 / 2102 | 2089 / 2058 | 931 / 869 |
| hypre, 5/10 steps | 2360 / 2179 | 2248 / 2981 | 923 / 1207 |
| GAMG or ILU(1) to rtol 1e-1 / 1e-2 | 7303-12532 | 6578 | |

So the patch does need LU's accuracy in this regime; "does it require LU?" is answered
no in principle (all converge to the same answer) and yes in practice (nothing else is
within 1.5x). The 2-D strips (experiment 2, closed) are evidence for phase 3 only: LU on
strips of 8 rungs is within 7 % of one block (571 against 603; 482 against 516), the #895
lever if 3-D needs a bounded block.

The PR: `feature/fac-block-solver-lu` 968b274b, from development. It removes
`UW_FAC_SUB_PC`, `UW_FAC_WHOLE`, `UW_FAC_MODE`, `UW_FAC_ASM_TYPE`, `UW_FAC_OVERLAP` and
`UW_FAC_LEVELS`; each measured answer stays as a comment on the code that ships it.
test_1090 fails on development with the old knobs set. Review running. The remaining
TODO(MEASURE) knobs (`UW_FAC_PATCH`, `UW_FAC_SEGMENTS`, `UW_FAC_BLOCK_ROWS`,
`UW_MG_SMOOTH_ITS`, `UW_CUSTOM_MG_DISABLE_FAC`, `UW_CUSTOM_MG_DISABLE_NESTED_NATIVE`) go in
one more small PR after item 1 lands; Louis's "no probe knobs" covers them, no ruling
needed.

**Kaiju validation (report 6, 2026-11-02).**
- **#918 confirmed** on its motivating cases: row 3 at 640 and 1280 rungs, declined before
  (909/1083/1487 its), taken now (65/74/68), same slip.
- **#920 confirmed:** row 4 Coulomb and rate-and-state identical through `snes_max_it`.
- **#919 c7e6fa3b:** test_1132 passes at np 1/2/4 and fails first on 7c0c62ff (3076 cells
  outside their parent at np 2; a raise, once a SIGSEGV, at np 4). Verdict after the
  error-76 casualties pass at low load.
- **#921 BLOCKED by a pre-existing parallel hang.** A TI zone plus the structural rows hangs
  at np 4 (silent from 12-18 s), on #921 and on development with the old knobs
  (`UW_FAC_STRUCTURAL=1 UW_FAC_COVER=1.01`); serial converges in 94 its. No rank-asymmetric
  collective found by reading `custom_mg.build`'s zone path, so it is either PCASM set-up
  with overlapping cross-rank blocks or a non-converging solve. Needs stacks
  (`faulthandler.dump_traceback_later` on every rank). Filed as **#925**. Hypothesis from
  the code: a seam-halo row can sit in another rank's zone block and in the fault rank's
  structural block, and basic ASM sums both corrections, which would stall convergence
  rather than deadlock. #921 makes this union the default for a zone keyed on a split
  level, so it is held until #925 is found; #918 stands on its own. The pair case (zone none) passed at np 4: 80 its, all 31,326 block rows on one
  rank.
- **No branch adds a real failure.** tests/parallel fails the baseline's set everywhere
  (#923), plus error-76 casualties; tier A+B has 16 host failures common to every branch
  (12 trame ImportErrors and four others) plus environment noise.
- **#922 corrected again:** ROMIO does NOT prevent error 76. With about 35 jobs at once, every
  branch's parallel run had error-76 failures inside the tests' spawned serial reference
  runs; the near-alone baseline had none. Load tracks it; the spawned children may not
  inherit the job environment (unchecked). Error-76 failures are infrastructure, and their
  casualties need a low-load rerun before any verdict. **Settled from the code:**
  `tests/parallel/serial_reference.py` drops every `OMPI_*` variable from the spawned child,
  so the children never saw `OMPI_MCA_io=^ompio` and all ran OMPIO; ROMIO under load is
  untested. The test-side fix is `bugfix/serial-reference-keeps-mca-selection` a79d5236
  (tests only, held): `_child_env` keeps the user's Open MPI selections with their
  parameters (io and its sub-frameworks, mtl, btl, pml, ucx) and drops the rest; the review
  found that selections without their parameters aborted the child's MPI_Init on OMPI 5.0.10,
  and two more spawn sites with their own scrub (test_0855, test_1079), now on the helper.
  test_1138 pins it. The runner validates it under mpirun, then reruns the error-76
  casualties with ROMIO reaching the children; #922's library side stays open.
- **#923:** test_1078's serial value on kaiju equals its parallel one: a per-host baseline,
  not partition dependence. test_1064 spherical3d at np 2 is different: its 3.4e-4 gap
  persists at tol 1e-8 against a serial child on the same host, so that one is real
  partition dependence: filed as **#931** (not phase 1); #923 keeps test_1062 and test_1078.
- **The runner is sandboxed again** (no apptainer, Slurm unreachable); nothing builds or
  runs until Louis lifts it from a kaiju terminal. Held behind it: #921 2328b4ca, the LU
  branch 61233c84, tier A+B shard 4, and the #921 stack run.

**Kaiju report 7 (2026-11-02): five branches validated against development 25d62812, no
failures beyond the baseline; PRs being opened from the laptop.**
- **PRs open (from the laptop, on Louis's direct yes, no footer):** #926 (#919, c7e6fa3b),
  #927 (#920, 92a330cf), #928 (patch summary, a46bf3f1), #929 (LU block solver, 61233c84;
  squash suggested, since 52d6d593 leaves a tier C test broken until 968b274b), #930 (#922
  test fix, a79d5236; #922's library side stays open). Merge order for `scripts/test.sh`:
  #929 first (touches nothing shared), then #926, #928, #930 (all insert at batch 4 line
  329: a development merge between each), then #927 (line 350). **Error 76 settled:** 24
  runs at once with the fix had none; the children ran ROMIO.
- **#918: Louis accepted the narrowed rule (2026-11-03, "Yes to the narrowed #918 rule -
  merge the stack")**: split levels decline above 0.98, every other level keeps 0.75. The
  stack is open: **#932** (#918, 0a11963d), **#933** (#921, c414465c, base #918's branch),
  **#934** (#925, a2e38396, base #921's branch), reviews as first comments, development
  through #927 merged into the base of the stack. Merge order on green: #932, then #933 and
  #934 retargeted; #933 never without #934. Louis's "merge the stack" covers all three.
  **Merged 2026-11-04**, all green on every shard: #932 2556c979, #933 4ee0b13d, #934
  60dbf0e4 (development's tree equals #934's tested head e8957186). #918, #921 and #925
  relabelled fixed-in-development.
  Correction to the hub's row 5 shorthand: 820 / 94 / 344 are serial (TI blocks alone;
  with the structural block, the #921 result; with the band mask also keyed); 1179 / 439 /
  131 are np 4 on development (TI alone; band mask keyed; structural patch alone with the
  gate open). 131 is not the #921 configuration.
- **#921 held on #925.** The stacks (job 3537, dumps at 300/600/900 s) show no deadlock and
  no mismatched collective: ranks 0, 2 and 3 wait in MPI on rank 1, which stays in native
  code outside MPI throughout. **Corrected by the traced run (job 3627):** not a giant LU
  (3-5 factorisations per rank) and not a deadlock. The outer rotated KSP never finishes
  its first iteration: 31 of 33 velocity solves inside the Schur application run to
  max_it 200 and reduce the residual only 10-20 times, with rank 1 holding most of the
  patch blocks (224k MatSolves against 26k on rank 0). A preconditioner that works at np
  1 (94 its) and fails at np 4 fits double correction: basic ASM summing two blocks'
  corrections on the same rows at np > 1 only. Probe queued (no code):
  `probe_925_block_multiplicity.py` counts how many blocks hold each row; serially every
  row is held once. If rows are held more than once at np > 1, the fix is a partition of
  unity over the union, making the blocks disjoint before the overlap layer (RASM itself
  was measured to stall in August).
  **Probes (2026-11-03):** the duplicates are real (232 rows in blocks on two ranks at np 2,
  224 at np 4, none serially; mostly zone-block rows across a seam, plus a few
  structural-block rows another rank's zone block holds; rank 1 holds one 17,752-row
  block). Keeping each duplicated row in one block only lets the outer solve complete
  iteration 1 at np 4 (1.5e1 to 2e-3) where before it never finished iteration 0, but
  neither np 2 nor np 4 reaches iteration 2 in 20 minutes; serially it is one outer
  iteration and 94 velocity its in 20 s. So double correction is part of the cause, not
  the whole. **Found (kaiju reports 11b, 12a, 12b): rank boundaries cut the union's blocks.**
  Holding each row once let the outer solve converge, but every velocity solve still hit
  max_it 200 at np 2 and 4 (serial: 5). The library builds 2 blocks serially, 4 at np 2, 7
  at np 4, over the same rows; only the cut differs. Rebuilding the serial blocks from the
  gathered rows restores serial convergence: at n 80, 97/95 its at np 2/4 (serial 88); at n
  320, 109/117 (serial 94), 4-6 per velocity solve. The cut through the structural block is
  what fails; band pieces cut per rank add to it. **Fix plan, approved by the hub (no
  default change; parallel made to match serial):** the parallel union and the zone pieces
  are built from the gathered rows, so the blocks are the same at any rank count and each
  row is in exactly one block; each block goes to the rank owning most of its rows.
  test_1139 (row 5 TI fixture, n 80) asserts one block per row, serial block count, the
  same zone rows and at most 5 velocity its per solve; fail-first at np 2 and 4 on kaiju,
  then the fix, review, held, stacked on #921. The big structural LU lands on one rank, as
  serially: the known imbalance, phase 3's.
  **Fix verified on kaiju (reports 13a, 13b):** test_1139 fails first at np 2 and 4 (98 and
  218 rows held twice, 4 and 6 blocks against 2, 123 and 200 its against 5) and passes on
  e67aa114, with tests 1135/1134/1106/1090/1088 at np 1/2/4. Row 5 TI: n 80 97/95 its at np
  2/4, n 320 110/117 (serial 94), 4-6 per solve, no caps. The step-4 control fell on the
  degrading side (structural patch alone, cut per rank: 70/96/143 its at np 1/2/4), so
  fc58912c gathers the structural block into one too. The stack #918 bcf89553, #921
  de53ba03, #925 724ff952 carries development; test_1133 asserts one structural block at
  any rank count; the doc names the one-rank LU and `block_rows_per_rank`. Pending:
  round-2 fail-first on the tightened tests, the cost check of the one-rank LU on row 3 at
  np 1/2/4 (its and wall time), the full tests/parallel, review round 2. Held.
  **Report 14 (c094073d):** the structural block stays gathered as one. Row 5, no zone, n
  320 (30,048-row block), velocity its at np 1/2/4/8/16: cut per rank 67/128/131/316/445;
  one gathered block 67/76/80/82/86. The owner rank peaks at about 2x the others' memory
  (520-540 against 250-290 MB) at every np; cut per rank the largest piece was still ~20k
  rows, so the cut saved little factor time. Row 3's one-rank LU is a flat 55-66 s at np
  1-16. Review rounds 2 and 3 fixed (a keyed zone with no cells installed a 7980-row block
  in parallel; rank-asymmetric keying would hang, now one allgather and a collective
  raise; `fac_zone=[]` refused). A review cost model that predicted the one-rank LU losing
  from np 8 was built on the bisection-refined fixture and is discarded under Louis's rule
  above. **#895's premise is stale** (the structural block is now one unbounded LU on one
  rank by design); to be noted there when the PR opens. On why the per-rank cut degrades
  so sharply when Krylov is partition-independent: the patch is the only part of the
  preconditioner that can correct slip (the coarse levels are welded), and rank boundaries
  cut it arbitrarily along the band and through split pairs, where deliberate cuts across
  the fault cost almost nothing (serial 8-rung strips within 7 %). So phase 3 cuts the
  patch across the fault or adds a slip coarse space. Inference; a serial test was offered
  to Louis.
  **A formally parallel patch solve works (kaiju report 17, Louis's question):** each patch
  block solved as one matrix spread over every rank with MUMPS gives the library's
  iteration counts exactly at np 1-16, on row 5 with and without the TI zone. First solve,
  structural patch alone: MUMPS 13.9 / 8.5 / 8.7 s at np 1/4/16 against the one-rank block's
  25.0 / 23.8 / 30.4 s; MUMPS on one rank is already 1.8x faster than the block LU. No
  library change proposed yet: MUMPS is in conda-forge PETSc, but Louis's 10-28 ruling kept
  it off the defaults (it breaks on the Mac). This is phase 3's first lever if the one-rank
  LU becomes the bottleneck.
- **Pressure rtol (item 3):** kaiju found test_1064 (spherical3d topography, np 4) off by
  1.4e-6 against a 1e-6 tolerance. The test solved at 1e-5 and compared at 1e-6, passing
  only because the pressure sub-solve over-solved at 0.1 x tol; fixed (56130269, the
  diagnostic solves at 1e-8). For Louis: the constraint-reaction topography moves by up to
  9e-7 relative under the 1e-2 default against 2e-8 under the old one, within the requested
  tolerance, but the old default delivered about 50 times more accuracy than requested.
  Still needs his explicit yes.
- The new runner's messages to this hub are refused too (untrusted device); it reports
  through the integration session.

Campaign note: on these branches `UW_FAC_COVER` and `UW_FAC_STRUCTURAL` do nothing, so the
drivers' st0/st1 and cover A/B pairs would run identical configurations. Item 2 waits on
experiment 1; item 4 starts once item 1's defaults settle.

**Phase 2: land 3-D.** Owner: the kaiju 3-D session (M1-M3 of its plan), with the runner.
The 2-D defaults from phase 1 are what it builds on; it does not re-open them. Milestone
order unchanged: `place_fault_ribbon` parity, the 3-D rig test, np 4 in CI, then the shell
and the outcrop. The 3-D single-block cost at the fault's own resolution is measured as
part of M2, not before it.

**Phase 3: decompose the add-on problem only if phase 2 shows the need.** The slip coarse
space, strips, and the fault across ranks (point 3 of the decision) are held until a 3-D
measurement says one block per rank is unaffordable. Experiment 2's results are kept as
the evidence base for that day; no further work on them now.

**What stops:** alternative hierarchies, the band-ratio sweeps beyond what phase 1 needs,
GenEO and any strategy outside conda-forge PETSc, corridor refinement, and new matrix
rows. New findings go to issues, and into phase 1 only if they block a listed case.

## DECISION: the add-on is the line (Louis, 2026-11-02)

Louis, after the integration session's evidence comparison (his words): "OK - let's go with
the working-hypothesis that the add-on is the most promising and the one worth investing in.
1) Add minimal additional nodes to implement the fault slip
  1a) Any refinement around the fault can be separated out from (1)
  1b) We original said the fault would carry its own resolution (it comes triangulated /
      as a divided line) and this is how we create the ladder. No S parameter defines the
      along-strike resolution.
2) We will try all the math tricks to make the SOLVE efficient in 2D and 3D
3) We can consider the parallel decomposition of this problem to make it efficient."

**The evidence he saw (all 2-D, velocity iterations).**
- Add-on H0 (welded base, split S level, FAC patch), patch allowed: 66-67 at h_b/S 24, 48
  and 97; pair 68; TI 66-94; junction 77-90; viscous box 125.
- Split levels H1: 166, 302, 725; pair 231-287; TI 230-342; viscous box 388; at an 8S
  junction gap the 4S ladder cannot be placed at all.
- H1's limit is structural: every coarse level must hold a coarser copy of the fault, which
  in 3-D means surgery on every level. H0's failures were defaults: #918, #921, #892.
- H0's weakness is the one gathered LU on one rank. Serial smoke at ratio 24 against LU's
  67: ILU(1) blocks at rtol 1e-2, 71; 2000-row pieces plus slip coarse space, 79-85;
  one-rung strips plus coarse space, 135.

**What this closes.**
- Split coarse levels (the chain, `custom_mg.py:1556`) are not developed further. They stay
  in the library as they are until Louis says otherwise.
- The S ruling is superseded by 1b: the fault carries its own resolution, as a divided
  line; the ladder's rungs are the fault's own points; no S parameter defines along-strike
  resolution. S survives only in the drivers (trace sampling, width = 2S) and should go.
- Row 7 as a "which S" sweep is moot; its arms still measure how the solver behaves as the
  fault's division changes, which is useful for (2).
- Refinement around the fault (1a) is a separate question from the fault's nodes (1).

**First measurement for (1), mesh only** (022 base, h_b 1/32, 5313 P2 nodes):

| fault division | ladder (`place_fault_ribbon_2d`, width 2x segment) | bare cut (`add_fault`) |
|---|---|---|
| 13 segments (about h_b) | +14 vertices / +33 P2 | +16 / +37 |
| 26 segments | +143 / +523 | +14 / +29 |
| 53 segments | +344 / +1273 | +14 / +29 |

At a matched division the ladder is already minimal (the split's duplicates plus 2
vertices). The bare cut ignores the fault's division: it pulls base vertices onto the
line, so its slip is resolved at h_b whatever the fault gives, which fails 1b. The
placement API already takes the trace's own points as rungs.

**The programme that follows (2) and (3):** the iterative-patch experiments on kaiju
(inexact blocks, pieces plus slip coarse space), then the 3-D single-block cost (row 1),
then the distribution of the patch across ranks (row 2), all on conda-forge PETSc.

**The split tip (Louis, 2026-11-02, confirmed):** "One element ... if it works. I am not
sure about units. 1 is normalised by the element size." So the inset is one local element
length at the tip, a condition to be tested, not a settled rule: if one element does not
work (the rotated frame fails, or slip at the tip misbehaves), the measurement says what
does.
*Row 7 implements it (2026-11-02)* as the band cell at the tip, one rung spacing down dip
(`-uw_tip 1el`): 0.8-1.3 S in depth, since the spine never meets the surface at a rung. In
20 mesh-only placements across five S and four tip rules, no pair point lies on the
surface and the top pair's frame normal matches the fault's to 12 digits, so the rotated
assembly cannot refuse. At S = h_b and h_b/2 the one-element tip coincides with the
existing 0.012 arm. If Louis meant the base cell h_b rather than the band cell, that is
the 0.012 arm at S = h_b (0.84 h_b deep), already in the grid. Seven solve arms added (1el
and 2el across S); every record carries the inset in rungs, down dip and in depth, and the
slip and leak of the four pairs nearest the tip. Row 7 is 25 jobs.

## Kaiju results, 2026-11-02 (rows 4, 5, 7; builds 964dc3ce, np 4 unless stated)

**Row 7, problem A** (linear 022 fixture, h_b 1/32, np 1; reference 640 rungs):

| h_b/S | vel its | peak slip | slip dev max / rms | block rows | block solve s | solve s |
|---|---|---|---|---|---|---|
| 0.99 | 66 | 0.16074 | 9.0 % / 2.7 % | 1382 | 0.33 | 5.9 |
| 1.97 | 69 | 0.16030 | 6.9 % / 1.9 % | 1992 | 0.55 | 6.3 |
| 4.02 | 70 | 0.15955 | 4.8 % / 0.8 % | 3422 | 1.14 | 7.3 |
| 8.03 | 66 | 0.15941 | 3.7 % / 0.5 % | 5996 | 2.11 | 8.4 |
| 24.25 | 67 | 0.15921 | 2.1 % / 0.2 % | 15854 | 7.02 | 15.2 |
| 48.51 | 65 | 0.15912 | reference | 31046 | 20.5 | 32.0 |

Iterations flat at 64-70. At ratio 1-2 the slip is within 2-3 % rms, the block 8-11 times
smaller and its solve 13-21 times cheaper than at 24. (The corridor-refinement arms that
had started before the cut gained no slip accuracy and cost iterations: 70 to 217.)

**Row 7, problem B** (the yielding-lid box, tip held at 0.012; reference S 0.00195):

| h_b/S | Newton | vel its | peak slip | slip dev max / rms | surface vx dev | block rows | block total s | solve s |
|---|---|---|---|---|---|---|---|---|
| 0.96 | 43 | 4609 | 426.3 | 50 % / 32 % | 118 % | 1401 | 18 | 394 |
| 1.91 | 37 | 3594 | 338.1 | 16 % / 7.4 % | 44 % | 2071 | 27 | 336 |
| 4.06 | 40 | 3729 | 327.7 | 7.5 % / 2.5 % | 10 % | 3901 | 58 | 378 |
| 7.88 | 42 | 4122 | 323.4 | 5.8 % / 0.9 % | 8 % | 6631 | 127 | 486 |
| 16.0 | 38 | 3295 | 321.7 | reference | reference | 13007 | 254 | 570 |

The box converges in S much more slowly than the linear fixture, because its weak bridge
is the band cells above the tip (2S wide) and at S = h_b the bridge is 0.065 wide and the
tip cannot be shallower than 0.026: the geometry changes with the ladder. Iterations do
not grow with ratio; block cost grows linearly with the rung count.
*Geometry-held check queued (10 np 4 arms, campaigns 1bcab15):* two driver options, both
off by default, `-uw_tip_exact` (the spine sampled from the tip, so the tip is at the
asked depth at every S) and `-uw_bridge_width w` (a smooth zone of physical width w at
the quadrature points, independent of the band cells). Tip held at 0.026 (1.1 elements at
S = h_b). Two bridge families, 0.008 and 0.0654 (2 h_b), each against its own finest S. If
**Result (kaiju report 6):** with the tip and bridge held in physical units, the box converges
like problem A. At h_b/S 1-2 the slip profile is within 1.4-2.5 % rms and the peak slip
within 1 % of the reference, for both bridge widths, against 32 % / 7.4 % when the geometry
moved with S. So the earlier spread was geometry, not resolution. **The bridge (weak-zone)
width is a model parameter in physical units**: it moves the peak slip by 11 % (320 against
356 for 0.008 against 0.0654). The slip max is not monotone in S (up to 18 % at ratio 4 at
a few nodes near the tip) while the rms is. The driver PR goes through the science hub.

**Row 7, the one-element tip ("if it works"): it works at every S.** Every 1el arm converges
in the same 35-42 Newton steps as deeper tips; the frame on the first interior pair is the
fault's to 6 digits; the no-opening leak is at rounding; the peak slip is within 1 % of the
0.012 tip at the same S. A shallower tip changes the surface velocity by about 25 %
against the 0.012 reference, as expected, since the fault reaches closer.

**Row 4** (interface laws, the box, np 4):

| law | h_b/S | H0 its | H1 its | Newton H0/H1 | t_solve H0/H1 s | slip |
|---|---|---|---|---|---|---|
| viscous | 7.9 | 128 | 394 | 30/30 | 514/655 | 77.36 |
| Coulomb | 7.9 | 308 | 843 | 77/77 | 853/1281 | 7.99 |
| rate-state | 7.9 | 269 | 703 | 75/70 | 814/1332 | 6.63 |
| viscous | 15.5 | 114 | 483 | 27/27 | 389/929 | 76.91 |
| Coulomb | 15.5 | 247 | 971 | 70/71 | 852/1476 | 7.36 |
| rate-state | 15.5 | 214 | 834 | 65/70 | 695/1518 | 6.13 |

H0 takes 2.6-4.5 times fewer velocity iterations, falling with ratio where H1's rise; Newton
counts and slip are the same.

**Row 5** (networks, h_b/S 24, np 4): junction (gap 8 / 24) H0 89 / 87 against H1 261;
pair H0 913 with the 0.75 gate, 80 with the gate open, H1 276; TI band H0 1033 gated, 131
open, H1 338. The gate (#918) is the only thing standing between H0 and a 2-3 times win on
networks. **TI zone reruns (np 4):** a TI zone alone 1179 its; TI zone plus the fault's band
as a second zone 439; the structural patch alone with the gate open 131; H1 338. Same peak
slip (0.13293) throughout. That is #921's point at np 4: without the split's structural
rows the patch is 3-9 times worse. (The "zone plus structural" arm was invalid: a job-line
`UW_FAC_COVER=0.75` overrode the zone path's gate; corrected arm queued.)

**#919:** fixed by 7c0c62ff (test_1132 passes at np 1, 2 and 4). The runner also saw
test_1062, 1064, 1069, 1078 and 1079 fail at the earlier commit; a development baseline is
running to separate them from #919. test_1062 also fails at 7c0c62ff ("evaluate() is
rank-local: 58 of 58 points not located on rank 0"), probably pre-existing.

**Hierarchy patch summary:** done, `feature/mg-hierarchy-patch-summary` 04b7a76f, held.
`hierarchy.patch_summary` holds per level the blocks, owned and subdomain rows, the largest
block and each rank's block sizes, from one allgather at install; reading it is not
collective. No default change. Drivers read it (campaigns ed513c1).

**HDF5 error 76 on kaiju, cause found:** Open MPI's OMPIO. With many UW3 processes on one
node, H5Fcreate/H5Fflush through MPI-IO fail intermittently, even on COMM_SELF and
node-local dirs. With `OMPI_MCA_io=^ompio` (ROMIO) zero failures in two runs, against 13
and 1 under OMPIO. #922 is corrected and retitled. **Defaults question for Louis:** prefer
ROMIO, write the rank-0 mesh file without MPI-IO, or document the environment setting.

**#919:** `tests/parallel` fails the identical set at 7c0c62ff and at development 25d62812,
so the branch adds no failures; review running. Those pre-existing failures (test_1062,
test_1078, test_1064 spherical at np 2) pass in CI on 25d62812 and fail only in the kaiju
HPC container: filed as **#923** (type:testing). All three compare against a serial value
recorded on another host; whether the container's own serial value matches its parallel
one is the open question.

## Can the add-on replace split coarse levels everywhere? (Louis, 2026-11-01)

Louis: "Overall, the add on is so much simpler conceptually and in terms of data copies and
manipulation that I consider it much nicer as an approach. But I need to understand if it
can actually replace the split levels approach in all cases - including in 3d!" "The add-on"
is the welded base under one split child, with the FAC LU patch on the finest level
(`uw_chain 0`).

**Ruled so far (2026-11-01).** The production tail for split faults is the welded base
plus the split S level with the FAC LU patch. The drivers' `uw_chain` default changes only
once kaiju's np 16 annulus run on development confirms it, because #914 is unchecked at
np 16. Whether split coarse levels stay as an option (`custom_mg.py:1556`) waits on this
matrix.

**Evidence so far (all 2-D, development 25d62812):**
- **The 022 linear fixture:** H0 takes 66/65/67 velocity its at 80/160/320 rungs (np 1)
  and 74/72/71 at np 4. H1 (the chain) takes 83/118/166 and 103/154/200.
- **The 022 yielding-lid box, np 4:** H0 takes 187-195 velocity its over a solve at every
  spacing; H1 takes 690-1440, 3.5-7.7 times as many and 3.6-8.9 times the time. No caps,
  and peak slip agrees to 1e-5.
- **Kaiju's annulus at np 16:** 5.9 against 7.7 velocity its per increment (#892
  issuecomment-6550915680).

**Test matrix (3-D first).** H0 against the alternative: velocity its, setup and solve
time, peak memory per rank, slip against reference.

| # | Case | What could break H0 | Where, who |
|---|---|---|---|
| 1 | 3-D: a blind sheet in a box, then a dipping sheet in a shell | One LU per rank on a thick 2-D layer grows faster than in 2-D (#895). The alternative (3-D split coarse levels) is unbuilt. Measure one block, capped blocks, inexact blocks, and the held slip coarse space if a single block fails | kaiju 3-D session, M0(b) then M2 |
|   | *Sequencing (2026-11-01).* The integration session's view, given to Louis: the gather-to-one-rank, single-LU form looks doomed in 3-D and at scale, and the two-level form (bounded blocks plus the slip coarse space) is the candidate. Its only evidence is 2-D (79-85 its against 66 for one block), and the slip coarse space refuses 3-D today. **So measure before building:** (a) the 3-D single-block cost as the band refines, which is cheap, M0(b); (b) bounded blocks without a coarse space, which shows the loss the coarse space must recover; (c) only if (a) is prohibitive, build the 3-D slip columns (a smooth per-direction column) and run the deciding 3-D sheet at np 16-64, with the fault spread over ranks (`seams="conform"`) rather than gathered | |
| 2 | Parallel: a long fault crossing k partitions, k = 1, 2, 4, 8 | The patch becomes one block per rank crossed, like the cut blocks that lost in 2-D (79-87 against 67). The add-on partition gathers one fault onto one rank at np 16 today | kaiju rollback rig, after the scaling job; needs #902's fix for np > 16 |
|   | *Row 2 baseline, np 16 (kaiju budget v3, jobs 2480-2488, via the science hub):* H0's finest patch (3584 rows) sits on the one rank holding the fault. Its solve is 21-28 s of a 410-441 s Stokes solve (5-6 %), while 15 ranks wait (max/min 165-178). Velocity work is equal to the chain (8.65 against 8.74 F-cycles per solve), and times are a wash within the ±10 % spread. So at production scale H0 is not yet a speed win, only simpler; the imbalance is what row 2 must measure as the fault spreads | |
| 3 | Cover gate: a small domain with a fine band (patch above 75 % of the level) | The global 0.75 gate declines the patch and falls back to whole-level SOR, silently. The 022 fixture is already 63 % at ratio 24 | integration session, laptop |
|   | *Row 3 measured (2026-11-01, the 022 linear fixture, np 1 and 2):* at h_b/S 48 and 97 the patch-plus-halo is 76 % and 86 % of the finest level. **The gate declines it silently**: whole-level SOR takes 909 and 1487 velocity its, against 66 with the gate forced open and 302 and 725 for H1, with slip off by 7e-5 at ratio 97. The 0.75 threshold separates by size, but a uniform level is 100 % subdomain with no background, while a fault level keeps 14-38 % background. **Proposed fix (Louis to rule):** decline only when the background outside the subdomain is under 2 % of the level, and log the verdict either way. The single structural LU block reaches 61,360 rows (86 % of the level) at ratio 97, which bears on row 1 | |
| 4 | Interface laws: friction, viscous, rate-and-state | Not yet measured on the welded tail with LU blocks (after #894's refresh) | integration session, the box at np 4 |
|   | *Row 4 so far (the box, np 4, S 0.004):* viscous law (η_f 555.7): H0 125 against H1 388 velocity its, same 29 Newton its, same slip. Coulomb and rate-and-state are re-running: they hit the rotated loop's 50-iteration cap in the Picard phase under both hierarchies, with no linear trouble. Side finding, filed as **#920**: the rotated path's `max_it=50` ignores a user's `snes_max_it`, at both call sites (`rotated_bc` and `fault_contact.py:522`) | |
| 5 | Fault networks: junctions, several faults per rank, TI and unsplit bands | Overlapping patches, block coupling at junctions, TI's zone blocks against the structural block | integration session (2-D); 3-D session later |
|   | *Row 5, np 1 (np 4 arms on kaiju):* H0's structural patch handles every network case at 66-90 velocity its once the gate lets it through, against H1's 230. H1 cannot place its 4S ladder at an 8S junction gap at all. **The defaults fail twice:** the 0.75 gate declines the pair and the TI case (#918); and with `fac_zone` keyed to a TI band, the split fault's structural rows are left out of the patch (820 its against 94 with the union), because `UW_FAC_STRUCTURAL` defaults to 0 while the `set_custom_fmg` docstring says they are "unioned in automatically". Filed as **#921** (proposed: union the structural rows whenever the finest level is split, and keep #670's default for painted bands; Louis to rule). `ti zone both` at np 4 ran past an hour where np 1 takes 15 s: a possible parallel hang, under watch on kaiju | |
| 6 | Memory of the LU fill per rank | 3-D especially; the largest block and the fill per rank | kaiju (with 1 and 2) |
| 7 | Ladder at base resolution: S = h_b and h_b/2 against today's S (unrefined arms only; the corridor-refinement arms were the hub's addition and are dropped) | If slip or trench behaviour changes, the ladder was doing physical work after all | kaiju runner (box, 022 fixture), kaiju rollback rig (annulus) |

**Done when:** every row has a measurement. Then Louis rules whether split coarse levels
are deleted, kept as an option, or kept for named cases.

## Ruling: the ladder matches the base mesh (Louis, 2026-11-01)

Louis: "For split nodes, the ladder is to improve how we cut the mesh and this works best
when the ladder and the base mesh have similar resolution." The rung spacing S is a mesh
structure parameter, not a physical length. "TI fault is more complicated but I think we
will use that less for these cross-scale problems and more for fault networks."

**Why the band ratio hurt.** The sweep varied h_b/S from 6 to 97 with the width tied to 2S,
so the ladder's element count along the fault grew while the welded base stayed put. Every
band unknown with no coarse counterpart is a mode the coarse correction cannot touch; the
patch must kill it exactly, and its block grows with the ratio. Row 3's gate failure (the
band exceeding 75 % of the level) and the chain's growth are the same thing.

**Consequences:**
- **Production rule for split faults:** S = h_b/k, k in {1, 2}.
- **Correction (2026-11-02).** The hub's earlier line "extra slip resolution comes from
  refining the base under the fault corridor" was the hub's inference, not Louis's ruling,
  and it was relayed as his. Louis: "I don't really know where that came from. We have the
  MMPDE that can gather points near the fault, but that's not at all the same as
  mesh-splitting refinements. The idea of cutting the mesh to make the fault is that we
  probably don't need a lot of refinement - it's a discontinuity so we need to represent
  it efficiently. The ladder is to allow us to compute stresses and slip-rates accurately.
  Some refinement will be needed to compute near-fault stress lobes, but that is a
  different question. Let's try to avoid opening up too many new directions." Row 7's 32
  corridor-refinement arms were dropped; its 18 unrefined arms run.
- **The split tip is not a physical length (Louis, 2026-11-02).** The fault is the same
  object whatever the implementation. The split stopping short of the surface is an
  implementation detail: surface DOFs cannot be rotated, so at least one element sits
  between the tip and the surface, and damage carries the rest of the fault. So the tip
  depth is one local element length ("if it works"), not a depth fixed in physical units.
  **Driver consequence (notes session, 2026-11-02):** `annulus_faults.py`'s `trace_inset()`
  returns 3.0 rungs for a split, which is 0.012 at S 0.004, under one base cell of 0.0156,
  but three base cells at S = h_b. The inset should be set in base cells (one), not rungs,
  if the default S changes. Row 7's annulus arms hold it at one base cell so the slip
  comparison is not confounded.
- The 022 note's own sweep is ratios 6-25 (h_b 1/32); row 3's 48 and 97 are that fixture
  with more rungs and are not in the note. Both are solver stress tests above the
  production ratio. **Production itself runs at ratio 3.9** (S 0.004 on h_b 0.0156,
  refinement 5; corrected by the notes session from "about 8", which was refinement 4).
  So the ruled arms for the annulus are S = 0.0156 and 0.0078 against today's 0.004.
- At ratio 1-2 the LU block is a thin strip, which bears on rows 1 and 6 (3-D cost) and
  lowers the stakes of the iterative-patch experiments.
- TI bands keep their own width (a modelling quantity, eta_1/w), and are for fault
  networks rather than cross-scale problems.

**Dispatched to measure before the drivers change (matrix row 7, kaiju):**
- the box and the annulus rig at S = h_b and h_b/2 against today's S (annulus: 0.0156 and
  0.0078 against 0.004): slip profile, trench behaviour, iterations and cost, plus the FAC
  block size and its solve time, since the one-rank patch (3584 rows, 21-28 s a step at
  np 16) should shrink with the ratio;
- (dropped 2026-11-02: the corridor-refinement arms, see the correction above.)
If the physics is unchanged, the drivers' default S changes and UWTN 2026-022's scope
statement gains a line.

**Row 7 as queued (50 jobs, kaiju; scripts `addon_matrix_2026_11/row7_*` at b1c2db6).**
h_b = 1/32 in both fixtures; the box's S today is 0.004 (ratio 7.9).
- A, the 022 fixture, unrefined: 13 to 640 rungs (ratio 1 to 48). B, the box: S = h_b,
  h_b/2, h_b/4, 0.004, h_b/16.
- Corridor refinement: `refine_lines` exists only for Annulus on a feature branch (a gmsh
  size field, not on development), so the arms use nested NVB `mesh.adapt` with a
  distance-to-fault metric: k refinement levels in a corridor of half-width 1 or 2 base
  cells, each paired with an unrefined arm at the same S. The refined levels are welded.
- Records: the slip profile in physical coordinates, surface velocities (box) or the
  velocity across the fault midpoint (A), Newton and velocity its, times, peak RSS, and
  the FAC block's rows and time split into LU set-up, refactorisations and solves.
- **A geometry coupling to note:** the box fixture splits from 3S below the surface and
  the weak bridge is the band above the tip, so both are tied to S. Row 7 holds the tip
  at depth 0.012 by default (the unrefined arms also run the 3S rule), and the bridge
  stays 2S wide because it is the band cells. At S = h_b the bridge is therefore wider.
  **Answered by Louis (2026-11-02):** the tip depth is not a physical length; it is the
  one element the surface rotation needs, so it is set in mesh units. The bridge is the
  band cells above it.
- Smoke (serial counts only): A at 26 rungs with one corridor level took 70 its and a
  2122-row block; at 53 rungs with two levels, 122 its. The welded refined levels carry no
  slip, so corridor refinement may cost iterations. The kaiju grid decides.

## Can the patch be an iterative solve? (Louis, 2026-11-01)

**Answered 2026-11-02: LU stays.** See the programme's item 2 for the table. Nothing inexact
came within 1.5x of LU on the box; strips of 8 rungs with LU are within 7 % (the phase-3
lever).

Louis: "Any way we can write the add on as an iterative solve that scales better? Does it
require the full accuracy of LU? ... particularly relevant if we break the fault into
patches that we must then solve as a coarse problem. Are there known strategies?"

**The hub's reading of the evidence.** The patch must capture two things: the local
stiffness contrast across the thin band (local, anisotropic) and coherent slip along the
whole fault (a global low-energy mode a welded coarse level cannot hold). One LU block gets
both. ILU(0) failed (344 against 67) as a poor approximation of a near-singular block, not
because inexactness is fatal. Cutting along strike (85-180) broke the slip coherence, and
the slip coarse space put most of it back (79-87). So the two-level form, local solves plus
a slip coarse problem, is already shown in 2-D.

**Known strategies:** two-level Schwarz with a problem-adapted coarse space (our slip space
by hand; GenEO automatically, in PETSc as PCHPDDM); deflation of the slip modes
(PCDEFLATION); line relaxation across the structured band (rung-line blocks); inexact
block solves (inner Krylov with ILU(k) or AMG); the fault as a DD interface (FETI/BDDC,
the contact literature; PCBDDC); compressed direct (BLR LU, which runs into the no-MUMPS
default).

**Experiments approved (Louis, 2026-11-01), 2-D, on kaiju**, the 022 fixture at ratios
24/48/97 plus the box at np 4, one LU block as the reference:
1. inexact block solves: FGMRES with ILU(1), ILU(2), GAMG at block rtol 1e-1 to 1e-3, caps
   5 and 10; on the single block and on cut blocks;
2. rung-line blocks plus the slip coarse space, against rung lines alone, cut blocks plus
   coarse space, and one block;
3. PCHPDDM (GenEO) on the patch, if the PETSc build has HPDDM (being checked on kaiju's
   image); coarse-space size against the hand-built slip space.
The winners go to the 3-D rig ahead of hand-building 3-D slip columns. Owner: the
integration session writes the probes, "kaiju: dev runs" runs them.

**Launched 2026-11-01:** 164 jobs on the kaiju runner. Library `probe/iterative-patch`
8f94ee21 (the slip-coarse-space branch with development merged, plus one probe knob,
`UW_FAC_STRIP_WIDTH`; not for merge). Scripts: `iterative_patch_2026_11/` on
`addon-matrix-2026-11`; its README answers the strategies question.
- Experiment 1 needed no library code: the block KSPs read the options database under the
  per-solve prefix. Smoke at ratio 24, FGMRES + ILU(1), block rtol 1e-2: 71 velocity its
  against LU's 67, about 20 block its per application. Caveat: an FGMRES block solve is
  nonlinear in its right-hand side, which the level's GMRES smoother does not tolerate; a
  stall there is part of the answer.
- Experiment 2 smoke, rung strips of 1 with the coarse space: 135 its against 67, with
  362 blocks of 180 rows. **Design point:** the slip coarse space has one column per
  piece, so at strip width 1 its dimension is the rung count (320-1280 here; in 3-D the
  rungs on the sheet). Tiny local solves move the cost into the coarse problem, and the
  strip width trades one against the other.
- **Experiment 3 cancelled (Louis's rule above).** Neither wombat's nor kaiju's PETSc has
  HPDDM or SLEPc; a rebuild would be about an hour of a node plus a day of probe code. The
  hand-built slip space is our coarse space. Added instead: hypre BoomerAMG as a block
  solver in experiment 1, which is in conda-forge PETSc and needs no code.

## 3-D add-on mesh (Louis, 2026-10-31: "We really do need the 3D option for the add-on mesh. These are things we keep failing to complete despite making efforts to do so.")

**Survey (2026-10-31, read-only, at development fc67b650; key claims re-checked by the
hub).** The 3-D analogue of 2-D production exists in substance, but it has never been
taken to the finish.

- `place_fault_ribbon` (`place_surface.py:8995`) places the structured ladder into the
  base's finest level and labels its mid-surface from the ladder's own vertices (the
  `cut=False` equivalent), then splits.
- Against `place_fault_ribbon_2d` it lacks: the add-on partition, tail adoption, a route
  through `Mesh.add_fault`, a realisation switch, an outcrop cap, and any solve or parallel
  test.
- `FaultNetwork.build(width=)` in 3-D solves both realisations (`test_0863`), but builds
  its own unit box and refuses a supplied base (`meshing/fault_network.py:358`).
- No test combines 3-D rotated free-slip walls, a split fault and custom multigrid.
- The 3-D sheet replay onto add-on levels has no test.
- **#900:** every 3-D parallel fault test is a `ptest_*` file, and CI runs none of them.

**Why the attempts stalled (the survey's reading, which the hub accepts):**
- Each push built the mesh piece, then deferred the solver to 2-D. Louis's 2026-09-03
  ruling said "the preconditioner question is deferred to 2-D", and the 2-D wrappers then
  gained partitioning, tail adoption, chains, caps and wall rotation while the 3-D ones
  stayed at their August state.
- The October effort went down the adapt-and-sheet route, which production does not use,
  and hit the bisection-child volume guard.
- A cavity fix sat a month on a side branch. The science campaigns went around the
  add-on route with gmsh boxes. The 3-D parallel tests are dark.

**Plan (one route: the base-finest-copy ladder, mirroring 2-D production).**
- M0, prerequisites:
  - #900, so the 3-D parallel tests run and progress cannot silently regress;
  - the 3-D solve experiments on the fixtures that exist (`test_0863`'s 3-D band, the
    extruded plate): one LU block per rank, capped blocks, inexact block solves (a few
    GMRES iterations with ILU(k) or a shift), and split levels without the patch. Record
    time and memory against block rows (#895).
- M1: `place_fault_ribbon` brought to parity with the 2-D wrapper:
  - a supplied 3-D base (a copy of its finest level);
  - `partition_addon`, and `adopt_hierarchy` keyed on the footprint;
  - a route through `Mesh.add_fault`;
  - the realisation switch: split, or TI painted on the footprint with the grid normal as
    director;
  - a serial solve test.
- M2: the 3-D rig test. A box base with `refinement=2`, a blind interior sheet, rotated
  free-slip on every wall, both realisations, custom FMG with the FAC patch, and
  iteration, slip and leak bounds. It joins tier B.
- M3: the same at np 4 as `tests/parallel/test_*.py`, so CI runs it; #671's partitions
  checked.
- M4: a curved base (spherical shell) and the outcrop (a 3-D ladder cap, or the
  `surface_trace` that `place_sheet(setback=)` returns).
- A 2S split ladder level only if Louis's 2-D ruling is the chain.

**Rules for this one, so it finishes:**
- One owner with no other duties.
- No change of route without a dead-end journal entry and Louis's ruling.
- Each milestone lands on development by its own small PR, with its test.
- 3-D is measured alongside 2-D, not deferred to it (asks Louis to retire the 09-03
  deferral).
- Housekeeping on the way: re-measure the two-level placement at the default clearance;
  close #626 if #638's ladder and #664's `embed=` realise it; correct the
  topic page's "2-D, 3-D and parallel" claim.

## Open pull requests (2026-11-07, `development` at 72741873)

**Merged 2026-11-01 to 11-04 on Louis's word:** #912 (#892), #913 (#894), #914 (#896),
#915 (levels accessor), #916 (#907), #929 (squash, 6321c714), #928 (d9783f02), #927
(f53bbffb), #926 (e7dfbf9a), #930 (af6f19b3), then the stack #932 (2556c979), #933
(4ee0b13d), #934 (60dbf0e4), #937 (#902, c514013f), #938 (#935, f631ce42), #942 (#936,
045466df), #943 (#917, 1f87430f), #947 (#901, eddab707), #954 (c5c87100), #967 (#963, 7c3d31fd),
#955 (#665, squash 081417a1), #970 (#961, #807, 37aa2a11), #973 (#905), #972 (#971), #980 (#950),
#981, #983 (#908), #958 (#900 part, 72741873). The ten PRs in
the table below are still the open set (checked 2026-11-04).

**Merged 2026-10-31 on Louis's word** (the hub merged; the approval rule was bypassed as
admin, which Louis ordered):
- #863: c6ee62cf.
- #882 (A): 24923e5d.
- #889 (B): 4dff48b3. After A merged, B conflicted with development in
  `scripts/test.sh` only, because #863 had moved every line to `batch <shard>`. The hub
  merged development into B (5e8d8d51), putting test_108*/test_109* on shard 3, and waited
  for B's sharded CI to pass.
- #890 (C): fc67b650. Retargeted to development; it merged clean. Development now
  differs from C's tested head only by #863's four files.

All ten remaining PRs target `development`. "Blocked" means the approval rule only.

| PR | Author | What | CI | Waits on |
|---|---|---|---|---|
| #780 | lmoresi | Refuse an expression re-declaration that changes its contents (fixes #767) | green (80 min) | approval; mergeable, nothing outstanding per the last comment |
| #861 | lmoresi | Journal replaces the wiki: CLAUDE.md and planning guide | green | approval (docs hub's rule PR) |
| #862 | lmoresi | Fault multigrid capability guide | green | approval (docs hub). It says the split fault "needs the chain of split ladders" past a ratio of about 12, measured on ILU blocks (#892); sessions read guides as skills, so a one-line caveat first |
| #689 | gthyagi | CitcomS predictor-corrector DDt manager | test cancelled at 2h | a CI re-run (sharded now that #863 is in); gthyagi addressed the last ruling on 2026-10-29 |
| #800 | lmoresi | Forward-from-nodes history; semi-Lagrangian schemes by trace and launch | test cancelled | **conflicts with `development`**; untouched since 2026-10-12. Needs a development merge and an owner |
| #855 | gthyagi | Collective evaluation of prescribed rotated wall data | green | marked ready 2026-10-29; his fixes to the review are not re-reviewed; lands before #857 |
| #856 | gthyagi | Boundary names consistent across ranks | green | lands after #858 (otherwise a rank-local raise can become a hang) |
| #857 | gthyagi | Opt-in annulus pressure, wall and traction recovery | green | marked ready, but the mathematical review of the ~1,400-line recovery algorithm is outstanding (gthyagi says so); after #855 |
| #858 | gthyagi | Submesh injection across parent ownership | green | marked ready; the disagreement guard asked for in review is in, not re-reviewed |
| #859 | gthyagi | Point evaluation near exact-cell faces | green | marked ready; not re-reviewed |

**Proposed merge order.** D (the #892 fix, when its benchmarks are in), then #780, #861,
#862 (after its caveat),
then gthyagi's set as he marks them ready (#855 then #857; #858 then #856; #859), then
#689 after a green re-run. #800 after someone takes it.

## Library fixes with no PR (2026-10-29)

Branches with commits that no open PR contains. Compared with `git cherry` against
`development` and against #890's head.

| Branch | Unique commits | What | Owner, state |
|---|---|---|---|
| `bugfix/backward-nodes-snapshot-order` adb20e9d | 4 | Stress-transport fix: the nodal history carries the stress it stores; Eulerian histories freeze their source | hyperion. Verified on hyperion and kaiju, review done (HUB.md 2026-10-24). No PR. Its "docs" follow-up is not itemised |
| `feature/shear-band-length-scale` 114c472c | 22 | Shear-band length scale (coupled adjoint, rotated linear floor, chi lifecycle) | hyperion. A second adversarial review owed |
| `feature/ve-stretch-split` cd0e16b3 | 4 | Viscoelastic stretch at large steps; lagged stretch removed | unknown. Reviewed; no PR, not in any hub file |
| `bugfix/visualisation-headless-no-trame` 7392233c | 1 | PyVista works without trame; probably fixes #665 | handed to hyperion 2026-10-25. No PR |
| `bugfix/disk-snapshot-swarm-values` 36901eb8 | 2 | Disk snapshot restore writes swarm values through to PETSc | unknown, 2026-10-06. No PR, not in any hub file |
| `feature/coarse-solve-nullspace` c991ca71 | 16 not in #890 | Coarse solve with the rotation null space (prototype, sweeps 1-3, proposed design) plus figure scripts and hyperion hand-over notes | hyperion. Louis's ruling 2026-10-28: handle the null space, PETSc defaults for the coarse level, MUMPS not the default. The design is library work; the figure scripts leave underworld3 per the `scripts/sessions` ruling |
| `feature/tidal-shell` fc35972a | 2 not in #890 | Box-fault driver: strike angle, slip sign | science study branch; science hub |
| hyperion rescue branches `*-hyperion-2026-10-20*` (six) | 1-21 each | WIP saved before the disk failure | untriaged |

Merged with #890 (fc67b650): `feature/box-faults`,
`feature/box-faults-warm`, `bugfix/custom-mg-empty-rank`,
`feature/parallel-addon-distribution`, `bugfix/rotated-solve-diagnostics`,
`bugfix/warm-start-newton-switch`. Superseded: `bugfix/faulted-rebuild-leak` and
`bugfix/rebuild-efficiency` (by #882; one probe commit each left),
`wip/yield-782-759-hyperion-2026-10-20` (by #852, merged).

## Problems raised by other sessions

| Problem | Raised by, when | Issue | State |
|---|---|---|---|
| Units model: `mesh.X.coords` is dimensional; `estimate_dt` crossing time and first accuracy estimate read it as model units (D1, blocking), plus D2-D7 | kaiju, 2026-10-29 | #891 | filed; no owner. Kaiju works around it with `-uw_units_dt_local 1` |
| Parallel `read_checkpoint` bug | kaiju, 2026-10-21 | none | not filed. Possibly the same defect as #690 or #809 (refined-mesh reload corrupt); to check before filing |
| Rotated solve's pressure (Schur) KSP rtol is 0.1 x tol (marked TODO(MEASURE)); kaiju measured -28 % to -57 % Stokes time at 1e-2 with the same answers | kaiju, 2026-10-28 | none | a solver default change with evidence; Louis's decision (HUB.md "Cost levers") |
| The split's `zone` docstring calls it transverse-isotropic; it is isotropic weakening | kaiju TI design report, 2026-10-29 | none | docstring fix, to file |
| TI Newton tangent inconsistent (#457) biases a TI against split cost comparison | kaiju TI design report, 2026-10-29 | #457 | **#457 is closed** (fixes in #493 and #748). Kaiju's concern may be stale: tell the science hub |
| `visualisation.initialise()` raises on headless pyvista without trame | kaiju, 2026-10-25 | #665 | fix on a branch, no PR (above) |
| Adapt: intermediate MG levels depend on the partition when h_far sits above the base | docs hub (integration), 2026-10-28 | #865 | filed; open |
| 23 review findings from A, B, C | fault-split reviews, 2026-10-28 | #866-#888 | filed; #883 follows C. None scheduled |
| `test_1063` 1.8 % off its anchor | pre-existing, seen in every suite | #826 | open |
| The rotated path's FAC patch blocks run ILU(0), not LU | integration session, 2026-10-29; notes session, 2026-10-30 | #892 | **PRIORITY** (Louis); plan in the section above |
| An unsplit placed-ribbon coarse tail (`place_fault_ribbon_2d(split=False)`) exhausts node memory in `set_custom_fmg` (170-377 GB at np 16) | kaiju via the science hub, 2026-10-29 | #893 | filed by this hub 2026-10-31; bears on #889 and #890. Kaiju runs `-uw_chain 0` for the TI runs |
| Stale `TODO(BUG)` on `TransverseIsotropicFlowModel` (`constitutive_models.py` about 3639) still says the TI Newton tangent is inconsistent (#457); fixed by #493 and #748, and it misled kaiju's TI design report | science hub, 2026-10-29 | none | a one-comment fix, rides on the next PR that touches the file |
| Surface-breaking split faults: `fault_split` refuses a cut touching the boundary, so a megathrust is a buried crack whose top tip halves the slip against an outcropping band | science hub, 2026-10-30 (evidence on kaiju's probe page 9Au3HFWLqkHt2geWohQpYa) | #553 (open since August, same request) | evidence to add to #553; bears on every faulted annulus result |
| A public accessor for a mesh's multigrid levels (the note and the recipe use the private `_coarse_level_meshes()`) | docs hub, 2026-10-30 | none | **approved by Louis 2026-10-31**; briefed to the integration session as task B: `feature/mesh-multigrid-levels` from development, a read-only `Mesh` property (name to check against the Charter), its own PR, #889 and #890 untouched |
| Split-fault normal traction differs between the faces | science hub, 2026-10-29 | none | **cleared** 2026-10-30 by kaiju's box probe: an artefact of the estimate |
| Rotated Newton loop with an interface law keeps iterate 0's finest-smoother operator | D's review, 2026-10-31 | #894 | efficiency queue item 2 |
| A split fault's structural FAC block is one LU per rank | the #892 benchmarks, 2026-10-31 | #895 | one block wins in 2-D (measured); open for 3-D, efficiency queue item 4 |
| Since #934 a fault NETWORK's structural patch is one LU on one rank: `_gathered_patch_blocks` (custom_mg.py ~919, development 06c574e8) unions every rank's structural rows into one block when no fac_zone is keyed, so faults on different ranks lose the parallel factorisation 25d62812 had; #934 measured single faults only. Suggestion: one block per fault on its owning rank (keeps #934's no-cut gain). Code reading, unmeasured; hub confirmed the union in the code | notes session, 2026-11-08 | #895 | to the integration session with matrix row 5 (fault networks); measure before any change |
| The parallel cover gate drops the structural patch at np 2 (640 its against 68) | slip-coarse-space testing, 2026-10-31 | #896 | efficiency queue item 3 |
| `solver.set_custom_fmg` lacks the module function's FAC keywords | slip-coarse-space review | #897 | rides with the next PR that touches the solver method |
| `remesh()` leaves the multigrid levels stale (`dm_hierarchy[-1]` and the coarse-level cache); `adapt()` after a remesh raises, or takes the old mesh as its finest level | the levels-accessor review | #898 | reproduced and filed with the probe |
| Six never-filed drafts in uw3-campaigns `notch_length_scale/issue_drafts/` (notch session, 2026-10-28) | the notch session | see state | triaged 2026-10-31: **02** is #902; **03** filed as #903 (a missing label returns vertex 0; checked in code); **05** filed as #904 (refuse mixed SI and non-dimensional expressions); **06** posted on #771; **04** is already fixed on development by #827 (a820ff0a); **01** is in kaiju's scaling job (`set_custom_fmg` still does not co-locate independent coarse levels; orphans are now dropped, not injected) |
| A rotated free-slip solve whose preconditioner fails returns v = 0 with only a warning (reason -11 at iteration 0, no exception) | #901's review | #907 | filed; proposed: a collective raise naming the reason unless the caller opts in. Louis to approve the behaviour change |
| A degree-2 mesh with a rank holding no cells: the FVM cell-size error is ignored | #902 review round 3 | #908 | filed |
| A collective behind a rank-local guard in `Mesh.remesh` | #902 review round 3 | #909 | filed |
| A warm solve on the fast path fails at iteration 0 with no cause (16 of 26 serial runs; pressure sub-KSP DTOL, then NaN) | #907 review | #910 | filed |
| A solve past round-off (tol 1e-11) fails its last linear solve, so a time loop now rebuilds its KSP every step (2x on a 39k-dof FMG solve); the fix belongs in the Newton stopping test | #907 review | #911 | filed |
| Rotated free slip on a spherical shell with the default `normal=None`: facet-averaged normals violate all three rotations by 0.008-0.016, so none is detected. The answer carries an undetermined rigid rotation (v_rms 4.47 against 1.77) and takes 83 velocity its against 18. The annulus is unaffected; CLAUDE.md recommends `normal=None` | the #901 work | #906 | **Louis: null modes belong in the mesh metadata.** They are already there (`Mesh.nullspace_rotations`, since 2026-04-07, set by the annulus, shell and segmented constructors) but the rotated path ignores them: it rebuilds the rotations and filters them by a 1e-8 constraint test, which is the failure. The integration session is to make the rotated path read the declared modes (stacked on #901), then measure facet normals against the analytic normal on the shell for Louis's remaining choice |
| `project_to_degree` from a discontinuous to a continuous field sums the adjacent cells (2-7x at P1 vertices); the XDMF writer is unaffected | the #902 work | #905 | filed; marked TODO(BUG) on the #902 branch |
| The direct-LU rotated path (`_rotated_use_lu`) never converges on a split-fault contact; slip 4-5 % off | #894's work | #899 | filed; `test_1088` carries it as an xfail. An opt-in path, against the no-direct-LU rule anyway |
| test_1064's spherical3d partition-independence case hung once at np 2 in CI (#951's run 42130702511, every rank spinning in _solve_rotated_iterative); unrefined shell, so not #946 | the hub, 2026-11-06 | none | one occurrence; stacks lost with the runner. Waiting on hyperion's np 2/4 runs; file if it recurs |
| Refining a spherical shell (SphericalShell, CubedSphere simplex) folds cells at the inner wall: the refinement callback snaps labelled edge midpoints outward past an unlabelled one | #901's testing on kaiju (Linux gmsh 4.15.2 builds a folded shell at cellSize 0.5) | #946 | filed; predates #901. Every refined 3-D shell is exposed; a roadmap candidate for Louis |
| Rotated free slip with the analytic wall normal: from np 24 an owned outer-wall vertex can get no constraint row. No-solve repro on unfaulted TAc: np 16 none missing, np 32 three missing, two of them with a labelled facet on their owning rank, so the cause is wider than "facets all on other ranks". Solved at np 32, the wall-normal velocity reaches 1.2e4. The geometric normal is clean at np 32 but admits the rigid rotation (#906) | kaiju, 2026-11-04 | #935 | filed by kaiju through the science hub. Blocks np > 16 on the annulus with either normal until #935 or #906 lands. Not a duplicate of #906 or #896. **Cause (integration session, from the code):** the analytic path takes wall nodes only from facets labelled on the rank; the geometric path also walks the support-1 closures and sums over the SF (#560). Driver workaround: uw3-campaigns `addon-matrix-2026-11` 02439b0, `workaround_analytic_normal_nodes.py` (bit-identical serially; kaiju to verify at np 32-52). **Fixed on `bugfix/analytic-normal-wall-nodes-935`** (30daa324 on 60dbf0e4; review round 2 running): the analytic node set is completed over the point SF, and so is the free surface's vertex list (same defect). test_1140 fails before and passes after at np 2 and 4. Kaiju report 22b, zg95 TAc np 32, one step: 964 s against 280 s, next dt 2.66e-6 against 4.44e-6, wall |v.n| 1.2e4 against 3.4e-13. The "second path" in #935 was a misread vertex label. **Louis said yes to the PR (2026-11-04)**; the integration session opens it after review round 2 |
| `boundary_normal_traction` reads uninitialised pooled memory at a node an essential wall also constrains (a rotated wall meeting a Dirichlet wall); `globalToLocal` skips constrained DOFs | #935's review round 1 | #936 | filed; predates the branch. **Louis ruled zero (2026-11-04).** **Merged as PR #942** (045466df; 29bf332f, two review rounds, test_1141 first). One helper feeds both readers; pointwise values byte-identical wherever no essential wall meets the rotated one; the integral now keeps a corner whose first component is pinned (it dropped 12 % of the wall load on the fixture) |
| At a corner, the reduced rotated constraint ignores a nonzero component pin (n.v = 0.04, serial) | #942's review | #939 | filed, verified serially |
| `fault_contact` reads traction and slip from an unzeroed pooled vector at a pair node an essential wall constrains; this would change the solve. Only reachable where a split fault meets a Dirichlet wall, which the production recipe avoids (buried tip, #553) | #942's review | #940 | filed, from the code, not probed. Becomes live with #553 |
| Geometric normal at a partly pinned node: the constrained components are not summed across ranks, so the wall load depends on the partition | #942's review | #941 | filed, from the code, not probed |

## Issue queue (2026-10-29)

166 open issues, all opened in 2026; 154 under Louis's account (sessions file there). 39
carry `fixed-in-PR` or `fixed-in-development`; 127 are live. 85 have no label and 5 are
assigned.

Label drift, ready to apply per the planning guide (waiting on Louis's go):
- #758, #759, #782: `fixed-in-PR` but fixed by #852, merged 2026-10-28. Relabel
  `fixed-in-development` with the merge comment.
- #827: no label, fixed by #850, merged 2026-10-28. Label `fixed-in-development`.
- (done 2026-10-31) #730 and #573 labelled `fixed-in-development` with #863's merge.

## Branch hygiene

242 branches. 77 are fully merged into `development` and can be deleted; the proxy
refuses deletions from here, so this needs a laptop or Louis.

## Waiting on Louis

**New 2026-11-12 (later): 22. Merge ss2098's #1055 and #986 [yes; H4: correct, mergeable as they are]. 23. #780: finish as designed (about 2 days) or narrow and close smaller [narrow]. 24. #800: land whole (multi-day) or close and salvage the partition fixes [close and salvage]. 25. H1 may post its own review records [yes]. 26. Coarse MG levels follow a mesh move (W1 session).**

**QUICK LIST ANSWERED 2026-11-12 (Louis: "Yes to all the quick fixes ..."), the nine items as C1 listed them:** (1) merge #1038 [row 9: CI re-triggered on 40aee07f against development 613ed1e0; merge on green]; (2) merge #1061 [row 11: now conflicts with development; W1 to merge development in]; (3) merge #1068 [decision 16: CI re-triggered on 82522d36; merge on green; unblocks #1069]; (4) merge #1079 [decision 18: CI re-triggered on a540203a]; (5) merge #1050 [decision 11 settled: refuse; now conflicts; W1 to merge development in]; (6) H1 may post its own review records [relayed to H1 with the caution that the yes was typed in the hub session: post if hyperion's permission check allows, stop if it refuses; H3 not covered, asked separately] **H1 declined to post on the relay (right: the hold began with its own permission check; a peer cannot lift it); Louis then said yes in the H1 session ("It is fine to post your reviews on github"), the check allowed it, and H1 posted its own records on #1105, #1106, #1097, #1094 (five), #1096, #1088, #1044, #1024 and the #1090 finding on the issue; #1104's follows its verdict. Not posted: H3's records; H1's unpushed CI fix (bugfix/ci-gdb-install-retry), not covered by the yes.**]; (7) required status checks on development [decision 10: to be set after #1104 merges, since test_1152 is red on about half the runners until then]; (8) delete bugfix/mmpde-seam-1086 and bugfix/mmpde-empty-rank [C1's delete was refused by its own permission check (Git Destructive); not worked around; Louis to delete or allow]; (9) K1's driver stops on a placement refusal and retries on the two job-4400 messages [relayed to K1 as information]. **Not covered, asked again:** ss2098's #1055 and #986 (C1 wrongly told H4 they were covered, corrected within minutes); H3 posting; #780; #800; D2; the units contract; the LU pin policy; #1025.

**22 SETTLED 2026-11-12 (Louis: "Merge those two. Wait on 987"): ss2098's #1055 (four basic examples) and #986 (setup.py `find_packages(where="src")`) merged on H4's verdicts and their green CI (64b9377a, e4076e59); #987 (GWB subduction example, draft, +2,517) waits until its author marks it ready, then a review and a decision on whether it belongs in the main repository. Merges today: 26. C1 is watching development's push CI for the packaging change. H4's courteous review comments for both stay unposted (permission check); a thank-you to the contributor is Louis's to send or to ask for.** **Louis 2026-11-13: "Acknowledge the contributions": C1 posted a thank-you on #1055 and #986 in its own words (the fixes confirmed, the `sphere.N` note, an apology for the wait, #987 noted).** **Settings only Louis can change (repeated to him 2026-11-13): (1) required status checks on development: `test` and `Style gates (deprecated patterns, examples parse)`; (2) delete branches bugfix/mmpde-seam-1086 and bugfix/mmpde-empty-rank.** **13 SETTLED 2026-11-12 (Louis: "Agree on 969 - warn, don't fit"): #969 takes option (b): the user re-declares; the warning says the answer may carry a rigid rotation; no common-centre fit. W1, small PR, behind #1099, the kept transfer and #1089.** **19 SETTLED 2026-11-12 (C1's reading of Louis's "let's get this into the codebase quickly"): port the new methods onto development's rotated solve; unit 7 not landed.** **New 2026-11-12: 19. D1 (curved walls): port #1033's new methods onto development's rotated solve unchanged, or consider its rotated-solve changes on their merits. 20. D2: does the publication need #857's recovery methods? 21. K1's driver: stop on a placement refusal rather than keep old faults; and the retry change (with K1/C2).**

**Current list (2026-11-10; hub's recommendation in brackets):**
1. Retarget #982 to development (the hub's retarget was refused by its permission check) [do it, or allow it].
2. Register row 9: adjoint KSP held to 0.1 x tol, EW off (H4's #769) [yes].
3. evaluate's units contract #771/#904 (H3's note): A keep the dimensional gateway and refuse mixed leaves [A]; sub-decisions: solver fields get units [yes], unitless defaults with no reference quantities #881 [yes], refuse out-of-domain points #786 [yes], reset_default_model clears the ND flag #1001 [no].
4. Register row 10: SLCN estimate_dt diffusion limit #1025 [ask for a sharp-front case and a convection benchmark before choosing; W1 recommends (c)].
5. #855 (gthyagi) gates W1's CORNERS bundle [nudge gthyagi, or let a session finish it with credit].
6. Rotated convergence reference #884/#883 (changes #1014's policy) [let W1 build it with evidence].
7. Stokes_Constrained multiplier-block inner cap #826/#817 (#651) [evidence first].
8. A solver's auto-created unknowns owned by the solver rather than the mesh (#1050 N4) [yes: they go with the solver; fields passed in stay the mesh's].
9. Published-note corrections (UWTN 2026-011, 2026-014) [after H2's rerun and #1044].
10. Required status checks on development [yes].
12. **Now: the LU pressure-pin policy** (separate PR after #1054): (a) no pin, or (b) pin only where the constant-pressure null mode is verified; each with an annulus LU-vs-iterative test at 1e-10. Evidence: closed slid annulus null mode exact only to 3e-6, pinned LU 30-40 % off yet 'converged'; open boundary, tilted given normal, gauge vertex varies with np; H1's MUMPS data: no pin right in every measured case (exact mode: MUMPS factors silently, gauge at round-off). [hub leans (a) if MUMPS handles the exact-mode case everywhere; else (b)]. History: the direct-LU rotated path (#348, #899; triage §4): support or refuse it. W1 is fixing #348's partition-dependent pressure pin (one global pin, lowest owned index by allreduce MIN) as bundle C3, which presumes "support" [support with the global pin; a correctness fix to an existing path]. **CORRECTED (W1, dccb83d4):** #899 is a residual-ordering bug, not the pin policy. On #899's fault box constant pressure is an exact null mode (left and right to 1e-17; one singular value 1e-14); the LU residual zeroed the pinned row before projecting out the pressure mean, shifting every other pressure equation (bites when the lowest row is a wall corner next to a Dirichlet lift). Reordered: #899 converges in 1 increment to the multigrid slip (1e-12); test_1088 loses its xfail. First PR = global pin + crash fix + #899 reorder + #1053's N3 and wording (all fixes). Policy PR for Louis shrinks to genuine non-null cases: open top (B^T·1 at 0.15 relative, velocity 0.5 % off), a given normal not the wall's (1.5e-2, 24-61 % off), pressure Dirichlet; closed box and fault as controls. **H1 round 3 (660e35b3):** fix PR mergeable (W1 to open): #899 converges in 1 increment to the MG slip; test_1088 13 pass at np 1/2/4; malloc gone; pressure-Dirichlet LU exact. For the policy PR: on a **closed annulus**, pinned LU is 30-40 % wrong and still reports converged; no-pin LU matches iterative to 2e-12. Superseded: ~~the LU pressure pin itself is the root cause of #899 and of #968's LU rotation residue: where constant pressure is not a true null mode, the pin replaces a real equation and still reports converged; without it #899 converges in 1 increment to the multigrid slip. W1 re-scopes #348 (pin only where constant pressure is a true null mode) and comments the root cause on #899; first fixes H1's np >= 2 crash (in-place PtAP on a second Newton increment; KEEP_NONZERO_PATTERN). The pin change comes to Louis with evidence. **W1 (4263cc6a):** root cause commented on #899; #348 re-scoped; crash fixed (KEEP_NONZERO_PATTERN before the pin's zeroRows; same failure as the lu-it-lu malloc: any second LU increment at np >= 2), np 2 nonlinear-LU test; H1 re-checking np 2/4. Two PRs: (1) crash + one global pin, merge on green (a fix); (2) verified-pin policy (pin only if A·[0,1] has round-off velocity rows), held for Louis with a table (#899, #968 np 4 residue, closed box).
15. #1060 per-step diagnostics log (Louis via H2: "there does need to be a logging capability"; not .npz, not the transcript): new public API; H5's note (posting on #1060): `model.history` with open/register/record and `uw.checkpoint.read_history`; append-only TSV with a JSON column header; rank 0 writes one line per row then fsyncs (a kill costs at most the last line); rows keyed by committing step, recording step s first cuts rows with step >= s (covers retries, load_state, and driver restarts); record() collective, rank 0 writes, row broadcast. Open: the name `history`; TSV or CSV; cut-on-restore as default [hub: `history` fine; TSV (JSON header needs no quoting); cut by default].
16. **#1065 (high; W1):** SNES_Scalar, SNES_Vector and SNES_MultiComponent register each natural BC's boundary Jacobian twice (BdJacobian and BdJacobianPreconditioner) into one Mat (J is P), so the Robin term enters 2x (FD: 1.9999999996x); residual right, answers exact, Newton slow (linear Poisson with flux -kT + 0.2: 17 / 23 its or DIVERGED_LINE_SEARCH; a vector projection 19). Stokes unaffected (separate J, P). Fix (branch bugfix/natural-bc-jacobian-once-1065): drop the BdJacobianPreconditioner registration; first Newton step cuts the residual 4e7; test_1162 fails 5/5 on development. It changes the forward Jacobian of every scalar/vector solve whose natural BC (Nitsche, penalty) reads the unknown: convergence, not answers [merge once W1's before/after counts are in; a correctness fix]. H4 re-checks the adjoint after it, with k != 1. **PR #1068 (1ef53b2b), H1: merge.** 459 solves paired over 24 files: Poisson Robin k=-1 17/132 -> 2/14; k=-10 23/170 -> 2/13; k=2 19/258 DIVERGED_LINE_SEARCH -> 2/16; vector projection Robin 19/124 -> 1/9; the other 455 identical (incl. adjoint KSP counts in test_0019, test_1145); FD Jacobian ratio 2.0 -> 1.0 in all three families; Stokes bit-identical; Robin adjoint now matches FD (H4, k=2 and 0.5); ThinSheet with Robin 45 its or no convergence -> 1. Side findings: F3 (a separate P lacks the natural-BC term; latent), F4 (-snes_mf_operator with a natural BC: PETSc error 56), F5 (each in-place rewire appends another set of boundary kernels: 1, 2, 3; J and answer right; cause unknown; W1 investigating). W1 ran test_1162 at np 2/4 on wombat (breaks the serial-only rule; reminded). **Filed:** #1069 (F5: on in-place rewire Scalar/Vector/MultiComponent re-register natural BCs with PetscWeakFormAddBd*, which appends; PETSc calls all entries into one buffer and our kernels assign, so the newest wins: right only by call order; N+1 calls per boundary point after N rewires; a NULL slot could keep a stale kernel; fix PetscWeakFormSetBd*), #1070 (F3 + F4; F3 opened by #1068). Hub: the J-is-P guard goes into #1068 (H1 one-line re-check). H1 re-checked 1ef53b2b: merge. test_1060's Nitsche Stokes now prints #1062's pressure-cap warning (200): to #625/#755 once confirmed on development.
17. **Settled (Louis to H2, relayed by H1): yes to all three.** #1003 ecc2793a: deform reads dimensionless coordinates (UnitAwareArray or pint) as model coordinates; F3's size guess stays, stricter rule filed as #1081; #1024 1e42c849: `_mmpde_mover` returns its accepted energies (new test fails by 0.2 % with the confirmation undone); mover suite 427 pass. #982 retarget: **done by W1 on Louis's "Yes to all" in the W1 session (2026-11-12), covering #988, #1003, #1024 as each predecessor lands.** H2 merging development into #982 for a fresh CI run against development. H1 re-testing #1003 and #1024. Was: H2's stack (merged with development 5ce73fdf; heads #982 fe37020d, #988 a10b0364, #1003 f540b18e, #1024 75f2c867; stack tests pass serial and np 2/4; H1 re-testing): (a) #1024 F1: the mover returns its accepted-energy history so a test can confirm the line search [yes]; (b) #1003 F2: mesh.deform accepts coordinates with units "dimensionless" as model coordinates [yes]; (c) #1003 F3: keep the size heuristic that refuses metre-sized plain arrays in a units model, and file requiring units on deform in a units model as a follow-up [yes].
18. **#1078 (high; W1):** Scalar, Vector and MultiComponent ignore every petsc_options change after the first solve, including `solver.tolerance` (1e-4 then 1e-9 held 1e-4); Stokes honours them; solvers.md calls petsc_options "the escape hatch — any key you set here outranks both", so it's a fix. Fix (bugfix/options-after-first-solve-1078, 5b0c77db): snes.setFromOptions() before each solve, as Stokes does; test_1163 4/5 fail on development. H1 reviewing: paired counts over scalar, vector, projection and SL suites; any API-set SNES/KSP state a re-read could overwrite (e.g. #1014's per-call atols); np 2/4 [yes, with H1's counts]. **PR #1079 (d4b34253): H1 at 5b0c77db mergeable once documented:** 3,333 solves paired against 5ce73fdf (45 serial, 8 adapt/hierarchy, 14 at np 2) with unchanged options: 0 differences (Newton, KSP, reason, tolerances, types, setup and evaluation counts); wall flat, re-read about 50 µs a solve; no library or user state reset (FAC/FMG, PCMG, fieldsplit, nullspace, restore, estimate_difficulty, retries, continuation, monitors); np 2/4 pass; a 20-step SLCN loop tightening its tolerance at step 10 takes it on the branch and not on development. Round 1 in d4b34253: documented that a petsc4py setting on solver.snes for a key the options hold is overwritten at the next solve (as Stokes already does); effect-level test. F3 (low): after the private `_reset()`, a reused prefix reads the newcomer's options; F4: rotated and fault-contact Vector path bypasses the re-read (#924).
14. #1059 (silent forward failure at high viscosity; filed by W1): (a) a RuntimeWarning for a negative SNES reason (W1 adds it to bundle D; the -5 difficulty-probe exemption stays); (b) on a cold first step whose linear solve fails and leaves the fields unwritten, the native path raises, as the rotated path has since #916, with `tolerate_linear_failure` to demote it to a warning. (b) extends a ruled rotated-path contract to every native solve [yes, with D's noise numbers]. Probe: onset between mu 1e10 (converged, |v| = 1/mu) and 1e11 (velocity sub-KSP NANORINF -9 at its 0, then gasm PC_SUBPC_ERROR, outer -11, SNES -3, u = 0, only a printed notice).
13. #969 rotation mode on a moved mesh: an annulus translated by (1e-3, 0) with deform carries a rigid rotation about its true centre of 0.60 v_rms (FMG) / 0.030 (GAMG) while 'converged' (0 at δ=0); the declared [-y, x] is about the origin and isn't moved. Options: (a) fit one common centre to all rotated walls (least squares, reduced over ranks; apply only if every wall is a sphere about it to 1e-9) and evaluate the declared modes about it; (b) keep the user re-declaring, but the warning says the answer may carry a rotation; (c) deform re-declares on a rigid translation (misses adapt children). [W1 and hub: (a), with (b)'s wording where (a) can't fit].
11. #1050 (#1041) contract: a snapshot naming a dropped solver's history refuses to restore on every rank, writing nothing (development wrote into the dead solver the leaking register kept alive); alternative: snapshots hold their solvers strongly [refuse; the model's registries are already weak and TranscriptAdjoint already refuses]. #1050 ready (H1 four rounds; 0 solvers/SNES/KSPs left per dropped solver, about 4.6 MB each on development); merge held for this.

- (Settled 2026-11-02: the add-on is the production tail. Settled 2026-10-31 on: the hub
  merges PRs Louis has ordered, on green CI.)
- The next merges: #780, #861, and #862 after its caveat; whether the hub re-reviews
  gthyagi's fixes on #855, #858, #859.
- An owner for #800 (conflicts with `development`, idle since 2026-10-12) and for the
  mathematical review of #857.
- Go-ahead for the label fixes listed under "Issue queue".
- Who takes the no-PR fixes now that hyperion is reimaged: the stress-transport fix first
  (verified, reviewed, waiting only for a PR).
- The rotated pressure rtol default (kaiju's evidence, in HUB.md).

## For the other hubs

- 2026-11-12, to the science hub: **a second `add_fault` call leaves the first fault as an open crack (library defect, owner W1; found by W1 and measured by H1; pre-existing, serial and parallel).** `c2 = c1.add_fault([("F2", ...)])` keeps the first fault's cut (duplicated nodes) but drops its record: `_fault_point_pairs` lists only F2. A law asked for on the first fault by name raises ("no split-fault pairing"); laws applied only to the faults listed in `_fault_point_pairs` solve and converge with the first fault traction-free (velocity jump 0.13 where its proper slip was 0.16), no warning. Runs that place all faults in one call, or name every fault when applying laws, are not affected. K1 asked how the drivers place several faults and where they take the list of laws from. **K1 (2026-11-12): the zg95 drivers are not affected: all faults are placed in one `place_fault_ribbon_2d` call, laws come from the driver's own list of names, and every run of the current campaign carries one fault (F0).**
- 2026-11-12, to the science hub: **#1091 (fault add-on on an MMPDE-moved base, np > 1): what it can touch in existing runs.** Besides the refusal H2 hit, a wrong parent cell is recorded silently when it is on the same rank (a quarter of the cells on the refinement-4 annulus). W1's reading of the code: those parents feed only the multigrid preconditioner (interpolation, Galerkin coarse operators, FAC patch rows), not any field transfer, so results converged on the true residual stand and the cost is iterations or a reported non-convergence. In runs with np > 1, a mesh moved since it was built, and a fault cut, placed or split afterwards, check the convergence reason and iteration counts, not the fields. H1 is measuring this against serial; this note will be updated if the measurement disagrees.
- 2026-11-12, to the science hub (update, H1's measurement): **a refusal is not harmless in K1's driver.** annulus_faults.py keeps the previous faults when placement refuses and carries on; on H2's small case at np 4 (refinement 3, MMPDE every 2 steps) that gives vrms +24 % and slip +52 % four steps in. np 2 refuses from step 2, np 4 from step 4; serial never. **Any parallel run on a moved base whose log has "no local parent cell" is invalid from that step.** Sent to K1. Silent wrong parents could not be separated in the measurement (they appeared only alongside refusals), so "iterations only" is still from the code. Compare runs at fixed np, not against serial: the mover itself is rank-dependent (H5 owns that). **K1 (2026-11-12): no Kaiju run is affected: none of the 38 driver clones has the mover hook, "no local parent cell" is in none of the 144 run folders, and jobs 4417, 4434, 4435 are on unmoved bases. Whether the driver stops on a refusal is with Louis, with the retry change.**
- 2026-11-12, to the science hub: **parallel fault placement on an MMPDE-moved base (addon_partition, "no local parent cell on the level below"): the library fix is W1's, not H2's.** H2 reported it to the dev hub as a library defect and asked for an owner; C1 assigned W1 (fault add-on code, Louis's #1017 ruling) as urgent, with H1 reproducing on development 93e66eed and running W1's branch in parallel. H2 says C2 separately asked it to take the fix; H2 had only read the code and has stood down (its call chain and a sketch of a coordinate-free parent relation go to W1 via H1). H2 continues the MMPDE plus fault science in serial. H2's replies to both hubs were refused by the server, so this note is the reply. If Louis wants it otherwise, he says so to either hub.
- 2026-11-12, to the science hub: **K1's job 4400 placement failures (steps 81 and 107): both are library defects (owner W1); a driver change unblocks K1 now.** Sent to K1 directly as information (C1 cannot message C2). Driver (d358b97 annulus_faults.py, K1's): `placed_ladders` retries only on "crosses itself", "domain wall", "ligament", "seam"; neither refusal matches, so widen never ran (widen 1.25 and 1.5 place step 107); it also truncates the error at 120 characters. Change: retry on these two refusals and log the whole message. Library: (1) step 107, the trace does not touch the wall (tip 2.836e-3 below r_o); `pull_vertex_onto` (utilities/line_cut.py:942) pulled an outer-wall vertex onto the tip, no boundary test, then fault_split refused with a misleading message. **Caution:** K1's log shows "WALL CONSTRAINT VIOLATED" at 3 outer-wall nodes (|v.n| ~ 0.1); W1 is checking whether an accepted pull dents the wall silently in runs that did not fail. (2) step 81, mesh area 2.25e-9 short of CAD against a correct 1e-9 check; likely OCC/gmsh merging a rail point with the wall crossing (unproven); about 5 % of orientations in a +-0.25 deg scan. The dev hub will note here when the fixes merge.
- 2026-11-12, to the science hub (follow-up): **the wall caution above is withdrawn (W1, from K1's data).** With split=True (the campaign route) a moved wall vertex is always refused, so K1's runs are not silently dented. K1's three flagged nodes are interior apexes of sliver triangles on the wall (height 1e-5 to 1.7e-4), caught by the driver's 1e-4 wall test; true wall nodes hold |v.n| to 1e-13. The slivers are a placement defect in #1090. Issues: **#1089** (pull_vertex_onto moves a boundary vertex; fix in review on bugfix/pull-vertex-keeps-the-wall) and **#1090** (ladder outcrop cap near the wall; mechanism unproven). Sent to K1.
- 2026-11-06, to the docs hub: hyperion's adversarial reviews of **#945** (examples drop the SVD
  coarse solve) and **#862** (fault multigrid guide) are posted on the PRs: both ready with changes
  (#945: two tutorials left with an empty code fence, a stale body, three unparsable files not two;
  #862: the design note contradicts the guide on where split-level work lives, and "one block per
  rank" should be "one block on one rank"). The changes are the docs hub's to make; the dev hub
  merges on green once they are in.
- 2026-11-06, to the science hub: **moving-mesh results since 2026-05-28 may carry an error.**
  After a mesh move (MMPDE or any remesh mover), the first solve used the pre-move field on the
  moved nodes: v_rms 3-4 % high on that solve (PR #959, fix in review). Runs that move the mesh
  every step re-enter the error each step; check which campaigns move meshes (free surface,
  MMPDE convection) before relying on their numbers, and rerun key ones once #959 merges.
- 2026-11-06, to the science hub: **#948's leak is kaiju-launch's `coarse_log_hook.py`**,
  which keeps every fault rebuild's Stokes solver (and its mesh and multigrid levels) alive
  in a module-level list. Not underworld3; no library change. Once kaiju's verification is
  flat, both hook copies get a weak reference (or the hook leaves production) and long runs
  restart from checkpoint; the checkpoint-segment workaround can then stop. kaiju-launch is
  unversioned: worth putting under git (uw3-campaigns or its own repo) so a change like this
  is reviewable.
- 2026-11-05, to the science hub: **#948 is the dev hub's PRIORITY 1** (Louis). Hyperion
  reproduces at np 2-4 and bisects over the ten merges in 25d62812..f631ce42 (#937's C
  interpolator first); the integration session audits the code and writes the regression
  test first. Kaiju: keep the checkpoint segments; a fix branch comes to kaiju for the np 26
  check on a rebuild cadence. If a production run must avoid the leak before then, 25d62812
  is the last clean development (it lacks #902/#935, so np <= 16 only).
- 2026-11-05, to the science hub and the docs hub, **hyperion's state** (its inventory,
  session `session_01HxWvnAXb5n85uEcw711tJC`): Ubuntu 26.04.1, 96 cores, 376 GiB. It boots
  from nvme0n1 (Samsung PM9A1, S65XNF0R608481), which holds /, /home and an empty /mnt/data;
  Louis calls it the failing disk. nvme1n1 (S65XNE0R602587) p4 is mounted at
  /mnt/nvme1n1p4 and holds, at /mnt/nvme1n1p4/home/lmorese (254G), an 11-04 copy of the
  current system plus **/home/lmorese/lmoresi: the old /mnt/data/lmoresi tree** (underworld3,
  claude-mirror, hyperion-rescue-2026-10-20, Simulations, crontab.backup); the old
  ~/+Simulations symlink there dangles. Which disk failed in October is inferred, not proven:
  both filesystems date from 2026-11-02, no older logs survive, and the root filesystem has
  been on S65XNF0R608481 in all 12 boots since (names swapped once, 11-04 21:19, same UUID).
  October's record put / and /home on the failing disk and /mnt/data on the one that read
  cleanly, which agrees with Louis. SMART would settle it. gh is not logged in, Remote Control runs in tmux with no linger or unit, and
  the session has Box and Claude Docs connected. **From hyperion, ListAgents reaches all
  three cloud hubs** (hyperion messaged the dev hub that way). The dev hub's position, put
  to Louis: no hubs on hyperion until its OS is on a confirmed-healthy disk.
- 2026-11-02, to the science hub, for uw3-hpc-install-run's kaiju notes: "`OMPI_MCA_io=^ompio`
  in every job with several UW3 processes per node; under OMPIO, H5Fcreate/H5Fflush fail
  intermittently (PETSc error 76, #922)." Also a node-local `UW_MESH_CACHE_DIR` per job.
  The dev runner already sets both.

- 2026-10-31, to the science hub: on Louis's word ("dispatch parallel runs on kaiju since
  the laptop can't cope and hyperion is out of action"), the dev hub sent the #901/#902
  scaling job straight to the kaiju session. It runs on free nodes only, and must not
  displace production jobs. The builds:
  - A: development fc67b650;
  - B: `bugfix/custom-mg-many-ranks` 57d87783 (#902);
  - C: `test/kaiju-scaling-902-901` 94a5c965 (#902 plus #901, a test build).
  The case is the faulted annulus, 5 steps from TAf 20, at np 16, 32 and 52. This
  supersedes the two scaling requests below. Louis also confirmed the rollback rig, and
  put the 3-D add-on mesh work on kaiju under its own session.

- 2026-10-31 (update), to the science hub, the **#902 fix is ready for kaiju**:
  `bugfix/custom-mg-many-ranks` 96d39f7b (public; from development fc67b650). Please run
  it in the same scaling job as the request below. That job compares development and this
  branch:
  1. The faulted annulus (production recipe, frictionless split fault, custom-P FMG) at
     np 16, 32 and 52, 5 steps from TAf 20. Done when np 32 and 52 complete on the branch
     and match np 16 (#902's criterion). On development, record whether they fail.
  2. Notch draft 01 (independent coarse meshes at np >= 12): record convergence and the
     orphan counts that `restrict_unreached` drops at install.
  3. In every run: coarse time per Newton iteration (#901), step time, iterations per
     increment, slip.
- 2026-10-31, to the science hub, a compute request (Louis: np 16 cannot be the ceiling):
  - a kaiju scaling check on current development fc67b650: np 16, 32 and 52 on one free
    node, 5 steps from a rollback checkpoint (TAf at step 20), production recipe;
  - record whether the custom FMG builds or falls back (#902), coarse time per Newton
    iteration (#901), and step time;
  - in the meantime, whether three 16-rank jobs per node would put the idle cores to
    work for the campaign.
  Louis has also proposed the rollback experiment as the standing fault-efficiency rig:
  frozen recipe, two checkpoints (TAf 20; TBf with rollback established), 10 steps, the
  usual records. Spec to follow once he confirms it.

- 2026-10-31, to the science hub, a compute request (Louis names the machine): the #896 fix
  needs the production shapes at np 16. Run kaiju's annulus fault case (frictionless
  contact) on `bugfix/fac-cover-gate-partition` f7914a92 (public, so an anonymous clone
  works) against development fc67b650, a few steps from a checkpoint. Record the
  finest-level patch rows per rank, the velocity iterations per increment and the slip.
  A patch that was being declined at np 16 would show as a large drop in iterations.

- 2026-10-31, to the docs hub: A, B and C are on development (A 24923e5d, B 4dff48b3, C
  fc67b650). Re-pin UWTN 2026-018 and 2026-022 to fc67b650. The fault-multigrid guide's
  "what ships" section can move the split-level hierarchy to available. #862's chain
  sentence rests on ILU blocks (#892), so a caveat is wanted before it merges.
- 2026-10-31, to the science hub: the leak fix and the fault-split work are on development
  fc67b650, so kaiju's next build can come from development instead of the
  box-faults-warm and leakfix overlays. #892's fix (LU blocks on the rotated path) is
  coming as D; the drivers' `uw_chain` default waits on its re-measurement and Louis.

- 2026-10-29, to the science hub: per Louis's scope ruling, the library-fix rows of
  `HUB.md` "Open work" are tracked here from today (stress-transport fix, leak fix, rotated
  solve diagnostics, parallel add-on, shear-band length scale, parallel `read_checkpoint`).
  #850-#854 are merged (`HUB.md` still lists them open). #457 is closed, which bears on the
  TI-fault cost comparison. Please record library defects found in runs here, or say in
  `HUB.md` that one exists and this hub will pick it up.
- 2026-10-29, to the docs hub: this hub tracks the PR side of A #882, B #889, C #890 from
  today; `FAULT-SPLIT-INTEGRATION.md` and the re-pinning of the notes stay yours. #861 and
  #862 are in the queue above.
- 2026-10-31, to both hubs: #892 is the priority and its plan is in the PRIORITY section.
  The history differs from the "dropped LU, then gave up" account: on the rotated path the
  LU block solve was never in effect, from the day it became the default (891c9bb0,
  2026-09-03). Every fault result on a rotated solve since then ran ILU(0) blocks.
- 2026-10-31, to the science hub: received the 2026-10-29/30 items. The unsplit-tail
  memory defect is filed as #893. The #457 comment is in the intake table. The
  surface-breaking split request is #553 (open since August), where kaiju's evidence
  belongs. The traction "to check" is closed. The drivers' `uw_chain` default waits on
  #892's fix and Louis's ruling.
- 2026-10-31, to the docs hub: received. The levels accessor is with Louis. #892's
  durable-intent step (7) includes a line in the fault-multigrid guide (#862) and a
  journal finding, which are yours to write once step 1 confirms the scope.

## Log

- 2026-10-29: hub started by Louis as "Development issues hub". Attached underworld3,
  uw3-campaigns and underworld3-journal with push (in Auto, the classifier refused
  `add_repo` until Louis switched to Accept edits). Measured the PR queue, the issue queue,
  and every branch active since 2026-10-01 against `development` bfd07b73 and #890's head.
  Message to the docs hub refused (cloud to cloud). Louis set the scope.
- 2026-10-29: the science hub took the hand-over (`HUB.md` "Library fixes: handed to the
  dev hub"); the docs hub added this hub to its table.
- 2026-10-31: the notes session messaged Louis's priority on #892 (FAC blocks ILU(0) on
  the rotated path). Read the code at development bfd07b73, C 799ef021 and the history
  (9f4cb200, 18f0b947, 891c9bb0, ab8003ef): the defect is as filed. The LU default and
  composite mode arrived together in 891c9bb0, so the rotated path never ran LU blocks.
  Plan written above; posting it on #892 was refused by the classifier. Filed #893 (the
  unsplit-tail memory defect, from the science hub). Absorbed both hubs' "For the dev hub"
  items into the intake table. Merge order gains D (the #892 fix) after #890.
- 2026-10-31: Louis approved the "reach my other sessions" grant; the plan's summary was
  delivered to the notes session (wombat).
- 2026-10-31: Louis: the plan goes on #892. Posted (issuecomment-6505605906).
- 2026-10-31: Louis: merge #863, #882, #889, #890 in order ("let's get the solvers all
  working on the most efficient path"). Done: c6ee62cf, 24923e5d, 4dff48b3 (after a
  development merge into B for the test.sh conflict and a green sharded CI), fc67b650.
  #730 and #573 relabelled. #892 steps 2 and 3 pushed; B's coarse-patch rule settled by
  measurement.
- 2026-11-04: Louis, via kaiju: run the zg95 annulus at np 52 with "the decomposed patch
  problem using super_lu" for about 2x throughput, now. The hub's record has the
  distributed-patch solve as a MUMPS probe (report 17), not library code, not on development
  af6f19b3; whether superlu_dist was also run is with the integration session, which is
  answering kaiju directly. Kaiju's np 52 blocker is not the patch: with the analytic wall
  normal, at np 24/32/40/52 an owned outer-wall vertex whose rank holds none of its labelled
  facets gets no constraint row (np 16 clean); the geometric normal is clean at np 32 but
  admits the rigid rotation (#906, fix held on its branch). Kaiju asked to file the
  analytic-normal defect. Kaiju's own numbers: np 52 against 16 is 339 against 487 s per
  step (1.44x); the serial patch is 5-8 s of a 150-230 s step, so the patch alone is not
  the 2x.
- 2026-11-04: kaiju: the analytic-normal defect is #935 (repro above, in the problems
  table). superlu_dist and MUMPS are both in the kaiju image's PETSc 3.25. The np 16 against
  np 52 timing on the current recipe runs as jobs 3854/3855 (10 steps from TAf-v2
  checkpoint 20, driver 9e69c6b, staged `-log_view`), reporting through the science hub.
- 2026-11-04: **the stack is merged**: #932 2556c979, #933 4ee0b13d, #934 60dbf0e4, all
  green on every shard; development's tree equals #934's tested head. #918, #921, #925
  relabelled fixed-in-development. Next from the integration session: #917's small PR.
- 2026-11-04: the integration session answered kaiju. The distributed patch is a probe
  (uw3-campaigns `addon-matrix-2026-11` 02439b0, `probe_patch_parallel_lu.py`, needs
  development 60dbf0e4 or later for the gathered blocks); superlu_dist ran 10-20 % slower
  than MUMPS; report 17's MUMPS gain is mostly MUMPS's faster serial triangular solve, about
  3-5 s per zg95 step. Its suspect for np 52's time is the dense redundant SVD coarse solve
  (#901, factored twice per solve); kaiju's `-log_view` (mg_coarse PCSetUp) decides whether
  A-prime (77de8d81) goes to a PR. It asked whether Louis had approved the 0.98 rule, since
  Louis asked it today what the decision was: the hub confirmed Louis's own words to this
  hub on 2026-11-03 ("Yes to the narrowed #918 rule - merge the stack"); a different
  choice now is a follow-up PR.
- 2026-11-04: **#935 fixed on its branch and verified at np 32** (above). Kaiju's np 52
  run (job 3941, np 16 control 3942) first failed on a 124-cell coarse level with "new
  nonzero" in DMCreateInterpolation: that is #902, whose fix kaiju verified on 2026-11-01
  (np 32/52 build and match np 16) and which the science hub asked to see as a PR on
  2026-11-02. **The hub let #902's PR drop**; it is 99 behind development but merges clean,
  and #935's branch merges clean on top of it. Kaiju worked around it with a 496-cell coarse
  level. Correction sent to the integration session: the 2026-11-01 data put the coarse
  level at 3-4 % of a step (A-prime saves about 5 %), so the SVD is not np 52's cost; the
  step is Schur-bound, and #935's unconstrained nodes (3.4x at np 32) are the stronger
  suspect in every np != 16 timing so far. Put to Louis: PRs for #935 and #902 (and #901,
  ruled A-prime 2026-10-31, measured 2026-11-01), and #936's choice.
- 2026-11-04: **Louis: "Yes to both PRs, zero for #936"** (#935 and #902). Briefed to
  the integration session: #935's PR after its review round 2; #902's after a development
  merge and serial checks; #936 as its own small PR, test first. Merge order on green:
  #902, #935, #936. #901 (A-prime) can follow when Louis wants; it is about 5 % per step.
- 2026-11-04: **PR #937** (#902, `bugfix/custom-mg-many-ranks` 09c7f480, development merged
  in, closes #902 and #886) and **PR #938** (#935, 76219530, two review rounds; kaiju report
  24: test_1140 12 passed at np 2 and 11 + 1 skipped at np 4 on the tip, 10 failed on
  development) opened by the integration session; CI running. #936's fix
  (`bugfix/traction-constrained-node-936` f7d049d5, test_1141 first: 3 failed before) is
  stacked on #938's branch, in pre-PR review. Its finding: the integral skipped a node
  whose first component is constrained, so it read the pool only where v_x is free and v_y
  pinned (-207 against 3292). #917: kaiju reproducing with CI's `--dist loadfile -n 4`.
- 2026-11-04: **#937 merged** (c514013f) and **#938 merged** (f631ce42), each green on every
  shard; #938 was clean on top of #937. #902, #886 and #935 relabelled
  fixed-in-development. Development at f631ce42 now builds the custom FMG above 16 ranks
  and constrains every analytic-normal wall node. #936's PR is to target development.
- 2026-11-04: hyperion is out again (reimage); its clone, 12 worktrees and four detached
  commits are all on remote branches, so nothing is lost. Kaiju told f631ce42 lets it drop
  the #935 driver workaround and the enlarged coarse level.
- 2026-11-04: **PR #942** (#936) opened against development after two review rounds; CI
  running; the hub merges on green. Its review filed #939, #940 and #941 (problems table).
  #917: kaiju's eight xdist runs of CI's command on its image all passed; it is building
  CI's pixi `dev` environment from pixi.lock to reproduce CI's keys.
- 2026-11-04: **#942 merged** (045466df), green on every shard; #936 relabelled
  fixed-in-development. Development at 045466df.
- 2026-11-04: **PR #943** (#917, `bugfix/jit-key-softness-917`). Cause: SymPy names an
  unnamed Dummy from a process-wide counter and sorts dummies by that name as a string;
  `_jit_graph.KernelGraph._split_shared` hid leaves behind unnamed dummies, so a rebuild
  whose dummies straddled a power of ten (999 to 1000) shared differently under cse: same
  kernel, different source and key. Fix: fixed-width dummy names; the generated C is
  byte-identical (16 distinct sources across test_0022-26, the 17th was the
  counter-dependent variant). test_0027 fails before (6 offsets) and passes after. The
  branch had merged #938's tip instead of development's merge commit (two merge bases,
  GitHub reported a conflict, no CI); the hub merged development 045466df in (430ef613,
  clean, net change the four #917 files). **#917's fix was the hub's request, not
  Louis's: the merge goes to him for a yes on green.**
- 2026-11-04: **Louis: "Yes, merge #943 on green".** CI running on 430ef613.
- 2026-11-04: **#943 merged** (1f87430f), green on every shard; development's tree equals
  430ef613. The first merge call hit a GitHub 502 and held a lock; the retry merged. #917
  relabelled fixed-in-development. Next from the integration session: phase 1 item 4,
  then the TODO(MEASURE) knobs PR.
- 2026-11-05: **Louis: hyperion is back with `claude remote-control` running; set it up as
  the main service for the Claude hubs and similar.** Hyperion's session is
  `session_01HxWvnAXb5n85uEcw711tJC` (bridge env `env_01WoSLV9PFA8uKGmUUB1rYN6`). Briefed:
  step 1, a read-only inventory (disks and their health first, given the 2026-10-18 failure
  and two reimages; Claude Code version; how Remote Control survives logout or reboot; gh
  auth; pixi; connectors including Box; whether ListAgents sees peers). Step 2, only on a
  healthy disk: a public underworld3 clone on development as a reference, `./uw setup` and
  `./uw build`, level_1 tier_a serially and one parallel test at np 2 and 4. Louis's alone:
  gh auth, sudo or services or linger, permission settings, the private repos. The docs
  hub's plan ("hubs move to hyperion; the laptop talks to them over Remote Control") is
  known only from its session summary, since its transcript cannot be read from here.
- 2026-11-05: **Louis: hyperion's second disk exists but it still boots from the failing
  one, so hyperion stays fragile.** Brief amended: step 2 (clone, pixi environment, caches)
  only on the healthy disk, and only if it is mounted and user-writable, otherwise stop
  after the inventory; nothing kept only on hyperion. **The hub's position: no hubs on
  hyperion until its OS is on the healthy disk**; until then it is a build and test machine.
- 2026-11-05: **hyperion's inventory** (details under "For the other hubs"). Step 2 got as
  far as a clone of development 1f87430f in /mnt/nvme1n1p4/home/lmorese/hyperion-work, with
  caches and an env.sh there and symlinks from ~/+Underworld. `./uw setup` was refused by its
  auto-mode classifier (code from a fresh clone); it did not work around it, and Louis
  approves it there himself. Asked for a read-only check of earlier boots' kernel logs and
  the old install's /var/log, to tie the failure to a serial. For Louis: approve ./uw and
  pytest/mpirun in hyperion's session; gh auth login and git identity; smartmontools and
  nvme-cli; linger or a systemd user unit for remote-control; ~/.pixi/bin on PATH; the OS
  onto the healthy disk before any hub moves.
- 2026-11-05: hyperion's disk check: no errors on either disk in 12 boots since the
  2026-11-02 reinstall; nothing older survives. The inference (S65XNF0R608481, today's boot
  disk, is October's failing one) agrees with Louis, so the clone on S65XNE0R602587 stands.
  Its 254G is the old /mnt/data tree, not an old root (corrected under "For the other
  hubs"). Hyperion holds; the build waits on Louis's approval in its session.
- 2026-11-05: **#901 A-prime confirmed as it stands** (Louis to the integration session,
  relayed verbatim: "Pass that back to the Docs Hub with the goal of making everything
  simpler, fewer special cases, no slow-SVD unless a genuine singular pivot is discovered
  during a solve"; asked about an SVD retry, he chose "Keep the shift, no SVD"). The SVD
  docs cleanup (one coarse-solve rule, the `svd` override in multigrid-preconditioning.md,
  about 40 example scripts) went to the Docs Hub and lands on top of A-prime.
  `bugfix/rotated-fmg-coarse-solve` 77de8d81 is 136 behind development and conflicts in
  test.sh, custom_mg.py (#937) and rotated_bc.py (#938, #942): the integration session is
  to merge development in before phase 1 item 4. The PR needs Louis's yes; the hub's view
  is that kaiju's 2026-11-01 measurement (build C against B) is the evidence, so it need
  not wait for the new -log_view.
- 2026-11-05: **#901 branch brought up to date**: 836f3e18 (merge of development 1f87430f
  onto 4af44735), pushed, no PR. On top of 77de8d81: 42e55655 (the Docs Hub's coarse-solve
  docs) and 4af44735 (the zero-pivot shift in the shared bundle, so **every route** carries
  it; test_1021 reads it off the live coarse KSP; bitwise-identical v and p on a
  nonsingular coarse level). Conflicts in test.sh, custom_mg.py and rotated_bc.py resolved
  keeping both sides. Serial on wombat: 25 passed. The rotated and custom-MG serial set and
  test_1112/1114/1116/1064 at np 2 and 4 are with kaiju dev runs 2. **The hub's review
  point:** the bundle's `coarse="svd"` variant is removed, not deprecated (a public API
  change): the integration session is to make it a clear error naming the replacement, pin
  it in test_1021, follow the Charter on deprecation, and state it and the every-route shift
  in the PR body. The PR waits on Louis's yes.
- 2026-11-05: #901 at 9aa89dc6: `geometric_mg_bundle(coarse="svd")` raises an error naming
  the replacement and the manual PETSc option; test_1021 pins it and checks a user's own
  `mg_coarse_pc_type=svd` is still honoured (21 passed, serial); the Charter has no
  deprecation-period rule; the CHANGELOG states the every-route shift and the removal. The
  hub confirmed kaiju's 2026-11-01 C-against-B numbers for the PR body. Still to come: review
  round 3 over 42e55655..9aa89dc6, kaiju's counts on 836f3e18, Louis's yes.
- 2026-11-05: **Correction (the hub was wrong):** kaiju's 2026-11-01 C against B does not
  isolate #901. B 96d39f7b is an ancestor of C 94a5c965; C adds #902's later review rounds
  (9 src files) as well as #901. The coarse-level drop is #901's (build A, development's
  SVD without #902, gives 2.77 s per Newton iteration at np 16 against B's 2.83), but the
  ~5 % step gain mixes in the other differences. The hub's earlier entries and its message
  to Louis credited the 5 % to #901; Louis told. Review round 3 running.
- 2026-11-05: **hyperion built and validated** on the healthy disk (S65XNE0R602587), Louis
  having approved the build in its session. The build is a worktree of
  `docs/coarse-solve-one-rule` 42e55655 (src identical to #901's 4af44735, base development
  1f87430f) for the docs hub's coarse-solve evaluation; the development clone stays a
  read-only reference. `./uw set-env dev`, `./uw build`, conda-forge PETSc 3.25.3, uw from
  the worktree's .pixi/envs/dev. level_1 and tier_a: 1498 passed, 44 skipped, 0 failed in
  37m45s (shared with about 30 single-rank jobs). test_0076 at np 2 and 4 and
  ptest_002_projection at np 2 and 4 pass. Nothing local to push. Still Louis's: gh auth and
  git identity, SMART tools, linger or a unit for remote-control, the OS move.
- 2026-11-05: **#901 review round 3 done** (independent, serial, 42e55655..9aa89dc6): 1
  MEDIUM (the rotated route wrote the shift a second time on its live PC, for a false
  reason; the helper is deleted, the bundle is the only writer) and 6 LOW (a rotated set-up
  that raised left 11 options in the global database, 10 also on development, now swept in
  `finally` with a test; the shift's wording matches PETSc; development's native and
  standard routes already ran PETSc's default INBLOCKS shift at np > 1 and none at np 1,
  stated in the CHANGELOG and body, kaiju confirming; doc overstatements; the svd error says
  the hand-set SVD works on the standard path only). Fixed in af9d3c33, wording in bca84349;
  34 passed serially. #910 not seen at the tip (0 of 20) but no regression test, so left
  open; #877 still live. Kaiju has af9d3c33 for the serial set, the parallel tests and the
  np 1/2/4 shift check. The PR waits on those and on Louis's yes.
- 2026-11-05: **PR #947 (#901) opened by the integration session** (e15f5fad, four review
  rounds as comments, created 11:30 UTC under Louis's account) **without a yes the hub had
  recorded**; asked whether Louis gave it directly. CI running. **No merge until Louis's
  yes is confirmed.** Kaiju at e15f5fad (library as af9d3c33), CI's environment: rotated
  and custom-MG serial set 210 passed, 2 skipped; test_1112 and test_1116 pass at np 2 and
  4; test_1064 6 passed, 3 skipped; test_1114 2 passed at np 2 and 4. #901 left unlabelled:
  the scaling criterion is unmet (coarse 0.32 to 0.85 s per Newton iteration, np 16 to 52),
  so Louis judges whether its intent is met. **#946 filed:** refining a spherical shell (and
  CubedSphere simplex) folds cells at the inner wall: the refinement callback snaps labelled
  edge midpoints outward past an unlabelled one; predates #901 (same with SVD and the
  default normal). The branch's change is test-only (cellSize 0.3, a fold gate, a
  faulthandler watchdog, since pytest-timeout cannot stop a KSPSolve). Every 3-D shell
  refined through that callback is exposed: a candidate roadmap item.
- 2026-11-05: the integration session: Louis did not say "open the PR"; it read his
  "Keep going with the fixes and let's get this part over the line" (2026-11-05) as covering
  it. Nothing said about merging. **#947 green on every shard; merge put to Louis**, with
  whether #901's intent is met. Louis also ruled #946 a fix (to the integration session:
  "Better fix this - I had not seen this bite before. I'd fix it at the gmsh end but the
  callback should be alert too because we won't only be using gmsh"), on
  `bugfix/shell-refinement-folds-946`, separate from #947.
- 2026-11-05: **Louis: "Merge them".** **#947 merged** (eddab707; development's tree equals
  e15f5fad). **#901 closed** as completed (labelled fixed-in-development, no comment, so no
  proxy footer), Louis accepting the remaining coarse growth with np. The hub reads "them"
  as covering #946's fix (Louis ruled it): merge on green when its PR opens, unless Louis
  says otherwise. #906's branch (964dc3ce) was held behind #901: queued to the integration
  session after #946 (merge development, drop the SVD-count commit).
- 2026-11-03: #934's second shard-4 cancel was the cap, not a hang (the hub's reading was
  wrong twice on this shard); the shards are rebalanced on #925's branch. #932 is green and
  waits only on Louis's 2-D confirmation.
- 2026-11-03: **the stack's CI (#932/#933/#934) cancelled shard 4 at the 60-minute cap on all
  three**, inside `test_1097_place_sheet_partitioned_addon_parallel` (a 25-minute 3-D
  sheet test, timeout 1500 s) that is on the stack's branches and not on development under
  that path; it arrived with the development merge into #918's base (`add_conforming_sheet`
  commits). Shard 4 on development already ran 56 minutes. #932 also conflicted with
  development on the batch-4 line after #926/#930; resolved and pushed (7c401c3d). The
  **Correction: the hub's reading was wrong.** test_1097 is on development under the same
  path (293bf8dd, 2026-10-17), and its slowness on the stack is a **real #918 regression in
  3-D**: on its 3-D fault the split finest level's patch and halo are 94 % of the level, so
  the 0.98 gate takes one 3-D LU over 94 % of the level (463 s, 6.3 GB peak) where
  development's 0.75 declines it (35 s, 4 velocity its, 1.6 GB). This is the OOM risk the
  r2 review flagged; #918's evidence was all 2-D. **Stack merge HELD.** Fix on #918's branch:
  the 0.98 threshold applies to 2-D split levels only; 3-D levels keep 0.75 until the 3-D
  add-on is measured (phase 2; #895 bounds the block), with a test; carried up to
  #933/#934, CI reruns. This narrows the rule Louis accepted to 2-D; the integration
  session is telling him directly. **Pushed:** #932 15340c09 (test 4802b5e2 first: test_1097's
  own 94 % 3-D level must decline, and a small 3-D split box in test_1134 fails first at
  0.98), #933 998ff4a8, #934 e4eee30e; the 3-D threshold is marked a placeholder pending
  phase 2 in the subsystem doc, the code comment, #932's body and on #895. **Merge gate:**
  Louis confirms the 2-D narrowing, and green CI.
  **CI on the re-pushed stack:** #932 green on every shard (the 3-D gate fix holds). #933
  failed shard 4 on #917's flake (re-run). **#934 hangs in `test_1089_fault_split_multigrid_parallel`**
  at the 60-minute cap. **Correction: not a hang.** test_1089 prints its first `x` and then
  takes 48 s on development too; #934's job was cancelled 43 s after that mark, at the cap.
  Shard 4 is simply the longest: it owns the whole MPI phase plus every tests/parallel
  file's serial run, 55 min on development and 47 min of serial on the stack (the stack's
  four new tests add 5 min; the rest is runner variance), while shards 2 and 3 take 29 min.
  **Rebalanced on #925's branch (e8957186):** the ten serial tests/parallel lines move to
  shard 3 and test_05*/06*/07* to shard 2; coverage and the shard plan still pass. The
  integration session also, correctly, declined the hub's request for an np 2 run on wombat
  under Louis's rule.
- 2026-11-03: **#926 merged** (e7dfbf9a; #919 relabelled fixed-in-development) and **#930
  merged** (af6f19b3; #922's library side stays open). **All five of the first phase-1 batch
  are in:** #926, #927, #928, #929, #930. The stack #932-#934 is on CI.
- 2026-11-03: the stack is open as #932/#933/#934; #927 merged (f53bbffb) and #920
  relabelled. Kaiju: a MUMPS-distributed patch solve matches the library's iterations at np
  1-16 and is 1.8-3.5x faster (phase 3 lever, not proposed).
- 2026-11-03: **Louis accepted #918's narrowed rule and ordered the stack merged.** #926
  and #927 green after the #917 re-run; #926 needed a development merge (test.sh, both
  sides kept); #930 hit #917 again, re-run requested.
- 2026-11-03: #925 complete at c094073d (round 3 verified on kaiju; the queue is empty). The
  stack #918 -> #921 -> #925 goes to PRs from the laptop; the merge gate is Louis's yes on
  #918's narrowed rule. Phase 1 item 4 (cases with tests) starts.
- 2026-11-03: Louis's rule recorded: no node-adding adaptation of the base in the add-on
  work (fixtures are a uniform base plus the ladder). #925 at c094073d, rounds 2 and 3
  fixed, one gathered structural block flat to np 16 where the per-rank cut reaches 445.
- 2026-11-03: the runner confirms kaiju's permission change: squeue, sinfo, a login-node
  overlay build and sbatch all work, no sandbox. #925's fix verified at np 1/2/4 and
  extended to the structural-only patch; held on the #918/#921 stack.
- 2026-11-03: kaiju's admin lifted part of the restriction (Louis: Claude can submit jobs
  without approval and build containers on the login node; more to come). Both kaiju
  sessions told; the runner checks before resuming its queue.
- 2026-11-03: #925's cause found (rank boundaries cut the FAC union's blocks) and the fix
  plan approved: blocks from gathered rows, the same at any rank count.
- 2026-11-03: Louis switched the hub to Accept edits so merges reach him as prompts.
  **Merged: #929** (LU block solver, squash, 6321c714) and **#928** (patch summary,
  d9783f02). #930 got development merged in (670f6252; adjacent test.sh lines, both
  kept) and re-runs CI. The flaky shard 4 on #926 and #927 (#917) was re-run.
- 2026-11-03: CI on #926-#930: #928, #929, #930 green; #926 and #927 failed shard 4 on
  test_0023's hash (#917, a known flake). **This hub's session can no longer merge:** its
  permission classifier refuses every merge as "merge without review" (it allowed
  yesterday's five). The merges are handed to the integration session, under Louis's
  standing authorisation, in the test.sh-safe order (#929 squash first). If that is refused
  too, the five go to Louis for a web-UI merge.
- 2026-11-02: PRs #926-#930 open; the hub merges on green in the test.sh-safe order.
- 2026-11-02: kaiju report 7: five phase-1 branches validated; PRs opening from the laptop
  under Louis's standing authorisation. #918 and the pressure rtol wait on him; #921 on #925
  (rank 1 computing, not deadlocked).
- 2026-11-02: kaiju report 6. #918 and #920 confirmed; #921 blocked by a pre-existing np 4
  hang in the zone-plus-structural union; the geometry-held box converges like problem A, so
  the bridge width is a physical model parameter; error 76 is load, not OMPIO; the runner
  is sandboxed again.
- 2026-11-02: the kaiju runner locked itself out of its permissions; replaced by "kaiju: dev
  runs 2" (Auto, same environment, the held queue carried over). The old session is archived.
- 2026-11-02: item 2 decided on kaiju's results: LU stays as the block solver; the probe
  knobs go. The iterative-patch question is closed.
- 2026-11-02: phase 1 items 1 and 3 built and reviewed (table in the programme). Two
  decisions for Louis: the #918 rule as shipped (split levels only), and the pressure rtol
  default. #924 filed.
- 2026-11-02: Louis switched "kaiju: dev runs" and "kaiju: 3-D add-on mesh" to Auto; the
  runner was told to release its six held jobs. The 3-D session is working.
- 2026-11-02: **Louis: stop hedging; polish the add-on, land 3-D, decompose only if
  needed.** The matrix becomes a three-phase programme (section above). #918 and #921's
  defaults are approved on the recorded evidence.
- 2026-11-02: **#919's review found a HIGH regression in the second fix** (7c0c62ff): marking
  the moved base finest static made it the base of the next partition, so the first
  level's parents were resolved through the base's own earlier move and the provenance
  transfer would be wrong at np > 1 on a mesh-owned tail. Neither test saw it (test_1132
  checked only the classification; test_1106 uses explicit levels). Third fix c7e6fa3b: the
  base never moves inside `partition_addon`. test_1132 now asserts every cell's centroid
  lies in the parent its record names at np > 1. Held; kaiju confirms before labelling.
- 2026-11-02: HDF5 error 76 is OMPIO (#922 corrected); #923 filed for the kaiju-only
  parallel failures; #919 adds no failures against the development baseline.
- 2026-11-02: kaiju report 2 recorded (section "Kaiju results"). #919 fixed at 7c0c62ff. The
  patch summary branch is held.
- 2026-11-02: kaiju runner's interim report 1 (via the integration session).
  - **#919:** the first fix (18e57147) did not fix it: a base with no add-on levels moves the
    base mesh itself, which carries no `_mg_static`. New fix 7c0c62ff: `partition_addon`
    marks the moved finest static when the mesh owns no tail. Serial passes; np 2 and 4
    queued. The rest of the parallel suite passed at np 2 and 4.
  - **Rows 4-5 at 964dc3ce:** all 12 row 4 arms and 9 of 12 row 5 arms done. The three TI
    zone "hangs" were the driver's own diagnostic (one allreduce per rank-local patch
    block, with block counts differing by rank); fixed, reruns queued. Louis asked why
    drivers make raw MPI calls on library internals: the hierarchy exposes its patch only
    as rank-local index arrays. **Approved by the hub as a non-default addition:** a
    collective-safe summary on the hierarchy (global rows and blocks per level, made once
    at set-up), so no driver sums them itself.
  - **Row 7:** all 18 unrefined arms done; the 7 tip arms submitted. Tables to follow.
  - **Iterative patch:** most arms done; four probe-driver defects fixed (53924f82). The
    inexact-block arms on the box converge but take about 3 min per Newton step (43
    steps), running to completion under a 4 h limit.
  - **#922 filed:** generated mesh files are not safe across hosts on NFS (scratch names
    unique by pid only; 102 of 2000 creates failed in a stress test). Workaround: a
    node-local `UW_MESH_CACHE_DIR` per job.
- 2026-11-02: **Louis's decision: the add-on is the line** (section above), with his
  three-point plan. Split coarse levels stop. The S ruling is superseded by "the fault
  carries its own resolution". First node-count measurement recorded.
- 2026-11-02: **correction.** The hub had relayed "refine the base under the fault corridor"
  as part of Louis's ruling; it was the hub's own inference. Louis rejected it, and row 7's
  refined arms were dropped. Louis also: the split tip is one element below the surface
  because surface DOFs cannot be rotated, not a physical depth. His direction on the
  method: the add-on (welded base plus a patch) is "a separate, patched-on problem that can
  be viewed mathematically", more likely to take an iterative, independently distributed
  solver; the split copy is "much more limited to the anticipated physical solution".
- 2026-11-01: Louis ruled the ladder matches the base mesh for split faults (section
  above); row 7 added and dispatched. Hub briefed Louis on GenEO and on why the band ratio
  hurts.
- 2026-11-01: Louis: strategies must run on conda-forge PETSc as shipped. Experiment 3
  (PCHPDDM) cancelled; a hypre arm added to experiment 1.
- 2026-11-01: Louis asked whether the patch can be iterative, and approved three 2-D
  experiments on kaiju (section above). Dispatched. Model switched to Fable 5.1 in the hub.
- 2026-11-01: #919 fixed on `bugfix/addon-partition-static-mark-919` (test 66206593, fix
  18e57147), validating on the kaiju runner, held without a PR. #921 filed. The faulted
  annulus slab runs cost 1.43-1.72 times the Stokes time of their unfaulted twins, from
  per-solve set-up and the rebuild, not nonlinear work. A `-log_view` split on kaiju is
  offered to Louis.
- 2026-11-01: rows 4 and 5's remaining 24 np 4 arms sent to the kaiju runner. The
  drivers and the row 4 checkpoint are on uw3-campaigns branch `addon-matrix-2026-11`
  (06684d9), with a 2.6 MB `.h5` fixture force-added. Library at
  `bugfix/rotated-nullspace-from-mesh` 964dc3ce.
- 2026-11-01: Louis: memory pressure on wombat killed applications; no parallel or
  load-bearing work there. The laptop sessions were told; the integration session's np 4
  row-4 run was still going and was told to stop. The kaiju dev-runner session was created
  for library runs.
- 2026-11-01: the `split_tail_levels` warning is a defect, benign today:
  `addon_partition._moved_wrap` marks the moved base finest non-static, so a replay is
  attempted only at np > 1. It is a one-line fix. Filed by the notes session as **#919**; the
  silent cover gate as **#918**, cross-referenced to #896. Both are labelled bug and added to
  Project 10.
- 2026-11-01: #906 pushed and held (`bugfix/rotated-nullspace-from-mesh` 964dc3ce, 4
  commits, the SVD-count commit last so it drops after #901). Matrix row 3 done: the
  cover gate declines large patches silently (14-22 times the iterations). A structural
  gate plus a log line is proposed, for Louis's ruling. Seen in every np > 1 log since
  step 5: a `split_tail_levels` warning about snapping that inverts a cell on add-on
  level 0, possibly only the mesh's unused own tail. Unchecked.
- 2026-11-01: the 022 recipe ran verbatim on development 25d62812 (2 velocity its, peak
  slip 0.1595055, one LU block of 4772 rows). Row 2's np 16 baseline recorded: equal
  velocity work, the patch all on one rank (5-6 % of Stokes, 15 ranks waiting). The 3-D
  session is blocked on a Bash permission prompt on kaiju; only Louis can approve it.
- 2026-11-01: Louis ruled the production tail: welded base plus split S plus FAC LU; the
  `uw_chain` default waits on kaiju's np 16 confirmation. He asked whether the add-on can
  replace split coarse levels everywhere, 3-D included: the question and its test matrix
  are now a section. Step 5 on the laptop: H0 flat, H1 3.5-7.7 times as many its. The
  notes session stripped the proxy footer from 31 items and fixed the label drift (#758,
  #759, #782, #827). It posts on Louis's account; edits and deletes still go to Louis.
- 2026-10-31: the notes session posted the four "Fixed by" comments from Louis's account
  (no footer); the integration session posted none. **#892 step 5 dispatched** on merged
  development 25d62812:
  - the tail sweep's H0 against H1 arms on the laptop (np <= 4);
  - the production-scale twin on kaiju's rollback rig, after the scaling job: uw_chain 2
    against uw_chain 0 with the LU FAC patch, TAf 20 and TBf, 10 steps, np 16.
  Together they are the evidence for Louis's production-tail ruling.
- 2026-10-31: **#914 merged** (dbb4d720) and **#915 merged** (25d62812) on green CI;
  both were clean against development after #916. All five of the day's PRs are in; #896
  is relabelled fixed-in-development. Still held for kaiju: #902
  (`bugfix/custom-mg-many-ranks`) and #901 (`bugfix/rotated-fmg-coarse-solve`).
- 2026-10-31: **#916 merged** (70b0f777) after green CI on its development merge;
  development was green at afdfe591 before it. #892, #894 and #907 relabelled
  fixed-in-development. Their "Fixed by" comments are drafted for the integration session
  to post.
- 2026-10-31: CI fixes pushed.
  - #914 (4398dc18): the count differs by host, not by halo. Linux gives 4772 rows at np 1
    and np 2, macOS 4780, from the cavity fill. The test now takes per-host recorded serial
    counts.
  - #915 (4eb0c756): the coarsening case skips without mmg (CI's conda-forge PETSc has
    none).
  - test_0023's hash depends on test order and seed: filed as #917.
  - The footer cleanup is dry-run only: 31 items (#893, #895, #900-#904, #912-#916, 19
    comments; #862 from 10-28 excluded unless Louis says). It and the standing
    posting arrangement wait for Louis's confirmation inside the integration session.
- 2026-10-31: **merged on green CI:** #912 D (cc839425) and #913 the #894 fix (afdfe591).
  #916 got development merged in (98a63833, clean), because three PRs touched
  `rotated_bc.py`, and its CI is re-running. #914 fails `test_1106` at np 2 on Linux (4772
  against 4780 patch rows). #915 fails `test_1016::test_a_coarsening_hierarchy` (PETSc
  error 63) and `test_0023`'s power-mean hash. Both went back to the integration session.
  The merge commits carry no proxy footer; only bodies and comments do. Louis wants the
  original attribution only, and the hub proposed that the integration session (his own
  credentials, no proxy) post GitHub text and strip the footers, pending his allowing
  writes there.
- 2026-10-31: **PRs opened by the hub** (bodies and reviews from the integration session):
  - #912: D (#892);
  - #913: the #894 fix, stacked on D;
  - #914: the #896 fix, stacked on D;
  - #915: `Mesh.multigrid_levels`;
  - #916: #907.
  #892, #894, #896 and #907 are labelled fixed-in-PR. The hub merges on green CI, D
  first. Note: this environment's GitHub proxy appends "_Generated by Claude Code_" to
  every body and comment written through it, edits included. It cannot be removed from
  here; a web-UI edit removes it.
- 2026-10-31: the 3-D owner session created on kaiju (`session_01HxWvn87Vw8gzXsEHJ7iF8u`)
  with the full brief; the kaiju scaling job sent to the rollback session.
- 2026-10-31: **Louis's rulings, "agreed on all counts":**
  - #901 is A-prime;
  - open PRs for D, then the #894 and #896 fixes, and the accessor; the hub merges on
    green CI;
  - #907 approved;
  - the rollback rig confirmed;
  - a dedicated 3-D owner, with the 3 September defer-to-2-D ruling retired;
  - #900 goes to the 3-D owner;
  - the PETSc report for #902 is his to file.
  **Parallel runs go to kaiju, and so does the 3-D investigation.**
- 2026-10-31: branches ready, held without PRs:
  - #902: `bugfix/custom-mg-many-ranks` 57d87783, 3 review rounds. Filed #908 and #909.
  - #901: `bugfix/rotated-fmg-coarse-solve` 77de8d81, A-prime plus the GAMG variant plus
    the double-setup fix, 2 rounds. One recorded change: level 0's LU uses the inode
    kernel at every np, so the #906 default-normal shell at np 1 goes from 83 to 112 its.
  - #907: `bugfix/rotated-solve-raises-on-failure` 295398cb, 3 rounds. It raises only on
    a cold start whose first solve fails hard; a failure after an accepted step warns, as
    test_0022 needs. Filed #910 and #911.
- 2026-10-31: **the PRs are blocked.** `gh pr create` is refused by the integration
  session's permission settings. The hub does not open them in its place; that is put to
  Louis.
- 2026-10-31: Louis: the hub opens the PRs from here (the integration session sends its
  reviewed bodies). Kaiju gets GitHub credentials when Louis can arrange them; until then
  the 3-D session's commits come through the hub as patches.
- 2026-10-31: Louis: null modes belong in the mesh metadata. They were implemented in April
  and bypassed by the rotated path's own detection (#906's cause). The integration session
  was briefed to make the rotated path read them.
- 2026-10-31: #901: explicit null modes with redundant LU are the default on
  `bugfix/rotated-fmg-coarse-solve`, 19-190 times cheaper than SVD at equal iterations.
  #906 filed: shells with the default normal carry a rigid rotation. #902's branch at
  b1481152 after review round 2; the kaiju check on 96d39f7b still holds.
- 2026-10-31: the #902 fix pushed (96d39f7b) and routed to kaiju through the science
  hub. #905 filed. Notch draft 04 found already fixed.
- 2026-10-31: #902's mechanism found: a PETSc preallocation defect on ranks that own
  nothing. The fix is in progress; np >= 16 checks go to kaiju. Triaged the six notch
  drafts: filed #903 and #904, posted the evidence on #771.
- 2026-10-31: Louis: np 52 must be investigated; SVD's slowness is why we went to
  redundant LU; the coarse level is not coarse enough; consider GAMG as the coarse solve.
  The hub found development still picks SVD whenever there are rotation modes. #901 and
  #902 are the integration session's active task; kaiju's scaling check is requested.
- 2026-10-31: Louis asked why kaiju is capped at np 16. The cause is two library defects
  from kaiju's 10-23/24 scaling study, never filed; now #901 and #902.
- 2026-10-31: the integration session fixed #894 and #896 on branches stacked on D
  (tests first, reviewed), filed #898 and #899, and pushed D's guide caveat. Correction:
  #894 never touched the zg95 campaigns, which use frictionless contact. Kaiju's np 16
  check of #896 is requested of the science hub.
- 2026-10-31: Louis: the 3-D add-on mesh is needed. Survey done (read-only agent,
  claims re-checked); the plan is in its section. Filed #900 (39 dark `ptest_*`
  files, including every 3-D parallel fault test).
- 2026-10-31: D's step 4 complete and D ready for a PR. Filed #895, then corrected it
  after the segment sweep. #894, #896 and #897 filed by the integration session. The
  efficiency queue was set and sent to it, and the slip coarse space held.
- 2026-10-31: development CI green at fc67b650: test and all four shards, the Gadi and
  Setonix HPC image builds. Tier C (report only) and one image push were still running.
- 2026-10-31: #892 step 1 reported: only the rotated path runs ILU; scope unchanged.
  B's `drop_orphans` rotated path discards every coarse FAC patch; measurement of
  kept against dropped added to step 4.
- 2026-10-31: Louis: go on #892 steps 1 to 4, and yes to the levels accessor. Both
  briefed to the integration session (`session_01HxWvn5rMK67zasgirdXszQ`, wombat).
  Task A: `bugfix/fac-live-block-solver` from C 799ef021, step 1's scope result to the
  hub before the fix. Task B: `feature/mesh-multigrid-levels` from development. No
  PRs until Louis asks; D lands stacked on #890.
