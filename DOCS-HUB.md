# Docs hub: state of Underworld documentation and technical notes

The docs hub session keeps this file current. It is the single point of truth for the
documentation in `underworld3/docs`, the wiki, and the technical notes: what is in flight,
who holds the pen, what is stale, and what waits for team input. Read it before acting. Newest
entries in the log at the bottom win over anything above them that they contradict.

It is the documentation counterpart of `HUB.md` (the science hub). The science hub keeps
machines, campaigns and library fixes; this hub keeps the writing. Where a piece of work
has both halves (a note that needs a figure from kaiju), the science hub owns the run and
this hub owns the note, and the two hubs message each other rather than sharing a table.

**Role (Louis, 2026-10-28).** This hub monitors and advises the sessions doing the
work; it does not dispatch it. Louis works with individual sessions directly and hands
them their tasks; the hub briefs a session only when asked. What the hub does on its
own: keep this file current from what sessions and GitHub show it; settle a question
that spans branches or sessions from the sources and record the answer once in the
journal, with the closure lines; write the weekly digest; run the monthly graduation
and closure pass; re-pin the notes when merges land; open the small docs PRs from the
inventory. Check-ins read a session's transcript and record state; they do not steer.
The science hub is different by design: it dispatches work across machines and
monitors them all.

## Restarting the hub

The hub is a Claude Code cloud session on `underworldcode/underworld3`, branch from
`development`. It holds no state that is not in this file, on GitHub, or in session
transcripts. If it dies:

1. Start a new cloud session on `underworldcode/underworld3` with this prompt:
   > You are the docs hub for the Underworld team's work: documentation, the wiki and
   > the technical notes. Read `DOCS-HUB.md` in lmoresi/uw3-campaigns (main) and follow it.
   > The previous hub was `<session id below>`; read its transcript (claude-code-remote
   > `list_events`) only for detail this file lacks. Then confirm the state to the team in
   > a few lines.
2. Attach `Underworld-Technical-Notes/underworldcode.org` (push) and `lmoresi/uw3-campaigns`
   (push) with `add_repo`; approve the cards. Without them the hub can read both repos
   through the anonymous git proxy but cannot push, list pull requests, or update this file.
3. Approve the "reach my other sessions" card when the hub first messages a machine.
4. Re-arm any check-ins (scheduled tasks are bound to the session that made them).

