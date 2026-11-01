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
| hyperion | `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra"): reimaged 2026-10-27; owner of several fix branches below |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H` ("kaiju: rollback experiments"): no GitHub credentials; fixes arrive as patches through a hub |
| kaiju, 3-D add-on mesh owner | `session_01HxWvn87Vw8gzXsEHJ7iF8u` ("kaiju: 3-D add-on mesh"), created by the dev hub 2026-10-31 on Louis's word; milestones M0-M4 of the 3-D plan, #900 first; patches come through the dev hub |

## Access (measured 2026-10-29)

| What | State |
|---|---|
| `underworldcode/underworld3` | attached with push; the token's repository role is admin |
| `lmoresi/uw3-campaigns`, `underworldcode/underworld3-journal` | attached with push |
| **GitHub text (Louis, 2026-10-31)** | this hub's proxy appends a "Generated by Claude Code" footer to every body and comment it writes, edits included, and Louis wants the original attribution only. So **the hub drafts and a laptop session posts** issues, comments and PR bodies, with Louis's credentials. The notes session (`session_011S876ckjYqqth1aPyojrhh`) posts the hub's drafts on Louis's account (comments, relabels, issues; edits and deletes of existing text go to Louis). The integration session files its own findings directly (Louis, 2026-11-01). The hub keeps merges, retargets and labels, which carry no text. The integration session strips the footers already posted |
| GitHub REST (`gh api repos/...`) | works. Paginate by `&page=N`: `gh api --paginate` follows `repositories/{id}` links, which the proxy refuses |
| GitHub GraphQL (`gh issue list`, `gh pr list`, `gh project`, Project 10) | refused from cloud sessions. `scripts/triage.py` uses `gh issue list`, so it does not run here |
| Review threads, auto-merge, ready-for-review | through the proxy's `pulls/{n}/ccr/...` REST routes |
| Branch deletion | refused by the proxy (docs hub, 2026-10-27); a laptop or Louis deletes |

## Standing rules (team)

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
| 2 | Parallel: a long fault crossing k partitions, k = 1, 2, 4, 8 | The patch becomes one block per rank crossed, like the cut blocks that lost in 2-D (79-87 against 67). The add-on partition gathers one fault onto one rank at np 16 today | kaiju rollback rig, after the scaling job; needs #902's fix for np > 16 |
|   | *Row 2 baseline, np 16 (kaiju budget v3, jobs 2480-2488, via the science hub):* H0's finest patch (3584 rows) sits on the one rank holding the fault. Its solve is 21-28 s of a 410-441 s Stokes solve (5-6 %), while 15 ranks wait (max/min 165-178). Velocity work is equal to the chain (8.65 against 8.74 F-cycles per solve), and times are a wash within the ±10 % spread. So at production scale H0 is not yet a speed win, only simpler; the imbalance is what row 2 must measure as the fault spreads | |
| 3 | Cover gate: a small domain with a fine band (patch above 75 % of the level) | The global 0.75 gate declines the patch and falls back to whole-level SOR, silently. The 022 fixture is already 63 % at ratio 24 | integration session, laptop |
|   | *Row 3 measured (2026-11-01, the 022 linear fixture, np 1 and 2):* at h_b/S 48 and 97 the patch-plus-halo is 76 % and 86 % of the finest level. **The gate declines it silently**: whole-level SOR takes 909 and 1487 velocity its, against 66 with the gate forced open and 302 and 725 for H1, with slip off by 7e-5 at ratio 97. The 0.75 threshold separates by size, but a uniform level is 100 % subdomain with no background, while a fault level keeps 14-38 % background. **Proposed fix (Louis to rule):** decline only when the background outside the subdomain is under 2 % of the level, and log the verdict either way. The single structural LU block reaches 61,360 rows (86 % of the level) at ratio 97, which bears on row 1 | |
| 4 | Interface laws: friction, viscous, rate-and-state | Not yet measured on the welded tail with LU blocks (after #894's refresh) | integration session, the box at np 4 |
|   | *Row 4 so far (the box, np 4, S 0.004):* viscous law (η_f 555.7): H0 125 against H1 388 velocity its, same 29 Newton its, same slip. Coulomb and rate-and-state are re-running: they hit the rotated loop's 50-iteration cap in the Picard phase under both hierarchies, with no linear trouble. Side finding: the rotated path's `max_it=50` ignores a user's `snes_max_it` | |
| 5 | Fault networks: junctions, several faults per rank, TI and unsplit bands | Overlapping patches, block coupling at junctions, TI's zone blocks against the structural block | integration session (2-D); 3-D session later |
| 6 | Memory of the LU fill per rank | 3-D especially; the largest block and the fill per rank | kaiju (with 1 and 2) |

**Done when:** every row has a measurement. Then Louis rules whether split coarse levels
are deleted, kept as an option, or kept for named cases.

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

## Open pull requests (2026-10-31, `development` at fc67b650)

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

- After #892's fix and the re-measurement: the production multigrid tail for faults
  (welded base with the FAC LU patch, or the chain).
- Confirm the role above (proposes and briefs on your go; never approves or merges).
- The next merges: #780, #861, and #862 after its caveat; whether the hub re-reviews
  gthyagi's fixes on #855, #858, #859.
- An owner for #800 (conflicts with `development`, idle since 2026-10-12) and for the
  mathematical review of #857.
- Go-ahead for the label fixes listed under "Issue queue".
- Who takes the no-PR fixes now that hyperion is reimaged: the stress-transport fix first
  (verified, reviewed, waiting only for a PR).
- The rotated pressure rtol default (kaiju's evidence, in HUB.md).

## For the other hubs

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
