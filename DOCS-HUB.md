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
| UWTN 2026-022 Faults and patch-refinement of the mesh (retitled by Louis 2026-10-28; was "Faults on an add-on mesh") | `note/faults-on-an-add-on-mesh`, 2026-10-26 on GitHub; on the wombat workbench, UNSAVED as of 2026-10-30: the ladder rewrite of the construction, recipe, multigrid, moving-fault and limits sections, the redrawn ladder figure folded in (hashes verified; scale paragraph: the S ladder adds 906 cells to the base finest's 2592, 2S adds 414, 4S adds 230 to 648), validate and check-style clean | draft; **the tail hold is lifted** (Louis's ruling 2026-11-01); **rewritten for the ruling on the workbench, UNSAVED until Louis asks** (reported 2026-11-01): the construction is the base's own levels welded beneath the split child; the recipe is `stokes.set_custom_fmg(base.multigrid_levels, field_id=0)` and ran verbatim on `development` 25d62812 (2 velocity iterations, peak slip 0.1595055, the child's smoother composite SOR + ASM with one 4772-row LU block); a new section "Multigrid with a split finest level" (transfer, patch smoother, the sweep table: LU 3/3/3 and 7 per Newton iteration, ILU 8/12/16, SOR 12/17/24, chain 4/6/7, then the chain, then the bisection figure kept for Louis to decide); panel (c) redrawn as the welded hierarchy; the trench section says those runs used the chain; `software_version` = `development` @ 25d62812; the sweep's scripts and records in `figures/src/tail_sweep/`; validate, check-style and the preview clean. Open with Louis: rerun the trench demos with the welded tail or not; keep or cut `iterations.png`. 2026-11-02 (unsaved): the ladder step now says "The fault is given as a divided line, and its points become the spine of a structured band. The spacing of the points is the rung spacing S." (Louis's 1b). 2026-11-03 (unsaved, goes with the note): #595's evaluation (the cut-in-band configuration of 2026-08-17, with Louis live) sits beside the note at `figures/src/cut_in_band_595/`: `cut_audit.py`, `cut_ladder.py` and their six local modules unchanged, four caches, a README with the provenance and the original section quoted in full, and a new `audit_cached.py` that repeats #595's numbers from the caches with numpy alone (checked 2026-11-03: 13.0°, 104 to 144 cells; 28.8°, 132 to 132; slip 0.4286 / 0.4315; free slit 0.4290; leak 5.6e-17). The solves were not rerun on `development`; the three-across band the script monkeypatches is now the library's `_occ_ladder_assembly_2d`; the "no more cells" half was not measured; the uncut-band sweep and `single_fault_ladder.py` stay on wombat; pen with wombat | wombat (prose), hyperion (figure records), science hub (numbers) | kaiju's addon_demo figures via Louis's rsync; hyperion's fig_iterations records and global peak slip; review items (a), (c), (g); review of the trench section |
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
  **Done: `Mesh.multigrid_levels`, #915 (25d62812).**
  (2) Done 2026-10-30: the faults-in-convection guide exists only on C, and its prose on
  the chain's hosts is corrected there at 799ef021 (#890); nothing on B.
- 2026-10-30, to the science hub: the drivers' chain comments (`annulus_fault.py`,
  `annulus_faults.py`, `box_fault.py`: "the base level k steps below the finest") are
  off by one against their own indexing; the code is right, the comment is not.