| | Session id |
|---|---|
| docs hub (current) | `session_01HxWvn87HYCEJodpgCdaBro` ("Underworld Docs and technical notes Hub"), started 2026-10-27 |
| science hub | `session_013CgVT1Gx9WTvaZVqU58HsQ` ("Underworld Cloud Hub"); keeps `HUB.md` |
| laptop (wombat), notes workbench | `session_011S876ckjYqqth1aPyojrhh` ("Notes workbench with git branches"): the notes workflow, UWTN 2026-018 and 2026-022 prose |
| laptop (wombat), adjoint notes | `session_018wSha1nV5DddcThnCRoFab` ("CONTRIBUTING.md figure script placement"): holding; has the unpushed 2026-023 renumber for PR #58 |
| laptop (wombat), run transcripts | `session_01Na7qBenCp67rDTZhFGTh5V` ("Sinking blob adjoint Taylor test"): `note/run-transcripts` (UWTN 2026-019) |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H`: holds a restart-limitation doc patch, unpushed (see Open work) |
| laptop (wombat), fault-split integration | `session_01HxWvn5rMK67zasgirdXszQ` ("Fault Models Code Unification"), opened by Louis 2026-10-28 for `FAULT-SPLIT-INTEGRATION.md` items 2 and 3; reports here |
| dev hub | `session_01HxWvn6vA38fdYLUxnxDk4g` ("Development issues hub"), from 2026-10-29; keeps `DEV-HUB.md`: the PR queue (A #882, B #889, C #890, and #861, #862), library fixes without a PR, problems sessions raise. `FAULT-SPLIT-INTEGRATION.md` and the notes' re-pin stay with this hub. Cloud to cloud cannot message; the hubs read each other's files and each keeps a "For the other hubs" section. |

Messaging: the hub can message the laptop sessions. Sessions on machines whose Claude
Code cannot prove a trusted device (hyperion) are read through their transcripts.

## Where the writing lives

| What | Where | Access from this hub (2026-10-27) |
|---|---|---|
| Library documentation (MyST, Sphinx) | `underworldcode/underworld3` `docs/`, on `development`; merges by PR | attached, push to side branches |
| Working notes (what we think is true now, with the dead ends) | `underworld3.wiki.git`, Home lists topic, benchmark, campaign and process pages | cloned read-only; push untested |
| The plan | GitHub Project 10 "Underworld roadmap" (Area `docs` for this hub's items) | **not reachable**: Projects are GraphQL-only and GraphQL is blocked from cloud sessions (`gh project` answers "unknown owner type"). Annotations go through a laptop session or a team member. |
| Technical notes (micro-preprints, DOIs) | `Underworld-Technical-Notes/underworldcode.org`, one branch per note `note/<slug>`, `WRITING-PLAN.md` for the programme, `CONTRIBUTING.md` for the house style | attached with push (2026-10-27, after Louis switched the session to Accept edits so the call prompted him instead of the classifier) |
| Hub state, campaign scripts | `lmoresi/uw3-campaigns` (`HUB.md`, this file) | attached with push (2026-10-27) |
| Machine knowledge | `underworld-community/uw3-hpc-install-run` | not attached |

## Standing rules (team)

- The Style Charter (`docs/developer/UW3_STYLE_CHARTER.md`) wins over the surrounding
  prose and code. Match it, flag deviations, do not silently fix them.
- All documentation under `docs/`, MyST Markdown for Sphinx; verify with the docs build.
  Never the repository root, `src/` or `tests/`. The JOSS paper is frozen.
- One governing document per topic (`docs/developer/index.md` authority map). A new
  document on a topic that has one is subordinate and says so in its first lines.
- A wiki page graduates to `docs/` when it has stopped moving. A finding on a wiki page
  that `docs/` contradicts is a docs bug, filed as one.
- Work on side branches of `development`, never `development` or `main`. Push after every
  commit. Open PRs only when a team member asks. Commit messages end with
  "Underworld development team with AI support from Claude Code" and carry no
  Co-Authored-By line.
- Technical notes: one branch per note; nobody pushes to `main`; a PR only when a team member asks;
  IDs allocated only after fetching every branch and the open PRs (a fork PR is invisible
  to `ids_on_branches()`, which is how PR #58 collided with 2026-021); `metadata.yml
  status:` is canonical; the `myst.yml` toc block is generated. Prose follows
  CONTRIBUTING "How the notes read": every paragraph introduces itself, headings name and
  do not argue, no announcing or withholding. Every figure and table ships its script;
  `software_version` pinned to the underworld3 commit the numbers came from.
- Figures from machines: the machine commits script and PNG to underworld3 under
  `scripts/sessions/<area>/uwtn_<id>/`; the note copies them in one commit naming the
  underworld3 hash. PNGs never travel through hub patches.
- Checks before any review request: `pixi run validate`, `pixi run check-style`,
  `python3 scripts/preview_build.py --slugs <slug> --base-url /x`, run on a machine with
  the notes environment (this hub has no pixi), results and hash reported here.

## Technical notes in flight

Moved from `HUB.md` on 2026-10-27 and corrected against the repository.

| Note | Branch, head date | Status | Pen | Waiting on |
|---|---|---|---|---|
| UWTN 2026-012 Benchmarking Stokes flow in annulus and spherical-shell geometries | `note/annulus-spherical-stokes-benchmarks`, 2026-08-13 | review (PR #11 per the laptop session) | unknown; untouched since August | a reviewer, or a decision to park |
| UWTN 2026-018 Faults in parallel: partitioning the add-on once | `note/faults-in-parallel`, 2026-10-25 | draft | wombat workbench | 3 figures from hyperion (parallel-pipeline, load-per-processor, band-through-the-boundary); team answers to Q1-Q4 (below) |
| UWTN 2026-019 A transcript for every run | `note/run-transcripts`, 2026-10-06 | draft; the laptop session reported it "ready for review" on 2026-10-07 | wombat (adjoint Taylor session) | a team read; metadata still says draft |
| UWTN 2026-020 Symbolic FEM and adjoint forms | merged to `main` 2026-10-25 (PR #59) | **published** 2026-10-25, v1.0.0; a `deposit/symbolic-fem-and-adjoint-forms-…` branch exists, so the deposit has run | — | **PR #61** (Deposit: symbolic-fem-and-adjoint-forms, github-actions, opened 2026-10-26): a maintainer's merge, which records the DOI |
| UWTN 2026-021 Model derivatives and their uses | `note/model-derivatives-and-their-uses`, 2026-10-26 (older copy on `note/discrete-adjoint`, same id and title) | draft, held | wombat adjoint session | the viscosity-floor example's result; the laptop session calls it ready to publish, the metadata says draft |
| UWTN 2026-022 Faults and patch-refinement of the mesh (retitled by Louis 2026-10-28; was "Faults on an add-on mesh") | `note/faults-on-an-add-on-mesh`, 2026-10-26 on GitHub; on the wombat workbench, UNSAVED as of 2026-10-30: the ladder rewrite of the construction, recipe, multigrid, moving-fault and limits sections, the redrawn ladder figure folded in (hashes verified; scale paragraph: the S ladder adds 906 cells to the base finest's 2592, 2S adds 414, 4S adds 230 to 648), validate and check-style clean | draft; **not to publish until the tail sweep reports**; pen with wombat | wombat (prose), hyperion (figure records), science hub (numbers) | kaiju's addon_demo figures via Louis's rsync; hyperion's fig_iterations records and global peak slip; review items (a), (c), (g); review of the trench section |
| UWTN 2026-023 Underworld3 v3.2.0 release note (was 2026-021) | PR #58, jcgraciosa's fork `note/underworld3-v3-2-0` | draft | jcgraciosa | the two-line renumber (committed as 22ffc81 in the wombat adjoint session's scratch worktree, unpushed: that session may not push to the fork); then telling jcgraciosa why his branch changed |

The other open pull requests on the notes repository, listed on 2026-10-27. Every one
waits on a team merge or ruling; none has moved since September except #58, #60, #61.

| PR | Branch | Opened or last touched | What it is |
|---|---|---|---|
| #61 | `deposit/symbolic-fem-and-adjoint-forms-…` (bot) | 2026-10-26 | the deposit for UWTN 2026-020; merging it records the DOI |
| #60 | `docs/workbench` | 2026-10-26 | the workbench: every note in one checkout, each branch built from its own files |
| #58 | jcgraciosa `note/underworld3-v3-2-0` | 2026-10-26 | UWTN 2026-023 (above) |
| #57 | `note/fault-mesh-banner` | 2026-10-02 | banner image for UWTN 2026-017 (published 2026-09-20 via #54) |
| #55 | `deposit/putting-a-fault-in-a-mesh-…` (bot) | 2026-09-20 | **the deposit for UWTN 2026-017, open five weeks**: the note is live without its DOI recorded, the "reserved, not published" state `scripts/outstanding.py` exists to flag |
| #53 | `note/time-derivatives-supg` | 2026-09-08 | update of UWTN 2026-007 (time derivatives) for the composing solvers |
| #52 | `docs/examples-units` | 2026-09-07 | every example is dimensional, or says plainly that it is not |
| #51 | `docs/version-history` | 2026-09-07 | an updated note says what changed, and where the old one is |
| #24 | `docs/r1-scope` | 2026-08-17 | R1 scope: three approaches in order, and what the note leaves out (R1 published since as 2026-016; may be moot) |
| #22 | `note/analytic-solutions` | 2026-08-19 | UWTN 2026-015, testing a solver against exact solutions; no draft metadata on the branch beyond `main`, so the article state needs a look |
| #11 | `note/annulus-spherical-stokes-benchmarks` | 2026-09-08 | UWTN 2026-012 (above) |

Branches with no open PR and no draft metadata beyond what is on `main`:
`note/bc-unwrap-and-edits`, `note/binder-note`, `note/browser-note-abstract`,
`note/browser-note-v1-1`. Each is either merged, abandoned, or a note whose article
directory was never created; to triage.

`WRITING-PLAN.md` still lists M2, M3, M4, F1-F5, C1, S1, S2 and the original numbered plan
as not started; the fault notes being written (018, 022) are F3/M3 territory and the plan
does not yet say so.

## underworld3 documentation: state on `development` (7222caf, 2026-10-27)

Measured here, not inherited.

| Item | State |
|---|---|
| Docs build | Sphinx builds (exit 0) with `nb_execution_mode = 'off'`. On `development`: 46 "document isn't included in any toctree" warnings and 140 autodoc warnings (`main`: 50 and 138); the autodoc ones are this container's (no underworld3 installed) and not a docs defect. The toctree count is the number to drive to zero or to an explicit exclude list. |
| Pages not reachable from any toctree | 137 of 270 `.md` by a walk of the toctrees (Sphinx's count is lower because `conf.py` excludes some trees). Deliberate for `reviews/`, `planning/`, `ai-notes/` and `design/` archives; **not** deliberate for `guides/memory-diagnostics.md`, `guides/release-process.md`, `subsystems/checkpoint-output-and-reload-methods.md`, `subsystems/mesh-metric-redistribution.md` and the four `release-notes/v3.*.md`, which are live documents nobody can navigate to. |
| July 2026 docs audit (`reviews/2026-07/DOCS-STANDARDS-COHERENCE.md`) | DOC-01, 02, 03, 04, 06, 08 closed. DOC-07 (status headers on design docs) regressed: seven design docs added since carry none (`FREE_SURFACE_ROADMAP_2026-07`, `ROTATED_FREESLIP_LINEAR_REUSE`, `SPLIT_NODE_FAULT_METHOD_2026-08`, `fault-parallel-placement-2026-09`, `fault-patch-multigrid-2026-08`, `point-location-capability`, `solver-strategies-catalogue`). DOC-05 (undocumented public API) not re-measured. |
| Two changelogs | Root `CHANGES.md` stops at 2026-05-20 and nothing in the release process refers to it; `docs/developer/CHANGELOG.md` (the one `release-process.md` names) has a Q3 section last touched 2026-09-10, so October's merges (#677, #744, #746, #756, #794, #838, #845 among them) are unrecorded. Decide: retire `CHANGES.md` with a pointer, or keep it as the user-facing summary and say so. |
| Docstring review queue | regenerated 2026-09-03; a sweep after v3.2.0 is due (the release checklist asks for it). |
| Capability guides and skills | `.claude/skills/` are symlinks into `docs/developer/guides/`; a change to a solver, constitutive model, history scheme or boundary mechanism must update the guides that name it, in the same change (CLAUDE.md ruling on `development`). Nobody checks this across PRs today. |
| v3.2.0 release documents | `release-notes/v3.2.0.md`, feature manifest, committee pre-read and feature table landed on `main` via the release branch; they are on `development` too. The technical note for the release is PR #58 above. |
| Wiki | 19 pages; Home's lifecycle rule says a topic page graduates to `docs/` when it stops moving. No page has graduated yet. Candidates to check against `docs/`: Solvers and multigrid, Transport histories, Fault multigrid (each has a `docs/` counterpart that may now disagree). |

## For the other hubs

- 2026-10-30, to the dev hub: two items from the UWTN 2026-022 work that belong on the
  PR side. (1) A public accessor for a mesh's multigrid levels: the production recipe
  and the note's "Using it" code need `base._coarse_level_meshes()[:-1] + [base]`, and a
  published note cannot name a private method; a `Mesh` property that returns the
  levels coarsest to finest, on B or C or as a small PR before the note publishes.
  (2) Done 2026-10-30: the faults-in-convection guide exists only on C, and its prose on
  the chain's hosts is corrected there at 799ef021 (#890); nothing on B.
- 2026-10-30, to the science hub: the drivers' chain comments (`annulus_fault.py`,
  `annulus_faults.py`, `box_fault.py`: "the base level k steps below the finest") are
  off by one against their own indexing; the code is right, the comment is not.

## Open work

| What | Where | State |
|---|---|---|
| Restart-limitation documentation | kaiju session, branch `kaiju/restart-limitation` 1135f78, **unpushed** (kaiju has no GitHub credentials; fixes come as patches through a hub) | to collect as a patch and push; which branch of underworld3 it targets is unknown |
| Docs follow-ups of the stress-transport fix | underworld3 `bugfix/backward-nodes-snapshot-order` (hyperion) | HUB.md lists "docs" among the follow-ups; not itemised |
| Kaiju machine documentation | `underworld-community/uw3-hpc-install-run` PR #1 | open; machine knowledge, stays with the science hub unless the team moves it |
| Status headers on seven design docs | `docs/developer/design/` | one-line `**Status:**` each after a git-history check; a docs PR |
| Eight live pages missing from the toctrees | `docs/developer/index.md`, `docs/index.md` | add them; a docs PR, can ride with the status headers |
| Changelog decision and October backfill | `CHANGES.md`, `docs/developer/CHANGELOG.md` | needs a team ruling on the two files, then a backfill from `git log --first-parent` |
| Docstring sweep after v3.2.0 | `scripts/docstring_sweep.py` | needs a machine with underworld3 built; this hub cannot run it |
| Wiki graduation check | wiki topic pages vs `docs/developer/subsystems/` | a read, then either a docs PR or a note on the wiki page |
| WRITING-PLAN reconciliation | `WRITING-PLAN.md` | record 018, 019, 020, 021, 022, 023 against the plan's M/F/original numbering |
| **Phase 1: the journal** (`INFORMATION-FLOW-PROPOSAL.md`) | `underworldcode/underworld3-journal` (Louis created it 2026-10-28; the App may not create repositories), three commits on `main` | PUSHED 2026-10-28: scaffold (`myst.yml`, `scripts/build_index.py`, entry template, Pages workflow), the wiki migrated (100 entries: 55 from commits, 45 dead ends; 18 pages; 72 figures), the week-44 digest, README with the three rules, the frozen-wiki Home text. Rule PRs open: underworld3 #861 (CLAUDE.md journal paragraph; the planning guide's Journal layer and entry rules), notes #62 (one CONTRIBUTING convention). Still to do: Pages enabled by hand (the API path is blocked for the hub), the wiki freeze from a laptop, then the guide and subsystem PRs from `WIKI-INVENTORY.md` and the Friday digest. |

## Waiting for team input

- **Eleven open pull requests on the notes repository** wait on team input (table above). The
  two deposit PRs (#61, #55) are bookkeeping and cost nothing to merge; #55 has waited
  since September.
- (done 2026-10-27) The split: Louis ruled it through the science hub, which froze its
  notes section (HUB.md b7b791d). Compute-side figure production stays requestable there:
  hyperion's (i) fig_iterations records and (j) global peak slip at np 8 for 2026-022, and
  the three 2026-018 figures, all queued behind the leak-fix PR.
- **The fault-split integration** (`FAULT-SPLIT-INTEGRATION.md`): decided 2026-10-28,
  spun off to the laptop's development session (build d81a2588, suites, review 3's
  fixes, the root's review, PRs A, B, C in order). The hub tracks it here and re-pins
  the notes when the merges land.
- **Enable Pages on the journal**: `underworldcode/underworld3-journal`, Settings, Pages,
  source "GitHub Actions". The proxy refuses the hub the Pages API path. Until then the
  workflow's build job runs and its deploy job fails; the site is
  <https://underworldcode.github.io/underworld3-journal/> once enabled.
- **Merge or rule on** underworld3 #861 and notes #62, the two rule PRs.
- **Read the first digest** (`digests/2026-W44.md`) and say whether it is the page a
  collaborator would read; the next one is Friday 31 October.
- **The information-flow proposal** (`INFORMATION-FLOW-PROPOSAL.md`, 2026-10-27): the
  go-ahead for Phase 1 was given 2026-10-27 and the journal is its own repository;
  still open are public-or-private (built public, like the wiki), the board's fate,
  and `docs/archive/` against journal entries for the dated trees (Phase 2).
- **Project 10**: cloud sessions cannot reach it. Either a laptop session annotates docs
  items on the hub's behalf, or docs items are tracked here only. Say which.
- Carried over from `HUB.md`, unanswered as of 2026-10-27:
  - 2026-018: (1) title "Faults in parallel: partitioning the add-on once" OK? (2)
    re-measure the parallel split-level iteration counts on hyperion? (3) wall times
    65/34/25 s quoted, the 72/38/30 left out as "before": correct? (4) `software_version`
    moves to a development sha on merge.
  - 2026-022: (a) keep the three "route" passages as motivation or cut to rule plus reason?
    (c) `stokes._rotated_freeslip_info` is a private attribute in a published note; (d)
    the restart table needs a script; (f) link 018 once published; (g) check the
    iterations.png alt text against the figure.
  - Regenerate `PREVIEW_TOKEN` in the notes repository (every PR preview has failed since
    2 October; production deploys are unaffected).
  - Delete the empty branch `hub-push-test` on the notes repository
    (`git push origin --delete hub-push-test`); the proxy refuses ref deletions.
  - The wombat workbench tool (`scripts/note.py`, `pixi run note sync`) awaits a go-ahead.
  - PR #58: push the 2026-023 renumber (or let jcgraciosa do it) and say why on the PR.
- The two changelogs: retire `CHANGES.md`, or keep it as the user-facing summary?
- Observed in passing: the science hub's two scheduled check-ins ("Hyperion vigilance",
  "Read hyperion progress") have failed with ACCESS_DENIED on every firing since
  2026-10-27 01:25 UTC; they read the hyperion session, which requires a trusted device.
  They are re-arming but doing nothing.

## Log

- 2026-10-27: hub started on `underworldcode/underworld3`, branch
  `claude/trusting-hypatia-8ft8up` from `development` 7222caf (the session opened on
  `main`; moved). Read `HUB.md`, the notes repository, the wiki and the July docs audit;
  measured the docs state above; built the docs with Sphinx 9.2 in the container. Found
  `HUB.md` stale on UWTN 2026-020 (merged and published 2026-10-25, listed as "review,
  green"). This file committed beside `HUB.md`. Both repositories attached by the end of
  the day (the notes one needed the session in Accept-edits mode so the request reached
  Louis); the open-PR table above is from the repository, not from a report.
- 2026-10-27: Louis ruled the split through the science hub ("the day-to-day flow of that
  work is quite distinct"); HUB.md froze its notes section and now names this hub. This
  hub's session id recorded in HUB.md. Louis approved the "reach my other sessions" grant;
  the two wombat notes sessions were messaged with it (delivered). The science hub cannot
  be messaged from here (cloud to cloud needs a trusted device); it learns of this hub from
  HUB.md, or Louis tells it.
- 2026-10-27/28: **Phase 1 started on the go-ahead.** The journal built locally and the
  wiki migrated into it (see Open work); `WIKI-INVENTORY.md` and the proposal gained the
  results-for-discussion and findings-as-examples points from the day's discussion
  (to be folded into the proposal text). Repository creation refused to the App, so the
  push waited on a team member creating the repository.
- 2026-10-28: **the journal is on GitHub** as `underworldcode/underworld3-journal` (Louis
  chose the name so other developers browsing the organisation know what it is). Pushed,
  CI's build job green on the first run (MyST site builds in 15 s), deploy job failing
  with "Ensure GitHub Pages has been enabled" until Pages is switched on by hand. Rule
  PRs opened: underworld3 #861, notes #62.
- 2026-10-28: **the wiki is frozen.** Wombat pushed `underworld3.wiki` dbb1d645 (Home.md
  only, the journal's frozen text word for word; the other 18 pages checked against their
  journal counterparts first), with Louis's approval. Phase 1 is complete except for the
  Pages switch and the two rule PRs.
- 2026-10-28: Louis: the fault-split work must reach `development` because the notes
  describe it. Mapped the nine branches (one root, two lineages, three small branches on
  development), built the candidate head d81a2588 with two hand-resolved hunks, checked
  both notes' recipes against it, wrote `FAULT-SPLIT-INTEGRATION.md`. The fault-multigrid
  capability guide (ff1d244) documents what ships on development and names the rest as
  branch work.
- 2026-10-28: Louis's rulings on the integration: spin it off to the laptop (hyperion's
  reimage is slow); multiple PRs resolved rapidly; docs PRs merge on the docs build, not
  the full suite; coarse solve: handle the null space, PETSc defaults for the coarse
  level, MUMPS not the default (breaks on the Mac). `feature/fault-split-integration`
  pushed (d81a2588); `docs/fault-multigrid-guide` pushed and its PR opened; the ruling is
  the journal's first new entry.
- 2026-10-28 (later): the laptop integration session validated d81a2588: suites green
  but for two pre-existing failures, UWTN 2026-022's numbers reproduce to ten digits.
  Development moved 38 commits under the head, so B and C each take a development
  merge; B's review found two solver-default changes for non-fault users that need
  Louis's ruling. Details in `FAULT-SPLIT-INTEGRATION.md`; journal entry written; the
  recipe's partition-dependent level count sent to the notes session; `test_1063` is
  #826 already; the adapt level-subsampling finding filed as #865.
- 2026-10-28 (evening): Louis's construction question for UWTN 2026-022 settled from
  the code and the drivers: production uses the placed ladder with a hand-built split
  chain (no bisection); adapt-and-cut is the automated library route the hierarchy
  comparison was made on, and the note's two figures and construction text come from
  it while its tables and trench figures come from the ladder. Journal entry
  `2026-10-28-which-fault-mesh-construction-is-used-in-practice`; answers to the notes
  session's five questions sent; the guide (PR #862) gained the paragraph. The ribbon
  replay is the first library item after B and C.
- 2026-10-29: the laptop reports A open as underworld3 #882 (suites green but #826),
  B development-merged and reviewed, C local with B and A merged in. Louis's ruling
  that every `scripts/sessions` file leaves B and C means **UWTN 2026-022 and 2026-018
  may not cite `scripts/sessions/fault_mg/...` in underworld3**; the notes' own
  `figures/src/` copies are the citable scripts until the originals land in
  uw3-campaigns. Two journal entries from B's review. Details in
  `FAULT-SPLIT-INTEGRATION.md`.
- 2026-10-29 (later): B open as #889 with the non-fault evidence in its body; C pushed
  (4698938f), opening stacked on #889; the datum-only continuation case measured and
  not a must-fix (#883 follows C). Journal: the follow-up measurement supersedes the
  morning's finding, the first use of `status: superseded`.
- 2026-10-29 (evening): all three fault-split PRs open and mergeable: A #882, B #889,
  C #890 (stacked on B). Twenty-three issues filed from the three reviews. The hub's
  remaining items: re-pin UWTN 2026-018 and 2026-022 to #890's development merge
  commit; the fault-multigrid guide's "what ships" section moves the split-level
  hierarchy from pending to available once B merges.
- 2026-10-29 (night): two more settled for UWTN 2026-022. The tail question (ratio-12
  rule against production's `uw_chain = 2`) is a journal `decision` with closure lines:
  the welded tail serves a linear rig at a modest ratio; production uses the lean
  split chain because a yielding lid caps the welded velocity solve (measured in the
  faults-in-convection guide). The ladder construction figure Louis asked for was
  routed on his word to the laptop integration session and exists on wombat at
  `~/+Simulations/uwtn_2026_022_ladder/` (script, PNG/PDF/SVG, README; notes
  repository only, nothing to underworld3); relayed to the notes session with its two
  forced differences (the note's own fixture; base 1/8 to 1/32, ratio 6.06 on every
  level).
- 2026-10-30: the notes session's review of the figure (three drawing fixes, relayed)
  corrected the hub's nesting wording: production widens the band with the level, so
  the chain nests along the spine only; vertex nesting was the rig's constant-width
  case. Journal correction entry written; the guide on PR #862 amended.
- 2026-10-30 (later): the notes session found the chain's hosts off by one in the
  journal, the guide prose, the drivers' comments and the figure's panel (c): the code
  puts `2S` on the finest base level and `4S` one down; and the rig's band-ratio table
  is confounded with cell aspect (three nodes across a fixed width). Both confirmed from
  the drivers and the guide's cell counts; correction entry; the fault-multigrid topic
  page gained a "Current understanding" section; the guide on #862 corrected; the
  panel (c) redraw routed to the integration session under Louis's figure ask. Louis:
  a dev hub now keeps `DEV-HUB.md` and the PR side; added to the table above.
- 2026-10-30 (night): panel (c) redrawn as the production chain (four panels, cells
  162, 878, 3006, 3498 coarsest first; hashes with the notes session); the convection
  guide's prose fixed on C (799ef021). **Louis: "I am very unsure at this point that we
  recorded the best cases. This should be resolved before we publish any results."**
  The notes session, on his word, commissioned a tail sweep from the integration
  session (welded, lean chain, graded chain; ratios 6, 12, 25; the linear fixture at np
  1 and 4, and the yielding-lid box at three spacings); results to
  `~/+Simulations/uwtn_2026_022_tail_sweep/`. The 2026-10-29 tail ruling is marked
  provisional above a ratio of about 8 in the journal (a `decision` entry with the
  sweep's terms) and on the topic page; UWTN 2026-022 keeps its numbers with their
  scope stated and publishes no tail result until the sweep reports.
- 2026-10-30 (late): wombat folded the redrawn figure into 022 on the workbench
  (unsaved), rewrote the scale paragraph from the counts, cut the "welded base is
  enough at a modest ratio" sentence to match the narrowed ruling. Louis's question on
  whether the add-on alters the base answered: never; each ladder lives in a copy of a
  base level, the lean chain adds cells in the band to those copies and no levels;
  topic page and guide reworded. The public levels accessor is Louis's to decide.
- 2026-10-31: the integration session measured the bare base counts the note had
  assumed (162, 648, 2592 by regular refinement: confirmed) and the hierarchy's (162,
  878, 3006, 3498; the child is 1.35 times the base finest); `count_cells.py` added
  beside the figure and the README updated (new hash 5cb3228c…); reported to the notes
  session directly. The fill differs by two cells between two numerically equal
  parametrisations of the trace (3006/3498 against 3008/3496), so the note's counts are
  the figure's mesh. The tail sweep is nearly done; the notes session asked for each
  level's smoother (the FAC patch) to be recorded with it.
