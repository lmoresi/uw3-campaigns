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
| hyperion | `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra"): reimaged 2026-10-27; owner of several fix branches below. Later Remote Control session `session_01HxWvn92dmiWUj5FX68AZc7` ("hyperion-transient-chipmunk"): **out again 2026-11-04** (OS on the wrong disk; reboot and reimage). Nothing on hyperion was unpushed; the Science Hub has the inventory. Assign no hyperion work until it is back |
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

## PRIORITY: the rotated path's FAC patch blocks run ILU(0), not LU (#892)

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

## Open pull requests (2026-11-04, `development` at f631ce42)

**Merged 2026-11-01 to 11-04 on Louis's word:** #912 (#892), #913 (#894), #914 (#896),
#915 (levels accessor), #916 (#907), #929 (squash, 6321c714), #928 (d9783f02), #927
(f53bbffb), #926 (e7dfbf9a), #930 (af6f19b3), then the stack #932 (2556c979), #933
(4ee0b13d), #934 (60dbf0e4), #937 (#902, c514013f), #938 (#935, f631ce42). The ten PRs in
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
| Rotated free slip with the analytic wall normal: from np 24 an owned outer-wall vertex can get no constraint row. No-solve repro on unfaulted TAc: np 16 none missing, np 32 three missing, two of them with a labelled facet on their owning rank, so the cause is wider than "facets all on other ranks". Solved at np 32, the wall-normal velocity reaches 1.2e4. The geometric normal is clean at np 32 but admits the rigid rotation (#906) | kaiju, 2026-11-04 | #935 | filed by kaiju through the science hub. Blocks np > 16 on the annulus with either normal until #935 or #906 lands. Not a duplicate of #906 or #896. **Cause (integration session, from the code):** the analytic path takes wall nodes only from facets labelled on the rank; the geometric path also walks the support-1 closures and sums over the SF (#560). Driver workaround: uw3-campaigns `addon-matrix-2026-11` 02439b0, `workaround_analytic_normal_nodes.py` (bit-identical serially; kaiju to verify at np 32-52). **Fixed on `bugfix/analytic-normal-wall-nodes-935`** (30daa324 on 60dbf0e4; review round 2 running): the analytic node set is completed over the point SF, and so is the free surface's vertex list (same defect). test_1140 fails before and passes after at np 2 and 4. Kaiju report 22b, zg95 TAc np 32, one step: 964 s against 280 s, next dt 2.66e-6 against 4.44e-6, wall |v.n| 1.2e4 against 3.4e-13. The "second path" in #935 was a misread vertex label. **Louis said yes to the PR (2026-11-04)**; the integration session opens it after review round 2 |
| `boundary_normal_traction` reads uninitialised pooled memory at a node an essential wall also constrains (a rotated wall meeting a Dirichlet wall); `globalToLocal` skips constrained DOFs | #935's review round 1 | #936 | filed; predates the branch. **Louis ruled zero (2026-11-04).** **PR #942** (29bf332f, two review rounds, test_1141 first). One helper feeds both readers; pointwise values byte-identical wherever no essential wall meets the rotated one; the integral now keeps a corner whose first component is pinned (it dropped 12 % of the wall load on the fixture) |
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