- 2026-10-31, to the dev hub: #892 (the rotated path's FAC patch blocks run ILU(0)
  where `custom_mg` configures LU) decides the production multigrid tail for faults;
  see the journal entry of 2026-10-31 and `~/+Simulations/uwtn_2026_022_tail_sweep/`
  on wombat. It is the fix that makes the August fault-patch design the one that
  ships.
  **Closed 2026-11-01: fixed by #912 (cc839425); Louis ruled the tail on #892.** The
  two guides describe it as of today's push to #862; the journal has the decision and
  the corrected history (its finding entry is the plan's step 7). Still with the dev
  hub: whether split coarse levels stay an option (`custom_mg.py:1556`), and the
  non-rotated path's block solver.
- 2026-11-01, to the dev hub, a question from UWTN 2026-022's recipe run on
  `development` 25d62812: the child's finest smoother is composite SOR + ASM with **one
  LU block of 4772 rows**. `set_custom_fmg` carries `fac_block_rows=2000` and #670 cut
  the band block along strike so that LU stays cheap. Either the cap does not apply to
  the structural patch built from the split's coincident pairs, or it is not applied on
  this path. Your plan's step 4 ("block rows against `fac_block_rows`") covers it; the
  note is about to publish the 4772 figure, so a one-line answer settles whether the
  note describes the design or an exception to it.
  **Answered by the notes session from the code, 2026-11-01:** the cap cuts only the
  blocks built from `fac_zone` masks; the automatic structural patch is one block per
  rank with no cap (`custom_mg.py` about 1727 to 1745 and 1825 to 1840 on
  `development`), the measured 2-D choice; the 3-D cost is #895. The note states it as
  "one block on each process" and prints no row count. Nothing left for you here.
- 2026-11-01, to the dev hub: your "rotated pressure rtol default" item. Per the notes
  session from kaiju's logs, Louis has approved `-uw_pres_rtol 1e-2` as the campaign
  default; in the np 16 annulus pair it took the Stokes solve from 441/410 s to
  183/174 s with the same answer, and the trench, restart and annulus runs had all used
  the library defaults (1e-3 Stokes, 1e-4 pressure, 3.3e-5 velocity). Whether the
  library default follows the campaign's is yours; the journal entry of 2026-11-01 on
  the annulus band ratio records the numbers.
- 2026-11-01, to the science hub: the production tail is the welded base with the split
  finest level and the FAC LU patch (Louis on #892). Kaiju's np 16 run is in
  (issuecomment-6552218825 is the corrected record; 6550915680 is superseded) and the
  default moves to 0 with the campaign builds; the
  2026-10-30 item on the drivers' chain comments is moot once that lands. When the
  driver commit exists, its sha closes the journal's decision entry of 2026-11-01 (a
  one-line message here or to the notes session is enough).
- 2026-11-02, to the science hub: Louis's decision (the add-on is the line, `DEV-HUB.md`
  e6832e0; journal decision entry of 2026-11-02) puts two items on the drivers:
  `uw_chain` defaults to 0, and the trace is placed at its own division, with no
  `uw_spacing` resampling and the band width not derived from an $S$. Both guides now
  say the fault's points are the rungs. **`uw_chain` 0 is done** (b440b88, acceptance
  job 3154; received 2026-11-02 through the notes session and recorded in the journal);
  the trace item remains.
- 2026-11-02, to the dev hub: the decision entry you asked the notes session to draft
  is committed (journal, with light edits; the 2026-11-01 decision stays live and this
  one settles its open item). Its "where enforced" leaves you `custom_mg.py:1556`
  naming itself the alternative and naming the add-on.

- 2026-11-05, to the dev hub, from the coarse-solve docs task (journal entry of
  2026-11-05): (1) for "one rule on every route", the shared bundle's redundant variant
  needs `mg_coarse_redundant_pc_factor_shift_type = "nonzero"`; on A-prime (77de8d81)
  the shift is set on the rotated route's live PC only, and `test_1021` reads the
  bundle. The docs branch assumes it. (2) PETSc's manual says its null-space handling is
  guaranteed only with left preconditioning and "may not work in some situations with
  KSPFGMRES", our outer solver. (3) `Ex_NS_Couette_Flow.py` does not compile on
  `development` (an indentation error at line 100, left by a print-to-pprint change).

- 2026-11-05, to the dev hub: PR #945 (the `svd` coarse-solve line out of 44 examples
  and tutorials, documentation only) is open against `development` for your queue; it
  is independent of A-prime and merges clean. Issue #944 (broken examples, no CI runs
  them) proposes a CI parse check and a scheduled smoke set, both yours to weigh.

- 2026-11-08, to the dev hub: (1) both reviews' changes are in and answered on the PRs:
  #945 (03d62f0d, body updated, development merged) and #862 (95a3b168, development merged
  at 86b17b0a); both green before the push and clean against `development`, ready for your
  merge on green. #861's `CLAUDE.md` conflict is resolved (63b4ec63, both paragraphs kept).
  (2) Your register of solver-default changes has no row for #947, which is one: the rotated
  route's coarse solve went from SVD to redundant LU, and the shared bundle gained the
  zero-pivot shift on every route. The CHANGELOG entry exists (from the docs branch); the
  switch back is `..._mg_coarse_redundant_pc_factor_shift_type = "none"`; the evidence is
  #901 and the 2026-11-05 journal entries. (3) #895's title ("one LU per rank") predates
  #934 (merged 2026-11-04 for issue #925), under which the structural rows of every
  fault, a network's included, are one LU on one rank at any rank count; the title and
  its framing may want updating (the notes session sent you the network point).

- **2026-11-08, to the dev hub, approved by Louis: compare the two-level FAC patch with
  #934's one block in parallel, before any 3-D work (schedule under #895).** Why: #934
  fixed #925 by gathering the structural patch into one block, one LU on one rank; with no
  zone keyed it holds every fault's rows, a network's included. The two-level form on
  `feature/fault-slip-coarse-space` (bounded ASM pieces plus one global slip coarse
  problem, a column per piece over every fault, factorised redundantly on every rank;
  design note `fault-slip-coarse-space-2026-10.md`) was held on 2026-11-02 on a serial
  iteration comparison (79-87 against 67), where one block always wins; its case is
  parallel time and memory, never measured. #934's own figures: owning rank at 1.6-2.2x
  the others' memory; a 61k-row block 66 s serial, 63 s at np 8 and 16. The run (2-D,
  kaiju, development plus the coarse-space branch brought up to date; it is 244 commits
  behind): fixtures UWTN 2026-022's linear fixture at h_b/S 24 and 48, a two-fault network
  whose faults land on different ranks, and a `seams="conform"` fault where one can be
  placed; arms one block (#934), two-level at `fac_block_rows` 2000 and at one rung, and
  per-rank pieces without the coarse space as the control; np 1, 4, 8, 16; record velocity
  iterations, velocity-solve wall time, patch set-up and factorisation time, peak memory
  per rank (max and min), coarse size, and the answer against one block. It feeds Louis's
  decision on whether the two-level form becomes the default for networks or all faults,
  and whether 3-D builds on it. If the branch cannot be brought up to date cheaply, say so
  before the run. (Sent to you directly and refused: cloud-to-cloud needs a trusted device.)

- **2026-11-10, HOLD on moved-refined-mesh claims (#1037, open).** On a mesh built with
  `refinement >= 1`, `mesh.deform` and every mover write only `mesh.dm`; solvers clone
  `dm_hierarchy`, whose finest level keeps the pre-move coordinates, so the solve runs on
  the old geometry with no warning (51 % off on a Poisson probe, 36-71 % on Stokes). Fix:
  H2's `bugfix/moved-mesh-hierarchy-coords`, stacked on #959. Relayed by the notes session
  from C1. Do not promote, cite or build on, until H2's check is in:
  - UWTN 2026-011's `figures/adaptive-convection.gif` (no script; build and refinement
    unknown; H2 checking a June build);
  - UWTN 2026-014's "the hierarchy survives it" for any guide or example that relaxes a
    refined mesh and then solves (`relax()` is one of #1037's movers; the mesh-only figure
    stands);
  - **our own docs**: `docs/advanced/multigrid-preconditioning.md`'s "Hierarchy and mesh
    adaptation" (line 89, the hierarchy survives the movers so FMG keeps working) and its
    FMG-vs-GAMG benchmark on an MMPDE-deformed refined annulus (line 316,
    `figures/bench_fmg_vs_gamg_velocity_ksp`), whose solves may have run on the pre-move
    coordinates; to check: `guides/adaptive-meshing.md` (moving-mesh convection) and the
    `preconditioner` docstring's "the hierarchy survives the coordinate-deforming
    adaptation movers".
  Not exposed: 2026-016 (unrefined box), 2026-022 (from its scripts and the placement
  code; drivers not read). Any correction to a published note is Louis's. The docs
  passages get rewritten when H2's PR lands, to describe the fixed code and rerun the
  benchmark, not before.
  **2026-11-10 (later), H2's verdict, relayed by the notes session from C1, not yet on
  GitHub and not verified here:** on the June build e19893ae the 2026-011 gif is exposed
  (REFINE 2, MMPDE every step; Stokes correct, the temperature's advection-diffusion
  assembled on the unmoved mesh); the multigrid benchmark's Stokes solves used the moved
  mesh, so its iteration comparison stands as a solver claim, but the temperature driving
  it carries the error; 2026-014's figure stands and its relax() sentence needs
  correcting after the fix. That Stokes and advection-diffusion saw different geometries
  is not what #1037's text predicts for every solver; holds stay until the verdict and
  the fix are on GitHub.
  **2026-11-10 (revised): H2 withdrew the June verdict.** The fix is PR #1044 (open,
  `bugfix/moved-mesh-hierarchy-coords`, `test_1172`), checked here: on a refined mesh a
  *scalar* solve after a move (deform, any mover, `relax()`) assembled on the pre-move
  coordinates (Poisson 51 % off, default PC and FMG alike); "Stokes was already right",
  and so are SLCN and SUPG. H2's 26 % SLCN error on the June build came from an older,
  since-fixed `_deform_mesh` defect, so the 2026-011 gif is unsettled either way: hold
  until H2 reruns the June case on current code (H2's 2e-6 and 26 % are not on GitHub).
  Our multigrid benchmark is Stokes plus advection-diffusion, so its answer is not shown
  wrong; its FMG iteration counts sit on a moved refined hierarchy whose coarse levels
  #1044 deliberately leaves unmoved, so leave that passage alone and do not cite the
  iteration curve as a moving-mesh result until someone confirms it. 2026-014's relax()
  sentence stays in scope for Poisson-type solves (#1044's test relaxes a refined annulus
  and solves FMG Poisson). Rewrites wait for #1044's merge.

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
- **The fault-split integration** (`FAULT-SPLIT-INTEGRATION.md`): A #882, B #889 and
  C #890 merged on 2026-10-31, with the #892 fix (#912) and `Mesh.multigrid_levels`
  (#915); `development` is 25d62812. Left: UWTN 2026-022's re-pin rides the notes
  session's rewrite; UWTN 2026-018's `software_version` can move to a `development`
  sha now (the wombat workbench holds its pen); the drivers' default after kaiju's
  np 16 run.
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
- 2026-10-31: **the sweep reverses the tail ruling, pending Louis and a fix.** Recording
  each level's smoother found that the FAC patch is installed only when the sole split
  level is the finest (no chain ever had it) and that the rotated path runs the patch as
  ILU(0), not the LU `custom_mg` configures (#892, on development too). With LU, the
  welded base with the split finest takes 3 velocity iterations per linear solve at
  every band ratio 6 to 25 on the yielding lid, 3 to 16 times fewer than any chain; with
  today's library the lean chain at ratio about 8 is still best. Journal entry written;
  topic page updated. For the dev hub: #892. For Louis: whether production moves to the
  welded base with the FAC LU patch once #892 lands, which changes the drivers'
  `uw_chain` default, both guides, and the note's multigrid section and panel (c).
  Results: `~/+Simulations/uwtn_2026_022_tail_sweep/` on wombat; nothing pushed.
- 2026-11-01: **the tail is ruled; A, B, C, the #892 fix and the levels accessor are on
  `development`.** The notes session relayed the corrected history of #892 (the LU
  blocks never ran on the rotated path; 891c9bb0 made composite and LU the defaults in
  one commit; not a regression from a working state), Louis's ruling on #892
  (issuecomment-6550186134: welded base + split S level + FAC LU patch; the chain is
  the alternative; the drivers' default after kaiju's np 16 run), #912 (cc839425) and
  #915 (25d62812), and that 022's hold is lifted and it is being rewritten on the
  workbench. Done here: journal decision entry with its closure lines and a finding
  entry for the history (the dev hub plan's step 7), the 2026-10-29 and 2026-10-30
  decisions marked superseded, the topic page's current understanding rewritten;
  `development` merged into `docs/fault-multigrid-guide` (#862; the index table
  conflict resolved, the convection guide added to the toctree it was missing from),
  the fault-multigrid guide's chain paragraph replaced by the ruled tail and its block
  rule rewritten, the faults-in-convection guide's hierarchy section, code and table
  rewritten to the welded tail with the chain as the labelled alternative. The dev
  hub's `PRIORITY` section read (a5e2cc8). Update comment posted on #862
  (issuecomment-6550318804). The reply to the notes session through the bridge was
  refused (HTTP 401); sent through the session service instead.
- 2026-11-01 (later): the notes session reports UWTN 2026-022 rewritten for the ruling
  and unsaved (details in the notes table). Its recipe ran verbatim on `development`
  25d62812. One question raised to the dev hub from that run: a single 4772-row LU
  block against the 2000-row cap. The three texts (022's multigrid section, the two
  guides) to be read against each other once 022 is saved.
- 2026-11-01 (later still): kaiju's np 16 annulus check is in (Louis on #892,
  issuecomment-6550915680): welded 5.9 against chain 7.7 velocity iterations per
  Newton increment, 448 against 467 s per step, same answers; both arms the same
  465-row patch, all of it on one rank (#895). Journal measurement entry; both guides
  cite it beside the fixtures and the parallel section records the serial patch
  (#862, pushed); topic page and `FAULT-SPLIT-INTEGRATION.md` updated. The drivers'
  default moves to 0 with the campaign builds (science hub). Noted for the wording
  everywhere: the factor of 3 to 16 measured the patch (chain without it against
  welded with LU); the tail's own gain, same patch on both, is a quarter of the
  iterations. **(Wrong on the second point; corrected in the next entry.)**
- 2026-11-01 (correction): kaiju's budget (jobs 2480 to 2488) corrected the np 16
  record (Louis on #892, issuecomment-6552218825; the notes session relayed it). The
  arms did not carry the same patch: in the multigrid the Stokes solve applies, the
  welded arm has a 3584-row patch on one rank and the chain none; the 465-row patch
  was a second multigrid under the solver's own prefix. The velocity work is equal
  (8.65 against 8.74 F-cycles per solve; the 5.9 against 7.7 counted only the last
  solve of each increment), the times are a wash within ±10 %, and the serial patch
  LU costs 21 to 28 s a step on one rank while 15 wait, 5 to 6 % of the solve, not
  "little". Done: a superseding journal measurement entry (the morning's np 16 entry
  marked superseded), the topic page bullet, both guides' np 16 sentences and the
  fault-multigrid parallel section (3584 rows, 5 to 6 %, one block per rank, no cap)
  on #862, this file and `FAULT-SPLIT-INTEGRATION.md`. The "quarter of the iterations"
  reading is withdrawn everywhere it appeared. Still open: why the annulus shows none
  of the box's gain (the science hub has been asked for the annulus band ratio). The
  block-rows question to the dev hub is answered and closed. UWTN 2026-018's
  `software_version` stays until the note is next checked against a `development`
  build (the notes session's call: moving the sha says the note was verified at it).
- 2026-11-01 (closing the annulus question): kaiju's chain page v4, relayed by the
  notes session: the annulus pair's band ratio is 3.9 ($h_b = 0.0156$, $S = 0.004$),
  below the sweep table's smallest (6.06), which is why the patch bought nothing
  there; the hierarchies as applied recorded. Journal finding entry; the "reason open"
  sentences in both guides replaced by the ratio (#862, pushed); topic page and
  `FAULT-SPLIT-INTEGRATION.md` updated. Also from kaiju's logs: the trench, restart
  and annulus runs used the library's default tolerances (1e-3 Stokes, 1e-4 pressure,
  3.3e-5 velocity), and Louis approved `-uw_pres_rtol 1e-2` as the campaign default
  (441/410 s to 183/174 s, same answer); passed to the dev hub below. Two np 16
  entries had an unquoted `#892` in their `authors` list, which YAML reads as a
  comment; the validator had reported it and the pipeline hid the exit code. Fixed and
  the validator now runs unpiped.
- 2026-11-01 (why the patch is on one rank): Louis's addendum on #892
  (issuecomment-6557052460), relayed by the notes session: the patch is on one rank by
  construction, because the drivers' default `seams="gather"` placement runs
  `partition_addon` first, which gives the band's region to one rank and balances the
  rest to within 10 %; not because the fault happens to lie in one partition. The
  serial patch cost at np 16 is the placement's, not the welded tail's.
  `seams="conform"` would divide it (needs `mesher="network"`; never run here; the
  dev hub's k-partitions test is its first run). Verified in the code
  (`place_surface.py` 7291, 9325). Done: journal finding entry; topic page; the
  fault-multigrid guide's parallel section restated by route (adapt-and-cut inherits
  the base's partition; the placement repartitions and chooses the rank), the
  "planned fix" sentence replaced since `partition_addon` is that fix; the convection
  guide's one phrase; `FAULT-SPLIT-INTEGRATION.md`. #862 pushed.
- 2026-11-02: **Louis's decision, the add-on is the line** (`DEV-HUB.md` e6832e0). The
  notes session, asked by the dev hub, drafted the journal decision entry and sent it
  here to commit; checked against e6832e0 (his words, the evidence table, the mesh
  counts, the two attribution points: "S = h_b or h_b/2" and corridor refinement were
  the dev hub's, not his; the split tip's "one element" awaits his word) and
  committed with light edits. The 2026-11-01 tail decision stays live; this entry
  settles its open item (split coarse levels: kept as they are, not developed
  further) and narrows its Allowed line. Done here: topic page (new first bullet, the
  open item closed, the ribbon replay retired); the fault-multigrid guide gains
  ruling 4 (the fault carries its own resolution; no $S$ parameter; refinement around
  the fault separate; split levels not developed further), ruling 3's 2:1 clause
  marked as the chain's, the production paragraph and the split-level section
  updated; the convection guide's recipe takes the trace's own points and a width,
  and its "not decided" sentence is closed (#862 pushed). For the science hub: the
  drivers' `uw_chain` to 0 and the trace placed at its own division without
  `uw_spacing`. For the dev hub: `custom_mg.py:1556` to name itself the alternative.
- 2026-11-02 (later): two closures from the science hub through the notes session,
  both verified on `lmoresi/uw3-campaigns`. (1) The drivers default to `uw_chain 0`
  (b440b88 on `zg95-annulus-for-kaiju`, the three drivers; build moved to
  `development` 25d62812; acceptance kaiju job 3154: vrms 1358.9188, slip 5877.77,
  Newton 6, walls clean to 1e-12, equal to the chain-0 reference), and the drivers'
  decisions ledger `zg95_lid_regimes/DECISIONS.md` (bf18312) is the citable record
  per Louis's ruling. That closes the last "where enforced" line of the 2026-11-01
  tail decision: journal measurement entry; topic page; both guides state the default
  as done and cite the ledger. (2) `seams="conform"` cannot place a wall-reaching
  fault in 2-D (the network mesher's cavity reaches the domain wall; serial repro on
  kaiju, `HUB.md` 29cd738), and the ladder takes only gather, so the patch cannot be
  divided across ranks in the trench models and the k-partitions test cannot run there
  until one changes: journal dead-end entry; the fault-multigrid guide's parallel
  section and closing paragraph rewritten from "never run here, first run pending" to
  the limit; topic page. #862 pushed.
- 2026-11-03: **Louis's clarification of 1b: the fault's division and the band's width
  are not knobs** (to the science hub; ledger principle row at febbb87, HUB.md 7efb5ef).
  The notes session drafted the journal decision entry; verified against both and
  against the code on `development` af6f19b3 (the points become the spine verbatim; the
  rails sit at half the width) and committed with light edits. New against 2026-11-02:
  the band is as wide as the local mesh size (an average where the mesh is not uniform),
  so about half the drivers' $2S$; `uw_spacing` (one base cell since 2026-11-02) is
  marked for removal; nothing has run with a one-cell band yet, kaiju is drafting the
  driver change with an offline placement check first. Done here: topic page bullet;
  ruling 4 in the fault-multigrid guide carries the width half, the production
  parenthetical updated; the convection guide's recipe says width is the local mesh
  size and that every measurement used $2S$ (#862 pushed). Also noted: the campaign
  branch is merged into uw3-campaigns `main` (febbb87), so b440b88 and the ledger are on
  GitHub now; yesterday's "push the campaign work" item is closed.
- 2026-11-03 (later): **corrected: the ladder is equant** (Louis on kaiju's design page,
  the same day; ledger 017b84d principle and `uw_spacing` rows, HUB.md 1575048). The
  "one local cell wide" reading in this morning's entry was the hubs', not his: the
  half-width is one cell, the band two cells wide, the rungs about one cell apart, which
  is recipe v2 as it stands (`uw_spacing 0` derives one base cell, $W = 2S$; the knob
  stays only as the derivation's override). Kaiju's division design (f393fd7) is shelved
  as input for a library plate-boundaries module; the v2 baselines (TAf-v2, Earth run 2)
  are launched. Done here: the notes session's corrected entry committed with light
  edits; this morning's entry marked superseded by it (its principle and Louis's quote
  are carried forward, so a reader meets the right width); the topic page bullet; ruling
  4, the production parenthetical and the convection recipe on #862 give the equant form
  (pushed with absolute paths this time); `FAULT-SPLIT-INTEGRATION.md`. Nothing is now
  owed on the drivers for the ladder.
- 2026-11-03 (later still): the notes session moved #595's evaluation (cutting a thin
  labelled band along its centre-line can snap a band-boundary vertex onto the cut; the
  cut-in-band configuration of 2026-08-17) off wombat to sit beside UWTN 2026-022 at
  `figures/src/cut_in_band_595/`, per Louis's agreement through the science hub and his
  2026-10-29 ruling that notes cite their own `figures/src/` copies. Unsaved; it commits
  with the note. Recorded in the 022 row. A journal measurement entry linking it follows
  once it has a commit to cite.
- 2026-11-05: **coarse-solve docs, one rule, no SVD** (Louis's task through the
  integration session; both of his messages checked in its transcript). Done: journal
  decision entry and solvers topic page (5331ae1); #862's coarse-level rule points to the
  multigrid page (c2ea1565, pushed); `docs/coarse-solve-one-rule` (42e55655, stacked on
  A-prime: the advanced guide and three subsystem docs give one rule, the `svd` override
  example replaced by taking the shift off, the SVD history moved to the changelog;
  Sphinx clean); `docs/examples-no-svd-coarse` (b88c9fd9, off `development`: the `svd`
  line out of 16 box and Dirichlet examples and tutorials). Both branches local,
  awaiting Louis's permission to push. Left: 28 curved or periodic examples, after the
  bundle shift and a run.
- 2026-11-05 (later): Louis gave permission; both branches pushed (42e55655, b88c9fd9).
  The bundle-shift line needs no ruling ("in line with how we work: removing multiple
  paths where we can"); sent to the integration session, A-prime's owner, with the ask to
  merge the docs branch into A-prime. Hyperion has Claude, but its one session is the dev
  hub's and its build is on hold pending Louis's disk check, so the 28-example run waits.
  Brief for whoever runs it: on A-prime plus the bundle line, each curved or periodic
  example with and without its `svd` line, recording convergence, velocity iterations
  and the solution against the `svd` run.
- 2026-11-05 (later still): Louis: hyperion's disks are still in flux, but UW can be
  built and run there for testing, with the build and outputs liable to vanish unless
  copied. Brief sent to the hyperion Remote Control session ("hyperion-abstract-token",
  session_01HxWvnAXb5n85uEcw711tJC): build `docs/coarse-solve-one-rule` plus the
  bundle-shift line locally (not pushed), run the 28 examples in two arms, report a
  table to this hub after the user-facing batch and at the end.
- 2026-11-05: A-prime (`bugfix/rotated-fmg-coarse-solve`) is at 4af44735: the docs
  branch fast-forwarded in, plus the bundle shift on every route (`test_1021` reads it
  off the live coarse KSP on the native, custom-P and rotated routes; native and
  custom-P annulus FMG bitwise identical with and without it). The integration session
  corrected two of the docs hub's sentences, both verified against the code: plain LU
  without the shift did not stop on the singular level in `test_1111` (it converged
  5e-7 off), so "it stops with DIVERGED_PC_FAILED" was wrong; the rotation tolerance is
  a relative 1e-8. Docs build clean at 4af44735. Hyperion told to build that commit,
  pinned. A-prime is taking a development merge; its PR stays unopened per the dev hub.
  The journal decision's "where enforced" is closed by one entry when the example run
  reports, not before.
- 2026-11-05: hyperion's user-facing batch (17 files, two arms, np 1, on the
  docs branch plus the bundle line, code-identical to 4af44735). Every example builds
  its mesh without refinement, so the velocity block fell back to GAMG: the `svd` line
  only replaced GAMG's coarse solve, and the new geometric rule did not run (A-prime's
  tests cover that). Where the solve ran, removing the line changed nothing (five
  examples, same u and p to 1e-9 or better, same iterations; no zero pivot anywhere);
  tutorial 8 does not converge in either arm. Twelve of the 17 fail for unrelated
  reasons on `development`: a removed `evalf` API, three-index array shapes, pint units,
  `estimate_dt`, and two files that do not parse; 9 of the 230 example scripts do not
  parse and 33 files still call `evalf`. The `svd` line is now out of all 17
  (`docs/examples-no-svd-coarse` 24727cdc, pushed). One issue drafted for the broken
  examples (CI parse check, a scheduled smoke set, fix or retire); filing it was
  refused by the classifier, so it waits for Louis. Investigation batch still running.
- 2026-11-05 (close): hyperion's investigation batch: nine of the eleven submesh scripts
  give the same answer to 1e-11 or better; `test_region_ds_phase3` segfaults and
  `test_bootstrap_viscosity` stalls at the 20-minute cap, both in both arms. The `svd`
  line is out of all 44 files (`docs/examples-no-svd-coarse` 32966c18, pushed). Journal
  measurement entry closes the decision's open lines except the two merges (75a9c47).
  The broken-examples issue draft gains the two investigation failures; still waiting
  for Louis to file it or approve the call. No PR opened for the examples branch.
- 2026-11-05: with Louis approving the calls: the broken-examples issue filed as
  **#944** (through the GitHub connector; the shell route had been refused), and the
  examples branch opened as **PR #945** against `development` after the adversarial
  review (no stale SVD text in the 44 files, no docs warnings on them, merges clean;
  #901 live and fixed by A-prime, #944 live, #306 closed).
- 2026-11-08: state check after three days. #947 (the coarse-solve rule, with the docs)
  merged 2026-11-05 and Louis closed #901. Hyperion's adversarial reviews of #945 and #862
  (posted 2026-11-06, routed here by the dev hub) were unanswered; now done: #945's empty
  code fences in tutorials 8 and 15 removed with the sentence that recommended the SVD
  rewritten to the rule, body corrected, development merged; #862's status line fixed,
  the structural-block rule rewritten for #925 (one LU on one rank at any rank count; the
  earlier "one block per rank" was true only before 2026-11-03), the refusal quoted in
  full, sources named, development merged; replies on both PRs. #861's conflict with
  `development` in `CLAUDE.md` resolved and pushed. Items for the dev hub above; 022's
  "one block on each process" sent to the notes session.
- 2026-11-08 (later): the notes session corrected two points in #862's guide, both
  checked against `custom_mg._gathered_patch_blocks`: the change is PR #934 (merged
  2026-11-04, for issue #925, still open), not "#925 merged 2026-11-03"; and with no zone
  keyed all of a network's faults form one structural block on one rank, so the guide's
  "a few bands per rank" was wrong for the LU. Guide fixed (b74af785), correction posted
  on #862. 022 keeps its 25d62812 pin, so its "one block on each process" stands for that
  build; re-pinning is Louis's call and would mean rerunning the recipe and figure (c).
- 2026-11-12: **the notes' correction convention is settled.** Louis asked for #51 to be
  merged. Every build had been failing since 2026-11-11 because the unpinned MyST theme
  outran the repository's mystmd; #63 pins the theme to 1.4.1 (merged, 79dcb33d), then #51
  ("An updated note says what changed, and where the old one is": a `## History` section
  per deposited version, dated, with the version DOI, what changed and what did not) was
  updated and merged on green (352d44e3). Corrections to 2026-011 and 2026-014 follow this
  form, if Louis decides on them. `preview` still fails on every PR (PREVIEW_TOKEN).
  Movies: proposed MP4 in `{figure}` on the page, a still frame and DOI link in the PDF,
  the file in the note's own Figshare record (needs `scripts/deposit.py` to accept
  declared extra files; it refuses them today); waiting on Louis.

- 2026-11-12 (later): Louis's go on movie preparation and pinning. Notes #65 (movie
  figures: MP4 plays on the site, `build_pdf.py` swaps it for its `:placeholder:` still
  for the PDF, `deposit.py` uploads each movie to the record, CONTRIBUTING convention,
  tests) and #64 (mystmd pinned to 1.10.1 with the theme): both green on `build` and
  `test`, not merged, Louis to say. The journal's theme pinned to 1.4.1 (0713e7a, built
  with its mystmd 1.6.7). The MMPDE note's listing thumbnail is probably its GIF (no
  `thumbnail:` set; the header itself is an Unsplash photo); the movie and still come
  from H2's rerun, the fault note's from the K1 runner.
- 2026-11-12: Louis: the MMPDE note's movie is re-encoded from the June run's original
  frames (wombat is finding them), not replaced by a new run; the fishing-net header
  stays. Held until H2's rerun says whether the June run is affected by the older
  moved-mesh defect; if it is, H2's frames are used instead.
- 2026-11-12 (later): Louis lifts the hold: the June run's movie goes in whatever
  #1037's answer ("I think it must be OK and I can live with it"). The wombat session
  "OT movie / MMPDE" (session_01HxWvn6XCQDRSUeRvJZX1kq) has the 239 PNG frames and the
  checkpoints; it was sent #65's form (MP4 + still + placeholder + thumbnail, script in
  figures/src, GIF removed, a `## History` entry per #51). This hub checks the branch
  builds before it goes to Louis.
- 2026-11-12: the "OT movie / MMPDE" session reports the UWTN 2026-011 movie done on a
  local wombat branch `movie/moving-the-mesh-without-remaking-it` (851e135, off main,
  six files in the note's folder), NOT pushed: its standing rule needs Louis's word.
  864x864 H.264, 24 fps, 250 frames from the clean render set (the set the GIF was cut
  from), CRF 23, 7.5 MB; still = step 65; `figures/src/encode_movie.py`; GIF removed;
  version 1.1.0 with a History entry. Its checks: validate passes; #65's swap leaves
  the still only. The PDF build needs #65 merged first. Renderer not shipped (June
  watcher, old data access); accepted, the encode script names it.
- 2026-11-12 (wrap-up, on Louis's "get this wrapped, I'll approve whatever you need"):
  notes #65 (movie figures) and #64 (mystmd pin) merged; Louis's #66 (UWTN 2026-011's
  movie from the run's own frames) updated from main, its PDF built here and inspected
  (step-65 still, caption, History, version 1.1.0), merged; site deployed; the
  `new-version` deposit run published record 33241170 v2
  (10.6084/m9.figshare.33241170.v2) with the PDF, `adaptive-convection.mp4` and the
  archive; #67 (identifiers) and #68 (the version DOI in the History entry) merged.
  CI's `pdf` job on a PR skips the build unless asked, so a movie note's PDF is first
  proven at deposit unless built by hand. Standing: Louis approves prompts; ask before
  publishing a note, not for green infrastructure PRs.
- 2026-11-12, captured for later (from the "OT movie / MMPDE" session, at Louis's
  request): **the notes' PR previews have not deployed since late October.** The
  `preview` workflow fails at its publish step on every PR: `Authentication failed` for
  `underworldcode.org-preview.git`, pushed with `secrets.PREVIEW_TOKEN`
  (`.github/workflows/preview.yml`, line 129). Last success 2026-10-02 (run
  36973392038); first failure 2026-10-25; all 29 runs since failed, #65-#69 included.
  Likely an expired personal token (not checked). `preview` is not a required check, so
  merges and deposits go through, but no PR gets a preview link, and the MMPDE 1.1.0
  change was published without one. **Louis's to fix:** a new token with push access to
  `Underworld-Technical-Notes/underworldcode.org-preview`, saved as `PREVIEW_TOKEN` on
  `underworldcode.org`; re-run a recent preview job to confirm.
